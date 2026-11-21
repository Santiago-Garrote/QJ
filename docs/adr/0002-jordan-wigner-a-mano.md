# ADR-0002: Jordan-Wigner implementado a mano y genérico

- **Estado:** Aceptado
- **Fecha:** 2026-11-21
- **Issue:** #2
- **Autor:** @Feyannibelli

## Contexto

Hay que pasar el Hamiltoniano electrónico de $\mathrm{H_4}$ (operadores fermiónicos sobre 8 espín-orbitales) a un `SparsePauliOp` de 8 qubits con la convención de la celda 0.1. Restricciones:

- `requirements.txt` solo tiene qiskit 2.5.2, qiskit-aer 0.17.2, pyscf, numpy, scipy, pandas y matplotlib. Sumar una dependencia obliga a fijarla en `requirements.txt`, en el `%pip` del notebook y que coincida con nixpkgs (`nix flake check`).
- El notebook tiene que correr en Colab de punta a punta.
- #8 necesita los operadores $N$, $S_z$ y $S^2$ con el mismo mapeo, y #14 necesita partir del mismo operador para el tapering.

## Decisión

Implementar Jordan-Wigner a mano en el notebook:

- `_jw_ladder(n)`: los operadores $a_j = Z_0 \cdots Z_{j-1}\,(X_j + iY_j)/2$ y sus adjuntos, como `SparsePauliOp`, cacheados.
- `jordan_wigner(h1_so, h2_so)`: genérica. Recibe matrices en espín-orbitales (un cuerpo y dos cuerpos en notación química $(PQ|RS)$) y arma $\sum h_{PQ} a_P^\dagger a_Q + \tfrac12 \sum (PQ|RS)\, a_P^\dagger a_R^\dagger a_S a_Q$. Saltea coeficientes < 1e-12 y los productos que dan cero ($P = R$ o $Q = S$), simplifica y verifica que los coeficientes sean reales.
- `spatial_to_spin_orbitals(h1, eri)`: pasa de 4 orbitales espaciales a 8 espín-orbitales conservando el espín, con el índice de qubit de la celda 0.1 (`alpha_qubit`, `beta_qubit`).
- Los productos se arman con `@` (`A @ B` = $A \cdot B$).

## Alternativas consideradas

- **A mano (elegida).** Unas 50 líneas, sin dependencias nuevas, controlamos el orden de qubits exactamente. Contra: hay que validarlo nosotros (se hace con las pruebas de HF y FCI).
- **qiskit-nature.** Hace todo el camino desde PySCF. Contras: está en mantenimiento y no es compatible de forma confiable con qiskit 2.x; su orden de qubits por defecto es el mismo bloque α/β pero habría que verificarlo igual; suma una dependencia que hay que fijar en nix.
- **OpenFermion + openfermionpyscf.** Muy probado. Contras: dependencias pesadas, su orden por defecto intercala α y β (habría que reordenar para cumplir la celda 0.1) y hay que convertir a `SparsePauliOp`.

## Consecuencias

- Cero dependencias nuevas: `requirements.txt`, el `%pip` y `nix flake check` no cambian.
- Validación cruzada con la implementación independiente de `scripts/h4_reference.py` (PR #18, misma convención de qubits): con los mismos orbitales, los dos operadores son idénticos término a término (diferencia de coeficientes 0) en las 19 distancias, y FCI coincide con `docs/analysis/data/h4_reference.json` (< 2e-14 Ha).
- 185 términos de Pauli por distancia (184 más la identidad), el mismo conjunto en toda la grilla. Dato para #6 (cantidad de grupos a medir).
- **Ojo con los números de `docs/analysis/state-of-the-art.md`:** se calcularon con α y β **intercalados**, no con la convención del notebook. Los conteos invariantes (184 términos, λ, energías) valen igual, pero no lo que depende del orden de qubits: allí dice 69 grupos QWC (con nuestra convención son 38–48, ver `docs/analysis/README.md`), y las simetrías Z₂ que lista (`ZIIZZIIZ`, `ZIZIZIZI`, `ZZIIZZII`) **no** valen para este operador. Con `Z2Symmetries.find_z2_symmetries` sobre `qubit_hamiltonian(d)` salen `ZIZIIZIZ`, `ZIZIZIZI` y `ZZZZIIII` (también 3, igual a 1,8 y 3,0 Å, así que se baja igual a 5 qubits). Dato para #14.
- #8 y #14 reutilizan `jordan_wigner` y `spatial_to_spin_orbitals` para sus operadores.
- **Trampa encontrada:** en Qiskit `A.compose(B)` es $B \cdot A$. Usarlo daba $a_Q a_P^\dagger$, el Hamiltoniano con partículas y huecos intercambiados, que a medio llenado tiene el mismo espectro en el sector $N=4$: la prueba contra FCI pasaba igual y solo la prueba de HF lo detectó. Por eso se mantienen **las dos** pruebas, y cualquiera que arme operadores fermiónicos tiene que usar `@`.
