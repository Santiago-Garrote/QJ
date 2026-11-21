"""Excitaciones como rotaciones de Givens entre dos estados de la base: pocos cz."""
import itertools
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from ansatz import HF_QUBITS, N_ORB, N_QUBITS, A, B

def q_single(qc, t, i, k):
    """exp(θ(Q†_k Q_i − h.c.)): |i=1,k=0> -> cos|..> + sin|i=0,k=1>."""
    qc.cx(k, i); qc.cry(2 * t, i, k); qc.cx(k, i)

def q_double(qc, t, i, j, k, l):
    """exp(θ(Q†_k Q†_l Q_j Q_i − h.c.)): |ij=11,kl=00> <-> |ij=00,kl=11>."""
    for m in (i, j, l): qc.cx(k, m)
    qc.x(l); qc.mcry(2 * t, [i, j, l], k); qc.x(l)
    for m in (l, j, i): qc.cx(k, m)

def _parity_wrap(qc, between, apply):
    """Aplica la versión fermiónica: signo (−1)^paridad de los qubits intermedios.
    exp(θ·P·K) con P = ±1 diagonal = rotación de ángulo ±θ: se implementa como
    rotación controlada por la paridad usando CZ-conjugación con una escalera de CX."""
    raise NotImplementedError

def build_q_upccgsd(layers):
    th = ParameterVector("θ", 12 * layers); qc = QuantumCircuit(N_QUBITS)
    for q in HF_QUBITS: qc.x(q)
    k = 0
    for _ in range(layers):
        for p, q in itertools.combinations(range(N_ORB), 2):
            q_double(qc, th[k], A(p), B(p), A(q), B(q)); k += 1
        for p, q in itertools.combinations(range(N_ORB), 2):
            q_single(qc, th[k], A(p), A(q)); q_single(qc, th[k], B(p), B(q)); k += 1
    qc.name = f"{layers}-QUpCCGSD"
    return qc


def _ucry(qc, t, controls, target, pattern):
    """RY(2θ) en target solo si controls == pattern (tupla de bits). Multiplexor Gray: 2^n CX."""
    n = len(controls); N = 2 ** n
    gray = [m ^ (m >> 1) for m in range(N)]
    pidx = sum(b << c for c, b in enumerate(pattern))          # índice del patrón (bit c = controls[c])
    # φ_m = (1/N) Σ_j (−1)^{popcount(j & gray_m)} a_j, con a = 2θ e_pidx
    coef = [(-1) ** bin(pidx & gray[m]).count("1") / N for m in range(N)]
    for m in range(N):
        qc.ry(2 * t * coef[m], target)
        changed = (gray[m] ^ gray[(m + 1) % N]).bit_length() - 1
        qc.cx(controls[changed], target)

def q_double_fast(qc, t, i, j, k, l):
    for m in (i, j, l): qc.cx(k, m)
    _ucry(qc, t, [i, j, l], k, (1, 1, 0))
    for m in (l, j, i): qc.cx(k, m)

def build_q_upccgsd_fast(layers, keep=None):
    """keep: lista opcional de (layer, kind, p, q) para podar excitaciones."""
    ops = [(L, kind, p, q) for L in range(layers) for kind in ("D", "S") for p, q in itertools.combinations(range(N_ORB), 2)]
    if keep is not None: ops = [o for o in ops if o in keep]
    th = ParameterVector("θ", len(ops)); qc = QuantumCircuit(N_QUBITS)
    for q in HF_QUBITS: qc.x(q)
    for n, (L, kind, p, q) in enumerate(ops):
        if kind == "D": q_double_fast(qc, th[n], A(p), B(p), A(q), B(q))
        else: q_single(qc, th[n], A(p), A(q)); q_single(qc, th[n], B(p), B(q))
    qc.name = f"{layers}-QUpCCGSD" + ("" if keep is None else f"-poda{len(ops)}")
    return qc, ops
