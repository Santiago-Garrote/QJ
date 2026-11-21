"""Extra #22: one stretched point of H4 on a real IBM machine, emulated locally first.

Modes:
    python scripts/ibm_hardware.py emulate [backend]   # local AerSimulator with the backend's CURRENT noise (no QPU time)
    python scripts/ibm_hardware.py submit  [backend]   # same circuits on the real QPU; saves the job id
    python scripts/ibm_hardware.py fetch   <job_id>    # waits for / downloads the job and computes E +- sigma

Credentials come from the account saved with QiskitRuntimeService.save_account (never stored in the repo).
Outputs go to results/ibm_<mode>.json (git-ignored).

Circuit: the notebook's ansatz building blocks (cells 4 and 12 of notebooks/h4_vqe.ipynb: contract + Givens excitations),
restricted to the N_OPS operators with the largest energy gradient at HF, angles fitted with statevector (allowed).
Energy: SamplerV2 counts on qubit-wise-commuting groups, E and sigma from the bitstrings (same estimator idea as #6).
"""
import json
import os
import sys
import time

import numpy as np
from pyscf import fci, gto, scf
from qiskit import ClassicalRegister, QuantumCircuit
from qiskit.quantum_info import SparsePauliOp, Statevector
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from scipy.optimize import minimize

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from h4_reference import h4_molecule, qubit_hamiltonian  # noqa: E402  (contract convention: alpha q0-q3, beta q4-q7)

D_POINT = 2.4          # Å, stretched point
N_OPS = 2              # operators kept in the short ansatz (full one is ~465 cz: noise-dominated on hardware)
SHOTS_PER_GROUP = 4000
SEED = 22

# --- notebook building blocks (contract + ansatz cell), executed from the notebook itself to stay identical ---------
nb = json.load(open(os.path.join(ROOT, "notebooks", "h4_vqe.ipynb"), encoding="utf-8"))
ns = {}
code = [("".join(c["source"])) for c in nb["cells"] if c["cell_type"] == "code"]
exec(next(s for s in code if s.startswith("# Contrato compartido")), ns)
exec(next(s for s in code if s.startswith("# Ansatz elegido (#4)")), ns)
OPS, HF = ns["ANSATZ_OPS"], ns["HF_BITSTRING"]


def short_circuit(ops, thetas):
    qc = QuantumCircuit(8)
    for q, bit in enumerate(reversed(HF)):
        if bit == "1":
            qc.x(q)
    for t, (_, kind, p, q) in zip(thetas, ops):
        if kind == "D":
            ns["givens_double"](qc, t, ns["alpha_qubit"](p), ns["beta_qubit"](p), ns["alpha_qubit"](q), ns["beta_qubit"](q))
        else:
            ns["givens_single"](qc, t, ns["alpha_qubit"](p), ns["alpha_qubit"](q))
            ns["givens_single"](qc, t, ns["beta_qubit"](p), ns["beta_qubit"](q))
    return qc


_HMAT = {}


def energy_sv(H, ops, th):
    """<psi|H|psi> with a cached dense 256x256 matrix (much faster than SparsePauliOp expectation per call)."""
    key = id(H)
    if key not in _HMAT:
        _HMAT[key] = H.to_matrix()
    v = Statevector(short_circuit(ops, th)).data
    return float(np.real(np.conj(v) @ (_HMAT[key] @ v)))


_CACHE = {}


