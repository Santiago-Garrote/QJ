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

NQ = 8  # spin orbitals, interleaved: qubit 2p = alpha, 2p+1 = beta
DISTANCES = [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0]
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
                acc.append(h1[p, q] * (AD[2 * p + s] @ A[2 * q + s]))
    # 1/2 sum (pq|rs) a+_{p s} a+_{r t} a_{s t} a_{q s}
    for p, q, r, s_ in itertools.product(range(n), repeat=4):
        v = eri[p, q, r, s_]
        if abs(v) < 1e-12:
            continue
        for si, ti in itertools.product((0, 1), repeat=2):
            P, Q, R, S = 2 * p + si, 2 * q + si, 2 * r + ti, 2 * s_ + ti
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
    """Basis states with N=4 and Sz=0 (2 alpha on even qubits, 2 beta on odd qubits)."""
    return [b for b in range(2 ** NQ)
            if bin(b).count("1") == 4 and sum((b >> k) & 1 for k in range(0, NQ, 2)) == 2]


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
