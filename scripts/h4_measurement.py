"""Measurement cost and state diagnostics for linear H4 / STO-3G.

For each spacing d, on the exact (FCI) ground state of the 8-qubit JW Hamiltonian:
  * K_qwc   = sum_g sqrt(Var_g) over QWC groups (optimal shot allocation N_g ~ sqrt(Var_g)),
              so that sigma = K_qwc / sqrt(N_total);
  * K_terms = sum_k |c_k| sqrt(1 - <P_k>^2) measuring each Pauli term separately;
  * lambda  = sum_k |c_k| (naive upper bound);
  * <S^2> of the ground state and of the first excited state in the N=4, Sz=0 sector;
  * weight of the Hartree-Fock determinant in the ground state.

Usage (from the repo root):
    python scripts/h4_measurement.py          # writes results/h4_measurement.json
"""
import json
import os

import numpy as np
from pyscf import scf
from qiskit.quantum_info import SparsePauliOp

from h4_reference import A, AD, NQ, ROOT, h4_molecule, one_norm, qubit_hamiltonian, qwc_groups, sector_indices

DISTANCES = [0.6, 0.9, 1.2, 1.5, 1.8, 2.1, 2.4, 2.7, 3.0]
HF_STATE = 0b00001111  # lowest two spatial orbitals doubly occupied (interleaved ordering)


def s_squared():
    num = lambda j: AD[j] @ A[j]
    sz = SparsePauliOp.sum([0.5 * (num(2 * p) - num(2 * p + 1)) for p in range(NQ // 2)])
    sp = SparsePauliOp.sum([AD[2 * p] @ A[2 * p + 1] for p in range(NQ // 2)])
    return (sp @ sp.adjoint() + sz @ sz - sz).simplify()


def expval(op_matrix, psi):
    return float(np.real(psi.conj() @ op_matrix @ psi))


def main():
    idx = sector_indices()
    S2 = s_squared().to_matrix()
    out = []
    for d in DISTANCES:
        mol = h4_molecule(d)
        mf = scf.RHF(mol).run()
        H = qubit_hamiltonian(mol, mf)
        w, v = np.linalg.eigh(H.to_matrix()[np.ix_(idx, idx)])
        psi0 = np.zeros(2 ** NQ, complex)
        psi0[idx] = v[:, 0]
        psi1 = np.zeros(2 ** NQ, complex)
        psi1[idx] = v[:, 1]

        labels, coeffs = H.paulis.to_labels(), H.coeffs.real
        k_qwc = 0.0
        for terms in qwc_groups(H):
            O = SparsePauliOp([labels[i] for i in terms], [coeffs[i] for i in terms]).to_matrix()
            k_qwc += np.sqrt(max(expval(O @ O, psi0) - expval(O, psi0) ** 2, 0.0))
        k_terms = 0.0
        for c, lab in zip(coeffs, labels):
            if set(lab) != {"I"}:
                e = expval(SparsePauliOp([lab]).to_matrix(), psi0)
                k_terms += abs(c) * np.sqrt(max(1 - e * e, 0.0))

        row = dict(d=d, k_qwc=float(k_qwc), k_terms=float(k_terms), one_norm=one_norm(H),
                   s2_ground=expval(S2, psi0), s2_first_excited=expval(S2, psi1),
                   gap_sector=float(w[1] - w[0]), hf_weight=float(abs(psi0[HF_STATE]) ** 2))
        out.append(row)
        print(f"d={d:.1f}  K_qwc={k_qwc:.3f}  K_terms={k_terms:.3f}  lambda={row['one_norm']:.3f}  "
              f"S2(gs)={row['s2_ground']:.3f}  S2(exc)={row['s2_first_excited']:.3f}  "
              f"gap={row['gap_sector'] * 1000:.2f} mHa  w_HF={row['hf_weight']:.3f}", flush=True)

    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    path = os.path.join(ROOT, "results", "h4_measurement.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print("wrote", path)


if __name__ == "__main__":
    main()
