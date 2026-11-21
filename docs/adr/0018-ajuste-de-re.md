# 0018. Ajuste de R_e

## Estado

Aceptada

## Contexto

La grilla de 0,1 Å da un mínimo entre 0,8 y 1,0 Å y la curva es asimétrica.

## Decisión

Polinomio de grado 4 en 0,6-1,4 Å, ponderado por 1/σ para VQE, con el mínimo buscado en una malla fina dentro de la ventana. Con FCI da R_e = 0,885 Å, estable entre grado 4 y 5. El barrido de sensibilidad conserva grados 2-5 para mostrar el sesgo.

## Alternativas consideradas

- Parábola: sesgada con ventana ancha.
- Spline cúbico: interpola el ruido.
- Ajustar hasta 3,0 Å: los puntos casi planos distorsionan.

## Consecuencias

R_e depende del modelo de ajuste y eso se cuantifica en el ADR siguiente.

## Referencias

Issue #7.
