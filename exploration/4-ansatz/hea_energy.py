import json, time, numpy as np
from scipy.optimize import minimize
from pyscf.fci import spin_op
from core import solve
from fast import h_sector, IDX
from fullspace import full_hamiltonian, NUM
from hea import gates, forward, circuit, _1q, RY, RZ, Y, Z, CZCHAIN
from ansatz import cz_count

def energy_grad(x, G, H):
    v = forward(x, G); lam = H @ v; e = np.vdot(v, lam).real; g = np.zeros(len(x)); k = len(x)
    for kind, q in reversed(G):
        if kind == "cz": v = CZCHAIN * v; lam = CZCHAIN * lam; continue
        k -= 1; P = Y if kind == "ry" else Z; U = (RY if kind == "ry" else RZ)(x[k])
        g[k] = 2 * np.real(np.vdot(lam, _1q(v, q, -0.5j * P)))
        v = _1q(v, q, U.conj().T); lam = _1q(lam, q, U.conj().T)
    return e, g

DS = [0.9, 1.8, 2.2, 3.0]; SYS = {}
for d in DS:
    s = solve(d); Hf = full_hamiltonian(s)
    assert np.allclose(Hf[np.ix_(IDX, IDX)].real, h_sector(s)), "H completo ≠ H del sector"
    s["Hf"] = Hf; s["gs_full"] = np.linalg.eigvalsh(Hf)[0]; SYS[d] = s
print("H completo ok (restricción = sector). E0 completo - E_FCI (mHa):", {d: round((SYS[d]["gs_full"] - SYS[d]["e_fci"]) * 1e3, 6) for d in DS}, flush=True)
for reps in (6, 8, 10):
    G = gates(reps); qc = circuit(reps); n = qc.num_parameters; t0 = time.time()
    row = dict(name=f"HEA(reps={reps})", cz=cz_count(qc), params=n, err_mHa={}, N={}, leak={}, S2_sector={})
    for d in DS:
        H = SYS[d]["Hf"]; rng = np.random.default_rng(1)
        best = min((minimize(energy_grad, rng.normal(scale=0.3, size=n), args=(G, H), jac=True, method="L-BFGS-B", options=dict(maxiter=20000)) for _ in range(6)), key=lambda r: r.fun)
        v = forward(best.x, G); w = abs(v[IDX])**2
        row["err_mHa"][d] = float((best.fun - SYS[d]["e_fci"]) * 1e3)
        row["N"][d] = float(np.sum(abs(v)**2 * NUM)); row["leak"][d] = float(1 - w.sum())
        vs = v[IDX] / np.linalg.norm(v[IDX]); vs = vs * np.exp(-1j * np.angle(vs[np.argmax(abs(vs))]))
        row["S2_sector"][d] = float(spin_op.spin_square0(vs.real.reshape(6, 6), 4, (2, 2))[0])
    row["secs"] = round(time.time() - t0, 1); print(json.dumps(row), flush=True)
