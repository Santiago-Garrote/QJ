# QJ · QuantumJam 2026

VQE energy curve of a linear H4 chain (STO-3G). Challenge statement: [`docs/`](docs/README.md).

```
docs/                    challenge statement
docs/analysis/           reference numbers, literature review, strategy (plan.html)
docs/adr/                architecture decision records (why things are the way they are)
notebooks/h4_vqe.ipynb   the deliverable (self-contained, runs in Colab)
scripts/                 classical reference data (PySCF) and measurement-cost analysis
results/                 generated outputs (git-ignored)
requirements.txt
```

Local setup: `nix develop` (then `jupyter lab`). Without Nix: `pip install -r requirements.txt jupyter`.

## Dependencies

`requirements.txt` is the single source of truth. To add or change a dependency:

1. Edit `requirements.txt` (pin versions to what nixpkgs ships: `nix develop` fails if they differ).
2. Copy the same list into the notebook's `%pip install -q ...` cell.
3. Run `nix flake check`: it fails if the notebook and `requirements.txt` disagree.
