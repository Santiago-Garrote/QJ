# Architecture Decision Records (ADR)

Registro de las decisiones técnicas del equipo: qué se decidió, por qué y qué alternativas se descartaron. Sirve para la sección **7. Decisiones, qué no funcionó y limitaciones** del notebook (#9) y para que nadie tenga que adivinar por qué algo está como está.

## Cómo agregar un ADR

1. Copiar la plantilla de abajo a `NNNN-titulo-corto.md` (número siguiente, en kebab-case).
2. Completarlo y sumarlo al índice.
3. Si la decisión cambia el contrato de la celda 0.1, avisar en el issue correspondiente.
4. Un ADR aceptado no se edita: si la decisión cambia, se crea uno nuevo que lo reemplaza y se marca el viejo como `Reemplazado por ADR-NNNN`.

## Índice

| # | Título | Estado | Issue |
|---|--------|--------|-------|
| [0001](0001-firma-qubit-hamiltonian.md) | Firma de `qubit_hamiltonian`: devolver `(op, e_nuc)` | Aceptado | #2 |
| [0002](0002-jordan-wigner-a-mano.md) | Jordan-Wigner implementado a mano y genérico | Aceptado | #2 |
| [0003](0003-signo-orbitales-y-cache.md) | Signo fijo de los orbitales y caché de RHF y Hamiltoniano | Aceptado | #2 |
| [0004](0004-registrar-decisiones-con-adrs.md) | Registrar decisiones con ADRs | Aceptado |  |
| [0005](0005-energias-con-samplerv2-no-estimatorv2.md) | Energías reportadas con SamplerV2, no con EstimatorV2 de qiskit-aer | Aceptado | #6 |
| [0006](0006-convencion-de-qubits-y-grilla.md) | Convención de qubits y grilla del contrato del notebook | Aceptado | #2, #6 |
| [0007](0007-standins-que-se-apagan-solos.md) | Stand-ins que se apagan solos | Aceptado | #6 |
| [0008](0008-una-rama-y-un-pr.md) | Una rama y un PR, commits con Refs y no Closes | Aceptado | #6, #7, #11, #12, #19 |
| [0009](0009-medicion-qwc-optima-rotacion-extra.md) | Medición base QWC con reparto óptimo; rotación de base como extra (#19) | Aceptado | #6, #19 |
| [0010](0010-modelo-de-ruido-standin.md) | Modelo de ruido stand-in hasta tener ruido.py | Aceptado | #11 |
| [0011](0011-fakefez-via-qiskit-ibm-runtime.md) | FakeFez vía qiskit-ibm-runtime | Aceptado | #12 |
| [0012](0012-hardware-real-en-backlog.md) | Hardware real de IBM en backlog (#22) | Aceptado | #22 |
| [0013](0013-pruebas-rapidas-con-qj-shots-scale.md) | Pruebas rápidas con QJ_SHOTS_SCALE | Aceptado | #6 |
| [0014](0014-presupuesto-de-shots-en-dos-etapas.md) | Presupuesto de shots en dos etapas con objetivo de σ por punto | Aceptado | #6 |
| [0015](0015-pyscf-un-hilo-para-reproducibilidad.md) | PySCF a un hilo para reproducibilidad bit a bit | Aceptado | #6 |
| [0016](0016-velocidad-aer-bindings-y-bloques.md) | Velocidad de Aer: menos costo por binding, repeticiones en un PUB y bloques de 600 | Aceptado | #6 |
| [0017](0017-sesgo-probar-aparte-y-documentar.md) | Sesgo: probar aparte y documentar, no ocultar | Aceptado | #6 |
| [0018](0018-ajuste-de-re.md) | Ajuste de R_e | Aceptado | #7 |
| [0019](0019-incertidumbre-en-dos-componentes-y-de.md) | Incertidumbre en dos componentes y D_e con propagación conjunta | Aceptado | #7 |
| [0020](0020-criterio-gana-a-ccsd.md) | Definición de gana_a_ccsd y err_vqe | Aceptado | #7 |
| [0021](0021-reutilizar-measure-energy-con-context-managers.md) | Reutilizar measure_energy de #6 con ruido mediante context managers | Aceptado | #11 |
| [0022](0022-layout-de-transpile-line-y-observable-permutado.md) | Layout de transpile_line y observable permutado | Aceptado | #11, #12 |
| [0023](0023-density-matrix-y-un-binding-por-grupo.md) | Matriz densidad y un binding por grupo con ruido | Aceptado | #11, #12 |
| [0024](0024-versiones-cortas-del-ansatz.md) | Versiones cortas del ansatz: operadores con mayor |θ*| reajustados | Aceptado | #11 |
| [0025](0025-error-de-la-rotacion-de-base.md) | Error de la rotación de base de medición | Aceptado | #19 |
| [0026](0026-cz-y-profundidad-mejor-de-tres-semillas.md) | cz y profundidad medidos sin rotaciones, mejor de 3 semillas del transpilador | Aceptado | #12 |
| [0027](0027-esquemas-de-medicion-avanzados.md) | Comparación de esquemas de medición (#19): validación sin convención y DF | Aceptado | #19 |
| [0028](0028-confiabilidad-sin-fci.md) | Confiabilidad sin FCI: proyección al singlete, Temple con gap por VQD y CCSD contra la cota inferior | Aceptado | #8 |
| [0029](0029-hardware-real-emular-primero.md) | Hardware real de IBM: emular primero y elegir un ansatz corto | Aceptado | #22, #13 |

## Plantilla

```markdown
# ADR-NNNN: Título

- **Estado:** Propuesto | Aceptado | Reemplazado por ADR-NNNN
- **Fecha:** AAAA-MM-DD
- **Issue:** #N
- **Autor:** @usuario

## Contexto
Qué problema hay y qué restricciones aplican.

## Decisión
Qué se decidió, en una o dos frases.

## Alternativas consideradas
- **Opción A:** pros / contras.
- **Opción B:** pros / contras.

## Consecuencias
Qué cambia para el resto del notebook y del equipo, y qué riesgos quedan.
```
