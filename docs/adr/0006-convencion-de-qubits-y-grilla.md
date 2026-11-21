# 0006. Convención de qubits y grilla del contrato del notebook

## Estado

Aceptada

## Contexto

Las celdas del notebook y los scripts de análisis (PR #18) debían compartir orden de qubits y distancias.

## Decisión

Alfa en q0-q3, beta en q4-q7, `HF_BITSTRING = 00110011` y 19 puntos de distancia (celda 4, el contrato compartido, que no se modifica). Los scripts de análisis se alinearon a esto. Con este orden el agrupado QWC greedy pasó de ~70 a 38-48 grupos.

## Alternativas consideradas

- Intercalar alfa y beta: agrupa peor (~70 grupos).

## Consecuencias

Todo el equipo depende de esta convención; cambiarla rompe #1, #2, #4 y #5.

## Referencias

PR #18; celda 4 del notebook.
