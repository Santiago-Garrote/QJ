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

- Corrida real reproducible: job `dc0urtmq4uuc73a3895g`, ~51 s de QPU. Emulación de los mismos circuitos: E = −1,53129 ± 0,0058 Ha (+343 mHa vs. FCI). Hardware: E = −1,48503 ± 0,0059 Ha (+390 mHa), 49 mHa por debajo de Hartree-Fock (~8 σ) y 46 mHa peor que su emulación (~5,6 σ combinadas): el modelo de `from_backend` no ve *crosstalk*, deriva ni errores coherentes.
- Una primera corrida (job `dc0uo5qnj2vs73del9s0`) no guardó los grupos medidos y el análisis los recalculaba: el mismo conteo dio −1,4883 o −1,4957 Ha según el proceso. Se corrigió: PySCF a un hilo, emular y mandar los mismos circuitos ISA en un solo proceso, y guardar los grupos (etiquetas y coeficientes) con el *job*; `fetch` usa esos grupos.
- Mejorar requiere menos qubits (#14) y mitigación (#13).

## Referencias

Issue #22; `scripts/ibm_hardware.py`; `docs/analysis/data/ibm_hardware_marrakesh_2.4A.json`, `ibm_scan_marrakesh_2.4A.json`.
