# 0023. Matriz densidad y un binding por grupo con ruido

## Estado

Aceptada

## Contexto

Con ruido cada binding es una evolución completa de ~700 compuertas. Con 4 bindings por grupo y 16 puntos, la celda de #11 tardó 835 s. La primera versión de #12 tardó ~190 s a escala 0,05. Sin ruido es barato.

## Decisión

`method='density_matrix'`, `min_group_shots=5000` (casi un binding por grupo) y `UNITS_PER_GROUP=1` en #12. En #11 solo 3 versiones del ansatz y un σ objetivo de 3 mHa, relajado por 1/sqrt(escala).

## Alternativas consideradas

- Trayectorias de statevector: más lentas por shot.
- Medir el estado ruidoso una vez: no reutilizaría `measure_energy`.
- Más versiones cortas.

## Consecuencias

#11 tarda ~104 s y #12 ~75 s a escala 0,05. A escala 1,0 el costo lo domina el número de bindings, así que debería ser parecido (no medido). σ sigue saliendo de la varianza por grupo; el reparto es algo más grueso.

## Referencias

Issues #11, #12.
