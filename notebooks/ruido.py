"""Modelo de ruido común de la QuantumJam 2026 (extra "Simulador con ruido").

Especificación del enunciado (igual para todos los equipos):
  - compuertas nativas: cz, sx, x y rz;
  - qubits conectados en línea (0-1-2-...-7);
  - probabilidad de error de 0,1 % por cz y de 0,005 % por compuerta de un qubit.

Interpretación: "probabilidad de error p" = con probabilidad p, después de la compuerta se aplica
un error de Pauli no trivial elegido al azar (15 posibles para cz, 3 para un qubit). Es un canal
depolarizante con parámetro λ = p · d² / (d² − 1) en la convención de Aer. Las rz también llevan
el error de un qubit, porque el enunciado no las excluye (en hardware real son virtuales).
No hay error de lectura ni de preparación: el enunciado no los menciona.

Uso:
    from ruido import BASIS_GATES, noise_model, transpile_noisy, noisy_sampler

    tqc = transpile_noisy(qc)                 # base cz/sx/x/rz, conectividad en línea
    sampler = noisy_sampler(seed=123)         # SamplerV2 de qiskit_aer con el ruido
    result = sampler.run([(tqc, params, shots)]).result()

    # o, con el sampler propio:  SamplerV2(options={"backend_options": backend_options()})

Ojo: transpilar SIEMPRE con transpile_noisy (o con la misma base y conectividad). Una compuerta
que no esté en BASIS_GATES (h, sdg, cx, ...) se simularía sin ruido.
"""
from __future__ import annotations

from itertools import product

from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap
from qiskit_aer.noise import NoiseModel, pauli_error
from qiskit_aer.primitives import SamplerV2

BASIS_GATES = ["cz", "sx", "x", "rz"]
P_CZ = 1e-3   # 0,1 % por cz
P_1Q = 5e-5   # 0,005 % por compuerta de un qubit


def _uniform_pauli_error(p: float, n_qubits: int):
    """Con probabilidad p, un Pauli no trivial al azar sobre n_qubits; con 1 − p, nada."""
    others = ["".join(l) for l in product("IXYZ", repeat=n_qubits) if set(l) != {"I"}]
    return pauli_error([("I" * n_qubits, 1 - p)] + [(l, p / len(others)) for l in others])


def noise_model(p_cz: float = P_CZ, p_1q: float = P_1Q) -> NoiseModel:
    """NoiseModel de Aer con el ruido del enunciado."""
    nm = NoiseModel(basis_gates=BASIS_GATES)
    nm.add_all_qubit_quantum_error(_uniform_pauli_error(p_cz, 2), ["cz"])
    nm.add_all_qubit_quantum_error(_uniform_pauli_error(p_1q, 1), ["sx", "x", "rz"])
    return nm


def coupling_map(n_qubits: int) -> CouplingMap:
    """Qubits en línea: 0-1-2-...-(n-1), bidireccional."""
    return CouplingMap.from_line(n_qubits)


def transpile_noisy(qc: QuantumCircuit, optimization_level: int = 3, seed_transpiler: int = 0) -> QuantumCircuit:
    """Transpila a la base y la conectividad del modelo (igual que transpile_line de la celda 0.1)."""
    return transpile(qc, basis_gates=BASIS_GATES, coupling_map=coupling_map(qc.num_qubits),
                     optimization_level=optimization_level, seed_transpiler=seed_transpiler)


def backend_options(method: str = "density_matrix", **kwargs) -> dict:
    """backend_options para SamplerV2/EstimatorV2 de qiskit_aer.

    density_matrix (por defecto) simula el canal una vez por circuito y después muestrea: con 8 qubits es
    mucho más rápido que statevector, que con ruido corre una trayectoria por shot.
    """
    return {"method": method, "noise_model": noise_model(**kwargs)}


def noisy_sampler(seed: int | None = None, method: str = "density_matrix", **kwargs) -> SamplerV2:
    """SamplerV2 de qiskit_aer con el modelo de ruido.

    Ojo con seed: con una semilla fija, Aer repite semillas entre pubs de una misma llamada a run(), y las
    mediciones de distintos pubs quedan correlacionadas. Para medir varios grupos, usar un sampler (o una
    semilla) distinto por pub.
    """
    return SamplerV2(seed=seed, options={"backend_options": backend_options(method, **kwargs)})
