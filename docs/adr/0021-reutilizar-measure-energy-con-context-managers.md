# 0021. Reutilizar measure_energy de #6 con ruido mediante context managers

## Estado

Aceptada

## Contexto

`measure_energy` y `_sample` crean el SamplerV2 internamente con `options={'backend_options': _AER_OPTIONS}`; #6 cambió mientras se trabajaba (primero `SamplerV2(seed=...)` sin opciones). FakeFez además necesita un circuito de 156 qubits leído en 8 bits, pero `_sample` asume `template.num_qubits` bits.

## Decisión

Para #11, el context manager `con_ruido()` reemplaza temporalmente `_AER_OPTIONS` por `{**orig, method: density_matrix, noise_model: nm}` y lo restaura. Para #12, `con_ruido_fez()` reasigna `_measurement_template` (plantilla transpilada envuelta en un proxy de 8 qubits), `SamplerV2` (wrapper sobre el de qiskit_aer con el ruido de FakeFez, que ignora las opciones sin ruido de #6) y `UNITS_PER_GROUP`, y llama a `measure_energy` sin modificar.

## Alternativas consideradas

- `functools.partial` sobre SamplerV2: se rompió cuando #6 pasó `options` (TypeError por keyword duplicada).
- Copiar `measure_energy` o editar issue6.py: prohibido, divergiría.
- EstimatorV2: oculta el error de lectura.

## Consecuencias

Cero lógica de medición duplicada, pero acoplada a nombres internos de #6 (`_AER_OPTIONS`, `_measurement_template`, `SamplerV2`, `UNITS_PER_GROUP`). Si #6 los renombra, falla de forma visible (KeyError); #12 ya se rompió una vez por el cambio de `options`.

## Referencias

Issues #6, #11, #12.
