import json, numpy as np
from scipy.optimize import minimize
from qiskit.quantum_info import Statevector
from core import solve
from ansatz import cz_count, qubit_generator, upccgsd_excitations
from fast import SectorAnsatz, h_sector, IDX
from givens import build_q_upccgsd
DS = [0.9, 1.8, 3.0]
SYS = {d: solve(d) for d in DS}
for d in DS: SYS[d]["H"] = h_sector(SYS[d])
for L in (1, 2, 3):
    qc = build_q_upccgsd(L); Asec = SectorAnsatz(upccgsd_excitations(), qubit_generator, L)
    x = np.random.default_rng(7).normal(scale=0.5, size=Asec.n)
    full = Statevector(qc.assign_parameters(x)).data
    agree = float(abs(abs(np.vdot(full[IDX], Asec.state(x))) - 1)); leak = float(1 - np.linalg.norm(full[IDX])**2)
    row = dict(name=qc.name, cz=cz_count(qc), params=Asec.n, circuit_vs_fast=agree, leak=leak, err_mHa={})
    for d in DS:
        H = SYS[d]["H"]; rng = np.random.default_rng(1)
        best = min((minimize(Asec.energy_grad, np.zeros(Asec.n) if t == 0 else rng.normal(scale=0.7, size=Asec.n), args=(H,), jac=True, method="BFGS", options=dict(gtol=1e-10, maxiter=10000)) for t in range(8)), key=lambda r: r.fun)
        row["err_mHa"][d] = float((best.fun - SYS[d]["e_fci"]) * 1e3)
    print(json.dumps(row), flush=True)
