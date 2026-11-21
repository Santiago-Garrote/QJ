"""Hardware-efficient (RY-RZ por qubit + cadena de CZ en línea) con gradiente adjunto exacto.
No conserva N ni S_z: optimizamos la fidelidad con el vector FCI (embebido en 256 amplitudes)
y reportamos la fuga fuera del sector N=4, S_z=0."""
import json, time
import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import Statevector
from core import solve, ci_to_state
from ansatz import cz_count, HF_QUBITS
from fast import IDX

N = 8
def _1q(v, q, M):
    v = v.reshape([2] * N); v = np.moveaxis(v, N - 1 - q, 0)
    v = np.tensordot(M, v, axes=(1, 0)); return np.moveaxis(v, 0, N - 1 - q).reshape(-1)
Z = np.array([[1, 0], [0, -1]], complex); Y = np.array([[0, -1j], [1j, 0]])
RY = lambda t: np.array([[np.cos(t/2), -np.sin(t/2)], [np.sin(t/2), np.cos(t/2)]], complex)
RZ = lambda t: np.diag([np.exp(-1j*t/2), np.exp(1j*t/2)])
bits = (np.arange(2**N)[:, None] >> np.arange(N)) & 1
CZCHAIN = np.prod([np.where(bits[:, q] & bits[:, q+1], -1, 1) for q in range(N-1)], axis=0)

def gates(reps):
    g = []
    for r in range(reps + 1):
        g += [("ry", q) for q in range(N)] + [("rz", q) for q in range(N)]
        if r < reps: g.append(("cz", None))
    return g

def forward(x, G):
    v = np.zeros(2**N, complex); v[sum(1 << q for q in HF_QUBITS)] = 1; k = 0
    for kind, q in G:
        if kind == "cz": v = CZCHAIN * v
        else: v = _1q(v, q, (RY if kind == "ry" else RZ)(x[k])); k += 1
    return v

def infid_grad(x, G, t):
    v = forward(x, G); ov = np.vdot(t, v); lam = t.copy(); g = np.zeros(len(x)); k = len(x)
    for kind, q in reversed(G):
        if kind == "cz": v = CZCHAIN * v; lam = CZCHAIN * lam; continue
        k -= 1; P = Y if kind == "ry" else Z
        U = (RY if kind == "ry" else RZ)(x[k])
        dv = _1q(v, q, -0.5j * P)                      # dψ/dθ en este punto = (−i/2)P ψ (ψ ya incluye U)
        g[k] = -2 * np.real(np.conj(ov) * np.vdot(lam, dv))
        v = _1q(v, q, U.conj().T); lam = _1q(lam, q, U.conj().T)
    return 1 - abs(ov)**2, g

def circuit(reps):
    th = ParameterVector("θ", 2 * N * (reps + 1)); qc = QuantumCircuit(N); k = 0
    for q in HF_QUBITS: qc.x(q)
    for r in range(reps + 1):
        for q in range(N): qc.ry(th[k], q); k += 1
        for q in range(N): qc.rz(th[k], q); k += 1
        if r < reps:
            for q in range(N - 1): qc.cz(q, q + 1)
    return qc

if __name__ == "__main__":
    DS = [0.9, 1.8, 3.0]; SYS = {d: solve(d) for d in DS}
    for reps in (2, 4, 6, 8):
        G = gates(reps); qc = circuit(reps); n = qc.num_parameters; t0 = time.time()
        x = np.random.default_rng(0).normal(size=n)
        assert abs(abs(np.vdot(Statevector(qc.assign_parameters(x)).data, forward(x, G))) - 1) < 1e-10
        row = dict(name=f"HEA(reps={reps})", cz=cz_count(qc), params=n, infid={}, leak={})
        for d in DS:
            t = ci_to_state(SYS[d]["ci"]); rng = np.random.default_rng(1)
            best = min((minimize(infid_grad, rng.normal(scale=0.3, size=n), args=(G, t), jac=True, method="L-BFGS-B", options=dict(maxiter=5000)) for _ in range(6)), key=lambda r: r.fun)
            v = forward(best.x, G)
            row["infid"][d] = float(best.fun); row["leak"][d] = float(1 - np.linalg.norm(v[IDX])**2)
        row["secs"] = round(time.time() - t0, 1); print(json.dumps(row), flush=True)
