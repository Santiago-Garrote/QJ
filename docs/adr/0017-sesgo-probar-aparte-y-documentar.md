# 0017. Sesgo: probar aparte y documentar, no ocultar

## Estado

Aceptada

## Contexto

El z de (media − E_sv)/(σ/√N) salió cerca de 3σ varias veces (3,69 a 3,0 Å; 2,9 a 1,8 Å a escala completa; 2,8 a 0,9 Å). Con tres distancias por corrida y semilla compartida, un z alto no prueba sesgo.

## Decisión

Se probó a 0,9 Å con 150 repeticiones y 4 semillas, fuera del notebook: z = +0,6, −1,3, +0,7, −0,8; sesgo máximo 1,1 mHa con error estándar ~1,4 mHa. Se documenta en el markdown final y cada distancia tiene su semilla.

## Alternativas consideradas

- Extender la prueba dentro del notebook: ~80 s más.
- No decir nada: deja un posible sesgo sin explicar.

## Consecuencias

'Sin sesgo' se apoya en la prueba extendida y en el χ² de la curva. La columna con z alto sigue en la tabla y queda explicada.

## Referencias

Issue #6.
