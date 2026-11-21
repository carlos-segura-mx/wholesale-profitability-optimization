# Datos y despliegue del dashboard

[English](DEPLOY.en.md) | [Presentación del caso](README.es.md)

## Aplicación

El repositorio contiene el Management Cockpit de cuatro módulos con datos sintéticos de 2025. El punto de entrada de Streamlit es `preview.py`, que utiliza `app_full_bilingue.py` cuando encuentra los once archivos de detalle. Esos archivos ya están incorporados en la rama `main`.

La aplicación tiene selector de idioma para español e inglés. Los módulos cubren resumen ejecutivo, desempeño comercial, inventario y evaluación de escenarios.

## Ejecutar localmente

Con Python 3.10 o posterior:

```bash
python -m pip install -r requirements.txt
streamlit run preview.py
```

No hace falta descargar datos por separado. Los archivos CSV comprimidos están en `data/` y `results_shelf_only/`; pandas los lee directamente.

## Reproducción y verificaciones

La fuente de datos está construida a partir de dos programas:

- `scripts/generate_case_data.py`: crea la operación sintética completa usando una semilla fija.
- `scripts/replay_case.py`: reproduce el escenario de reposición de anaquel con `--extra-dispatch 0`.

El flujo [build-data.yml](../.github/workflows/build-data.yml) vuelve a generar ambos conjuntos y contrasta las huellas SHA-256 de los once archivos originales antes de publicarlos. El escenario aprobado es exclusivamente de reposición de anaquel, sin despachos extraordinarios desde el centro de distribución.

El flujo [checks.yml](../.github/workflows/checks.yml) revisa la sintaxis, instala las dependencias y ejecuta pruebas funcionales de los cuatro módulos y ambos idiomas.

La generación y las pruebas se completaron correctamente el 21 de noviembre de 2026. Esas comprobaciones se realizaron en GitHub Actions. La revisión visual de la instancia pública de Streamlit se realiza por separado.

## Archivos principales

- `preview.py`: punto de entrada y selección de versión.
- `app_full_bilingue.py`: dashboard completo.
- `preview_bilingue.py`: respaldo ejecutivo agregado.
- `data/*.csv.gz`: información comercial y de inventario sintética.
- `results_shelf_only/ticket_deltas.csv.gz`: resultados por transacción del escenario.
- `tests/test_dashboard.py`: prueba funcional de módulos e idiomas.

Carlos Segura | CS Intelligence
