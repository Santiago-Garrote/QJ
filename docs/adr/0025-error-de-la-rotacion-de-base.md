# 0025. Error de la rotación de base de medición

## Estado

Aceptada

## Contexto

`measure_energy` agrega una puerta `u` por qubit para rotar la base, que no está en la base cz/sx/x/rz del modelo; sin error asignado sería ruido gratis.

## Decisión

El `u` recibe depolarizing 1-(1-5e-5)^5 (se descompone en 5 compuertas de 1 qubit). No se añade error de lectura porque el enunciado no lo menciona.

## Alternativas consideradas

- Dejar `u` sin ruido: subestima apenas.
- Transpilar la rotación a sx/rz: cambia el código de #6.

## Consecuencias

El aporte es ≈ 2,5e-4 por qubit, despreciable frente a los cz.

## Referencias

Issue #11.
