# Despliegue y archivos del dashboard

[English](DEPLOY.en.md) | [Presentación del caso](README.es.md)

## Estado actual

El punto de entrada público es `preview.py`. Mientras falten los archivos de datos detallados, muestra una versión ejecutiva agregada. Cuando están presentes los once archivos requeridos, inicia el tablero de cuatro módulos desde `app_full_bilingue.py`.

Ambas versiones permiten elegir español o inglés. Los datos corresponden a una operación simulada de 2025.

## Ejecutar localmente

Se requiere Python 3.10 o posterior.

```bash
python -m pip install -r requirements.txt
streamlit run preview.py
```

La vista agregada funciona sin datos externos. Para los cuatro módulos completos, el repositorio necesita los CSV comprimidos en `data/` y `results_shelf_only/`.

## Incorporar los datos detallados

El archivo `PORT01_PUBLIC_SYNTHETIC_DATA.zip` contiene once CSV sintéticos y se utiliza como paquete de entrada del flujo de GitHub Actions.

1. Cargar el ZIP validado en la raíz de la rama `main`.
2. Consultar la ejecución de [publish-data.yml](../.github/workflows/publish-data.yml) en la pestaña **Actions**.
3. Confirmar que finalicen las validaciones de integridad SHA-256 y los controles de ventas y surtido.
4. Verificar que el flujo haya incorporado los CSV comprimidos y retirado el ZIP de la versión actual.
5. Comprobar en Streamlit que abren los cuatro módulos, que responden los filtros y que el escenario se comporta según su alcance.

La carga no se considera terminada hasta comprobar estos pasos. Si faltan archivos, la aplicación sigue mostrando la vista resumida. No deben mezclarse estos datos sintéticos con información ajena al caso.

## Estructura útil

- `preview.py`: entrada a Streamlit y selección automática de versión.
- `preview_bilingue.py`: vista ejecutiva independiente.
- `app_full_bilingue.py`: análisis de cuatro módulos.
- `scripts/import_public_data.py`: verificación e importación del paquete.
- `.github/workflows/`: pruebas de código y publicación de datos.

**Estado:** La aplicación resumida se observó funcionando online. La versión completa sigue pendiente de cargar datos y realizar pruebas visuales.

Carlos Segura | CS Intelligence
