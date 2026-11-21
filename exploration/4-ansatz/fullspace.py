"""Hamiltoniano en el espacio de Fock completo (256×256) con el Jordan-Wigner verificado en check_signs.py.
Solo para explorar ansätze que no conservan N (no reemplaza a #2)."""
import numpy as np
import scipy.sparse as sp
from core import jw_ladder, N_ORB, N_QUBITS

_C = [jw_ladder(j, True).to_matrix(sparse=True).tocsr() for j in range(N_QUBITS)]
_A = [c.conj().T.tocsr() for c in _C]
so = lambda p, s: p + N_ORB * s  # espín-orbital (p, σ) -> qubit

def full_hamiltonian(s):
    h1, eri = s["h1"], s["eri"]; H = sp.csr_matrix((256, 256), dtype=complex)
    for p in range(N_ORB):
        for q in range(N_ORB):
            for sg in (0, 1):
                if abs(h1[p, q]) > 1e-12: H = H + h1[p, q] * (_C[so(p, sg)] @ _A[so(q, sg)])
    for p, q, r, t in np.ndindex(*(N_ORB,) * 4):
        v = eri[p, q, r, t]
        if abs(v) < 1e-12: continue
        for sg in (0, 1):
            for tau in (0, 1):
                H = H + 0.5 * v * (_C[so(p, sg)] @ _C[so(r, tau)] @ _A[so(t, tau)] @ _A[so(q, sg)])
    return (H + s["e_nuc"] * sp.identity(256)).toarray()

NUM = sum((_C[j] @ _A[j]) for j in range(N_QUBITS)).toarray().real.diagonal()
