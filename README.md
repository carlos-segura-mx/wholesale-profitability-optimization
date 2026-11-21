# Wholesale Profitability Optimization | Optimización de rentabilidad mayorista

**EN:** A commercial analytics portfolio case built on fictional wholesale data. The live application currently shows an aggregated executive preview. It is not the full four-module release.

**ES:** Caso de portafolio de analítica comercial desarrollado con datos mayoristas ficticios. La aplicación online muestra por ahora una vista ejecutiva agregada, no la versión completa de cuatro módulos.

**Live app / Aplicación online:** https://wholesale-profitability-optimization-uenabzltjvquoxm2k5yg2p.streamlit.app/

**Full documentation / Documentación completa:**

- [Español](docs/README.es.md)
- [English](docs/README.en.md)

The source code for both language options is in `preview_bilingue.py`. The deployed entrypoint is `preview.py`.

El código de ambas opciones de idioma se encuentra en `preview_bilingue.py`. El archivo de entrada desplegado es `preview.py`.

## Key findings / Resultados principales

| Metric / Indicador | Synthetic result / Resultado sintético |
| --- | ---: |
| Net sales / Ventas netas | MXN 54.42M |
| Gross margin / Margen bruto | 33.3% |
| Demand fill rate / Nivel de surtido | 94.90% |
| Recovered units / Unidades recuperadas | 4,004 |
| Displaced units / Unidades desplazadas | 2,525 |
| Full-scope illustrative incremental contribution / Contribución incremental ilustrativa, alcance completo | MXN 98,507.45 |

**EN:** These are modeled figures, not observed profits, client results, or verified causal effects. The business and data are fictional.

**ES:** Son cifras modeladas, no utilidades observadas, resultados de clientes ni efectos causales comprobados. El negocio y los datos son ficticios.

## Local use / Uso local

```bash
python -m pip install -r requirements.txt
streamlit run preview.py
```

**Author / Autor:** Carlos Segura | CS Intelligence
