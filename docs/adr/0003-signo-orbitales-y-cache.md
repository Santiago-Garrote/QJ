# ADR-0003: Signo fijo de los orbitales y caché de RHF y Hamiltoniano

- **Estado:** Aceptado
- **Fecha:** 2026-11-21
- **Issue:** #2
- **Autor:** @Feyannibelli

## Contexto

- Los orbitales moleculares de PySCF están definidos a menos de un signo: entre una distancia y la siguiente, un orbital puede salir multiplicado por −1. El espectro del Hamiltoniano no cambia, pero los coeficientes de los términos de Pauli sí.
- #5 optimiza el VQE con *warm start*: usa los parámetros óptimos de una distancia como punto de partida de la siguiente. Si un orbital cambia de signo, los parámetros óptimos también cambian de signo de golpe y el warm start arranca lejos del mínimo.
- `qubit_hamiltonian(d)` se usa en las secciones 3 a 6 y en los extras, muchas veces con la misma `d`.
- RHF es **inestable hacia UHF desde ~1,1 Å** (`docs/analysis/state-of-the-art.md`, sección 1; verificado con `mf.stability(external=True)` sobre `h4_scf` a 1,8 y 3,0 Å: estable internamente, inestable externamente).

## Decisión

1. **Fijar el signo:** después de RHF, cada orbital (columna de `mo_coeff`) se multiplica por el signo de su primer coeficiente con |c| > 1e-4, así ese coeficiente queda positivo. En $\mathrm{H_4}$ lineal STO-3G es el coeficiente del 1s del primer átomo, que vale ≳ 0,2 en los 4 orbitales. Si algún orbital no tiene ningún coeficiente por encima del umbral, se lanza un error (antes `np.sign` podía dar 0 y anular el orbital sin aviso). El umbral es 1e-4 y no 1e-8 para que un casi-nodo no se tome como referencia (review de #21).
2. **Orbitales RHF en toda la grilla**, también donde RHF es inestable hacia UHF. Los orbitales solo definen la base: el Hamiltoniano de 8 qubits representa exactamente el mismo problema (FCI no cambia) y el estado de referencia sigue siendo un singlete. Con orbitales UHF, α y β tendrían orbitales distintos, el determinante de referencia estaría contaminado de espín y ⟨S²⟩ = 0 dejaría de servir como diagnóstico en #8. Coincide con la recomendación de `state-of-the-art.md`.
3. **Caché con copias:** RHF (`conv_tol = 1e-11`, falla si no converge) y el Hamiltoniano se cachean con `functools.lru_cache` en funciones **privadas** (`_h4_scf_cached`, `_qubit_hamiltonian_cached`). Las públicas devuelven copias:
   - `qubit_hamiltonian(d)` devuelve `op.copy()`;
   - `h4_scf(d)` devuelve una copia del `mf` con sus propios `mo_coeff`, `mo_energy` y `mo_occ`.

   Así, modificar lo devuelto (por ejemplo `op.coeffs[0] = 0`, o `mf.kernel()` / `mf.stability()` en #1) no toca el caché ni desincroniza los orbitales del Hamiltoniano ya cacheado. Antes la protección era solo un aviso en el markdown (review de #21).
4. **Clave del caché normalizada:** `d` se redondea a 6 decimales antes de buscarla, así `qubit_hamiltonian(0.1 * 7)` (= 0,7000000000000001) reutiliza la entrada de 0,7 en vez de recalcular RHF (review de #21).

## Alternativas consideradas

- **Signo del coeficiente de mayor módulo.** Descartado: por la simetría de reflexión de la cadena, los átomos de los extremos tienen coeficientes de igual módulo, y el empate se rompe por ruido numérico, así que el criterio puede elegir átomos distintos en distancias vecinas.
- **Alinear cada distancia con la anterior (maximizar el solapamiento).** Más general, pero hace que el resultado de `d` dependa del orden en que se calculan las distancias. Innecesario para esta molécula.
- **No fijar nada.** Funciona para la validación (FCI es invariante), pero deja el warm start de #5 expuesto.
- **Sin caché.** Cada llamada repite RHF, integrales y Jordan-Wigner (~0,5 s por distancia); con muchas llamadas por sección suma minutos en Colab.

## Consecuencias

- Evidencia de que el problema es real: con el RHF de PySCF sin fijar signos (como en `scripts/h4_reference.py` del PR #18), entre 76 y 84 términos de Pauli cambian de signo de golpe entre distancias vecinas en 0,7, 1,3, 1,5 y 2,2 Å.
- Con la tolerancia por defecto de RHF (1e-9) los coeficientes difieren hasta 1,6e-6 de los convergidos; con `conv_tol = 1e-11` coinciden hasta ~1e-13.
- Verificado en la grilla: con el signo fijo, ningún término de Pauli cambia de signo de golpe entre distancias vecinas. Los únicos cambios (8 términos entre 0,6 y 0,7 Å) son coeficientes de ~1e-3 que cruzan cero de forma suave (comprobado con pasos de 0,02 Å).
- Toda la grilla (19 distancias, con FCI para validar) tarda ~14 s.
- Cada llamada a `qubit_hamiltonian` / `h4_scf` devuelve un objeto nuevo: comparar con `==`/`allclose`, no con `is`. El costo de copiar 185 términos es despreciable.
- Si #1 calcula HF/CCSD/FCI con su propio RHF, conviene que use `h4_scf(d)` para que todos compartan los mismos orbitales (las energías no cambian, pero sí cualquier cosa que dependa de los orbitales, como amplitudes de CCSD usadas para inicializar el ansatz).
- Limitación: el criterio depende de que el primer coeficiente no sea cero. Si se cambia la base o la geometría (extra #17), revisar que siga valiendo.
