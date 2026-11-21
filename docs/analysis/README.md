# Análisis del desafío: números de referencia y literatura

Análisis previo al notebook: qué tan difícil es cada parte del desafío, con números reales de H₄ lineal en STO-3G, y qué dice la literatura sobre cómo atacarlo.

- [`plan.html`](plan.html): versión visual e interactiva de este análisis (gráficos, calculadora de shots, checklist de entregables). Abrir en el navegador.
- [`state-of-the-art.md`](state-of-the-art.md): estado del arte con corridas propias (en inglés): QEB-ADAPT vs. UCCSD con conteos de CNOT, costo de medición por esquema (incluido basis-rotation grouping), la trampa de `EstimatorV2` en qiskit-aer, ruido en FakeFez, mitigación, SQD/tapering, chequeos de confiabilidad y un análisis de brechas contra este plan.
- [`data/`](data/): snapshot de los resultados de los scripts.
- Scripts que los generan: [`scripts/h4_reference.py`](../../scripts/h4_reference.py) y [`scripts/h4_measurement.py`](../../scripts/h4_measurement.py). Escriben en `results/` (ignorado por git); `data/` es una copia comiteada.

```bash
python scripts/h4_reference.py     # RHF, CCSD, CCSD(T), FCI + Hamiltoniano JW de 8 qubits
python scripts/h4_measurement.py   # costo de medición, <S²>, peso de Hartree-Fock
```

Los números se calcularon con PySCF 2.15.1 y Qiskit 2.4.1 (`requirements.txt` fija PySCF 2.14.0 y Qiskit 2.5.2; los resultados no deberían cambiar). El Hamiltoniano de Jordan-Wigner reproduce la energía FCI en cada distancia (el script lo verifica con un `assert`).

## Números de referencia

| d (Å) | FCI (Ha) | CCSD − FCI (mHa) | CCSD(T) − FCI (mHa) | gap S₀→T₁ (mHa) |
|---:|---:|---:|---:|---:|
| 0,6 | −1,960194 | +0,005 | 0,000 | 576,9 |
| 0,9 | −2,180317 | +0,008 | −0,017 | 288,7 |
| 1,2 | −2,102608 | −0,06 | −0,23 | 149,1 |
| 1,6 | −1,967560 | −3,01 | −3,81 | 53,6 |
| **1,8** | −1,924431 | **−9,11** | −10,35 | 29,8 |
| 2,0 | −1,897781 | −18,31 | −20,13 | 15,9 |
| 2,4 | −1,874652 | −30,56 | −34,17 | 4,14 |
| 2,6 | −1,870473 | −30,63 | −35,07 | 2,04 |
| 2,8 | −1,868350 | −27,67 | −32,52 | 0,98 |
| 3,0 | −1,867291 | −23,01 | −27,70 | 0,46 |

Tabla completa (16 distancias, con RHF y λ) en [`data/h4_reference.json`](data/h4_reference.json).

## Hallazgos

1. **CCSD cae por debajo de FCI.** Desde ~1,1 Å CCSD no es variacional: da energías menores que la exacta. El error es 9,1 mHa a 1,8 Å, toca 30,6 mHa a 2,6 Å y queda en 23,0 mHa a 3,0 Å. CCSD(T) es peor. Coincide con lo que reportan Bertels et al. (2022) para H₄ estirado.
2. **El punto más exigente del criterio central es 1,8 Å.** Es donde CCSD tiene su menor error dentro de la zona juzgada: hace falta |sesgo| + σ < 9,1 mHa. De 2,2 Å en adelante el margen supera los 20 mHa.
3. **Triplete casi degenerado a 2,7–3,0 Å.** El primer excitado del sector N = 4, S<sub>z</sub> = 0 es un triplete (⟨S²⟩ = 2) a 1,4 mHa (2,7 Å) y 0,46 mHa (3,0 Å), por debajo de la precisión química. Un estado con el espín equivocado igual da precisión química en energía, y la varianza ⟨H²⟩ − ⟨H⟩² deja de distinguirlos. **Hay que medir y reportar ⟨S²⟩.**
4. **Hartree-Fock deja de ser buena referencia.** Su peso en el estado exacto cae de 0,985 (0,6 Å) a 0,58 (1,8 Å) y 0,27 (3,0 Å). Conviene un ansatz multiconfiguracional y arranque en caliente desde el punto vecino.
5. **D<sub>e</sub> es donde CCSD pierde más.** Con FCI, R<sub>e</sub> ≈ 0,90 Å y D<sub>e</sub> ≈ 313 mHa; CCSD da ≈ 290 mHa (23 mHa menos). Son estimaciones gruesas sobre la grilla de 0,1 Å.

## Costo de medición

El Hamiltoniano tiene 185 términos de Pauli; un agrupamiento greedy en conjuntos que conmutan qubit a qubit (QWC) los reduce a ~70 grupos. Con reparto óptimo de shots (N<sub>g</sub> ∝ √Var<sub>g</sub>), σ = K/√N, con K calculado sobre el estado exacto:

