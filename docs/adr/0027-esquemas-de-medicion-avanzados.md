# 0027. Comparación de esquemas de medición (#19): validación sin convención y DF

## Estado

Aceptada

## Contexto

Las particiones y el reparto necesitan Var_g, y las convenciones de signo de Pauli, orden de bits y dirección de rotación son fáciles de errar. La factorización doble (DF) necesita h y eri compatibles con el Hamiltoniano de #2.

## Decisión

- Varianzas exactas (statevector) para diseñar particiones, reparto N_g ∝ sqrt(Var_g) y la columna de shots para 1 mHa; las energías salen de shots de SamplerV2 con σ de varianzas muestrales. Los conteos de shots no dependen de la escala.
- Un fragmento se acepta solo si V O V† es diagonal, y esa diagonal es la tabla por shot; además los fragmentos suman H y sus esperanzas suman E_sv.
- Integrales DF de PySCF con búsqueda de signos de MO (8 patrones) que reproduzca el Hamiltoniano de #2; si ninguno sirve, imprime AVISO y se omite DF en esa distancia (antes lanzaba RuntimeError).
- Red de Givens de rotaciones 2-qubit (`UnitaryGate`) entre modos JW adyacentes más signos Z: 2 cz cada una con `transpile_line`, como mucho 24 cz, conservando N y Sz (permite post-selección).
- Grupos totalmente conmutantes: generadores independientes en GF(2), Clifford con `StabilizerState.from_stabilizer_list`, medición tras C†; hasta 81 cz.
- Una llamada de SamplerV2 por fragmento con semilla propia y sin transpilar contra Aer: PUBs con distintos shots reutilizaban la semilla y correlacionaban fragmentos, y transpilar dominaba el tiempo.
- σ objetivo de 2 mHa a escala completa (no 1 mHa) para el chequeo de consistencia, por velocidad; #6 ya validó σ = K/sqrt(N).
- El markdown no fija valores de z (cambian con escala y entorno) y remite a la tabla impresa.

## Alternativas consideradas

- Estimar varianzas con shots piloto.
- Confiar en signos analíticos.
- Fallo duro ante desajuste de convención.
- Síntesis Clifford propia de pocos cz (no cambiaría la conclusión frente a DF).
- Un solo job por lotes.
- Hardcodear los z.

## Consecuencias

El notebook no se cae en 8.3 por un desajuste de convención, las convenciones se verifican numéricamente y los fragmentos son independientes.

## Referencias

Issue #19; commit 5b8e50e.
