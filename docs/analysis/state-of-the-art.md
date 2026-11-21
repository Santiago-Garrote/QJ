# H₄ VQE Challenge — State of the Art

Nov 21, 2026 · @Lucas

## Summary

For noiseless H₄, reaching FCI is a solved problem with adaptive ansätze; the challenge is won or lost on measurement: how few shots you need for a σ small enough to beat CCSD at 1.8 Å, and how convincingly you prove the stretched points are right without looking at FCI. Every number below comes from calculations I ran on the challenge's exact Hamiltonian (PySCF, OpenFermion, Qiskit 2.6, qiskit-aer 0.18) plus the literature cited in each section.

- **The bar.** RHF-CCSD overshoots FCI by 9.1 mHa at 1.8 Å and by 18–31 mHa from 2.0 Å on; 1.8 Å is the hardest judged point.
- **The ansatz.** QEB-ADAPT reaches FCI exactly at every stretched distance with 17–20 operators (about 160–205 CNOTs on all-to-all connectivity). One-step UCCSD stalls at 3.3 mHa at 1.8 Å. CEO-ADAPT-VQE (2025) is the published frontier for CNOT count.
- **The measurement.** For σ = 1 mHa at 1.8 Å: 2.7 × 10⁷ shots by the λ² bound, 3.5 × 10⁶ with QWC Pauli groups, 3.4 × 10⁵ with basis-rotation grouping. At 3.0 Å the last drops to 6.3 × 10³.
- **A tool trap.** qiskit\_aer's EstimatorV2 returns the exact expectation value plus optional Gaussian noise of a width you choose (default zero). Judged energies should come from SamplerV2 with real shots.
- **Reliability.** Chemically accurate energies with ⟨S²⟩ ≈ 0.3 occur at 2.4 Å, where the lowest triplet is only 4.1 mHa away. Energy variance and ⟨S²⟩ are the FCI-free proof.
- **Noise.** On FakeFez, exact circuits transpile to 520–640 CZ and land 600–800 mHa from FCI, worse than Hartree–Fock. The noisy part is a demonstration of limits and mitigation, not a race.
- **The field's direction.** IBM's sample-based diagonalization (SQD) is trivially exact here because the relevant sector has only 36 determinants; cite it, do not submit it as VQE.

## 1. The benchmark: what linear H₄ actually does

RHF-CCSD on linear H₄/STO-3G is not just inaccurate when stretched: it drops *below* FCI, by 9.1 mHa at 1.8 Å and up to 30.6 mHa at 2.4–2.6 Å. That makes 1.8 Å the hardest point in the judged zone, because it has the smallest margin to beat.

I ran the reference calculations myself (PySCF 2.15, STO-3G, equally spaced chain, RHF reference, all electrons, 4 spatial orbitals → 8 spin-orbitals). Your notebook should reproduce these numbers to the µHa; if it does not, the geometry, units or basis differ.

| d (Å) | E\_RHF (Ha) | E\_CCSD (Ha) | E\_FCI (Ha) | CCSD − FCI (mHa) | CCSD(T) − FCI (mHa) |
| --- | --- | --- | --- | --- | --- |
| 0.6 | −1.929564 | −1.960189 | −1.960194 | +0.005 | −0.000 |
| 0.7 | −2.069197 | −2.106993 | −2.106997 | +0.004 | −0.002 |
| 0.8 | −2.121387 | −2.167556 | −2.167561 | +0.005 | −0.007 |
| 0.9 | −2.124260 | −2.180309 | −2.180317 | +0.007 | −0.018 |
| 1.0 | −2.098546 | −2.166380 | −2.166387 | +0.008 | −0.043 |
| 1.2 | −2.003867 | −2.102671 | −2.102608 | −0.063 | −0.231 |
| 1.4 | −1.887790 | −2.029707 | −2.029070 | −0.636 | −1.052 |
| 1.6 | −1.772203 | −1.970572 | −1.967560 | −3.012 | −3.805 |
| **1.8** | −1.666867 | −1.933538 | −1.924431 | **−9.108** | −10.353 |
| 2.0 | −1.575616 | −1.916086 | −1.897781 | −18.305 | −20.134 |
| 2.2 | −1.499146 | −1.909120 | −1.882713 | −26.408 | −29.057 |
| 2.4 | −1.436459 | −1.905212 | −1.874652 | −30.560 | −34.171 |
| 2.6 | −1.385824 | −1.901099 | −1.870473 | −30.627 | −35.067 |
| 2.8 | −1.345365 | −1.896024 | −1.868350 | −27.675 | −32.522 |
| 3.0 | −1.313312 | −1.890304 | −1.867291 | −23.013 | −27.694 |

