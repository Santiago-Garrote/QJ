# ADR-0028: Argumento de confiabilidad sin FCI: proyección al singlete, cota de Temple con gap por VQD y CCSD contra la cota inferior

- **Estado:** Aceptado
- **Fecha:** 2026-11-21
- **Issue:** #8
- **Autor:** @Feyannibelli

## Contexto

- #8 pide argumentar que el VQE es confiable en la zona estirada ($d \geq 1{,}8$ Å) **sin mirar FCI**, y recién después compararlo con CCSD y FCI.
- En $\mathrm{H_4}$ estirado los estados se casi degeneran:
  - el triplete está a 29,8 mHa a 1,8 Å y a solo 0,46 mHa a 3,0 Å;
  - el siguiente **singlete** está a 76 mHa a 1,8 Å y a 1,2 mHa a 3,0 Å.
- El ansatz (#4) conserva $N$ y $S_z$ pero no $S^2$.
- La cota de Temple, $E_0 \geq \langle H\rangle - \mathrm{Var}/(E_1 - \langle H\rangle)$, necesita la energía $E_1$ del siguiente estado. Calcularla diagonalizando $H$ es hacer FCI.
- Varianza y $\langle S^2\rangle$ se pueden calcular con statevector, porque son diagnósticos del estado y no energías reportadas. La energía reportada la mide #6 con `SamplerV2`.

## Decisión

1. **Operadores con el mismo mapeo que el Hamiltoniano:** $N$, $S_z$ y $S^2 = S^+S^- + S_z^2 - S_z$, construidos con `jordan_wigner` (ADR-0002). $S^+$ se arma con `hermitian=False`.
2. **Temple dentro de los singletes.** El estado se proyecta al singlete con $P_0 = (S^2-2)(S^2-6)/12$, que es exacto en $N = 4$, donde solo hay $S = 0, 1, 2$. Temple se aplica a esa parte con $E_1$ = siguiente singlete. El peso del triplete descartado se reporta.
3. **$E_1$ por VQD** con el mismo ansatz, minimizando $\langle H\rangle + 0{,}05\langle S^2\rangle + \beta|\langle\psi_0|\psi\rangle|^2$:
   - β = 1 Ha;
   - 10 arranques al azar más el *warm start* desde la distancia anterior;
   - el gradiente adjunto de #5 sirve tal cual, porque la penalidad es el valor esperado de $\beta|\psi_0\rangle\langle\psi_0|$.

   Se reporta también la ventana con el gap a la mitad, como margen por si el VQD sobreestima $E_1$.
4. **CCSD contra la cota inferior.** Si $E_\text{CCSD} < \text{Temple}$, entonces $|E_\text{CCSD} - E_0| \geq \text{Temple} - E_\text{CCSD}$. La cota superior del error del VQE es la ventana $E_\text{sv} - \text{Temple}$, más el desvío medido $|E_\text{medida} - E_\text{sv}|$, más σ. Si esa cota es menor que el error mínimo de CCSD, el VQE le gana a CCSD sin usar FCI.
5. **Solo se mide con `SamplerV2` lo barato:** la fracción de shots en base Z con $N_\alpha = N_\beta = 2$. El resto (varianza, $\langle S^2\rangle$, Temple) es diagnóstico de statevector, y así se declara en el notebook.

## Alternativas consideradas

- **Temple con el siguiente autoestado de cualquier espín.** Descartada: es el triplete casi degenerado, que da una cota inútil a 3,0 Å, y la cota tampoco es válida si el estado tiene algo de triplete.
- **$E_1$ diagonalizando $H$ en el sector.** Es exacto, pero equivale a FCI y rompe el "sin FCI". Se usa solo en 6.3 para verificar el VQD (coincide a ≤ 0,013 mHa).
- **Solo Weinstein ($\sqrt{\mathrm{Var}}$).** No necesita $E_1$, pero es floja: 0,76 mHa a 2,4 Å contra 0,05 mHa de Temple. Queda como señal de mínimo local.
- **Medir $S^2$ y $H^2$ con shots.** Sería más "experimental", pero $S^2$ tiene 77 términos y $H^2$ muchos más. Duplica el trabajo de #6 sin cambiar la conclusión en un simulador sin ruido.

## Consecuencias

- Resultados con la energía de statevector:
  - ventana de Temple ≤ 0,071 mHa (≤ 0,14 con el gap a la mitad);
  - $E_\text{FCI}$ cae dentro de $[\text{Temple}, E_\text{sv}]$ en los 7 puntos;
  - CCSD queda por debajo de la cota de Temple en los 7 puntos, con error garantizado ≥ 9,1 mHa.
- Con la `vqe` de #6 con todos los shots ($\sigma \approx 0{,}8$ mHa):
  - la energía medida queda a ≤ 1,8σ del statevector;
  - ningún punto queda más de 2σ por debajo de Temple;
  - la cota del error del VQE es 1,0–2,3 mHa, menor que el error mínimo de CCSD (9,1 mHa), así que le gana a CCSD **sin FCI** en 7/7;
  - con FCI, también 7/7 y precisión química en 7/7 (error máximo 1,45 mHa).

  Las evidencias se recalculan solas si cambia `vqe`.
- La sección reutiliza de #5 `H_SECTOR`, `S2_SECTOR`, `LAMBDA_S2`, `sector_ansatz`, `params`, `vqe_state`, `multistart` y `starts_log`. Si #5 cambia esos nombres, hay que actualizarla.
- Limitación: el gap al siguiente singlete se cierra al estirar (1,2 mHa a 3,0 Å). En distancias mayores o sistemas más grandes, la ventana Var/gap crece y Temple pierde fuerza.
- Agrega ~25 s al notebook.
