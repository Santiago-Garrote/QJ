# 0026. cz y profundidad medidos sin rotaciones, mejor de 3 semillas del transpilador

## Estado

Aceptada

## Contexto

El backend entrega cz y profundidad; la plantilla de medición agrega rotaciones U.

## Decisión

Se reportan cz y profundidad del circuito ligado transpilado a FakeFez (opt 3, mejor de las semillas 0-2 por cz); la plantilla de medición reutiliza la semilla elegida.

## Alternativas consideradas

- Reportar desde la plantilla de medición.
- Una sola semilla.

## Consecuencias

Con el stand-in UCCSD salen 711 cz, frente a 500-650 del doc de análisis (que usa ADAPT). El ruteo de la plantilla puede diferir marginalmente. Con qiskit 2.4.1 local los cz difieren algo de las versiones fijadas.

## Referencias

Issue #12; docs/analysis/README.md.
