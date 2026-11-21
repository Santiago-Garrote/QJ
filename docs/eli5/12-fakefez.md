# #12: ruido de hardware con FakeFez

Volver al [índice ELI5](README.md). Glosario: [`docs/glosario.md`](../glosario.md). ADR: [`docs/adr/`](../adr/README.md).

## Qué pedía el issue

Un extra: medir **un** punto estirado (`d = 2,4 Å`) con el ruido de un chip IBM real simulado, `FakeFez` (156 qubits, Heron r2), y compararlo con las otras referencias. Pedía también explicar la diferencia con `ruido.py` ([#11](11-ruido.md)) y agregar la dependencia `qiskit-ibm-runtime`. Está en la sección "Extras" del notebook, subsección de #12.

## Qué construimos

- **Backend y ruido.** `FakeFez` viene de `qiskit_ibm_runtime.fake_provider`. El ruido sale de `NoiseModel.from_backend(FakeFez())`: errores por qubit y por par, T1/T2 (tiempos en que un qubit "se olvida") y error de lectura.
- **Transpilación al chip.** El circuito se adapta a la conectividad real (heavy-hex, con SWAPs extra) con optimización nivel 3 y la mejor de 3 semillas de layout. Recién ahí se cuentan `cz` y profundidad.
- **Medición.** `SamplerV2` con matriz densidad y shots reales. Se reutiliza `measure_energy` de #6: dentro de `con_ruido_fez()` se cambian temporalmente `_measurement_template`, el sampler y `UNITS_PER_GROUP`.
- **Cuatro circuitos**: ansatz completo, versión de 2 operadores, de 1 operador y el estado HF (0 operadores, 0 `cz`). El HF aísla el efecto de la lectura.
- **Dependencia**: `qiskit-ibm-runtime==0.47.0`, instalada con un `%pip` propio en la primera celda de esta sección (no en `requirements.txt`, ver [ADR 0011](../adr/0011-fakefez-via-qiskit-ibm-runtime.md)).

## Analogía

Es probar el mismo plano en un taller real en vez de un taller ideal. Las máquinas reales tienen herramientas con tolerancias distintas, y el taller no es una línea recta: para pasar una pieza de una máquina a otra lejana hay que moverla por intermediarios (los SWAPs).

## Números y gráficos clave

Con el ansatz provisorio y escala 0,05 (σ de unos 13 mHa): el ansatz completo, con 711 `cz` y profundidad 1794, suma unos +660 mHa por ruido. La versión de 2 operadores (145 `cz`) llega a 449 mHa de error, la de 1 operador (44 `cz`) a 396 mHa y el HF (0 `cz`) a 433 mHa. **Ningún circuito le gana al HF bajo FakeFez.** Esto coincide con el análisis de referencia: cientos de mHa lejos de FCI. Para comparar, el circuito exacto del análisis tenía 500 a 650 `cz`.

Con el ansatz real los `cz` y los errores son otros. Hay que leerlos de la tabla de la celda 12.3.

## Qué sigue siendo stand-in

- `ruido.py` (#3) no está en `main`, así que no hay números lado a lado. La comparación es una explicación cualitativa: `ruido.py` es despolarizante uniforme, con conectividad lineal y sin T1/T2 ni lectura. FakeFez es calibrado qubit por qubit, con unos 3,9e-3 por `cz`, lectura de unos 7,6e-3 y SWAPs por la conectividad heavy-hex.
- #1, #2, #4 y #5 son los reales.

## Cómo probarlo

1. Correr el notebook con `QJ_SHOTS_SCALE=0.05`. Esta celda tardó unos 75 s bajo carga.
2. Revisar la tabla con `E ± σ`, `cz` y profundidad en el backend, para los 4 circuitos.
3. Fuera de Colab, instalar antes `pip install qiskit-ibm-runtime==0.47.0` en el entorno.

## Cuidados (gotchas)

- **`EstimatorV2` esconde la lectura.** En el control con el HF, el Estimator se mueve 0,2 mHa y el Sampler unos 5 mHa. Porque no muestrea, no ve el error de lectura. Solo sirve para comparar.
- **Dependencia fuera de nixpkgs.** `qiskit-ibm-runtime` no está empaquetado en nixpkgs al commit de `flake.lock`, por eso no va en `requirements.txt` (rompería el shell de Nix) y se instala solo en esta sección. El pin 0.47.0 es la versión probada localmente.
- **`restringir()`** arma la versión corta. Con el ansatz real hay CX fijos entre rotaciones. Los de una excitación descartada se cancelan entre sí y el transpilador los elimina.
- **σ** es el error de los shots. No incluye la variación entre calibraciones.
- A escala 0,05, el efecto de lectura sobre el HF (5 a 8 mHa) no se distingue de σ (13 mHa). Se resuelve solo a escala completa.
- Con la máquina cargada hubo fallos transitorios (`bad allocation`). Volver a correr.
