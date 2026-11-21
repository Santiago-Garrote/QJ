# ADR-0001: Firma de `qubit_hamiltonian`: devolver `(op, e_nuc)`

- **Estado:** Aceptado
- **Fecha:** 2026-11-21
- **Issue:** #2
- **Autor:** @Feyannibelli

## Contexto

El issue #2 pide que `qubit_hamiltonian(d)` devuelva `(op, e_nuc, hf_bitstring)`. La celda 0.1 del notebook (contrato compartido, commit `37e578c`) la define como:

```python
def qubit_hamiltonian(d: float) -> tuple[SparsePauliOp, float]:
```

y ya fija el estado de Hartree-Fock como constante: `HF_BITSTRING = "00110011"` (q0, q1 = α 0,1 y q4, q5 = β 0,1 ocupados).

Las dos fuentes no coinciden, y el resto de las secciones (#4, #5, #6, #8, #14) programan contra la celda 0.1.

## Decisión

`qubit_hamiltonian(d)` devuelve `(op, e_nuc)`, como dice el contrato:

- `op`: Hamiltoniano **electrónico** como `SparsePauliOp` de 8 qubits (Jordan-Wigner, convención de la celda 0.1).
- `e_nuc`: repulsión nuclear en Ha. Energía total = `⟨op⟩ + e_nuc`.

El estado HF se toma de la constante `HF_BITSTRING`.

## Alternativas consideradas

- **`(op, e_nuc)`, como el contrato (elegida).**
  - Pros: no rompe a nadie, una sola fuente de verdad para el estado HF, no hay que tocar la celda 0.1.
  - Contras: ninguno relevante mientras el estado HF no dependa de `d`.
- **`(op, e_nuc, hf_bitstring)`, como el issue.**
  - Pros: la función es autosuficiente (quien la llama no necesita mirar la celda 0.1).
  - Contras: cambia el contrato; todo `op, e_nuc = qubit_hamiltonian(d)` falla con `ValueError: too many values to unpack`; el valor devuelto es siempre el mismo (con RHF y orbitales ordenados por energía, los ocupados son siempre los 2 más bajos de cada espín); quedan dos fuentes de verdad que pueden desincronizarse.

## Impacto en complejidad, velocidad y equipo

| | `(op, e_nuc)` | `(op, e_nuc, hf_bitstring)` |
|---|---|---|
| Velocidad | Igual: el costo está en PySCF y Jordan-Wigner, no en lo que se devuelve | Igual |
| Complejidad | Una sola fuente de verdad para el estado HF | Dos fuentes (constante y retorno) que pueden desincronizarse sin que nada falle |
| Celda 0.1 | No se toca | Cambia la firma |
| Resto del equipo | Sin cambios | #4, #5, #6, #8 y #14 tienen que adaptar el desempaquetado |
| Riesgo al integrar (#9) | Bajo | Conflictos y errores el día de la entrega |

## Consecuencias

- Ningún otro issue tiene que cambiar código.
- La validación de #2 comprueba la constante: `⟨HF_BITSTRING|op|HF_BITSTRING⟩ + e_nuc = E_HF` de PySCF. Resultado: error máximo ≈ 2e-14 Ha en las 19 distancias, así que `"00110011"` es correcto.
- El issue #2 ya se actualizó con esta firma (`(op, e_nuc)`, con la aclaración de que antes decía `(op, e_nuc, hf_bitstring)`).
- Revisar esta decisión solo si el estado de referencia pasara a depender de `d` (p. ej. UHF con ruptura de simetría o un espacio activo que cambie con la distancia). En ese caso, crear un ADR nuevo y avisar en el issue antes de tocar la celda 0.1.