Four facts from this run shape the strategy:

- **The bar to clear.** The challenge criterion |E\_VQE − E\_FCI| + σ < |E\_CCSD − E\_FCI| gives a budget of 9.1 mHa at 1.8 Å and 18–31 mHa beyond 2.0 Å. A noiseless VQE that reaches FCI only needs σ below about 9 mHa at 1.8 Å to win; the stretch goal of 1.6 mHa is the real contest.
- **CCSD converges but is non-variational.** PySCF's CCSD converged at every point, so the failure mode the jury will see is overcorrelation, not divergence. CCSD(T) is worse, not better. A VQE energy is a variational upper bound, so a VQE point lying *below* FCI is a red flag for a bug or shot noise, while CCSD lying below FCI is expected. That asymmetry is itself a reliability argument.
- **RHF becomes unstable toward UHF from 1.1 Å.** The external stability check fails from 1.1 Å onward (internal RHF→RHF stability holds everywhere). Keep the RHF orbitals anyway: the ansatz must stay a spin singlet, and switching to UHF orbitals would spin-contaminate the reference and break S² = 0 as a diagnostic.
- **Equilibrium and dissociation.** A quartic fit to dense FCI points gives R\_e = 0.888 Å and E\_min = −2.180506 Ha, so D\_e = E(3.0 Å) − E(R\_e) = 313.2 mHa (8.52 eV). E(3.0 Å) is still 0.96 mHa below four isolated STO-3G hydrogen atoms (4 × −0.466582 Ha), so 3.0 Å is close to, but not exactly at, the dissociation limit; say so when you report D\_e.

