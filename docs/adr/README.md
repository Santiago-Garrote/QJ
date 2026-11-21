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
