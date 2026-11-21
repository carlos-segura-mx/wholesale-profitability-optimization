# Wholesale Profitability Optimization — Management Cockpit

**Portfolio case · synthetic wholesale operations data · not affiliated with any real wholesaler**

A quantitative commercial analytics demonstration designed to support management decisions in sales, profitability, branch operations, inventory availability, and scenario sensitivity.

## Dashboard
The source package contains a four-module Streamlit application:

1. **Executive Overview:** branch KPIs, sales versus budget, operating contribution, and management threshold alerts.
2. **Commercial Performance:** category and SKU sales, gross margin, ticket and traffic measures.
3. **Inventory & Availability:** demand fill rate, unfulfilled demand, closing inventory, and operational diagnostics.
4. **Scenario Lab:** shelf-replenishment counterfactuals with explicit additional-cost and realization assumptions.

**Publication status (2026-11-21):** An interactive **aggregated synthetic executive preview** is committed as [`preview.py`](preview.py). It contains reconciled annual branch-level financial and fill-rate aggregates and whole-network scenario sensitivity; it does **not** replace the complete four-module dashboard. The original `app.py`, `monitoring.py`, and CSV data are available in the separately archived dashboard package and have not been uploaded to this repo. **The lightweight online preview has been launched and visually confirmed by the project owner in a browser screenshot (2026-11-21); interactive end-to-end QA is pending.**

## Analytical evidence and limitations

The model represents **four fictional branches, one fictional distribution center, 120 fictional SKUs, and 2025**. Baseline net sales in the synthetic case are approximately **MXN 54.42 million** and the demand fill rate approximately **94.90%**.

The shelf-only counterfactual produces **4,004 recovered units**, **2,525 displaced units**, and **1,479 net additional units**. Its whole-network common-engine accounting bridge yields an illustrative incremental contribution of **MXN 98,507.45 before unmodeled costs**. This is **not audited profit, observed savings, a causal estimate, or a live business forecast**. Filtered scenario views rely on ticket-level proxies and do not inherit the full-network accounting reconciliation.

There are no authentic transactions, prices, customers, inventory records, or internal datasets from Casa Santos Lugo or any other business.

## Live executive preview

[Open the live Streamlit executive preview](https://wholesale-profitability-optimization-uenabzltjvquoxm2k5yg2p.streamlit.app/)

This link points to the aggregated, synthetic `preview.py`, not to the complete four-module application. The screenshot confirmed initial page load and executive metrics; it has not yet demonstrated all filtering and scenario interactions.

## Reproduce the executive preview

Run locally:

```bash
python -m pip install -r requirements.txt
streamlit run preview.py
```

Deploy on [Streamlit Community Cloud](https://share.streamlit.io/) using this GitHub repository, branch `main`, and entrypoint `preview.py`. Once the full package is uploaded and tested, switch to `app.py` only after its data dependencies are present. The live preview URL is linked above. A separate full Management Cockpit release requires uploading and validating its dependencies.

## Provenance and scope

- Synthetic dataset generated solely for portfolio demonstration.
- No production integrations or scheduled data refresh.
- Indicators and scenario sensitivities require real-world validation before operational use.
- The executive 90-day action plan is separate from the dashboard.
- This repository does not grant a code license unless one is explicitly added later.

**Author:** Carlos Segura · CS Intelligence · Data · Analysis · Decisions