| d (Å) | K grupos QWC (Ha) | K término a término (Ha) | λ = Σ\|c<sub>k</sub>\| (Ha) | shots para σ = 1 mHa (QWC) |
|---:|---:|---:|---:|---:|
| 0,6 | 1,96 | 4,28 | 10,25 | 3,9 M |
| 1,2 | 2,18 | 4,39 | 6,39 | 4,7 M |
| 1,8 | 1,94 | 4,54 | 5,21 | 3,8 M |
| 2,4 | 1,78 | 4,22 | 4,70 | 3,2 M |
| 3,0 | 1,63 | 3,89 | 4,37 | 2,7 M |

Agrupar y repartir bien ahorra ~7× frente a la cota ingenua con λ a 1,8 Å. Para ganarle a CCSD a 1,8 Å con σ ≈ 3 mHa alcanzan ~0,4 M shots; la precisión química exige del orden de millones por punto.

## Recomendaciones

- **Ansatz:** QEB-ADAPT-VQE (conserva N, pocas cz por operador), con k-UpCCGSD como comparador y el hardware-efficient de Kandala como línea de base.
- **Parámetros:** optimizar sin ruido (está permitido) y arrancar cada d desde los θ del vecino, recorriendo la curva en ambos sentidos.
- **Medición:** EstimatorV2 con grupos QWC y más shots a 1,8–2,0 Å.
- **Confiabilidad:** ⟨N⟩ = 4, ⟨S<sub>z</sub>⟩ = 0, ⟨S²⟩ ≈ 0, energía estable al agrandar el ansatz, curva suave.
- **R<sub>e</sub>:** puntos densos entre 0,8 y 1,0 Å y ajuste local con bootstrap.
- **cz:** transpilar con base cz, sx, x, rz y acoplamiento lineal (como `ruido.py`).
- **Extras baratos:** comparar ansätze, ruido de `ruido.py`, verificación de simetría (filtrar N y S<sub>z</sub> en grupos en base Z).

## Literatura

| Paper | Qué aporta | Para nosotros |
|---|---|---|
| Bertels et al., [arXiv:2207.03063](https://arxiv.org/abs/2207.03063) (2022) | Estudia H₄ lineal estirado: CCSD por debajo de FCI desde ~1,05 Å, UHF rompe S² cerca de 1,00 Å, la ruptura de simetría frena ADAPT | El paper más cercano al desafío; justifica conservar simetrías |
| Kandala et al., Nature 549, 242 (2017) | VQE hardware-efficient para H₂, LiH, BeH₂ en 6 qubits | Referencia del enunciado; línea de base para comparar ansätze |
| Peruzzo et al., Nat. Commun. 5, 4213 (2014) | Introduce VQE | Cita de la introducción |
| Tilly et al., [arXiv:2111.05176](https://arxiv.org/abs/2111.05176) (2022) | Revisión de métodos y buenas prácticas de VQE | Respaldo para cada decisión |
| Grimsley et al., Nat. Commun. 10, 3007 (2019) | ADAPT-VQE: ansatz construido por gradiente | Curva error vs. operadores vs. cz |
| Yordanov et al., [arXiv:2011.10540](https://arxiv.org/abs/2011.10540) (2021) | QEB-ADAPT: excitaciones de qubits, circuitos más baratos en CNOT | Ansatz recomendado |
| Tang et al., [arXiv:1911.10205](https://arxiv.org/abs/1911.10205) (2021) | qubit-ADAPT: pool de Pauli, circuitos ~10× menos profundos | Alternativa; puede romper S² |
| Lee et al., [arXiv:1810.02327](https://arxiv.org/abs/1810.02327) (2019) | k-UpCCGSD, benchmark en H₄/STO-3G | Ansatz fijo de respaldo |
| Arrazola et al., Quantum 6, 742 (2022) | Rotaciones de Givens universales para unitarias que conservan N | Fundamenta que se puede alcanzar FCI |
| Verteletskyi et al., [arXiv:1907.03358](https://arxiv.org/abs/1907.03358) (2020) | Agrupamiento QWC como cobertura de cliques (~3× menos grupos) | 185 términos → ~70 grupos |
| Bravyi et al., [arXiv:1701.08213](https://arxiv.org/abs/1701.08213) (2017) | Tapering de qubits por simetrías Z₂ | Extra "≤ 6 qubits" |
| Temme et al., PRL 119, 180509 (2017) | Origen de ZNE y cancelación probabilística | Recurso oficial del desafío |
| Kandala et al., Nature 567, 491 (2019) | ZNE en hardware sobre problemas variacionales | Muestra que ZNE funciona en VQE |
| Giurgica-Tiron et al., [arXiv:2005.10921](https://arxiv.org/abs/2005.10921) (2020) | ZNE digital por plegado de compuertas | Receta para el extra de mitigación |
| Bonet-Monroig et al., PRA 98, 062339 (2018) | Mitigación por verificación de simetrías | Filtrar N y S<sub>z</sub>, casi gratis |
| Robledo-Moreno et al., [arXiv:2405.05068](https://arxiv.org/abs/2405.05068) (2025) | SQD | Por qué SQD está excluido (36 configuraciones) |

Los papers se revisaron a partir de resúmenes y fuentes secundarias. Conviene verificar en los PDF cualquier número puntual (por ejemplo, conteos de CNOT) antes de citarlo en el notebook.
