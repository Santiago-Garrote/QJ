# QuantumJam 2026: Romper una molécula, un qubit a la vez

Enunciado del desafío de la QuantumJam (Qiskit Fall Fest 2026, Computer Society ITBA, Buenos Aires, 21/11/2026), separado en archivos Markdown.

## TL;DR

- **Sistema:** cadena lineal de $\mathrm{H_4}$, espaciado uniforme $d$, base STO-3G.
- **Algoritmo:** VQE (SQD **no** vale para el desafío central).
- **Medición:** las energías tienen que salir de `EstimatorV2` / `SamplerV2` de `qiskit_aer`, no del statevector.
- **Curva:** ≥ 10 puntos en $d \in [0{,}6;\ 3{,}0]\ \text{Å}$, cada uno con $\pm\sigma$, comparada con CCSD y FCI.
- **Derivados:** $R_e$ y $D_e = E(3{,}0\ \text{Å}) - E(R_e)$.
- **Objetivo:** para $d \geq 1{,}8\ \text{Å}$, $|E_\text{VQE} - E_\text{FCI}| + \sigma < |E_\text{CCSD} - E_\text{FCI}|$.
- **Meta máxima:** $|E_\text{VQE} - E_\text{FCI}| < 1{,}6\ \text{mHa}$ en la zona estirada.
- **Entrega:** notebook de Colab en una carpeta de Drive compartida con el jurado. Tiene que correr de punta a punta e incluir una tabla (energía, σ, shots y `cz` por punto) más una explicación de las decisiones.

## Índice

| # | Archivo | Contenido |
|---|---------|-----------|
| 01 | [Motivación](challenge/01-motivacion.md) | Contexto físico: hamiltoniano, Jordan-Wigner, VQE, ruido |
| 02 | [El desafío](challenge/02-desafio.md) | Objetivos concretos y criterios numéricos |
| 03 | [Reglas](challenge/03-reglas.md) | Qué está permitido y qué no |
| 04 | [Entrega](challenge/04-entrega.md) | Formato del notebook y contenido obligatorio |
| 05 | [Cosas extra](challenge/05-extras.md) | Extras opcionales: ruido, mitigación, menos qubits, SQD… |
| 06 | [Evaluación](challenge/06-evaluacion.md) | Qué mira el jurado |
| 07 | [Recursos](challenge/07-recursos.md) | Papers, librerías y tutoriales |

¿Términos nuevos? Ver el [glosario](glosario.md), con todo explicado simple.

## Análisis

[`analysis/`](analysis/README.md): números de referencia reales (RHF, CCSD, CCSD(T), FCI), costo de medición, hallazgos, revisión de literatura y estrategia propuesta. Versión interactiva en [`analysis/plan.html`](analysis/plan.html); estado del arte y brechas del plan en [`analysis/state-of-the-art.md`](analysis/state-of-the-art.md).

## Decisiones (ADR)

[`adr/`](adr/README.md): registro de decisiones técnicas del equipo (qué se decidió, por qué y qué se descartó), con plantilla para sumar nuevas. Insumo de la sección 7 del notebook (#9).

## Fuente

`source/challenge.html` (y `source/challenge_files/`) es el snapshot original de la página. Los archivos de `challenge/` se generaron a partir de ese snapshot, con las fórmulas en LaTeX (`$…$`).
