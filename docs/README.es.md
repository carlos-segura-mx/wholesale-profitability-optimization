# Optimización de rentabilidad mayorista

[English](README.en.md) | [Dashboard interactivo](https://wholesale-profitability-optimization-uenabzltjvquoxm2k5yg2p.streamlit.app/) | [Código](../)

## El punto de partida

Vender más no siempre significa ganar más. En una distribuidora, una venta puede tener buen margen, pero la operación pierde oportunidades cuando no hay producto disponible. Reponer inventario ayuda a recuperar ventas, aunque también genera costos y puede desplazar otras compras.

Construí este caso para analizar esas decisiones con números y no solo con indicadores aislados. La pregunta principal es cuánto valor puede aportar una mejora en la disponibilidad de producto, después de considerar sus costos y efectos sobre las ventas existentes.

## Cómo lo trabajé

Preparé una operación mayorista simulada con cuatro sucursales, un centro de distribución, 120 productos y un año de información. Los datos son sintéticos y representan 2025.

El análisis relaciona ventas, costo de venta, margen, presupuestos, demanda solicitada y surtida, inventario y gastos operativos. A partir de esa base desarrollé un escenario de reposición de anaquel y revisé su contribución económica.

El tablero está organizado alrededor de cuatro temas: desempeño ejecutivo, resultados comerciales, inventario y disponibilidad, y evaluación de escenarios.

## Qué encontré

En el ejercicio, las ventas netas suman aproximadamente **54.42 millones de MXN**, con un **margen bruto de 33.3 %** y un **nivel de surtido de 94.90 %**.

En el escenario de reposición se recuperan **4,004 unidades**, pero también se desplazan **2,525 unidades** de otras ventas. El resultado neto es de **1,479 unidades adicionales**.

Después de incorporar los costos de manejo contemplados en el modelo, la contribución incremental anual estimada es de **98,507.45 MXN**, antes de otros costos que no están representados.

Ese último punto es clave: recuperar ventas no equivale automáticamente a generar la misma cantidad de utilidad. Si cambian los supuestos de realización, los costos de manejo o los costos adicionales, también cambia el resultado. Bajo algunas condiciones, la contribución puede ser negativa.

## Explorar el dashboard

[**Abrir la aplicación en Streamlit**](https://wholesale-profitability-optimization-uenabzltjvquoxm2k5yg2p.streamlit.app/)

El dashboard incluye los cuatro módulos del caso. Puedo comparar resultados por mes, sucursal y categoría, revisar productos e inventario, ajustar umbrales de gestión y explorar el efecto económico de una intervención de reposición.

Los datos de detalle ya forman parte del repositorio. La aplicación y sus cuatro módulos superaron las pruebas funcionales automatizadas en español e inglés.

## Alcance del ejercicio

Este es un caso de portafolio construido con datos sintéticos. No describe la operación ni los resultados de una empresa real. La simulación sirve para probar criterios de decisión y relaciones contables, no para atribuir ahorros observados o demostrar causalidad.

La conciliación económica corresponde al escenario completo de la red y del año. Las vistas filtradas son aproximaciones y no cuentan con la misma conciliación independiente.

## Herramientas y ejecución

Utilicé Python, pandas, Plotly y Streamlit. Para ejecutar el dashboard completo:

```bash
python -m pip install -r requirements.txt
streamlit run preview.py
```

La aplicación permite cambiar entre español e inglés. La generación de los datos y las comprobaciones de integridad están explicadas en las [notas técnicas](DEPLOY.es.md).

**Carlos Segura** | CS Intelligence
