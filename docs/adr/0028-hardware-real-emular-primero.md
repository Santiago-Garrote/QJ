# 0028. Hardware real de IBM: emular primero con la calibración actual y elegir un ansatz corto

## Estado

Aceptada

## Contexto

El extra #22 corre un punto estirado en un procesador real de IBM. El ansatz completo (465 `cz`) queda dominado por el ruido en hardware, el plan Open tiene ~10 min de QPU por mes y las colas son impredecibles. No es un resultado juzgado (las reglas piden `qiskit_aer`).

## Decisión

- Antes de usar QPU, emular localmente con `AerSimulator.from_backend(backend)`, que toma la calibración actual del equipo real, los mismos circuitos ya transpilados al layout del equipo.
- Elegir el tamaño del ansatz con un barrido en esa emulación: selección *greedy* tipo ADAPT sobre las excitaciones distintas del ansatz de #4, ángulos ajustados con statevector. Resultado en `ibm_marrakesh` a 2,4 Å: 2 operadores (28 `cz`) +342 mHa, 4 (60 `cz`) +361 mHa, 6 (114 `cz`) +431 mHa → se usan 2.
- Medir con `SamplerV2` de `qiskit-ibm-runtime` en 46 grupos QWC × 4000 shots y calcular E y σ desde los bitstrings, como #6.
- El notebook muestra los resultados guardados (no necesita credenciales); `scripts/ibm_hardware.py` (`emulate`, `scan`, `submit`, `fetch`) permite repetir la corrida con una cuenta propia. Las credenciales nunca van al repo.

## Alternativas consideradas

- Mandar el ansatz completo: ruido puro y más tiempo de QPU.
- Comparación de optimizadores (COBYLA/SPSA) con ruido emulado: mucho más cómputo para el tiempo disponible.

## Consecuencias

- Corrida real: job `dc0uo5qnj2vs73del9s0`, 51 s de QPU. E = −1,48834 ± 0,0058 Ha (+386 mHa vs. FCI), 52 mHa por debajo de Hartree-Fock (~9 σ) y 44 mHa peor que la emulación (~7 σ): el modelo de `from_backend` no ve *crosstalk*, deriva ni errores coherentes.
- Mejorar requiere menos qubits (#14) y mitigación (#13).

## Referencias

Issue #22; `scripts/ibm_hardware.py`; `docs/analysis/data/ibm_hardware_marrakesh_2.4A.json`, `ibm_scan_marrakesh_2.4A.json`.
