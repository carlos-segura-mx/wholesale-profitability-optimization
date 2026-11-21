# Wholesale Profitability Optimization

**Portfolio case | CS Intelligence | November 2026**

This project looks at decisions a multi-branch wholesaler faces every day: protecting margins, meeting demand, managing inventory, and separating an operational improvement from a verified financial benefit.

The business, its four branches, distribution center, products, and transactions are fictional. No internal files from Casa Santos Lugo or any other business were used.

## Live demonstration

[Open the Streamlit app](https://wholesale-profitability-optimization-uenabzltjvquoxm2k5yg2p.streamlit.app/)

The public application currently provides an aggregated executive view, including branch KPIs, adjustable management alerts, and scenario sensitivity. The bilingual source is available in [preview_bilingue.py](../preview_bilingue.py). This shorter preview is not presented as the complete management cockpit.

The original technical case contains four modules:

1. Executive overview. Sales, margins, contribution, budgets, and management alerts.
2. Commercial performance. Categories, products, and branch comparisons.
3. Inventory and availability. Fulfilled demand, shortages, and stock balances.
4. Scenario lab. Shelf replenishment and additional-cost sensitivity.

Publishing all four modules at the original level of detail still requires integrating the full synthetic data files and testing the cloud application.

## Reference figures

In the synthetic 2025 dataset, net sales are approximately **MXN 54.42 million**, with a **94.90% demand fill rate**. The shelf replenishment intervention recovers 4,004 units, displaces 2,525, and produces 1,479 additional net units.

The model's full-year accounting bridge estimates **MXN 98,507.45 in incremental contribution before unmodeled costs**. This is not observed profit, a causal effect, or a commercial forecast. Filtered views do not carry the same accounting assurance as the full-year network result.

## Run the executive preview

```bash
python -m pip install -r requirements.txt
streamlit run preview_bilingue.py
```

Choose **Español** or **English** in the sidebar. The preview uses precomputed figures from a fully synthetic exercise. It has no live connection to a point of sale, inventory system, or ERP.

## Publication standards

This repository separates public aggregated results from the underlying technical case files. It does not contain commercial records from real companies. Scenario assumptions and limitations are made explicit, without attributing results to an existing organization.

**Author:** Carlos Segura | CS Intelligence
