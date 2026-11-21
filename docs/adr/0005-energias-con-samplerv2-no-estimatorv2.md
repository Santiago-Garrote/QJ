# 0005. Energías reportadas con SamplerV2, no con EstimatorV2 de qiskit-aer

## Estado

Aceptada

## Contexto

El EstimatorV2 de qiskit-aer no muestrea: devuelve el valor exacto más ruido gaussiano de ancho `precision` (default 0) y `stds = precision`. Verificado en qiskit-aer 0.17.2. Reportarlo equivale a leer el statevector. La issue #6 se corrigió y renombró por esto.

## Decisión

Todas las energías reportadas salen de `SamplerV2` con shots reales y agrupado QWC propio. La varianza es σ² = Σ_g Var_g/shots_g, con Var_g la varianza por shot del grupo completo, y la semilla va fija en `seed_simulator`. Para d = 1,8 Å el agrupado propio da 37 grupos, frente a 46 de `group_commuting` de Qiskit. EstimatorV2 queda solo como control cruzado (celda 14), declarando que su `precision` no es una cantidad de shots.

## Alternativas consideradas

- EstimatorV2 con `precision` > 0: no tiene shots detrás.
- `group_commuting` de Qiskit: 46 grupos, más circuitos y menos eficiente.

## Consecuencias

Los números reportados son comparables con los de hardware. Hay que mantener el agrupado propio.

## Referencias

Issue #6; reglas en docs/challenge/*.md.
