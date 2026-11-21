# #19: esquemas de medición (gastar menos shots)

Volver al [índice ELI5](README.md). Glosario: [`docs/glosario.md`](../glosario.md). ADR: [`docs/adr/`](../adr/README.md).

## Qué pedía el issue

Comparar al menos dos esquemas de medición en distancias estiradas (QWC contra otros), con los shots necesarios para una σ objetivo. Las energías tienen que salir de `SamplerV2` con shots reales. Está en la sección "Extras" del notebook, subsección de #19.

## Qué construimos

Cuatro esquemas, todos sobre el mismo estado `|ψ(θ*)⟩` que mide [#6](06-medicion-sampler.md), en 1,8 / 2,4 / 3,0 Å:

| Esquema | Idea |
|---|---|
| **QWC #6** | Línea de base: grupos por *sorted insertion*. |
| **(a) QWC mejorado** | Mismos grupos, pero se elige la partición que minimiza `K = Σ √Var_g` entre unas 100 candidatas. |
| **(b) Conmutantes + Clifford** | Grupos donde todo conmuta (no solo qubit a qubit), diagonalizados con un circuito Clifford (`StabilizerState.from_stabilizer_list`). |
| **(c) Rotación de base (doble factorización, DF)** | Se reescribe el Hamiltoniano como suma de pocos fragmentos, cada uno diagonal tras una red de rotaciones de Givens por espín. |

Cada esquema se valida: `V O V†` es diagonal, los fragmentos suman H y las esperanzas exactas suman la energía del statevector. Cada fragmento se mide con su propia llamada a `SamplerV2` y su propia semilla.

## Analogía

Medir un Hamiltoniano es pesar muchas piezas con una balanza que solo pesa piezas "compatibles" a la vez. QWC las agrupa con una regla estricta, lo que da muchos grupos. DF reacomoda la mercadería antes de pesarla, con un paso de reordenado, de modo que alcanza con pocas pesadas. Cuesta un poco de preparación (los `cz` de la red de Givens) pero ahorra muchas mediciones.

## Números y gráficos clave

Shots para σ = 1 mHa (no dependen de `QJ_SHOTS_SCALE`):

| Esquema | 1,8 Å | 2,4 Å | 3,0 Å |
|---|---|---|---|
| QWC #6 | 2,33e6 | 2,02e6 | 1,99e6 |
| (a) | 0 a 5 % menos | igual | igual |
| (b) | 2,2x menos | 2,5x menos | 3,4x menos |
| (c) DF | 3,7e5 | 5,5e4 | 6,1e3 |

- DF usa 6x menos shots a 1,8 Å, 37x a 2,4 Å y 327x a 3,0 Å. Los 3,7e5 coinciden con los unos 3,4e5 del análisis de referencia.
- (b) cuesta hasta 81 `cz` por circuito. DF, como mucho 24.
- DF conserva `N_α` y `N_β`, así que permite **post-seleccionar** resultados por número de partículas y `S_z` (útil para #13).
- Recomendación: usar DF para el resultado principal de #6.
- La sección tarda unos 19 s a escala 0,05.

## Qué sigue siendo stand-in

Nada propio. Usa las piezas reales de #1, #2, #4 y #5 a través de la tubería de #6.

## Cómo probarlo

1. Correr con `QJ_SHOTS_SCALE=0.05`.
2. Las celdas 19.2 y 19.3 validan los fragmentos con asserts.
3. La celda 19.4 compara la energía medida con la de #6 con un umbral de 3 σ combinadas. Los valores de `z` dependen de la escala y la semilla.
4. La figura 19.5 muestra los shots por esquema.

## Cuidados (gotchas)

- **`EstimatorV2` no muestrea.** Solo `SamplerV2` sirve para reportar.
- **Signo de los orbitales.** DF necesita que el signo de los orbitales coincida con el Hamiltoniano de #2. Si ningún patrón de signos lo reproduce, `_ms_integrals` imprime un `AVISO` y devuelve `None`. DF se saltea en esa distancia (no se rompe la celda) y la figura deja una barra con NaN.
- Los z de la tabla 19.4 fluctúan entre corridas. Las mayores diferencias vienen del punto de #6.
- Los shots "exactos" para σ = 1 mHa se calculan con varianzas exactas, no con muestreo.
