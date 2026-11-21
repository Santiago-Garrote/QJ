import numpy as np
from pyscf import gto, scf, fci, ao2mo
from pyscf.fci import cistring
from qiskit.quantum_info import SparsePauliOp

N_ORB, N_QUBITS = 4, 8
def h4_geometry(d): return "; ".join(f"H 0 0 {i*d:.6f}" for i in range(4))

def jw_ladder(j, dagger, n=N_QUBITS):
    """a_j (o a†_j) en Jordan-Wigner: Z en qubits < j. a† = (X - iY)/2, a = (X + iY)/2."""
    z = "Z" * j
    def lab(p): return ("I" * (n - j - 1) + p + z)
    s = -1j if dagger else 1j
    return SparsePauliOp([lab("X"), lab("Y")], [0.5, 0.5 * s])

STR = cistring.make_strings(range(N_ORB), 2)
def ci_to_state(ci):
    v = np.zeros(2**N_QUBITS, complex)
    for ia, a in enumerate(STR):
        for ib, b in enumerate(STR):
            v[int(a) | (int(b) << N_ORB)] = ci[ia, ib]
    return v

def state_to_ci(v):
    return np.array([[v[int(a) | (int(b) << N_ORB)] for b in STR] for a in STR])

def solve(d):
    mol = gto.M(atom=h4_geometry(d), basis="sto-3g", unit="Angstrom", verbose=0)
    mf = scf.RHF(mol).run()
    h1 = mf.mo_coeff.T @ mf.get_hcore() @ mf.mo_coeff
    eri = ao2mo.restore(1, ao2mo.full(mol, mf.mo_coeff), N_ORB)
    cis = fci.FCI(mf); e_fci, ci = cis.kernel()
    return dict(mol=mol, mf=mf, h1=h1, eri=eri, e_nuc=mol.energy_nuc(), e_fci=e_fci, ci=ci, e_hf=mf.e_tot)

def energy_from_state(v, s):
    """<psi|H|psi> evaluado por PySCF en el sector N=4, Sz=0 (stand-in de #2)."""
    c = state_to_ci(v)
    nrm = np.vdot(c, c).real
    c = c.real / np.sqrt(nrm)  # el estado real es real en este ansatz
    return fci.direct_spin1.energy(s["h1"], s["eri"], c, N_ORB, (2, 2)) + s["e_nuc"], nrm
