import numpy as np
from pyscf.fci import addons, cistring
from core import *
rng = np.random.default_rng(0)
ci = rng.normal(size=(6, 6)); ci /= np.linalg.norm(ci)
v = ci_to_state(ci)
worst = 0
for p in range(4):
    for q in range(4):
        # a†_p a_q (alfa): PySCF
        t = addons.des_a(ci, 4, (2, 2), q); t = addons.cre_a(t, 4, (1, 2), p)
        jw = (jw_ladder(p, True) @ jw_ladder(q, False)).to_matrix(sparse=True) @ v
        worst = max(worst, np.abs(ci_to_state(t) - jw).max())
        # beta
        t = addons.des_b(ci, 4, (2, 2), q); t = addons.cre_b(t, 4, (2, 1), p)
        jw = (jw_ladder(4+p, True) @ jw_ladder(4+q, False)).to_matrix(sparse=True) @ v
        worst = max(worst, np.abs(ci_to_state(t) - jw).max())
# mixed: a†_pα a†_qβ a_sβ a_rα
for (p,q,r,s) in [(2,3,0,1),(3,2,1,0),(2,2,0,0),(3,3,1,1)]:
    t = addons.des_a(ci, 4, (2,2), r); t = addons.des_b(t, 4, (1,2), s)
    t = addons.cre_b(t, 4, (1,1), q); t = addons.cre_a(t, 4, (1,2), p)
    op = jw_ladder(p,True) @ jw_ladder(4+q,True) @ jw_ladder(4+s,False) @ jw_ladder(r,False)
    worst = max(worst, np.abs(ci_to_state(t) - op.to_matrix(sparse=True) @ v).max())
print("max |PySCF - JW| =", worst)
s = solve(0.9)
e, n = energy_from_state(ci_to_state(s["ci"]), s); print("E(FCI vec) - E_FCI =", e - s["e_fci"])
from qiskit.quantum_info import Statevector
from qiskit import QuantumCircuit
qc = QuantumCircuit(8); [qc.x(k) for k in (0,1,4,5)]
e, n = energy_from_state(Statevector(qc).data, s); print("E(HF state) - E_HF =", e - s["e_hf"])
