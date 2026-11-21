# 0015. PySCF a un hilo para reproducibilidad bit a bit

## Estado

Aceptada

## Contexto

Dos corridas idénticas daban shots totales y energías distintas (425.254 / 426.310 / 423.802). Los hashes mostraron que coeficientes de H, referencias y θ* ya diferían, y E_sv en ~1e-9 Ha. La causa es el orden de suma de los hilos OpenMP de PySCF; el ajuste de θ lo amplifica y mueve el reparto y el piloto.

## Decisión

`pyscf.lib.num_threads(1)` al inicio de la celda de stand-ins. Los redondeos de H (1e-12) y de θ* (1e-6) quedan como segunda defensa.

## Alternativas consideradas

- Redondear más grueso: solo baja la probabilidad.
- Hashear entradas: no arregla el origen.
- Limitar hilos solo en Aer: no era la causa.

## Consecuencias

Bits idénticos entre corridas, verificado. PySCF no es más lento en H4/STO-3G y la parte fija bajó de ~24 s a ~18 s. Las funciones reales de #1, #2 y #5 deberían mantener esto.

## Referencias

Issue #6.
