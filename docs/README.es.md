# Optimización de rentabilidad mayorista

**Caso de portafolio | CS Intelligence | Noviembre de 2026**

Este proyecto examina las decisiones que enfrenta una distribuidora con varias sucursales: vender con margen, atender la demanda, mantener inventario suficiente y distinguir una mejora operativa de un beneficio económico comprobable.

La empresa, sus cuatro sucursales, el centro de distribución, sus productos y todas las transacciones son ficticios. No se utilizaron archivos internos de Casa Santos Lugo ni de ningún otro negocio.

## Demostración

[Ver la aplicación en Streamlit](https://wholesale-profitability-optimization-uenabzltjvquoxm2k5yg2p.streamlit.app/)

La aplicación pública muestra por ahora una vista ejecutiva agregada con indicadores de las cuatro sucursales, alertas configurables y sensibilidad económica de un escenario. El código bilingüe está en [preview_bilingue.py](../preview_bilingue.py). No se presenta esta vista resumida como el tablero completo.

El caso técnico de origen incorpora cuatro módulos:

1. Resumen ejecutivo. Ventas, margen, contribución, presupuestos y alertas.
2. Desempeño comercial. Categorías, productos y comportamiento de las sucursales.
3. Inventario y disponibilidad. Demanda atendida, faltantes y existencias.
4. Laboratorio de escenarios. Reposición de anaquel y sensibilidad de costos.

La publicación de los cuatro módulos con su nivel de detalle original sigue pendiente de integrar los archivos sintéticos completos y validar su ejecución en la nube.

## Cifras de referencia

En el conjunto de datos sintéticos de 2025, las ventas netas ascienden a aproximadamente **54.42 millones de MXN** y el nivel de surtido es **94.90 %**. La intervención de reposición de anaquel recupera 4,004 unidades, desplaza 2,525 y deja 1,479 unidades netas adicionales.

La conciliación anual del modelo estima **98,507.45 MXN de contribución incremental antes de costos no modelados**. No se trata de una ganancia observada, una medición causal ni un pronóstico comercial. Los resultados para subconjuntos de datos no tienen la misma validación contable que el total anual.

## Reproducir la vista ejecutiva

```bash
python -m pip install -r requirements.txt
streamlit run preview_bilingue.py
```

Selecciona **Español** o **English** desde la barra lateral. La demostración utiliza cifras precalculadas de un ejercicio íntegramente sintético, sin conexión a puntos de venta, inventarios ni sistemas empresariales.

## Criterio de publicación

El repositorio separa los resultados agregados que pueden mostrarse públicamente de los datos técnicos del caso. No incluye información comercial de empresas reales. Los escenarios se documentan con sus supuestos y límites, sin atribuir resultados a una organización existente.

**Autor:** Carlos Segura | CS Intelligence
