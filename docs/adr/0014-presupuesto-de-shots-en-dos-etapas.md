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

## Actualización: objetivo de precisión química

En $d \ge 1{,}8$ Å el σ objetivo pasa a ser $\min(0{,}8\ 	ext{mHa},\ 	frac15|E_	ext{CCSD}-E_	ext{FCI}|,\ 3\ 	ext{mHa})$ y el tope por punto sube de 2 a 6 millones de shots. Motivo: el ansatz de #4 llega a FCI (≤ 0,003 mHa), así que el único error es estadístico; con σ ≤ 0,8 mHa, $|E - E_	ext{FCI}| < 1{,}6$ mHa (meta máxima del enunciado) con ~95 % de probabilidad. Costo estimado: ~3,5 × 10⁶ shots por punto estirado, ~2,8 × 10⁷ en la curva (antes ~6 × 10⁶). El tiempo de Aer lo domina el número de *bindings*, que no cambia, así que la corrida crece poco. Se corre a escala completa en Colab.
