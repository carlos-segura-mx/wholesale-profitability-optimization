# Wholesale Profitability Optimization

**Rentabilidad y disponibilidad en operaciones mayoristas | Profitability and availability in wholesale operations**

[Español](docs/README.es.md) | [English](docs/README.en.md) | [Dashboard interactivo / Live dashboard](https://wholesale-profitability-optimization-uenabzltjvquoxm2k5yg2p.streamlit.app/)

## El proyecto | About the project

**ES.** Construí este caso para explorar una pregunta de gestión: ¿qué pasa con la rentabilidad cuando una distribuidora vende, pero no siempre logra surtir lo que sus clientes piden? El análisis reúne ventas, margen, demanda no atendida, inventario y costos de reposición. Utiliza un negocio simulado con cuatro sucursales, un centro de distribución y datos sintéticos de 2025.

**EN.** I built this case around a practical management question: what happens to profitability when a wholesaler makes sales but cannot always fulfill customer demand? The analysis brings together sales, margins, unmet demand, inventory and replenishment costs. It uses a simulated business with four branches, one distribution center and synthetic data for 2025.

## Resultados del ejercicio | Case results

| Indicador / Metric | Resultado / Result |
| --- | ---: |
| Ventas netas / Net sales | MXN 54.42 million |
| Margen bruto / Gross margin | 33.3% |
| Nivel de surtido / Demand fill rate | 94.90% |
| Unidades recuperadas en el escenario / Recovered units in scenario | 4,004 |
| Unidades desplazadas / Displaced units | 2,525 |
| Contribución incremental estimada / Estimated incremental contribution | MXN 98,507.45 |

**ES.** La contribución estimada corresponde al escenario anual completo, antes de costos no incluidos en el modelo. No es una utilidad observada ni una estimación causal. El resultado depende de los supuestos del ejercicio.

**EN.** The estimated contribution refers to the full-year scenario before costs not included in the model. It is neither observed profit nor a causal estimate. The result depends on the assumptions used.

## Explorar | Explore

[**Abrir el dashboard / Open the dashboard**](https://wholesale-profitability-optimization-uenabzltjvquoxm2k5yg2p.streamlit.app/)

La versión online incluye indicadores por sucursal, alertas configurables y sensibilidad económica del escenario. El análisis completo contempla también desempeño por producto e inventario. Su despliegue con datos de detalle aún está pendiente.

The live version includes branch KPIs, adjustable alerts and scenario sensitivity. The complete analysis also covers product-level performance and inventory. Deployment with detailed data is still pending.

## Código | Code

Python, pandas, Plotly y Streamlit. Para ejecutar la versión online desde el repositorio:

Python, pandas, Plotly and Streamlit. To run the current online version from the repository:

```bash
python -m pip install -r requirements.txt
streamlit run preview.py
```

[Notas de despliegue (ES)](docs/DEPLOY.es.md) | [Deployment notes (EN)](docs/DEPLOY.en.md)

Carlos Segura | CS Intelligence
