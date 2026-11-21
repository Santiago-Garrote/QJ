"""Extra #22 + #13: error mitigation for the hardware point (readout correction + zero-noise extrapolation).

    python scripts/ibm_mitigation.py emulate   # everything on AerSimulator.from_backend noise (no QPU time)
    python scripts/ibm_mitigation.py submit    # one job: readout calibration + CZ-folded (x3) circuits on the real QPU
    python scripts/ibm_mitigation.py fetch     # combine with the 4 unfolded runs (results/ibm_repeats.json), write results

Inputs: results/ibm_hardware.json (reference run: job id, saved groups, energies) and results/ibm_repeats.json.
- Readout: per physical qubit, P(read 1 | prep 0) and P(read 0 | prep 1) from two calibration circuits (all 0, all 1)
  on the physical qubits our circuits measure; each group's distribution is corrected with the tensored inverse.
- ZNE: every cz in the ISA circuit becomes cz·cz·cz (same unitary, ~3x the cz noise; no re-transpilation), and
  E(0) = 1.5 E(1) - 0.5 E(3) (linear in the noise scale). Readout correction is applied before extrapolating.
"""
import json
import os
import sys

import numpy as np
from qiskit import QuantumCircuit
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import ibm_hardware as ih  # noqa: E402

RES = os.path.join(ROOT, "results")
SHOTS = ih.SHOTS_PER_GROUP


def measured_physical(circ):
    """clbit index -> physical qubit index, from the measure instructions of an ISA circuit."""
    m = {}
    for inst in circ.data:
        if inst.operation.name == "measure":
            m[circ.find_bit(inst.clbits[0]).index] = circ.find_bit(inst.qubits[0]).index
    return [m[k] for k in range(len(m))]


def fold_cz(circ, factor=3):
    out = circ.copy_empty_like()
    for inst in circ.data:
        reps = factor if inst.operation.name == "cz" else 1
        for _ in range(reps):
            out.append(inst.operation, inst.qubits, inst.clbits)
    return out


def calibration_circuits(backend, phys):
    pm = generate_preset_pass_manager(optimization_level=0, backend=backend, initial_layout=list(range(backend.num_qubits)))
    circs = []
    for flip in (False, True):
        qc = QuantumCircuit(backend.num_qubits, len(phys))
        for j, q in enumerate(phys):
            if flip:
                qc.x(q)
            qc.measure(q, j)
        circs.append(pm.run(qc))
    return circs


def confusion_from(cal_counts, phys):
    """{physical qubit: (p10, p01)} with p10 = P(1|0), p01 = P(0|1)."""
    c0, c1 = cal_counts
    n0, n1 = sum(c0.values()), sum(c1.values())
    out = {}
    for j, q in enumerate(phys):
        p10 = sum(n for b, n in c0.items() if (int(b, 2) >> j) & 1) / n0
        p01 = sum(n for b, n in c1.items() if not (int(b, 2) >> j) & 1) / n1
        out[q] = (p10, p01)
    return out


def corrected_quasi(counts, phys_of_clbit, conf):
    """Tensored inverse of the per-qubit confusion matrices applied to the measured distribution (8 clbits)."""
    n = len(phys_of_clbit)
    p = np.zeros(2 ** n)
    for b, c in counts.items():
        p[int(b, 2)] += c
    N = p.sum()
    t = (p / N).reshape([2] * n)  # axis j <-> clbit n-1-j
    for k in range(n):
        p10, p01 = conf[phys_of_clbit[k]]
        A = np.array([[1 - p10, p01], [p10, 1 - p01]])  # columns: prepared 0/1, rows: read 0/1
        t = np.moveaxis(np.tensordot(np.linalg.inv(A), t, axes=([1], [n - 1 - k])), 0, n - 1 - k)
    return t.reshape(-1), N


def energy_quasi(groups, quasis):
    """E and an approximate sigma from (quasi-)probabilities: Var per group with |p| weights, divided by its shots."""
    e, var = 0.0, 0.0
    for g, (q, N) in zip(groups, quasis):
        labels, coeffs = g.paulis.to_labels(), g.coeffs.real
        masks = [sum(1 << k for k, ch in enumerate(reversed(l)) if ch != "I") for l in labels]
        x = np.arange(len(q))
        vals = sum(c * (1 - 2 * (np.vectorize(lambda v, m=m: bin(v & m).count("1") & 1)(x))) for c, m in zip(coeffs, masks))
        mean = float((q * vals).sum())
        w = np.abs(q) / np.abs(q).sum()
        e += mean
        var += float((w * (vals - mean) ** 2).sum()) / N
    return e, float(np.sqrt(var))


def raw_quasi(counts):
    n = 8
    p = np.zeros(2 ** n)
    for b, c in counts.items():
        p[int(b, 2)] += c
    return p / p.sum(), p.sum()


def zne(e1, s1, e3, s3):
    return 1.5 * e1 - 0.5 * e3, float(np.sqrt((1.5 * s1) ** 2 + (0.5 * s3) ** 2))


