# 0014. Presupuesto de shots en dos etapas con objetivo de σ por punto

## Estado

Aceptada

## Contexto

El margen más chico frente a CCSD es a 1,8 Å (9,1 mHa), donde hace falta una σ menor.

## Decisión

Un piloto fijo (145.000 shots en total a escala 0,05) estima Var_g por grupo. Luego se reparte el resto con N_g ∝ sqrt(Var_g), óptimo e incluye covarianzas dentro del grupo, hasta alcanzar un `sigma_obj` por punto. A 1,8 Å se apunta a ~8 mHa a escala 0,05.

## Alternativas consideradas

- Mismo número de shots por punto: más simple pero desperdicia shots y no apunta a la barra de 1,8 Å.

## Consecuencias

A escala completa es más caro (~3,4e5 shots por σ = 1 mHa a 1,8 Å con rotación de base). No se corrió a escala completa por la regla de velocidad.

## Referencias

Issue #6.
