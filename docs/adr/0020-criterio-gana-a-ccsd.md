# 0020. Definición de gana_a_ccsd y err_vqe

## Estado

Aceptada

## Contexto

La issue pide err_vqe + σ < err_ccsd para d >= 1,8.

## Decisión

`err_vqe` usa la energía medida (ruidosa) contra FCI. La columna es `<NA>` para d < 1,8.

## Alternativas consideradas

- Evaluar para todo d: el enunciado solo lo pide desde 1,8.

## Consecuencias

Criterio conservador: hay que ganar aun sumando σ.

## Referencias

Issue #7; docs/challenge/*.md.
