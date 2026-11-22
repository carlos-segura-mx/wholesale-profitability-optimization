# Dashboard data and deployment

[Español](DEPLOY.es.md) | [Case overview](README.en.md)

## Application

This repository contains the complete four-module Management Cockpit using synthetic 2025 data. Streamlit starts from `preview.py`, which loads `app_full_bilingue.py` when it finds the eleven detailed data files. Those files are already committed to the `main` branch.

The application supports Spanish and English. Its modules cover executive results, commercial performance, inventory and scenario analysis.

## Run locally

With Python 3.10 or later:

```bash
python -m pip install -r requirements.txt
streamlit run preview.py
```

There is no separate dataset download. Compressed CSV files are included in `data/` and `results_shelf_only/`, and pandas reads them directly.

## Reproducibility and checks

The data are built from two scripts:

- `scripts/generate_case_data.py`: builds the synthetic operation from a fixed seed.
- `scripts/replay_case.py`: reproduces the shelf-replenishment scenario with `--extra-dispatch 0`.

[build-data.yml](../.github/workflows/build-data.yml) regenerates the data and checks the SHA-256 hashes of all eleven original files before publishing them. The approved scenario is shelf replenishment only, without extraordinary distribution center dispatches.

[checks.yml](../.github/workflows/checks.yml) compiles the source, installs dependencies and runs functional checks on all four modules and both languages.

Generation and automated tests passed on November 21, 2026. Those checks ran on GitHub Actions. Visual review of the public Streamlit instance is handled separately.

## Main files

- `preview.py`: entrypoint and version selection.
- `app_full_bilingue.py`: complete dashboard.
- `preview_bilingue.py`: aggregated executive fallback.
- `data/*.csv.gz`: synthetic commercial and inventory data.
- `results_shelf_only/ticket_deltas.csv.gz`: transaction-level scenario outputs.
- `tests/test_dashboard.py`: module and language checks.

Carlos Segura
