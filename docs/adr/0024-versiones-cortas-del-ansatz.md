# 0024. Versiones cortas del ansatz: operadores con mayor |θ*| reajustados

## Estado

Aceptada

## Contexto

Las issues #11 y #12 piden versiones cortas del ansatz para mostrar el compromiso expresividad/ruido. La rama del ansatz real de #11 nunca se había ejecutado: truncaba los primeros k parámetros sin reajustar y quedaba peor que HF (error > 900 mHa). Además `restringir()` fallaba con ValueError porque el ansatz real tiene CX fijos entre rotaciones.

## Decisión

Se eligen los k operadores (k = 2 y 12 en #11; 1 o 2 en #12) con mayor |θ*| máximo sobre la curva y se reajustan sus ángulos: en el stand-in con `_standin_fit_uccsd`, con el ansatz real con `sector_ansatz.energy_grad` y `H_SECTOR` de la sección 4 (BFGS por statevector, búsqueda de parámetros permitida). Siempre se mide con shots. En #12 se agrega la fila HF (0 cz) para aislar el error de lectura. Se eliminó el chequeo de puertas sin parámetros en `restringir()`: los CX de una excitación descartada se cancelan y el transpilador los elimina.

## Alternativas consideradas

- Truncar los primeros k sin reajuste: peor que HF.
- Elegir al azar.
- Selección ADAPT por gradiente.

## Consecuencias

Con el stand-in de 26 operadores las versiones cortas cuestan 145 y 635 cz, y con 2 operadores el sesgo es grande. En #12 las cortas quedan 275-425 mHa sobre FCI y ninguna supera a HF bajo FakeFez, así que el compromiso es poco informativo.

## Referencias

Issues #11, #12; commit c1a67dc.
