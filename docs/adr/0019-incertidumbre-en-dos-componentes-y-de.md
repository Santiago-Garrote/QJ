# 0019. Incertidumbre en dos componentes y D_e con propagación conjunta

## Estado

Aceptada

## Contexto

El bootstrap solo captura el ruido de medición. FCI y CCSD no tienen ruido y el sesgo del modelo de ajuste no lo ve el bootstrap. E(R_e) y E(3,0) salen de las mismas energías re-muestreadas.

## Decisión

Bootstrap paramétrico N(E_i, σ_i²) de 2000 muestras, más el semi-rango del barrido grado x ventana, combinados en cuadratura (misma lógica para los tres métodos). D_e = E(3,0) medido − E(R_e) del ajuste, re-muestreando ambos en cada réplica. Se reporta en mHa y eV, con la salvedad de que a 3,0 Å la cadena no está disociada: FCI queda 0,96 mHa por debajo de 4 H aislados.

## Alternativas consideradas

- Solo bootstrap: subestima el error.
- Solo sensibilidad.
- Cuadratura asumiendo independencia en D_e.

## Consecuencias

Con el stand-in la incertidumbre total queda dominada por la sensibilidad.

## Referencias

Issue #7.