def main():
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as RuntimeSampler
    mode = sys.argv[1]
    service = QiskitRuntimeService()
    ref = json.load(open(os.path.join(RES, "ibm_hardware.json"), encoding="utf-8"))
    groups = ih.groups_from_json(ref["groups"])
    backend = service.backend(ref["backend"])
    isa = [p[0] for p in service.job(ref["job_id"]).inputs["pubs"]]
    maps = [measured_physical(c) for c in isa]
    phys = sorted({q for m in maps for q in m})
    cal = calibration_circuits(backend, phys)
    folded = [fold_cz(c, 3) for c in isa]
    fci = ref["e_fci"]
    print(f"physical qubits measured: {phys} | cz per circuit x1 = {max(c.count_ops().get('cz', 0) for c in isa)}, "
          f"x3 = {max(c.count_ops().get('cz', 0) for c in folded)}", flush=True)

    def analyse(c1_list, c3, calc, label):
        conf = confusion_from(calc, phys)
        rows = {}
        for name, runs in (("x1", c1_list), ("x3", [c3])):
            es_raw, es_ro = [], []
            for counts in runs:
                es_raw.append(energy_quasi(groups, [raw_quasi(c) for c in counts]))
                es_ro.append(energy_quasi(groups, [corrected_quasi(c, m, conf) for c, m in zip(counts, maps)]))
            def avg(lst):
                e = np.array([x[0] for x in lst]); s = np.array([x[1] for x in lst])
                w = 1 / s ** 2
                return float((w * e).sum() / w.sum()), float(w.sum() ** -0.5)
            rows[name] = dict(raw=avg(es_raw), readout=avg(es_ro))
        out = dict(label=label, readout_errors={str(q): conf[q] for q in phys},
                   raw_x1=rows["x1"]["raw"], raw_x3=rows["x3"]["raw"], ro_x1=rows["x1"]["readout"], ro_x3=rows["x3"]["readout"])
        out["zne_raw"] = zne(*out["raw_x1"], *out["raw_x3"])
        out["zne_readout"] = zne(*out["ro_x1"], *out["ro_x3"])
        print(f"--- {label} (error vs FCI, mHa) | noiseless {(ref['e_short_noiseless'] - fci) * 1e3:+.1f} | HF {(ref['e_hf'] - fci) * 1e3:+.1f}")
        for k in ("raw_x1", "raw_x3", "ro_x1", "ro_x3", "zne_raw", "zne_readout"):
            e, s = out[k]
            print(f"  {k:12s} {(e - fci) * 1e3:+8.1f} ± {s * 1e3:5.1f}")
        mean_ro = np.mean([sum(v) / 2 for v in conf.values()])
        print(f"  mean readout error per qubit: {mean_ro:.3%}")
        return out

    if mode == "emulate":
        from qiskit_aer import AerSimulator
        from qiskit_aer.primitives import SamplerV2 as AerSampler
        nm = AerSimulator.from_backend(backend).options.noise_model
        def run(circs, seed):
            res = AerSampler(seed=seed, options={"backend_options": {"method": "density_matrix", "noise_model": nm}}).run(
                [(c, None, SHOTS) for c in circs]).result()
            return [ih.counts_of(r) if hasattr(r.data, "m") else r.data.c.get_counts() for r in res]
        c1 = run(isa, 2001)
        c3 = run(folded, 2002)
        calc = run(cal, 2003)
        out = analyse([c1], c3, calc, f"EMULATED {backend.name}")
        json.dump(out, open(os.path.join(RES, "ibm_mitigation_emulated.json"), "w"), indent=1)
    elif mode == "submit":
        job = RuntimeSampler(mode=backend).run([(c, None, SHOTS) for c in folded + cal])
        json.dump(dict(job_id=job.job_id(), n_folded=len(folded), n_cal=len(cal), phys=phys),
                  open(os.path.join(RES, "ibm_mitigation_submit.json"), "w"), indent=1)
        print("JOB", job.job_id())
    elif mode == "fetch":
        sub = json.load(open(os.path.join(RES, "ibm_mitigation_submit.json"), encoding="utf-8"))
        res = service.job(sub["job_id"]).result()
        c3 = [res[i].data.m.get_counts() for i in range(sub["n_folded"])]
        calc = [res[sub["n_folded"] + i].data.c.get_counts() for i in range(sub["n_cal"])]
        rep = json.load(open(os.path.join(RES, "ibm_repeats.json"), encoding="utf-8"))
        jobs = [ref["job_id"]] + rep["jobs"]
        c1_list = [[r.data.m.get_counts() for r in service.job(j).result()] for j in jobs]
        out = analyse(c1_list, c3, calc, f"HARDWARE {backend.name} (x1 = {len(c1_list)} runs)")
        out.update(job_x3_and_cal=sub["job_id"], jobs_x1=jobs)
        json.dump(out, open(os.path.join(RES, "ibm_mitigation_hardware.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
