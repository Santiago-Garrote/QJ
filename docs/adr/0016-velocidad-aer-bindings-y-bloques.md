# 0016. Velocidad de Aer: menos costo por binding, repeticiones en un PUB y bloques de 600

## Estado

Aceptada

## Contexto

El costo en Aer es por binding (~5 ms con method automatic), no por job ni por shot. 180 jobs separados tardaban ~100 s. Además, miles de bindings en un job fallan con 'bad allocation' porque Aer expande cada uno en memoria (volvió a aparecer con 100 repeticiones).

## Decisión

Se agregó `measure_energy_many` (repeticiones como bindings extra del mismo PUB; `measure_energy` es un wrapper). Opciones de Aer: `method="statevector"` (3x) y `max_parallel_experiments` = nº de CPUs (2,4x). `UNITS_PER_GROUP` baja de 4 a 2, `N_REPEATS` pasa a 40 y la semilla cambia por distancia. `_sample` parte los bindings en jobs de a lo sumo `MAX_BINDINGS_PER_JOB = 600`, cada uno con semilla `SeedSequence([seed, k])`.

## Alternativas consideradas

- Solo agrupar repeticiones: no ayuda, cada binding cuesta igual.
- Bajar N_REPEATS: menos potencia para validar σ.
- Un PUB gigante: frágil.

## Consecuencias

La curva baja de 26 s a ~6-12 s y la validación de ~100 s a 17-21 s. El reparto queda más grueso (2 por grupo). Los resultados a escala 0,05 no son comparables número a número con la versión anterior. Ninguna corrida falló tras el corte.

## Referencias

Issue #6.
