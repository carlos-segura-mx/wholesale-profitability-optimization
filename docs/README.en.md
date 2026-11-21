# Wholesale Profitability Optimization

[Español](README.es.md) | [Live dashboard](https://wholesale-profitability-optimization-uenabzltjvquoxm2k5yg2p.streamlit.app/) | [Source code](../)

## The starting point

More sales do not always mean more profit. A wholesaler can sell products at a healthy margin and still lose opportunities when stock is unavailable. Replenishing inventory may recover sales, but it also adds costs and can shift demand away from other purchases.

I built this case to look at those trade-offs quantitatively rather than treating each KPI in isolation. The main question is how much value better product availability can create once operating costs and displacement of existing sales are taken into account.

## How I approached it

I modeled a wholesale operation with four branches, one distribution center, 120 products and a full year of transactions. All data are synthetic and represent 2025.

The analysis brings together sales, cost of goods sold, margins, budgets, requested and fulfilled demand, inventory and operating expenses. I then developed a shelf-replenishment scenario and examined its financial contribution.

The dashboard covers four areas: executive performance, commercial results, inventory and availability, and scenario analysis.

## What the model shows

In this exercise, net sales total approximately **MXN 54.42 million**, with a **33.3% gross margin** and a **94.90% demand fill rate**.

The replenishment scenario recovers **4,004 units** but also displaces **2,525 units** from other sales. That leaves **1,479 additional net units**.

After the handling costs included in the model, estimated full-year incremental contribution comes to **MXN 98,507.45**, before costs that the model does not capture.

That distinction matters. Recovering sales does not mean all of those sales become profit. Changes in realization assumptions, handling costs or additional expenses change the outcome. Under some conditions, the estimated contribution turns negative.

## Explore the dashboard

[**Open the Streamlit app**](https://wholesale-profitability-optimization-uenabzltjvquoxm2k5yg2p.streamlit.app/)

The published version lets you compare branches, adjust alert thresholds and explore scenario sensitivity. It is an executive view based on aggregated annual figures.

The four-module dashboard code is also available in this repository, but the detailed version still needs its data files and cloud testing. I would rather make that distinction clear than describe a partial view as a finished release.

## Scope and limitations

This is a portfolio case built entirely on synthetic data. It does not describe the operations or results of an actual business. The simulation helps examine management decisions and accounting relationships; it does not demonstrate realized savings or causal impact.

The financial reconciliation covers the full network and year. Filtered scenario views are approximations and do not have the same independent reconciliation.

## Tools and local setup

I used Python, pandas, Plotly and Streamlit. To run the available dashboard:

```bash
python -m pip install -r requirements.txt
streamlit run preview.py
```

The app supports Spanish and English. Instructions for deploying the full version are in the separate [technical notes](DEPLOY.en.md).

**Carlos Segura** | CS Intelligence