def build_problem(n_ops=None):
    """Greedy ADAPT-style selection over the DISTINCT excitations of the notebook ansatz: at each step add the one with the
    largest |dE/dθ| at the current optimum, then refit all angles (statevector; parameter search only)."""
    n_ops = N_OPS if n_ops is None else n_ops
    if "base" not in _CACHE:
        mol = h4_molecule(D_POINT)
        mf = scf.RHF(mol).run()
        _CACHE["base"] = (qubit_hamiltonian(mol, mf), float(fci.FCI(mf).kernel()[0]))
    H, e_fci = _CACHE["base"]
    pool = list({(k, p, q): (0, k, p, q) for (_, k, p, q) in OPS}.values())
    snaps = _CACHE.setdefault("snaps", {0: ([], np.zeros(0))})
    start = max(k for k in snaps if k <= n_ops)
    chosen, th, h = list(snaps[start][0]), snaps[start][1].copy(), 1e-4
    while len(chosen) < n_ops:
        grads = [abs(energy_sv(H, chosen + [op], np.append(th, h)) - energy_sv(H, chosen + [op], np.append(th, -h))) / (2 * h)
                 if op not in chosen else -1 for op in pool]
        chosen.append(pool[int(np.argmax(grads))])
        r = minimize(lambda t: energy_sv(H, chosen, t), np.append(th, 0.0), method="BFGS")
        th = r.x
        snaps[len(chosen)] = (list(chosen), th.copy())
        print(f"  greedy: {len(chosen)} ops, noiseless err {(r.fun - e_fci) * 1e3:+.2f} mHa", flush=True)
    e_hf = energy_sv(H, [], [])
    return H, chosen, th, dict(d=D_POINT, n_ops=n_ops, e_fci=e_fci, e_hf=e_hf, e_short_noiseless=energy_sv(H, chosen, th),
                               ops=[list(map(str, o)) for o in chosen], thetas=th.tolist())


def measurement_circuits(qc, H):
    """One circuit per qubit-wise-commuting group: basis change on logical qubits, measure logical q -> clbit q."""
    groups = H.group_commuting(qubit_wise=True)
    circs = []
    for g in groups:
        basis = ["I"] * 8
        for lab in g.paulis.to_labels():
            for k, ch in enumerate(reversed(lab)):
                if ch != "I":
                    basis[k] = ch
        c = qc.copy()
        for k, ch in enumerate(basis):
            if ch == "X":
                c.h(k)
            elif ch == "Y":
                c.sdg(k)
                c.h(k)
        c.add_register(ClassicalRegister(8, "m"))
        c.measure(range(8), range(8))
        circs.append(c)
    return groups, circs


def energy_from_counts(groups, counts_list):
    e, var = 0.0, 0.0
    for g, counts in zip(groups, counts_list):
        labels, coeffs = g.paulis.to_labels(), g.coeffs.real
        masks = [sum(1 << k for k, ch in enumerate(reversed(l)) if ch != "I") for l in labels]
        vals, weights = [], []
        for bits, n in counts.items():
            x = int(bits, 2)
            vals.append(sum(c * (1 - 2 * (bin(x & m).count("1") & 1)) for c, m in zip(coeffs, masks)))
            weights.append(n)
        vals, weights = np.array(vals), np.array(weights, float)
        N = weights.sum()
        mean = float((vals * weights).sum() / N)
        e += mean
        var += float(((vals - mean) ** 2 * weights).sum() / (N - 1)) / N
    return e, float(np.sqrt(var))


def counts_of(pub_result):
    return pub_result.data.m.get_counts()


