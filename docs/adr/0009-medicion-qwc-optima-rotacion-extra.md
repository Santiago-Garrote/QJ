# 0009. Medición base QWC con reparto óptimo; rotación de base como extra (#19)

## Estado

Aceptada

## Contexto

Hay que ganarle a CCSD (error 9,1 mHa a 1,8 Å) con shots reales.

## Decisión

La medición base usa QWC con reparto óptimo N_g ∝ sqrt(Var_g). Alcanza con ~3e4 shots para σ = 9 mHa a 1,8 Å. La rotación de base (#19) se deja como extra.

## Alternativas consideradas

- Rotación de base como método principal: ahorra ~6x (~3,4e5 shots para σ = 1 mHa a 1,8 Å) pero es más compleja.

## Consecuencias

El método base es simple y suficiente. El ahorro de la rotación se documenta en la sección #19.

## Referencias

docs/analysis/state-of-the-art.md; issues #6 y #19.
