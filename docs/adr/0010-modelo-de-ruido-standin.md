# 0010. Modelo de ruido stand-in hasta tener ruido.py

## Estado

Aceptada

## Contexto

`ruido.py` depende de los organizadores (#3) y no está en main.

## Decisión

Un `NoiseModel` de Aer con la especificación del enunciado, como stand-in que se apaga solo cuando exista `ruido.py`. La corrida integrada imprime '[stand-in] ruido.py (#3) no está'.

## Alternativas consideradas

- Esperar a #3.

## Consecuencias

Los resultados con ruido se rehacen cuando llegue el modelo real.

## Referencias

Issues #3, #11.