def main():
    mode = sys.argv[1]
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as RuntimeSampler
    service = QiskitRuntimeService()

    if mode == "fetch":
        job = service.job(sys.argv[2])
        meta = json.load(open(os.path.join(ROOT, "results", "ibm_submit.json"), encoding="utf-8"))
        H, chosen, th, info = build_problem()
        groups, _ = measurement_circuits(short_circuit(chosen, th), H)
        print("status:", job.status())
        res = job.result()
        e, s = energy_from_counts(groups, [counts_of(r) for r in res])
        out = {**meta, "status": "done", "energy": e, "sigma": s, "err_vs_fci_mHa": (e - info["e_fci"]) * 1e3,
               "counts": [counts_of(r) for r in res]}
        json.dump(out, open(os.path.join(ROOT, "results", "ibm_hardware.json"), "w"), indent=1)
        print(f"HARDWARE {meta['backend']}: E = {e:.6f} ± {s * 1e3:.2f} mHa | err vs FCI {(e - info['e_fci']) * 1e3:+.1f} mHa")
        return

    backend = service.backend(sys.argv[2] if len(sys.argv) > 2 else service.least_busy(operational=True, simulator=False).name)
    if mode == "scan":
        # emulate several ansatz sizes with the backend's current noise and report the best trade-off
        from qiskit_aer import AerSimulator
        from qiskit_aer.primitives import SamplerV2 as AerSampler
        nm = AerSimulator.from_backend(backend).options.noise_model
        pm = generate_preset_pass_manager(optimization_level=3, backend=backend, seed_transpiler=SEED)
        rows = []
        for n in [int(x) for x in (sys.argv[3] if len(sys.argv) > 3 else "1,2,3,4,6,8").split(",")]:
            H, chosen, th, info = build_problem(n)
            groups, circs = measurement_circuits(short_circuit(chosen, th), H)
            isa = pm.run(circs)
            res = AerSampler(seed=SEED, options={"backend_options": {"method": "density_matrix", "noise_model": nm}}).run(
                [(c, None, SHOTS_PER_GROUP) for c in isa]).result()
            e, s = energy_from_counts(groups, [counts_of(r) for r in res])
            row = dict(n_ops=n, cz=pm.run(short_circuit(chosen, th)).count_ops().get("cz", 0),
                       noiseless_mHa=(info["e_short_noiseless"] - info["e_fci"]) * 1e3, emulated_mHa=(e - info["e_fci"]) * 1e3,
                       sigma_mHa=s * 1e3, hf_mHa=(info["e_hf"] - info["e_fci"]) * 1e3)
            rows.append(row)
            print(f"n_ops={n:2d} cz={row['cz']:3d} noiseless {row['noiseless_mHa']:+7.1f} mHa | emulated {row['emulated_mHa']:+7.1f} ± {row['sigma_mHa']:.1f} mHa", flush=True)
        json.dump(dict(backend=backend.name, d=D_POINT, rows=rows), open(os.path.join(ROOT, "results", "ibm_scan.json"), "w"), indent=1)
        return
    H, chosen, th, info = build_problem()
    qc = short_circuit(chosen, th)
    groups, circs = measurement_circuits(qc, H)
    pm = generate_preset_pass_manager(optimization_level=3, backend=backend, seed_transpiler=SEED)
    isa = pm.run(circs)
    cz = [c.count_ops().get("cz", 0) for c in isa]
    info.update(backend=backend.name, n_groups=len(groups), shots_per_group=SHOTS_PER_GROUP,
                cz_ansatz_logical=pm.run(qc).count_ops().get("cz", 0), cz_per_circuit_max=max(cz),
                depth_max=max(c.depth() for c in isa))
    print(json.dumps({k: v for k, v in info.items() if k != "thetas"}, indent=1))

    if mode == "emulate":
        from qiskit_aer import AerSimulator
        from qiskit_aer.primitives import SamplerV2 as AerSampler
        sim = AerSimulator.from_backend(backend)  # current calibration of the real device (gate + readout errors)
        t0 = time.time()
        sampler = AerSampler(seed=SEED, options={"backend_options": {"method": "density_matrix", "noise_model": sim.options.noise_model}})
        res = sampler.run([(c, None, SHOTS_PER_GROUP) for c in isa]).result()
        e, s = energy_from_counts(groups, [counts_of(r) for r in res])
        info.update(mode="emulate", energy=e, sigma=s, err_vs_fci_mHa=(e - info["e_fci"]) * 1e3, seconds=time.time() - t0)
        json.dump(info, open(os.path.join(ROOT, "results", "ibm_emulate.json"), "w"), indent=1)
        print(f"EMULATED {backend.name}: E = {e:.6f} ± {s * 1e3:.2f} mHa | err vs FCI {(e - info['e_fci']) * 1e3:+.1f} mHa "
              f"| noiseless short {(info['e_short_noiseless'] - info['e_fci']) * 1e3:+.1f} mHa | HF {(info['e_hf'] - info['e_fci']) * 1e3:+.1f} mHa "
              f"| {time.time() - t0:.0f} s")
    elif mode == "submit":
        sampler = RuntimeSampler(mode=backend)
        job = sampler.run([(c, None, SHOTS_PER_GROUP) for c in isa])
        info.update(mode="submit", job_id=job.job_id(), status="submitted")
        json.dump(info, open(os.path.join(ROOT, "results", "ibm_submit.json"), "w"), indent=1)
        print("JOB", job.job_id(), "on", backend.name)


if __name__ == "__main__":
    main()
