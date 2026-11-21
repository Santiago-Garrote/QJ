# 0010. Modelo de ruido: stand-in mientras faltaba ruido.py, después el oficial

## Estado

Aceptada (actualizada cuando llegó `ruido.py`, PR #27)

## Contexto

`ruido.py` dependía de #3. Mientras no estuvo en `main`, el extra #11 necesitaba un modelo de ruido para avanzar. Con #27, el equipo armó `notebooks/ruido.py` según el enunciado (Pauli no trivial al azar con probabilidad 0,1 % por `cz` y 0,005 % por compuerta de un qubit; base `cz, sx, x, rz`; qubits en línea). Como el repo es privado, la convención de #3 es pegarlo en el notebook con `%%writefile ruido.py` antes de importarlo.

## Decisión

- El notebook incluye una celda `%%writefile ruido.py` (copia exacta de `notebooks/ruido.py`) al inicio de la subsección de #11, y #11 usa `noise_model()` de ese archivo.
- El stand-in (`_standin_noise_model`, despolarizante con la misma especificación) queda solo como respaldo si el archivo faltara; se apaga solo.
- `ruido.py` no incluye la compuerta `u` que usamos para rotar la base de medición, y una compuerta fuera del modelo se simula sin ruido. Le agregamos el error de su descomposición (5 compuertas de un qubit), igual que hacía el stand-in.

## Alternativas consideradas

- Esperar a #3 sin avanzar con #11.
- Transpilar las rotaciones de medición a `sx/rz` en vez de agregar error a `u`: más fiel, pero cambia el circuito de medición compartido con #6.

## Consecuencias

- Los resultados con ruido de #11 salen del modelo oficial del equipo.
- Si `notebooks/ruido.py` cambia, hay que actualizar la celda `%%writefile` del notebook (son dos copias).

## Referencias

Issues #3, #11; PR #27; `notebooks/ruido.py`.
