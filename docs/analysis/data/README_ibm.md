# Datos de hardware real de IBM (#22, #13)

Todo en `ibm_marrakesh` (IBM Heron r2), H₄ lineal STO-3G, d = 2,4 Å, ansatz de 2 operadores (28 `cz`), 46 grupos QWC × 4000 shots.

| Archivo | Contenido |
|---|---|
| `ibm_hardware_marrakesh_2.4A.json` | Corrida de referencia (job `dc0urtmq4uuc73a3895g`): grupos medidos (etiquetas y coeficientes), ángulos, *counts* crudos, energía de hardware y de su emulación |
| `ibm_hardware_marrakesh_2.4A_run1_ambiguous.json` | Primera corrida (job `dc0uo5qnj2vs73del9s0`): *counts* crudos, **sin** los grupos guardados (energía ambigua ≈ 7 mHa, ver ADR 0029) |
| `ibm_raw_counts_repeats_and_mitigation.json` | *Counts* crudos de las 3 repeticiones y del job de mitigación (`cz` plegadas x3 + calibración de readout todo-0/todo-1) |
| `ibm_repeats_marrakesh_2.4A.json` | Energías por corrida, promedio, dispersión y χ² (hardware y emulación) |
| `ibm_mitigation_marrakesh_2.4A.json`, `ibm_mitigation_emulated_marrakesh_2.4A.json` | Crudo / readout / ZNE en hardware y emulado; errores de readout por qubit físico |
| `ibm_scan_marrakesh_2.4A.json` | Barrido emulado del tamaño del ansatz (2, 4, 6 operadores) |
| `../ibm_hardware_comparison_2.4A.png` | Gráfico comparativo de todo lo anterior |

Para reprocesar: los grupos de `ibm_hardware_marrakesh_2.4A.json` están en el mismo orden que los *counts* de todos los jobs (mismos circuitos). Scripts: `scripts/ibm_hardware.py`, `ibm_hardware_repeat.py`, `ibm_mitigation.py`.
