"""Simulación rápida en el sector N=4, S_z=0 (36 estados), con gradiente adjunto exacto."""
import numpy as np
from pyscf import fci
from qiskit.quantum_info import SparsePauliOp
from core import STR, N_ORB, N_QUBITS
from ansatz import HF_QUBITS

IDX = np.array([int(a) | (int(b) << N_ORB) for a in STR for b in STR])  # orden = ci.ravel()
HF_POS = int(np.where(IDX == sum(1 << q for q in HF_QUBITS))[0][0])

def _sector(op):
    K = -1j * op.to_matrix(sparse=True)[IDX][:, IDX].toarray()   # G = i(T - T†) -> K = T - T†
    assert np.abs(K.imag).max() < 1e-12
    return K.real

class SectorAnsatz:
    """Cada parámetro: grupo de generadores que conmutan, cada uno con K^3 = -K."""
    def __init__(self, excs, gen, layers=1):
        self.groups = [[_sector(gen(c, a)) for c, a in g] for g in excs] * layers
        for g in self.groups:
            for K in g: assert np.allclose(K @ K @ K, -K)
        self.Ksum = [sum(g) for g in self.groups]
        self.K2 = [[K @ K for K in g] for g in self.groups]
        self.n = len(self.groups)

    def _U(self, k, t):
        I = np.eye(len(IDX)); U = I
        for K, K2 in zip(self.groups[k], self.K2[k]):
            U = (I + np.sin(t) * K + (1 - np.cos(t)) * K2) @ U
        return U

    def state(self, x):
        v = np.zeros(len(IDX)); v[HF_POS] = 1
        for k in range(self.n): v = self._U(k, x[k]) @ v
        return v

    def energy_grad(self, x, H):
        Us = [self._U(k, x[k]) for k in range(self.n)]
        v = np.zeros(len(IDX)); v[HF_POS] = 1
        for U in Us: v = U @ v
        lam = H @ v; e = v @ lam; g = np.empty(self.n)
        for k in reversed(range(self.n)):
            g[k] = 2 * lam @ (self.Ksum[k] @ v)
            v = Us[k].T @ v; lam = Us[k].T @ lam
        return e, g

def h_sector(s):
    n = len(IDX); H = np.zeros((n, n))
    h2 = fci.direct_spin1.absorb_h1e(s["h1"], s["eri"], N_ORB, (2, 2), 0.5)
    for k in range(n):
        e = np.zeros(n); e[k] = 1
        H[:, k] = fci.direct_spin1.contract_2e(h2, e.reshape(6, 6), N_ORB, (2, 2)).ravel()
    return H + s["e_nuc"] * np.eye(n)
