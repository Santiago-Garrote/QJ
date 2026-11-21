# 0022. Layout de transpile_line y observable permutado

## Estado

Aceptada

## Contexto

`transpile_line` (opt 3 con acoplamiento en línea) puede elegir un layout y rutear con swaps. Medir el observable original sobre ese circuito daba errores de 1000 a 2500 mHa sin ruido.

## Decisión

`_observable_fisico` aplica `circ.layout.final_index_layout(filter_ancillas=True)` con `op.apply_layout`, y un assert compara contra la energía statevector de #6 (`E_SV[d]`) para el ansatz completo en cada distancia.

## Alternativas consideradas

- Forzar `initial_layout` trivial: cambia el conteo de cz del contrato.
- Swaps de vuelta: inflan los cz.
- Transpilar sin acoplamiento: no es lo que asume el modelo de ruido.

## Consecuencias

El conteo de cz sigue siendo el de `transpile_line` y el circuito medido es el del contrato. El aviso sobre el layout debería llegar al resto del equipo.

## Referencias

Issue #11.
