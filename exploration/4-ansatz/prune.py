import json, time, numpy as np
from scipy.optimize import minimize
from qiskit.quantum_info import Statevector
from core import solve
from ansatz import cz_count, qubit_generator, A, B
from fast import SectorAnsatz, h_sector, IDX
from givens import build_q_upccgsd_fast

DS = [0.6, 0.9, 1.4, 1.8, 2.4, 3.0]
TOL = 0.1  # mHa
SYS = {d: solve(d) for d in DS}
for d in DS: SYS[d]["H"] = h_sector(SYS[d])

def excs_for(ops):
    ex = []
    for (_, kind, p, q) in ops:
        if kind == "D": ex.append([((A(q), B(q)), (B(p), A(p)))])
        else: ex.append([((A(q),), (A(p),)), ((B(q),), (B(p),))])
    return ex

def fit(ops, x_prev=None):
    S = SectorAnsatz(excs_for(ops), qubit_generator); errs, xs = {}, {}
    rng = np.random.default_rng(3)
    for d in DS:
        H = SYS[d]["H"]
        starts = [np.zeros(S.n)] + ([x_prev[d]] if x_prev else []) + [rng.normal(scale=0.7, size=S.n) for _ in range(2)]
        r = min((minimize(S.energy_grad, x0, args=(H,), jac=True, method="BFGS", options=dict(gtol=1e-10, maxiter=10000)) for x0 in starts), key=lambda r: r.fun)
        errs[d] = (r.fun - SYS[d]["e_fci"]) * 1e3; xs[d] = r.x
    return max(abs(e) for e in errs.values()), errs, xs

_, ops = build_q_upccgsd_fast(2)
t0 = time.time()
worst, errs, xs = fit(ops)
print(f"full {len(ops)} ops worst={worst:.2e} mHa", flush=True)
changed = True
while changed:
    changed = False
    mag = sorted(range(len(ops)), key=lambda n: max(abs(xs[d][n]) for d in DS))
    for n in mag:
        trial = ops[:n] + ops[n+1:]
        prev = {d: np.delete(xs[d], n) for d in DS}
        w, e, x = fit(trial, prev)
        if w < TOL:
            print(f"drop {ops[n]} -> {len(trial)} ops, worst={w:.3f} mHa ({time.time()-t0:.0f}s)", flush=True)
            ops, xs, errs = trial, x, e; changed = True
            break
qc, _ = build_q_upccgsd_fast(2, keep=ops)
S = SectorAnsatz(excs_for(ops), qubit_generator)
x = np.random.default_rng(9).normal(size=S.n)
agree = abs(abs(np.vdot(Statevector(qc.assign_parameters(x)).data[IDX], S.state(x))) - 1)
res = dict(ops=ops, cz=cz_count(qc), params=len(ops), err_mHa={str(d): errs[d] for d in DS}, circuit_vs_fast=float(agree))
print(json.dumps(res), flush=True)
json.dump(res, open("pruned.json", "w"))
