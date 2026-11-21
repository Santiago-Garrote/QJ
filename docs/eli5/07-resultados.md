# #7: resultados (curva, R_e, D_e y tabla)

Volver al [índice ELI5](README.md). Glosario: [`docs/glosario.md`](../glosario.md). ADR: [`docs/adr/`](../adr/README.md).

## Qué pedía el issue

Convertir la tabla `vqe` de [#6](06-medicion-sampler.md) en los entregables del desafío:

- Un gráfico con las tres curvas (VQE con ±σ, CCSD, FCI) y un panel de errores.
- `R_e` y `D_e` para VQE, FCI y CCSD, con incertidumbre, en una tablita.
- Una tabla por punto con la columna `gana_a_ccsd`.
- Nada pegado a mano: todo se recalcula.

Está en la sección 5 del notebook (celdas 5.1 a 5.4).

## Qué construimos

- **`resultados`**: la tabla `vqe` más `e_ccsd`, `e_fci`, `err_vqe`, `err_ccsd` (en mHa) y `gana_a_ccsd`. Esa última es `err_vqe + σ < err_ccsd`, o sea exige ganar aun sumando la barra de error. Solo se evalúa para `d ≥ 1,8 Å`; antes vale `<NA>`.
- **Gráfico** de dos paneles. Izquierda: `E(d)` con ±σ contra CCSD y FCI. Derecha: errores en escala log, con una línea en 1,6 mHa (precisión química) y otra vertical en 1,8 Å.
- **`R_e`**: la distancia del mínimo. Se ajusta un polinomio de grado 4 entre 0,6 y 1,4 Å (VQE ponderado por 1/σ) y se toma el mínimo del ajuste.
- **`D_e = E(3,0 Å) − E(R_e)`**: cuánta energía cuesta romper la molécula.
- **Incertidumbre**: bootstrap paramétrico (2000 muestras: se vuelve a sortear cada energía como una normal con su σ y se repite el ajuste) más un barrido de sensibilidad (grados 2 a 5 por 4 ventanas). Ambas se suman en cuadratura.
- **Chequeo de disociación**: calcula 4 átomos de H aislados con UHF STO-3G. El FCI a 3,0 Å queda 0,96 mHa por debajo de ese valor, y se imprime y se explica.

## Analogía

Es el reporte final de un experimento: tomaste lecturas con ruido, ahora ajustás una curva suave para encontrar el punto más bajo. El bootstrap es repetir el experimento "en la imaginación" muchas veces para ver cuánto se mueve la respuesta.

## Números y gráficos clave

Con el ansatz provisorio y escala 0,05, los números eran de prueba de tubería y no resultados finales: `R_e` VQE 0,896 ± 0,084 Å contra FCI 0,885 ± 0,072 Å, `D_e` VQE 315,5 ± 25,5 mHa, y `gana_a_ccsd` en 3 de 7 puntos. Los resultados con las piezas reales salen de ejecutar el notebook integrado (también aparecen en la celda "Resultados clave", que da un resumen de una pantalla).

Referencias del análisis: CCSD se equivoca 9,1 mHa a 1,8 Å, y ese es el margen más chico a vencer.

## Qué sigue siendo stand-in

Nada propio. Hereda lo de #6, que ahora usa las piezas reales de #1, #2, #4 y #5.

## Cómo probarlo

1. Correr el notebook con `QJ_SHOTS_SCALE=0.05`.
2. Revisar que `resultados` tenga una fila por distancia y que `gana_a_ccsd` sea `<NA>` bajo 1,8 Å.
3. Mirar la figura de la celda 5.2 y la tablita de la celda 5.4.

## Cuidados (gotchas)

- **La sensibilidad domina la incertidumbre.** El barrido incluye grado 2 con ventanas anchas, que está sesgado. Con datos reales conviene decidir si se restringe a grados 3 a 5.
- **El mínimo puede caer en el borde de la ventana** si el VQE se parece poco a FCI cerca de 0,6 Å.
- **CCSD puede quedar por debajo de FCI** en algún punto. Por eso los errores se miden en valor absoluto.
- La energía de H aislado se calcula en la misma celda con PySCF. Es lo único que no viene de `refs` ni de `vqe`.
- Las cifras con escala 0,05 no sirven para reportar. Hay que correr con escala 1.
