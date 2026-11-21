# #6: medir la energía con shots reales

Volver al [índice ELI5](README.md). Glosario: [`docs/glosario.md`](../glosario.md). Decisiones de infraestructura: [`docs/adr/`](../adr/README.md).

## Qué pedía el issue

Llenar la tabla `vqe` del contrato: una fila por distancia `d` con `energy`, `sigma`, `shots` y `cz`. Reglas duras:

- La energía sale de **medir** circuitos con `qiskit_aer.primitives.SamplerV2` y una cantidad explícita de shots.
- Hay que reportar σ y validarla.
- Hay que documentar cuántos shots se gastan y cómo se reparten.
- El resultado tiene que ser reproducible.

Está en la celda 4.2 del notebook (de `4.2.0` a `4.2.8`).

## Qué construimos

**Partir el Hamiltoniano en grupos.** El Hamiltoniano es una suma de unos 185 términos de Pauli (productos de X, Y, Z, I sobre los 8 qubits). No se pueden medir todos a la vez. Pero términos que "caben" en la misma base de medición sí. Los agrupamos con la regla QWC (qubit-wise commuting): dos términos pueden ir juntos si, qubit por qubit, usan la misma letra o una es I. Salen entre 37 y 41 grupos.

**Medir cada grupo.** Para cada grupo se rotan los qubits a la base correcta (con `H` para X, con `S†H` para Y) y se miden todos en Z. Cada bitstring que sale vale un número (el valor del grupo en ese shot). Se promedia.

**Calcular σ.** Con la varianza de ese valor por shot se obtiene el error estándar. Importante: se usa la varianza del grupo entero, así ya incluye las covarianzas entre sus términos.

**Repartir shots en dos etapas.** Primero un piloto de 500 shots por grupo, para estimar cada varianza. Después se reparte el resto en proporción a la raíz de la varianza del grupo (los grupos "ruidosos" reciben más). La meta es σ de unos 3 mHa (1,8 mHa a 1,8 Å, donde el margen contra CCSD es el más chico).

Funciones y datos principales:

- `measure_energy(...)` y `measure_energy_many(...)` (varias repeticiones en un solo job).
- `qwc_groups`, `sigma_target`.
- `get_references`, `get_hamiltonian`: piden la pieza real al contrato y caen al stand-in solo si hace falta.
- La tabla `vqe`, con 19 filas.

## Analogía

Es una encuesta con presupuesto fijo. El Hamiltoniano es la población, cada grupo es un barrio. Primero se hace un sondeo chico en cada barrio (el piloto). Después se entrevista a más gente en los barrios donde las respuestas varían más, porque ahí hace falta más muestra para tener la misma precisión global.

## Números y gráficos clave

- A escala 0,05: 419.386 shots totales (145.000 del piloto), σ de unos 13 mHa por punto.
- Validación 1: medido contra statevector en los 19 puntos, `|z| ≤ 2` en todos (máximo 1,69, χ² = 13,4 con 19 grados de libertad).
- Validación 2: 40 repeticiones en 3 distancias. Dispersión real dividida σ calculada: 0,91, 0,98, 0,82. Si σ es correcta, el cociente cae en [0,82, 1,28] con 95 % de probabilidad.
- Validación 3: σ cae como `1/√shots` (pendiente medida −0,54, esperada −0,5).
- Sin sesgo en una prueba aparte (150 repeticiones a 0,9 Å).

Estas cifras son con el ansatz provisorio y a escala 0,05. La corrida a escala 1 no se midió.

## Qué sigue siendo stand-in

En el notebook integrado, nada: #1, #2, #4 y #5 reales están activos. Los números de arriba vienen de una corrida anterior con stand-ins, así que conviene volver a mirarlos con las piezas reales y escala 1.

## Cómo probarlo

1. Correr el notebook con `QJ_SHOTS_SCALE=0.05` (ver el [README](README.md)).
2. Las celdas `4.2.5` a `4.2.8` hacen las validaciones y fallan si algo no cierra.
3. Repetir la corrida: la tabla `vqe` tiene que salir idéntica.

## Cuidados (gotchas)

- **`EstimatorV2` de qiskit-aer no muestrea.** Devuelve el valor exacto más ruido gaussiano de ancho `precision`. Con `precision=0` coincide con el statevector hasta 1e-8 Ha. Por eso comparar "medido contra exacto" con Estimator no prueba nada. Lo usamos solo como control cruzado (`4.2.8`), nunca para reportar.
- **Reproducibilidad.** La fuente de azar oculta era PySCF: sus sumas en paralelo (OpenMP) cambian de orden entre corridas. Se arregla con `pyscf.lib.num_threads(1)`. Aer no era el problema.
- **`bad allocation`.** Muchos bindings en un solo job agotan memoria. Se parten en jobs de a lo sumo 600 (`MAX_BINDINGS_PER_JOB`).
- **Velocidad.** Con `method="statevector"` explícito el binding de Aer va 3 veces más rápido.
- **Un z alto aislado.** En la tabla de repeticiones aparece un z de 2,8 a 0,9 Å. La prueba aparte lo explica como fluctuación.
