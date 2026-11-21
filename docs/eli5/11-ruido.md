# #11: simulación con ruido despolarizante

Volver al [índice ELI5](README.md). Glosario: [`docs/glosario.md`](../glosario.md). ADR: [`docs/adr/`](../adr/README.md).

## Qué pedía el issue

Un extra: repetir la medición de [#6](06-medicion-sampler.md) en un simulador **con ruido** y comparar con y sin ruido contra FCI, en al menos 4 distancias. Además, explicar cuánto error aporta el ruido y por qué se relaciona con la cantidad de `cz`. Está en la sección "Extras" del notebook, subsección de #11.

## Qué construimos

- **Modelo de ruido.** Error despolarizante de 1e-3 en cada `cz` y 5e-5 en cada compuerta de un qubit (`sx`, `x`, `rz`), conectividad en línea. Es el modelo común del enunciado (`ruido.py`).
- **Medición.** Se reutiliza `measure_energy` de #6 sin copiarla. Solo se cambia el simulador a matriz densidad con el modelo de ruido, dentro de un context manager (`con_ruido()`). Las rotaciones de base de la medición también reciben error.
- **Tres versiones del ansatz** en 0,9 / 1,8 / 2,4 / 3,0 Å: el completo, una corta de 12 operadores y una de 2.
- **Tabla `RUIDO`** y 3 figuras con energía sin ruido, con ruido, error contra FCI y contra CCSD.
- **Versiones cortas.** Con el ansatz real, la versión corta conserva los `k` operadores con mayor `|θ*|` a lo largo de la curva y reajusta sus ángulos con statevector.

## Analogía

Es mandar un mensaje por teléfono descompuesto. Cada compuerta `cz` es un pasamano en el que el mensaje pierde un poquito de claridad. Con 700 pasamanos ya no se entiende nada. Acortar la cadena ayuda, pero un mensaje muy corto ya no dice lo que hacía falta.

## Números y gráficos clave

- El ruido cuesta unos 0,45 mHa por `cz`.
- Con el ansatz completo (con el stand-in de #4: 711 `cz`) el ruido sumó entre 324 y 654 mHa.
- Con ruido, ninguna versión llega al margen de CCSD (9,1 mHa). El mejor error con ruido fue 181 mHa a 0,9 Å y 228 mHa a 1,8 Å.
- Las versiones cortas tienen un sesgo enorme sin ruido (175 a 337 mHa) porque pocos operadores no alcanzan.
- La conclusión sobre el compromiso expresividad contra ruido se ve bien solo en 0,9 y 1,8 Å.

Estos números son con el ansatz provisorio y escala 0,05. Con el ansatz real (19 operadores) cambian las cifras, no la conclusión: el ruido es de cientos de mHa.

## Qué sigue siendo stand-in

- **`ruido.py` (#3)** todavía no está en `main`. Se usa `_standin_noise_model()` con exactamente la especificación del enunciado. Se apaga solo si existe `notebooks/ruido.py` o `ruido.py` con alguna de las funciones `get_noise_model`, `build_noise_model`, `noise_model`, `make_noise_model` o la variable `NOISE_MODEL`. Es la única pieza faltante en la corrida integrada.
- #1, #2, #4 y #5 son los reales.

## Cómo probarlo

1. Correr con `QJ_SHOTS_SCALE=0.05`.
2. Ver la tabla de la celda 11.4: la columna con ruido debe ser peor que la columna sin ruido en las 4 distancias.
3. Buscar la línea `[stand-in] ruido.py (#3)` para confirmar qué modelo se usó.

## Cuidados (gotchas)

- **`EstimatorV2` no sirve para medir con ruido**, porque no muestrea (valor exacto más ruido gaussiano). Hay que usar `SamplerV2`.
- No se agregó error de lectura (el enunciado no lo menciona). Eso lo cubre [#12](12-fakefez.md).
- No se reoptimizó con ruido (opcional del issue).
- A escala 0,05, σ de la diferencia con y sin ruido es de 6 a 11 mHa. A escala completa baja a 1,3 a 2,5 mHa. Como el ruido es de cientos de mHa, no cambia nada cualitativo.
- Con varias corridas en paralelo, Aer puede fallar con `bad allocation`. Es memoria, se resuelve volviendo a correr.
- Un modelo global de despolarización da 430 a 500 mHa a `d ≥ 1,8` y sobreestima. Sirve solo como orden de magnitud.
