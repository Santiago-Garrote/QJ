import itertools
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import ParameterVector
from qiskit.circuit.library import PauliEvolutionGate, efficient_su2
from qiskit.quantum_info import SparsePauliOp
from qiskit.transpiler import CouplingMap
from core import jw_ladder, N_ORB, N_QUBITS

HF_QUBITS = (0, 1, 4, 5)
OCC, VIR = (0, 1), (2, 3)
A = lambda p: p
B = lambda p: N_ORB + p

def fermionic_generator(create, annihilate):
    """i(T - T†) para T = a†... a..., Hermitiano: exp(-iθ·G) = exp(θ(T - T†))."""
    t = SparsePauliOp("I" * N_QUBITS)
    for c in create: t = t @ jw_ladder(c, True)
    for a in annihilate: t = t @ jw_ladder(a, False)
    return (1j * (t - t.adjoint())).simplify()

def qubit_generator(create, annihilate):
    """Igual pero con operadores de qubit (sin cadenas Z): Q† = (X - iY)/2."""
    def q(j, dag):
        lab = lambda p: "I" * (N_QUBITS - j - 1) + p + "I" * j
        return SparsePauliOp([lab("X"), lab("Y")], [0.5, -0.5j if dag else 0.5j])
    t = SparsePauliOp("I" * N_QUBITS)
    for c in create: t = t @ q(c, True)
    for a in annihilate: t = t @ q(a, False)
    return (1j * (t - t.adjoint())).simplify()

def _hf():
    qc = QuantumCircuit(N_QUBITS)
    for k in HF_QUBITS: qc.x(k)
    return qc

def _from_excitations(excs, gen, layers=1, name="ansatz"):
    """excs: lista de grupos; cada grupo comparte un parámetro: [(create, annihilate), ...]."""
    th = ParameterVector("θ", len(excs) * layers)
    qc = _hf(); k = 0
    for _ in range(layers):
        for group in excs:
            op = sum((gen(c, a) for c, a in group), SparsePauliOp("I" * N_QUBITS, [0])).simplify()
            qc.append(PauliEvolutionGate(op, time=th[k]), range(N_QUBITS)); k += 1
    qc.name = name
    return qc

def uccsd_excitations():
    ex = []
    for i, a in itertools.product(OCC, VIR):          # singles, cada espín con su parámetro
        ex.append([((A(a),), (A(i),))]); ex.append([((B(a),), (B(i),))])
    ex.append([((A(2), A(3)), (A(1), A(0)))])          # αα
    ex.append([((B(2), B(3)), (B(1), B(0)))])          # ββ
    for i, j, a, b in itertools.product(OCC, OCC, VIR, VIR):  # αβ
        ex.append([((A(a), B(b)), (B(j), A(i)))])
    return ex

def upccgsd_excitations():
    ex = []
    for p, q in itertools.combinations(range(N_ORB), 2):  # pares generalizados p→q (αβ juntos)
        ex.append([((A(q), B(q)), (B(p), A(p)))])
    for p, q in itertools.combinations(range(N_ORB), 2):  # singles generalizados, spin-adaptados
        ex.append([((A(q),), (A(p),)), ((B(q),), (B(p),))])
    return ex

def build(kind, layers=1):
    if kind == "UCCSD":   return _from_excitations(uccsd_excitations(), fermionic_generator, 1, kind)
    if kind == "QUCCSD":  return _from_excitations(uccsd_excitations(), qubit_generator, 1, kind)
    if kind == "k-UpCCGSD": return _from_excitations(upccgsd_excitations(), fermionic_generator, layers, f"{layers}-UpCCGSD")
    if kind == "HEA":
        qc = _hf(); qc.compose(efficient_su2(N_QUBITS, reps=layers, entanglement="linear"), inplace=True)
        qc.name = f"HEA(reps={layers})"; return qc
    raise ValueError(kind)

def transpile_line(qc):
    return transpile(qc, basis_gates=["cz", "sx", "x", "rz"], coupling_map=CouplingMap.from_line(qc.num_qubits),
                     optimization_level=3, seed_transpiler=0)

def cz_count(qc): return transpile_line(qc).count_ops().get("cz", 0)
