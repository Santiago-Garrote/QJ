# 0007. Stand-ins que se apagan solos

## Estado

Aceptada

## Contexto

Las piezas de compañeros (#1 referencias, #2 qubit_hamiltonian, #4 build_ansatz, #5 params) no estaban en main cuando se desarrollaron las demás secciones.

## Decisión

Cada sección llama a la función del contrato y solo ante `NotImplementedError` usa un `_standin_*` propio. Al llegar las piezas reales los stand-ins dejan de dispararse sin tocar código. La celda 4.2 imprime qué stand-ins se usaron.

## Alternativas consideradas

- Implementar las piezas ajenas (prohibido, duplica trabajo).
- Esperar a que lleguen (bloquea a todos).

## Consecuencias

En la corrida integrada la celda 4.2 imprimió 'ninguno (todas las piezas reales)'. Solo queda `ruido.py` (#3), que depende de los organizadores.

## Referencias

Issues #1, #2, #4, #5, #3.
