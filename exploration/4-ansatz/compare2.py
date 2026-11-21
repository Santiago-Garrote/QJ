import time, json, sys
import numpy as np
from scipy.optimize import minimize, check_grad
from qiskit.quantum_info import Statevector
from pyscf import cc
from core import solve
from ansatz import build, cz_count, fermionic_generator, qubit_generator, uccsd_excitations, upccgsd_excitations
from fast import SectorAnsatz, h_sector, IDX

DS = [0.9, 1.8, 3.0]
SYS = {d: solve(d) for d in DS}
for d in DS: SYS[d]["H"] = h_sector(SYS[d])
ccsd = {d: (cc.CCSD(SYS[d]["mf"]).run(verbose=0).e_tot - SYS[d]["e_fci"]) * 1e3 for d in DS}
cands = [("UCCSD", 1, uccsd_excitations(), fermionic_generator),
         ("QUCCSD", 1, uccsd_excitations(), qubit_generator),
         ("k-UpCCGSD", 1, upccgsd_excitations(), fermionic_generator),
         ("k-UpCCGSD", 2, upccgsd_excitations(), fermionic_generator),
         ("k-UpCCGSD", 3, upccgsd_excitations(), fermionic_generator)]
rows = []
for kind, L, excs, gen in cands:
    t0 = time.time(); qc = build(kind, L); A = SectorAnsatz(excs, gen, L)
    x = np.random.default_rng(7).normal(scale=0.5, size=A.n)
    agree = float(abs(abs(np.vdot(Statevector(qc.assign_parameters(x)).data[IDX], A.state(x))) - 1))
    H = SYS[1.8]["H"]
    gerr = check_grad(lambda x: A.energy_grad(x, H)[0], lambda x: A.energy_grad(x, H)[1], x)
    row = dict(name=qc.name, cz=cz_count(qc), params=A.n, circuit_vs_fast=agree, grad_check=float(gerr), err_mHa={})
    for d in DS:
        H = SYS[d]["H"]; rng = np.random.default_rng(1); best = None
        for t in range(8):
            x0 = np.zeros(A.n) if t == 0 else rng.normal(scale=0.7, size=A.n)
            r = minimize(A.energy_grad, x0, args=(H,), jac=True, method="BFGS", options=dict(gtol=1e-10, maxiter=10000))
            if best is None or r.fun < best.fun: best = r
        row["err_mHa"][d] = float((best.fun - SYS[d]["e_fci"]) * 1e3)
    row["secs"] = round(time.time() - t0, 1)
    print(json.dumps(row), flush=True); rows.append(row)
print("CCSD", json.dumps({d: round(v, 3) for d, v in ccsd.items()}))
json.dump(dict(rows=rows, ccsd=ccsd), open("compare2.json", "w"))
