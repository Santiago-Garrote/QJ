# 0013. Pruebas rápidas con QJ_SHOTS_SCALE

## Estado

Aceptada

## Contexto

La corrida completa de la sección 4.2 tarda ~3 min.

## Decisión

Las pruebas usan `QJ_SHOTS_SCALE=0.05` y la corrida reportada usa 1,0. En Windows se corre con `PYTHONUTF8=1` (la consola cp1252 falla al imprimir 'Δ'); en Colab no hace falta, así que no se cambió el código.

## Alternativas consideradas

- Reemplazar 'Δ' por 'Delta' en los prints: cambia el notebook por un problema del entorno local.

## Consecuencias

El notebook completo corrió en 357 s a escala 0,05 (solo la optimización de #5 tomó 86 s). El tiempo a escala 1 no se midió.

## Referencias

Issue #6.
