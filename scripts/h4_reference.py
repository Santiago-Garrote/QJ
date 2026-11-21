"""Classical reference data for linear H4 / STO-3G.

For each spacing d: RHF, CCSD, CCSD(T) and FCI energies (PySCF), plus the
8-qubit Jordan-Wigner Hamiltonian, its Pauli-term count, 1-norm and number of
qubit-wise-commuting (QWC) groups. The Hamiltonian is checked against FCI by
exact diagonalization in the N=4, Sz=0 sector, which also gives the gap to the
first excited state of that sector.

Usage (from the repo root):
    python scripts/h4_reference.py            # writes results/h4_reference.json
"""
import itertools
import json
import os

import numpy as np
from pyscf import ao2mo, cc, fci, gto, scf
from qiskit.quantum_info import SparsePauliOp

# Qubit convention = the notebook's shared contract (notebooks/h4_vqe.ipynb, section 0.1):
# qubit p = spin-orbital (p, alpha), qubit 4 + p = (p, beta); |1> = occupied; HF = "00110011".
NQ = 8
N_ORB = 4
# Same grid as the notebook contract: 0.6-1.7 every 0.1 A, then 1.8-3.0 every 0.2 A (19 points).
DISTANCES = [round(x, 2) for x in list(np.arange(0.6, 1.75, 0.1)) + list(np.arange(1.8, 3.01, 0.2))]


def so(p, s):
    """Qubit index of spatial orbital p with spin s (0 = alpha, 1 = beta)."""
    return p + N_ORB * s
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _annihilation(j):
    """JW annihilation operator a_j = Z_0..Z_{j-1} (X_j + iY_j)/2 (Qiskit little-endian labels)."""
    def label(p):
        s = ["I"] * NQ
        for k in range(j):
            s[k] = "Z"
        s[j] = p
        return "".join(reversed(s))
    return SparsePauliOp([label("X"), label("Y")], [0.5, 0.5j])


A = [_annihilation(j) for j in range(NQ)]
AD = [a.adjoint() for a in A]


def h4_molecule(d):
    return gto.M(atom=[["H", (0, 0, i * d)] for i in range(4)], basis="sto-3g", unit="Angstrom", verbose=0)


def qubit_hamiltonian(mol, mf):
    """Electronic Hamiltonian in the RHF MO basis, mapped with Jordan-Wigner to 8 qubits."""
    C = mf.mo_coeff
    h1 = C.T @ mf.get_hcore() @ C
    eri = ao2mo.restore(1, ao2mo.kernel(mol, C), C.shape[1])  # chemists' (pq|rs)
    n = h1.shape[0]
    acc = [SparsePauliOp(["I" * NQ], [mol.energy_nuc()])]
    for p, q in itertools.product(range(n), repeat=2):
        if abs(h1[p, q]) > 1e-12:
            for s in (0, 1):
                acc.append(h1[p, q] * (AD[so(p, s)] @ A[so(q, s)]))
    # 1/2 sum (pq|rs) a+_{p s} a+_{r t} a_{s t} a_{q s}
    for p, q, r, s_ in itertools.product(range(n), repeat=4):
        v = eri[p, q, r, s_]
        if abs(v) < 1e-12:
            continue
        for si, ti in itertools.product((0, 1), repeat=2):
            P, Q, R, S = so(p, si), so(q, si), so(r, ti), so(s_, ti)
            if P != R and Q != S:
                acc.append(0.5 * v * (AD[P] @ AD[R] @ A[S] @ A[Q]))
    return SparsePauliOp.sum(acc).simplify(atol=1e-10)


def qwc_groups(H):
    """Greedy sorted-insertion grouping into qubit-wise-commuting sets. Returns lists of term indices."""
    labels = H.paulis.to_labels()
    order = np.argsort(-np.abs(H.coeffs.real))
    groups = []
    for i in order:
        lab = labels[i]
        if set(lab) == {"I"}:
            continue
        for g in groups:
            if all(a == "I" or b == "I" or a == b for a, b in zip(lab, g["basis"])):
                g["basis"] = [b if b != "I" else a for a, b in zip(lab, g["basis"])]
                g["terms"].append(i)
                break
        else:
            groups.append({"basis": list(lab), "terms": [i]})
    return [g["terms"] for g in groups]


def sector_indices():
    """Basis states with N=4 and Sz=0 (2 alpha on qubits 0-3, 2 beta on qubits 4-7)."""
    return [b for b in range(2 ** NQ)
            if bin(b).count("1") == 4 and sum((b >> k) & 1 for k in range(N_ORB)) == 2]


def one_norm(H):
    labels = H.paulis.to_labels()
    return float(sum(abs(c) for c, l in zip(H.coeffs.real, labels) if set(l) != {"I"}))


def main():
    out = []
    idx = sector_indices()
    for d in DISTANCES:
        mol = h4_molecule(d)
        mf = scf.RHF(mol).run()
        mycc = cc.CCSD(mf)
        mycc.max_cycle = 500
        mycc.run()
        e_ccsd = mycc.e_tot if mycc.converged else None
        e_ccsd_t = e_ccsd + mycc.ccsd_t() if e_ccsd is not None else None
        e_fci = fci.FCI(mf).kernel()[0]

        H = qubit_hamiltonian(mol, mf)
        evals = np.linalg.eigvalsh(H.to_matrix()[np.ix_(idx, idx)])
        assert abs(evals[0] - e_fci) < 1e-6, f"JW Hamiltonian does not reproduce FCI at d={d}"

        row = dict(d=d, rhf=mf.e_tot, ccsd=e_ccsd, ccsd_t=e_ccsd_t, fci=e_fci,
                   gap_sector=float(evals[1] - evals[0]), n_pauli=len(H), one_norm=one_norm(H),
                   n_qwc_groups=len(qwc_groups(H)), sector_dim=len(idx))
        out.append(row)
        err = "n/a" if e_ccsd is None else f"{(e_ccsd - e_fci) * 1000:+.2f}"
        print(f"d={d:.1f}  FCI={e_fci:.6f}  CCSD-FCI={err} mHa  gap={row['gap_sector'] * 1000:.2f} mHa  "
              f"terms={row['n_pauli']}  lambda={row['one_norm']:.3f}  qwc={row['n_qwc_groups']}", flush=True)

    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    path = os.path.join(ROOT, "results", "h4_reference.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print("wrote", path)


if __name__ == "__main__":
    main()
