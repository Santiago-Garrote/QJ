# Exploración del ansatz (#4)

Scripts usados para elegir el ansatz de la sección 3 del notebook. No forman parte del entregable; están para reproducir la comparación.

Correr desde la raíz del repo: `nix develop --command bash -c "cd exploration/4-ansatz && python compare2.py"`.

| Script | Qué hace |
|---|---|
| `check_signs.py` | Verifica que la convención de signos de PySCF coincide con Jordan-Wigner (celda 0.1). |
| `compare2.py` | UCCSD, UCCSD de qubits y k-UpCCGSD (k = 1, 2, 3) a 0,9 / 1,8 / 3,0 Å. |
| `compare3.py` | k-QUpCCGSD con rotaciones de Givens. |
| `prune.py` | Poda greedy de 2-QUpCCGSD (tolerancia 0,1 mHa en 6 distancias). Resultado: `pruned.json`. |
| `core.py`, `ansatz.py`, `givens.py`, `fast.py` | Utilidades: PySCF, generadores, circuitos y simulación en el sector N=4, S_z=0. |
