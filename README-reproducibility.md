# Reproducibility Checklist

This document provides the exact steps to reproduce the experiments presented in the paper.

## Environment
- Python >=3.9
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- Ensure the `environment.yml` (if using conda) matches the `requirements.txt`.

## Random Seeds
- Global seed: **42**
- Experimental runs use seeds **42‑52** (inclusive). The seed for each run is computed as `seed_global * 1000 + run_idx` as defined in `src/experiment_hybrid.py`.

## Commands
- Run hybrid architecture experiment (Section 6.2):
  ```bash
  python src/experiment_hybrid.py
  ```
  This will generate `results/hybrid_comparison.csv` and `figures/figure4_hybrid_superiority.pdf`.

- Run source correlation experiment (Rule O3, Section 6.3):
  ```bash
  python src/experiment_hybrid.py
  ```
  (The script executes all tasks when run as `__main__`).

- To regenerate Figure 2 (learning curves):
  ```bash
  # The figure is produced by the hybrid experiment; locate `figures/figure2_learning_curves.pdf`.
  ```

## Data
- All result CSVs are stored in `results/`.
- Figures are stored in `figures/`.

## Verification
- Verify that the sum of belief masses equals 1.0 for any `CLAIMChannel.encode` output. A unit test is provided in `tests/test_channels.py`.

---
*Generated on $(date)*
