# Dashboard deployment and data files

[Español](DEPLOY.es.md) | [Case overview](README.en.md)

## Current status

The public entrypoint is `preview.py`. When detailed data files are missing, it runs an aggregated executive view. Once all eleven required files are available, it launches the four-module dashboard from `app_full_bilingue.py`.

Both versions let you select Spanish or English. The dataset represents a simulated wholesale operation in 2025.

## Run locally

Python 3.10 or later is required.

```bash
python -m pip install -r requirements.txt
streamlit run preview.py
```

The aggregated view does not require external data files. The full dashboard needs compressed CSVs in `data/` and `results_shelf_only/`.

## Add the detailed dataset

`PORT01_PUBLIC_SYNTHETIC_DATA.zip` contains eleven synthetic CSV files and serves as the input for the GitHub Actions publishing workflow.

1. Upload the validated ZIP to the root of the `main` branch.
2. Open [publish-data.yml](../.github/workflows/publish-data.yml) under **Actions**.
3. Confirm that SHA-256 checks and the sales and fill-rate controls pass.
4. Confirm that the workflow commits the compressed CSV files and removes the ZIP from the current branch state.
5. Check that the four Streamlit modules load, filters respond and scenario outputs match the selected scope.

The release is not complete until these checks pass. If the required files are missing, the app continues to show the smaller executive view. Do not mix these synthetic data with unrelated datasets.

## Repository files

- `preview.py`: Streamlit entrypoint and version selection.
- `preview_bilingue.py`: standalone executive view.
- `app_full_bilingue.py`: four-module analysis.
- `scripts/import_public_data.py`: data verification and import.
- `.github/workflows/`: source checks and data publishing.

**Status:** The executive preview has been observed running online. The full dashboard still requires data loading and visual testing.

Carlos Segura | CS Intelligence