Why H₄ is the textbook case: at large d the four electrons form four weakly coupled, singly occupied 1s orbitals, an antiferromagnetic-like singlet with many determinants of comparable weight. A single-reference method built on one RHF determinant cannot describe it. The H₄ chain is the minimal member of the hydrogen-chain family that the [Simons Collaboration benchmark (Motta et al., PRX 2017)](https://journals.aps.org/prx/abstract/10.1103/PhysRevX.7.031059) uses as a model of strongly correlated materials.

## 2. Ansatz: what reaches FCI, and at what CZ cost

The state of the art for small molecules is adaptive ansätze built from qubit-excitation-type operators, and my own runs on this exact Hamiltonian confirm it: QEB-ADAPT reaches FCI to 10⁻⁹ mHa at 1.8, 2.4 and 3.0 Å with 17–20 operators and roughly 160–205 CNOTs, while one-step UCCSD with the same 26 excitations stalls at 3.3 mHa at 1.8 Å.

### Measured on H₄/STO-3G (noiseless, statevector, BFGS with analytic gradients)

Pool = the 26 spin-conserving singles and doubles from the 4 occupied to the 4 virtual spin-orbitals (interleaved α/β ordering), operators allowed to repeat. CNOT counts use the Yordanov–Barnes circuits on all-to-all connectivity: qubit single = 2, qubit double = 13, fermionic single = 2n−1 and fermionic double = 2n+5 for an operator spanning n qubits ([Yordanov & Barnes, PRA 2020](https://arxiv.org/abs/2005.14475)). Linear-chain routing will add SWAPs on top, so treat these as lower bounds for your transpiled CZ counts.

| Ansatz | d (Å) | Ops / CNOT to reach 1.6 mHa | Ops / CNOT to reach 0.1 mHa | Best error |
| --- | --- | --- | --- | --- |
| QEB-ADAPT | 1.8 | 15 / 151 | 18 / 168 | \~0 (10⁻¹³ mHa) |
| QEB-ADAPT | 2.4 | 16 / 153 | 19 / 159 | \~0 |
| QEB-ADAPT | 3.0 | 13 / 136 | 17 / 188 | \~0 |
| Fermionic ADAPT | 1.8 | 15 / 239 | 17 / 273 | \~0 |
| Fermionic ADAPT | 2.4 | 10 / 162 | 19 / 291 | \~0 |
| Fermionic ADAPT | 3.0 | 9 / 125 | 17 / 271 | \~0 |
| UCCSD, 1 Trotter step, fermionic | 1.8 / 2.4 / 3.0 | 26 / 398 (fixed) | not reached at 1.8, 2.4 | 3.33 / 1.78 / 0.35 mHa |
| UCCSD, 1 Trotter step, qubit excitations | 1.8 / 2.4 / 3.0 | 26 / 250 (fixed) | not reached | 3.33 / 2.66 / 0.66 mHa |

What this says for the challenge:

- **Plain UCCSD is not enough for the stretch goal.** One Trotter step of UCCSD misses FCI by more than 1.6 mHa at 1.8 and 2.4 Å (best of 5 random starts). It still beats CCSD's 9.1 mHa margin at 1.8 Å, but only if σ stays under about 5.8 mHa.
- **ADAPT wins because it can reuse operators.** With 17–20 picks from a 26-operator pool, some excitations appear twice, which a fixed one-layer UCCSD cannot do. That extra flexibility is what closes the last few mHa in the strongly correlated region.
- **Qubit excitations cut CNOTs by about 40% at equal accuracy.** Dropping the Jordan–Wigner Z-strings costs nothing in accuracy here and is the reason QEB-ADAPT is regarded as the most hardware-efficient pre-2024 variant.
- **The 2024–25 frontier is CEO-ADAPT-VQE.** Coupled exchange operators implement up to three qubit doubles for the cost of one; the authors report CNOT count, CNOT depth and measurement cost cut by up to 88%, 96% and 99.6% versus early ADAPT for 12–14-qubit molecules, and outperform UCCSD on every metric ([Ramôa et al., npj Quantum Inf. 2025](https://arxiv.org/abs/2407.08696)). For an 8-qubit problem you would expect a smaller but real reduction over QEB-ADAPT; it is the most defensible "state of the art" choice if time allows.

### The alternatives, and why they rank lower here

| Family | What it is | Fit for this challenge |
| --- | --- | --- |
| ADAPT variants (fermionic, qubit, QEB, CEO, Overlap-ADAPT) | Grow the circuit one operator at a time by largest energy gradient | Best. Exact at 8 qubits, gives a natural error-vs-CZ curve for the report |
| Quantum-number-preserving gate fabrics ([Anselmetti et al., NJP 2021](https://arxiv.org/abs/2104.05695)) | Nearest-neighbour 4-qubit gates (orbital rotations + pair exchanges) that keep N\_α, N\_β and S² exactly | Strong second choice. Linear-local by construction, so no SWAPs on a line; preserves S² = 0, which ADAPT with a non-spin-adapted pool does not guarantee mid-run |
| Givens-rotation networks | Particle-conserving 2-qubit rotations between neighbouring spin-orbitals | Good for the noisy part: shallow and native to a line, but needs enough layers to be exact |
| UCCSD / k-UpCCGSD | Fixed chemistry-inspired circuit | Many CZs; one-step UCCSD fails the stretch goal (table above) |
| Hardware-efficient (Kandala et al. 2017) | Layers of single-qubit rotations + CZ ladders | Weakest: breaks N and S², gets trapped when stretched, and makes the symmetry diagnostics meaningless |

Overlap-ADAPT, which grows the ansatz by maximising overlap with a target wavefunction instead of energy, gives markedly shallower circuits for strongly correlated systems ([Feniou et al. 2023](https://arxiv.org/pdf/2301.10196)). It needs a classical target state, so for this challenge it should only be presented as a circuit-compression extra, never as the main result, or the jury may see it as using FCI to build the answer.

## 3. Classical optimization

At 8 qubits with statevector optimization allowed, optimization is a solved problem if you use exact gradients and a quasi-Newton method; the residual risk is local traps at large d, which ADAPT largely avoids by construction.

- **Use BFGS or L-BFGS-B with analytic gradients.** For excitation generators A with A³ = −A, exp(θA) = I + sin θ·A + (1 − cos θ)·A², so each gate is two sparse mat-vecs and a full reverse-mode gradient costs about two state passes. My H₄ runs converge to 10⁻⁹ mHa this way in seconds per distance. Gradient-free optimizers (COBYLA, SPSA) are only needed when optimizing on shots, which the rules do not require.
- **ADAPT is insensitive to rough landscapes.** Because each new parameter starts at zero and the circuit grows along the steepest direction, ADAPT "burrows" toward the global minimum and avoids barren-plateau regions in the noise-free case ([Grimsley et al., npj Quantum Inf. 2023](https://link.springer.com/article/10.1038/s41534-023-00681-0)). Initializing each iteration from the previous optimum is what makes this work.
- **Gradient troughs are the known failure mode.** ADAPT can stall when every pool gradient is near zero at a non-optimal state; recent remedies add operators in batches or restart from perturbed parameters ([Strategies for overcoming gradient troughs, 2025](https://arxiv.org/html/2512.25004v1)). If ADAPT stalls above FCI at some d, this is the first suspect.
- **Hessian recycling cuts iterations.** Passing the BFGS approximate Hessian from one ADAPT iteration to the next keeps it closer to the exact Hessian and reduces measurement cost ([Ramôa et al., QST 2025](https://www.inesctec.pt/en/people/luis-paulo-santos)). It matters little in a statevector loop but is worth one line in the report.
- **Sweep the curve in both directions.** Warm-starting d from d ± 0.2 Å is standard, but the operator sequence chosen at short d is often not the best at long d. Run ADAPT fresh at the stretched end (3.0 Å), sweep inward, then compare against the outward sweep: two continuous, overlapping curves are a strong reliability argument (Section 7).

## 4. Measurement and error bars: the real battleground

Once the ansatz is exact, σ decides everything, and the measurement scheme changes the shot bill by 10–400×: at 1.8 Å, basis-rotation grouping needs about 3.4 × 10⁵ shots for σ = 1 mHa versus 3.5 × 10⁶ for qubit-wise-commuting Pauli groups.

### First, a trap in qiskit\_aer's EstimatorV2

I read the source of qiskit-aer 0.18.4: `EstimatorV2` computes the **exact** expectation value with `save_expectation_value`, then, only if `precision > 0`, draws the result from a normal distribution N(exact, precision). The default precision is 0.0. So with Aer's Estimator there are no shots at all, the reported σ is whatever precision you pass, and with the default you are effectively reading the statevector. A jury that asks for "shots per point" and "don't read the statevector" will likely see this as a loophole.

The defensible setup: produce the judged energies with **`SamplerV2` and an explicit shot count per measurement basis**, compute E and σ from the bitstrings yourself, and use `EstimatorV2` only as a cross-check (with precision set to the σ your shot budget implies). State this choice in the report; it shows you understood the tool.

### What the Hamiltonian actually costs

The 8-qubit JW Hamiltonian has 184 non-identity Pauli terms, which sorted-insertion packs into 69 qubit-wise-commuting (QWC) groups. λ = Σ|c\_k| is 5.21 Ha at 1.8 Å, 4.70 Ha at 2.4 Å and 4.37 Ha at 3.0 Å, so the game plan's λ = 3.0 example underestimates the bound by about 3×. Shots for σ = 1 mHa with the variance-optimal split, computed at the exact ground state:

| Scheme | Distinct circuits | d = 1.8 Å | d = 2.4 Å | d = 3.0 Å |
| --- | --- | --- | --- | --- |
| λ² bound (game-plan calculator) | — | 2.7 × 10⁷ | 2.2 × 10⁷ | 1.9 × 10⁷ |
| Each Pauli term separately, optimal split | 184 | 2.1 × 10⁷ | 1.8 × 10⁷ | 1.5 × 10⁷ |
| QWC groups (sorted insertion), optimal split | 69 | 3.5 × 10⁶ | 3.0 × 10⁶ | 2.7 × 10⁶ |
| Basis-rotation grouping (double factorization), optimal split | 10 (8 at 3.0 Å) | **3.4 × 10⁵** | **5.4 × 10⁴** | **6.3 × 10³** |

Shots scale as 1/σ², so at the hardest point (1.8 Å, CCSD margin 9.1 mHa) the per-point budget is:

| Target σ at 1.8 Å | QWC groups | Basis-rotation grouping |
| --- | --- | --- |
| 9 mHa (bare win over CCSD with an exact ansatz) | 4.4 × 10⁴ | 4.2 × 10³ |
| 1.6 mHa (stretch goal, error ≈ 0) | 1.4 × 10⁶ | 1.3 × 10⁵ |
| 0.5 mHa (game plan's default) | 1.4 × 10⁷ | 1.4 × 10⁶ |

### The schemes, ranked for this challenge

1. **Basis-rotation grouping ([Huggins et al., npj Quantum Inf. 2021](https://arxiv.org/abs/1907.13117v4)).** Factorize the two-electron tensor, H = E\_nuc + one-body + Σ\_l (w\_l/2)(Σ L\_l,pq E\_pq)²; each leaf becomes diagonal in occupation numbers after a single-particle orbital rotation (a Givens network), so one circuit samples all its n\_p and n\_p n\_q at once. Only L + 1 bases, linear depth, and every shot reads out N\_α and N\_β, so you can post-select on N = 4, S\_z = 0 under noise. Its huge advantage at large d comes largely from the leaf close to N̂², which has zero variance in a fixed-N state. Cost: you write the factorization and the orbital-rotation circuits (about 40 lines with NumPy plus Qiskit's `XXPlusYYGate` or a Givens decomposition).
2. **General-commuting grouping with Clifford diagonalization.** Fewer, larger groups than QWC, at the price of entangling measurement circuits. A middle ground if the factorization is too much for the time available ([Yen et al., deterministic improvements with covariance estimates](https://ar5iv.arxiv.org/html/2201.01471)).
3. **QWC groups with variance-optimal allocation.** The baseline: easy with `SparsePauliOp.group_commuting(qubit_wise=True)` and SamplerV2. Weight shots as N\_g ∝ √Var\_g (the group variance already contains the within-group covariances), with Var\_g estimated from a pilot run.
4. **Classical shadows.** Random Pauli shadows are clearly worse than grouping for molecular Hamiltonians; in the locally-biased-shadows benchmark, H₂/JW has variance 0.40 with grouping versus 1.97 with plain shadows ([Hadfield et al.](https://arxiv.org/pdf/2006.15788)). Optimized variants (locally biased, derandomized, overlapped grouping, ShadowGrouping) close the gap ([Wu et al., Quantum 2023](https://www.arxiv.org/pdf/2105.13091)) but bring no advantage at 8 qubits worth the implementation time.

### Getting σ right

- **Estimator.** For each basis g, compute the per-shot value of the whole fragment (not term by term), take its sample mean and variance; then E = Σ\_g mean\_g and σ² = Σ\_g Var\_g / N\_g. Doing it per shot automatically includes the covariances between terms measured together, which a term-by-term formula misses.
- **Validate the formula.** Repeat the full estimate 20–50 times with different seeds and show the spread matches the predicted σ, or bootstrap over shots. This is the cheapest strong evidence you can give the jury.
- **Allocate where it is judged.** At fixed total shots, put most of them at 1.8–2.2 Å, where the CCSD margin is smallest; beyond 2.4 Å even a modest σ wins by a wide margin.

## 5. Noise and error mitigation

Under the FakeFez noise model, an exact ADAPT circuit for H₄ is hopeless: it transpiles to about 520–640 CZ gates and its energy lands 600–800 mHa above FCI, worse than Hartree–Fock. The noisy part of the challenge is therefore about showing limits and mitigation gains honestly, not about beating CCSD.

### What I measured on FakeFez (Heron r2 noise model)

FakeFez reports median errors of 3.9 × 10⁻³ per CZ, 7.6 × 10⁻³ per readout and 2.3 × 10⁻⁴ per √X. I built the QEB-ADAPT circuits in Qiskit (each operator as a `PauliEvolutionGate`, verified against the statevector to 0.03 mHa), transpiled at optimization level 3 for FakeFez (best of 3 seeds), and computed the noisy energy exactly with a density-matrix simulation.

| Circuit at d = 1.8 Å | Noiseless error (mHa) | CZ after transpiling | Noisy error (mHa) |
| --- | --- | --- | --- |
| HF only | 257.6 | 0 | 257.9 |
| ADAPT, 1 operator | 196.9 | 34 | 238.1 |
| ADAPT, 2 operators | 137.6 | 74 | 235.9 |
| ADAPT, 4 operators | 22.8 | 185 | 352.4 |
| ADAPT, 8 operators | 6.4 | 381 | 581.7 |
| ADAPT, 15 operators (< 1.6 mHa) | 0.9 | 522 | 686.3 |
| ADAPT, 18 operators (< 0.1 mHa) | 0.03 | 579 | 802.0 |

At 3.0 Å the picture is the same (473–643 CZ, 611–682 mHa noisy error). Three lessons:

- **The noise-optimal circuit has about two operators**, and even then the error is 236 mHa. At 3.9 × 10⁻³ per CZ, 580 CZs leave a circuit fidelity of roughly e^(−2.3) ≈ 10%.
- **Generic synthesis costs 3–4× the ideal CZ count.** `PauliEvolutionGate` plus heavy-hex routing gave 579 CZ where the Yordanov circuits on all-to-all connectivity need 168 CNOTs. Hand-built qubit-excitation circuits, a layout on a straight 8-qubit path, and nearest-neighbour Givens or QNP gates are the first things to fix before any mitigation.
- **Aer's EstimatorV2 hides readout error.** The HF state moved only 0.3 mHa under the full FakeFez model, consistent with readout error not being applied to saved expectation values. With a 0.76% median readout error per qubit, measured energies would be worse. Use SamplerV2 for any noisy number you report, otherwise mitigation will look better than it is.

### The mitigation toolbox, in order of payoff for this challenge

| Technique | What it fixes | Cost | Verdict |
| --- | --- | --- | --- |
| Symmetry post-selection | Shots that leave N = 4, S\_z = 0 | Free with SamplerV2 in the Z basis; free in every basis with basis-rotation grouping | Do it first |
| Readout mitigation (TREX, M3 or calibration-matrix inversion) | Readout bit-flips | A few calibration circuits | Do it; TREX is resilience level 1 in Qiskit Runtime ([IBM docs](https://quantum.cloud.ibm.com/docs/en/guides/configure-error-mitigation)) |
| Zero-noise extrapolation by CZ folding (factors 1, 3, 5) | Gate noise, to first order | 3× shots and deeper circuits | Worth showing on a short circuit; level 2 in Runtime combines it with TREX and gate twirling |
| Pauli twirling + dynamical decoupling | Turns coherent errors into stochastic ones, idle errors | Small | Pairs with ZNE |
| Purification / virtual distillation | Pushes toward the dominant eigenvector | Extra copies or post-processing | Research-grade; cite as future work ([O'Brien et al. 2022, in Anselmetti's thesis](https://kups.ub.uni-koeln.de/71111/1/anselmetti_thesis_print.pdf)) |
| Probabilistic error cancellation | Unbiased removal of learned noise | Sampling overhead exponential in CZ count | Not feasible at 100+ CZ |

In Qiskit Runtime, Sampler does not take resilience levels, so readout mitigation and post-selection on sampled bitstrings are yours to implement. A credible noisy deliverable is one stretched point (3.0 Å) with a 1–2 operator ansatz, ideally on a symmetry-tapered 4–6-qubit Hamiltonian, showing raw → post-selected → readout-mitigated → ZNE energies against the ideal value for the same circuit.

## 6. Beyond plain VQE: SQD, Krylov and tapering

IBM's own state of the art for chemistry has moved from VQE to sample-based diagonalization, and on H₄/STO-3G that method is trivially exact. That makes it a powerful discussion point and a risky main result.

- **Sample-based quantum diagonalization (SQD, also QSCI).** A circuit is used only to *sample* Slater determinants; the Hamiltonian is then diagonalized classically in the sampled subspace, with "configuration recovery" repairing noisy samples. IBM ran it on a Heron processor with the Fugaku supercomputer for N₂ and iron–sulfur clusters, using circuits of up to 77 qubits and 10,570 gates ([Robledo-Moreno et al., Science Advances 2025](https://arxiv.org/abs/2405.05068)); the open-source implementation is `qiskit-addon-sqd`.
- **Why it is a trap here.** The N = 4, S\_z = 0 sector of H₄/STO-3G has only 36 determinants (6 α strings × 6 β strings). A few hundred shots from almost any circuit, even a noisy one, sample all 36, at which point SQD *is* FCI: exact energy, zero σ, no dependence on the ansatz. It would "beat CCSD" everywhere, but the classical step is the full FCI, and the challenge asks for VQE. Use it in the report to show you know where the field is going and why H₄ is too small to need a quantum computer, not as the judged curve.
- **Sample-based Krylov diagonalization (SKQD).** Samples come from time-evolution circuits instead of a variational ansatz, which gives convergence guarantees when the ground state is concentrated on few determinants ([Piccinelli et al. 2025](https://arxiv.org/html/2508.02578)). Too deep for this event; one sentence in the outlook.
- **Qubit tapering.** Qiskit's `Z2Symmetries` finds 3 independent Z₂ symmetries in this Hamiltonian (Pauli strings ZIIZZIIZ, ZIZIZIZI and ZZIIZZII, the same at 1.8 and 3.0 Å), so it tapers from 8 to 5 qubits. The noiseless benefit is small, because the ansatz must be tapered consistently and tapered operators lose their locality; the payoff is in the noisy part, where 5 qubits mean fewer CZs and a smaller readout-error footprint. Pick the sector containing the HF state, and check that the tapered ground energy equals FCI before using it.

## 7. Reliability without looking at FCI

The strongest FCI-free evidence is the energy variance plus ⟨S²⟩: on this Hamiltonian, an energy that is already within chemical accuracy can still carry ⟨S²⟩ ≈ 0.3 and an energy standard deviation of 20–30 mHa, so energy convergence alone is not proof.

### Why spin matters so much when stretched

The stretched chain has low-lying excited states: the lowest triplet sits 29.8 mHa above the ground state at 1.8 Å but only 4.1 mHa above at 2.4 Å, with the first excited singlet at 10.8 mHa. A spin-contaminated state can therefore look almost converged in energy. My QEB-ADAPT runs (the qubit-excitation pool is not spin-adapted) show exactly that:

| d = 2.4 Å, QEB-ADAPT | Error vs FCI (mHa) | √Var(H) (mHa) | ⟨S²⟩ |
| --- | --- | --- | --- |
| 8 operators | 18.66 | 132.2 | 0.48 |
| 12 operators | 2.29 | 27.1 | 0.33 |
| 15 operators | 1.72 | 21.8 | 0.28 |
| 18 operators | 0.53 | 18.4 | 0.0004 |
| 20 operators | 0.000 | 0.000 | 0.000 |

At 1.8 Å the same pattern holds: 15 operators give 0.91 mHa error but √Var = 32 mHa; 18 operators bring √Var down to 3.0 mHa and the error to 0.03 mHa.

### The checklist, strongest first

1. **Energy variance ⟨H²⟩ − ⟨H⟩² → 0.** Only an exact eigenstate has zero variance, and the Weinstein bound guarantees an eigenvalue within √Var of ⟨H⟩. If you also estimate the gap Δ to the next singlet, Temple's bound E₀ ≥ ⟨H⟩ − Var/(E₁ − ⟨H⟩) gives a lower bound; with 18 operators at 1.8 Å it pins the energy to within 0.09 mHa. Compute it from the optimized circuit, and say plainly whether it came from the statevector (as an ansatz diagnostic) or from measurement.
2. **Symmetries: ⟨N⟩ = 4, ⟨S\_z⟩ = 0, ⟨S²⟩ = 0.** N and S\_z are guaranteed by number-conserving gates; S² is not, as the table shows. Report ⟨S²⟩ at every judged point. Spin-adapted pools or the QNP fabric of Section 2 enforce it by construction.
3. **Ansatz growth plateau.** Adding operators no longer lowers the energy and the largest pool gradient falls below a threshold (about 10⁻³ in my runs near convergence). Plot error-free quantities only: energy vs operator count and √Var vs operator count.
4. **Variational consistency.** The noiseless ansatz energy is a strict upper bound on the ground state, so a measured point that falls more than about 2σ below the Temple lower bound signals a bug or an underestimated σ. CCSD lying below VQE is expected (Section 1) and is not evidence against VQE.
5. **Path independence and smoothness.** Inward and outward warm-started sweeps, plus a few random restarts at 1.8 and 2.4 Å, should agree within σ, and the curve should be smooth when plotted against both.

## 8. Gap analysis against the game plan

The game plan's architecture (PySCF → interleaved JW → ADAPT/Givens → statevector optimization → measured energies → σ, R\_e, D\_e) matches the state of the art; the gaps are in how energies are measured, how shots are budgeted, and how reliability is argued.

| # | Change | Evidence | Effort |
| --- | --- | --- | --- |
| 1 | Produce judged energies with **SamplerV2 + explicit shots**, computing E and σ from bitstrings; use EstimatorV2 only as a cross-check | Aer's EstimatorV2 returns the exact value plus optional Gaussian noise of a chosen width, with default width 0 (Section 4) | Medium |
| 2 | Replace λ = 3.0 in the calculator with the real values (5.21 Ha at 1.8 Å, 4.37 Ha at 3.0 Å) and budget from measured group variances, not λ² | λ² overestimates the QWC-optimal cost by about 8× (Section 4) | Low |
| 3 | Use ADAPT with **operator reuse** (QEB pool for fewer CZs); do not fall back to one-step UCCSD | One-step UCCSD misses FCI by 3.3 mHa at 1.8 Å; QEB-ADAPT reaches it with about 170 CNOTs (Section 2) | Low, already planned |
| 4 | Report **⟨S²⟩ and √Var(H)** at every judged point; add the Temple bound | Chemically accurate energies with ⟨S²⟩ ≈ 0.3 occur at 2.4 Å (Section 7) | Low |
| 5 | Measure with QWC groups and N\_g ∝ √Var\_g first; upgrade to **basis-rotation grouping** if time allows | 3.5 × 10⁶ vs 3.4 × 10⁵ shots for σ = 1 mHa at 1.8 Å; the upgrade also enables post-selection (Section 4) | Medium → high |
| 6 | Concentrate shots at 1.8–2.2 Å | Smallest CCSD margin: 9.1 mHa at 1.8 Å vs 18–31 mHa beyond 2.0 Å (Section 1) | Low |
| 7 | Validate σ with 20–50 repeated estimates or a bootstrap | Cheapest convincing evidence that the error bar is right | Low |
| 8 | Noisy extra: 1–2 operator ansatz at 3.0 Å on FakeFez via SamplerV2, showing raw → post-selected → readout-mitigated → ZNE; hand-built excitation circuits on a straight qubit path | Exact circuits transpile to 520–640 CZ and land 600–800 mHa off (Section 5) | Medium |
| 9 | Mention SQD as the field's direction, explaining why it is exact (36 determinants) and therefore not the judged result | Section 6 | Low |
| 10 | State two caveats: RHF is externally unstable from 1.1 Å (kept on purpose for a singlet reference), and E(3.0 Å) is 0.96 mHa below four isolated atoms | Section 1 | Low |

What a 10⁵-shot budget per point buys at 1.8 Å, as a quick sanity check on the plan's "σ with 10⁵ shots" field: σ ≈ 16.5 mHa by the λ bound, 5.9 mHa with QWC groups and optimal allocation, and 1.8 mHa with basis-rotation grouping. Only the last two beat CCSD's 9.1 mHa margin there, and only basis-rotation grouping gets close to the stretch goal.

## Sources

Own calculations: PySCF 2.15.1, OpenFermion 1.8.1, Qiskit 2.6.2, qiskit-aer 0.18.4, qiskit-ibm-runtime FakeFez; linear H₄, STO-3G, RHF orbitals, interleaved Jordan–Wigner ordering. Challenge requirements as summarized in the team's [H₄ VQE Game Plan](https://claude.ai/artifact/BXw7JDtTSBZ5p6pj9ZXNDW); the original challenge page was not reachable from here.

- [Motta et al., Equation of state of the hydrogen chain, PRX 7, 031059 (2017)](https://doi.org/10.1103/PhysRevX.7.031059)
- [Yordanov & Barnes, Efficient quantum circuits for quantum computational chemistry, PRA 2020](https://arxiv.org/abs/2005.14475)
- [Ramôa et al., Reducing the resources required by ADAPT-VQE using coupled exchange operators, npj Quantum Inf. 2025](https://arxiv.org/abs/2407.08696)
- [Anselmetti et al., Local, expressive, quantum-number-preserving VQE ansätze, New J. Phys. 2021](https://arxiv.org/abs/2104.05695)
- [Feniou et al., Overlap-ADAPT-VQE, 2023](https://arxiv.org/pdf/2301.10196)
- [Grimsley et al., ADAPT-VQE is insensitive to rough parameter landscapes and barren plateaus, npj Quantum Inf. 2023](https://link.springer.com/article/10.1038/s41534-023-00681-0)
- [Strategies for overcoming gradient troughs in ADAPT-VQE, 2025](https://arxiv.org/html/2512.25004v1)
- [Ramôa et al., Recycling the Hessian in adaptive variational algorithms, QST 2025 (publication listing)](https://www.inesctec.pt/en/people/luis-paulo-santos)
- [Huggins et al., Efficient and noise resilient measurements for quantum chemistry, npj Quantum Inf. 2021](https://arxiv.org/abs/1907.13117v4)
- [Yen, Ganeshram & Izmaylov, Deterministic improvements of quantum measurements, npj Quantum Inf. 2023](https://ar5iv.arxiv.org/html/2201.01471)
- [Hadfield et al., Measurements of quantum Hamiltonians with locally-biased classical shadows](https://arxiv.org/pdf/2006.15788)
- [Wu et al., Overlapped grouping measurement, Quantum 2023](https://www.arxiv.org/pdf/2105.13091)
- [IBM Quantum docs, Configure error mitigation (TREX, ZNE, resilience levels)](https://quantum.cloud.ibm.com/docs/en/guides/configure-error-mitigation)
- [Anselmetti, PhD thesis incl. purification-based error mitigation, Cologne 2023](https://kups.ub.uni-koeln.de/71111/1/anselmetti_thesis_print.pdf)
- [Robledo-Moreno et al., Chemistry beyond the scale of exact diagonalization (SQD), Science Advances 2025](https://arxiv.org/abs/2405.05068)
- [Piccinelli et al., Randomized sample-based Krylov quantum diagonalization, 2025](https://arxiv.org/html/2508.02578)
- [Recent developments in VQE: survey and benchmarking, 2026](https://arxiv.org/abs/2602.11384)
