"""QEB-ADAPT-VQE en el sector N=4, S_z=0: agrega de a una la excitación de qubit con mayor gradiente."""
import itertools, json, time
import numpy as np
from scipy.optimize import minimize
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import Statevector
from pyscf.fci import spin_op
from core import solve
from ansatz import cz_count, qubit_generator, HF_QUBITS, A, B, N_QUBITS
from fast import h_sector, IDX, HF_POS, _sector
from givens import q_single, q_double_fast

def pool():
    P = []
    for s in (A, B):
        for p, q in itertools.combinations(range(4), 2):
            P.append(("S", (s(p),), (s(q),)))                       # annihilate p, create q
    for s in (A, B):
        for (p, q), (r, t) in [((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2))]:
            P.append(("D", (s(p), s(q)), (s(r), s(t))))
    for (p, r), (q, t) in itertools.product(itertools.combinations(range(4), 2), repeat=2):
        P.append(("D", (A(p), B(q)), (A(r), B(t))))
        P.append(("D", (A(p), B(t)), (A(r), B(q))))
    return P

POOL = pool()
KS = [_sector(qubit_generator(cre, ann)) for _, ann, cre in POOL]
for K in KS: assert np.allclose(K @ K @ K, -K)
K2 = [K @ K for K in KS]
I36 = np.eye(36)

def U(k, t): return I36 + np.sin(t) * KS[k] + (1 - np.cos(t)) * K2[k]

def energy_grad(x, ops, H):
    Us = [U(k, t) for k, t in zip(ops, x)]
    v = np.zeros(36); v[HF_POS] = 1
    for M in Us: v = M @ v
    lam = H @ v; e = v @ lam; g = np.empty(len(ops))
    for n in reversed(range(len(ops))):
        g[n] = 2 * lam @ (KS[ops[n]] @ v); v = Us[n].T @ v; lam = Us[n].T @ lam
    return e, g

def state(x, ops):
    v = np.zeros(36); v[HF_POS] = 1
    for k, t in zip(ops, x): v = U(k, t) @ v
    return v

def circuit(ops):
    th = ParameterVector("θ", len(ops)); qc = QuantumCircuit(N_QUBITS)
    for q in HF_QUBITS: qc.x(q)
    for t, k in zip(th, ops):
        kind, ann, cre = POOL[k]
        if kind == "S": q_single(qc, t, ann[0], cre[0])
        else: q_double_fast(qc, t, ann[0], ann[1], cre[0], cre[1])
    return qc

def adapt(H, eps=1e-3, max_ops=40):
    ops, x, hist = [], np.zeros(0), []
    while len(ops) < max_ops:
        v = state(x, ops)
        g = np.array([2 * (H @ v) @ (K @ v) for K in KS])
        k = int(np.argmax(np.abs(g)))
        if abs(g[k]) < eps: break
        ops.append(k)
        r = minimize(energy_grad, np.append(x, 0.0), args=(ops, H), jac=True, method="BFGS", options=dict(gtol=1e-10))
        x = r.x; hist.append((len(ops), r.fun))
    return ops, x, hist

if __name__ == "__main__":
    out = []
    for d in (0.9, 1.8, 2.2, 3.0):
        t0 = time.time(); s = solve(d); H = h_sector(s)
        ops, x, hist = adapt(H)
        qc = circuit(ops); xx = np.asarray(x)
        agree = abs(abs(np.vdot(Statevector(qc.assign_parameters(xx)).data[IDX], state(xx, ops))) - 1)
        e = hist[-1][1]; s2 = spin_op.spin_square0(state(xx, ops).reshape(6, 6), 4, (2, 2))[0]
        first_ok = next((n for n, en in hist if abs(en - s["e_fci"]) * 1e3 < 1.6), None)
        row = dict(d=d, ops=len(ops), cz=cz_count(qc), err_mHa=(e - s["e_fci"]) * 1e3, S2=float(s2),
                   ops_to_chem_acc=first_ok, circuit_vs_fast=float(agree), secs=round(time.time() - t0, 1),
                   seq=[POOL[k][0] + str(POOL[k][1]) + "->" + str(POOL[k][2]) for k in ops])
        print(json.dumps(row), flush=True); out.append(row)
    json.dump(out, open("adapt.json", "w"), indent=1)
