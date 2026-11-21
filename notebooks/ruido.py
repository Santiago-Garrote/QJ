"""Modelo de ruido común de la QuantumJam 2026 (extra "Simulador con ruido").

Lo que pide el enunciado (igual para todos los equipos):
  - compuertas cz, sx, x y rz;
  - qubits conectados en línea (0-1-2-...-7);
  - una probabilidad de error de 0,1 % por cz y de 0,005 % por compuerta de un qubit.

Cómo lo interpretamos: después de cada compuerta, con probabilidad p se aplica un error de Pauli
elegido al azar entre los no triviales (15 para cz, 3 para un qubit). La fidelidad de proceso de
cada compuerta queda en 1 − p. Las rz también llevan error, porque el enunciado no las excluye.
No hay error de lectura: el enunciado no lo menciona.

Sigue el estilo de los notebooks de los workshops (github.com/Computer-Society-ITBA/quantumjam-workshops):
transpilar con generate_preset_pass_manager, mapear el observable con apply_layout y medir con las
primitivas de qiskit_aer. Ejemplo:

    from ruido import transpilar, estimator_ruidoso, sampler_ruidoso, contar_cz

    transpilado = transpilar(circuito)                       # base cz/sx/x/rz, qubits en línea
    H_mapeado = H.apply_layout(transpilado.layout)
    energia = estimator_ruidoso().run([(transpilado, H_mapeado, parametros)]).result()[0].data.evs

    transpilado.measure_all()
    cuentas = sampler_ruidoso(semilla=5).run([(transpilado, parametros)], shots=10_000).result()[0].data.meas.get_counts()

estimator_ruidoso() se puede pasar directo como `estimator=` a la función vqe(...) de los workshops.

Importante: transpilar SIEMPRE con transpilar(). Una compuerta que no esté en COMPUERTAS_BASE
(h, sdg, cx, ...) se simularía sin ruido.
"""
from __future__ import annotations

from itertools import product

from qiskit import QuantumCircuit
from qiskit.transpiler import CouplingMap
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, pauli_error
from qiskit_aer.primitives import EstimatorV2 as AerEstimator, SamplerV2 as AerSampler

COMPUERTAS_BASE = ["cz", "sx", "x", "rz"]
ERROR_CZ = 1e-3   # 0,1 % por cz
ERROR_1Q = 5e-5   # 0,005 % por compuerta de un qubit
METODO = "density_matrix"  # con 8 qubits es mucho más rápido que statevector, que corre una trayectoria por shot


def _error_de_pauli(p: float, n_qubits: int):
    """Con probabilidad p, un Pauli no trivial al azar sobre n_qubits; con probabilidad 1 − p, nada."""
    paulis = ["".join(letras) for letras in product("IXYZ", repeat=n_qubits) if set(letras) != {"I"}]
    return pauli_error([("I" * n_qubits, 1 - p)] + [(pauli, p / len(paulis)) for pauli in paulis])


def modelo_de_ruido(error_cz: float = ERROR_CZ, error_1q: float = ERROR_1Q) -> NoiseModel:
    """NoiseModel de qiskit_aer con el ruido del enunciado."""
    modelo = NoiseModel(basis_gates=COMPUERTAS_BASE)
    modelo.add_all_qubit_quantum_error(_error_de_pauli(error_cz, 2), ["cz"])
    modelo.add_all_qubit_quantum_error(_error_de_pauli(error_1q, 1), ["sx", "x", "rz"])
    return modelo


def conectividad(n_qubits: int) -> CouplingMap:
    """Qubits en línea: 0-1-2-...-(n-1), en las dos direcciones."""
    return CouplingMap.from_line(n_qubits)


def transpilar(circuito: QuantumCircuit, optimization_level: int = 3, seed_transpiler: int = 0) -> QuantumCircuit:
    """Adapta el circuito a las compuertas y la conectividad del modelo (igual que transpile_line de la celda 0.1)."""
    pm = generate_preset_pass_manager(optimization_level=optimization_level, basis_gates=COMPUERTAS_BASE,
                                      coupling_map=conectividad(circuito.num_qubits), seed_transpiler=seed_transpiler)
    return pm.run(circuito)


def contar_cz(circuito: QuantumCircuit) -> int:
    """Cuenta las cz que quedan al transpilar el circuito."""
    return transpilar(circuito).count_ops().get("cz", 0)


def opciones_backend(metodo: str = METODO) -> dict:
    """backend_options para las primitivas de qiskit_aer."""
    return {"method": metodo, "noise_model": modelo_de_ruido()}


def backend_ruidoso(metodo: str = METODO) -> AerSimulator:
    """AerSimulator con el ruido, para usar con backend.run(transpilado, shots=...)."""
    return AerSimulator(**opciones_backend(metodo))


def sampler_ruidoso(semilla: int | None = None, metodo: str = METODO) -> AerSampler:
    """SamplerV2 de qiskit_aer con el ruido.

    Ojo con la semilla: con una semilla fija, Aer repite semillas entre los pubs de una misma llamada
    a run(), y las mediciones de distintos pubs quedan correlacionadas. Para medir varios grupos de
    términos, usar un sampler (o una semilla) distinto por pub.
    """
    return AerSampler(seed=semilla, options={"backend_options": opciones_backend(metodo)})


def estimator_ruidoso(precision: float = 0.0, semilla: int | None = None, metodo: str = METODO) -> AerEstimator:
    """EstimatorV2 de qiskit_aer con el ruido.

    Devuelve el valor esperado exacto del estado ruidoso. Con precision > 0, Aer le suma ruido gaussiano
    de ese ancho (no muestrea shots): para la barra de error de verdad, medir con sampler_ruidoso().
    """
    opciones = {"backend_options": opciones_backend(metodo), "default_precision": precision}
    if semilla is not None:
        opciones["run_options"] = {"seed": semilla}
    return AerEstimator(options=opciones)


# Nombres en inglés (los documentados primero en el issue #3).
BASIS_GATES, P_CZ, P_1Q = COMPUERTAS_BASE, ERROR_CZ, ERROR_1Q
noise_model, coupling_map, transpile_noisy = modelo_de_ruido, conectividad, transpilar


def noisy_sampler(seed: int | None = None, method: str = METODO) -> AerSampler:
    return sampler_ruidoso(seed, method)
