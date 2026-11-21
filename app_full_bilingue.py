"""Four-module portfolio dashboard, Spanish and English.
Tablero de portafolio de cuatro módulos, español e inglés.
All source data are fictional. Todos los datos son ficticios.
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
SCENARIO = ROOT / "results_shelf_only"

st.set_page_config(page_title="Wholesale Management Cockpit | Control de rentabilidad", page_icon="📊", layout="wide")
lang = st.sidebar.radio("Idioma / Language", ["Español", "English"], horizontal=True)

def T(es, en):
    return es if lang == "Español" else en

def money(x):
    return f"MXN {x:,.0f}"

def percent(a, b):
    return f"{a / b:.1%}" if b else T("No disponible", "Not available")

required = {
    "data": [
        "dim_location", "dim_product", "fact_sales", "fact_demand",
        "fact_budget", "fact_operating_expense", "fact_traffic",
        "fact_inventory_snapshot", "fact_ticket", "fact_operations_monthly"
    ],
    "results_shelf_only": ["ticket_deltas"]
}
missing = [
    f"{folder}/{name}.csv"
    for folder, names in required.items()
    for name in names
    if not (ROOT / folder / f"{name}.csv").exists()
]
if missing:
    st.title(T("Panel gerencial: versión completa", "Management cockpit: complete edition"))
    st.warning(T(
        "El código de los cuatro módulos está preparado, pero falta cargar el conjunto de datos sintéticos del paquete v0.7. Esta aplicación no sustituye esos datos por estimaciones.",
        "The four-module code is prepared, but the synthetic v0.7 data bundle is not yet in the repository. This app does not replace those files with estimates."
    ))
    st.code("\n".join(missing), language="text")
    st.link_button(
        T("Abrir vista ejecutiva disponible", "Open the available executive preview"),
        "https://wholesale-profitability-optimization-uenabzltjvquoxm2k5yg2p.streamlit.app/"
    )
    st.stop()

@st.cache_data(show_spinner=False)
def read(name, folder="data"):
    return pd.read_csv(ROOT / folder / f"{name}.csv")

products = read("dim_product")[["sku", "product_name", "category"]]
locations = read("dim_location")
sales = read("fact_sales").merge(products, on="sku", how="left")
demand = read("fact_demand").merge(products, on="sku", how="left")
budget = read("fact_budget")
expenses = read("fact_operating_expense")
traffic = read("fact_traffic")
stock = read("fact_inventory_snapshot")
ops = read("fact_operations_monthly")
deltas = read("ticket_deltas", "results_shelf_only")

sales["date"] = pd.to_datetime(sales["date"])
demand["date"] = pd.to_datetime(demand["date"])
traffic["date"] = pd.to_datetime(traffic["date"])
stock["date"] = pd.to_datetime(stock["date"])
deltas["date"] = pd.to_datetime(deltas["date"])
for frame in [sales, demand, traffic, stock, deltas]:
    frame["month_key"] = frame["date"].dt.strftime("%Y-%m")
sales["gross_profit"] = sales["net_sales"] - sales["net_cogs"]
branches = locations.loc[locations["location_id"].astype(str).str.fullmatch(r"B\d+"), "location_id"].tolist()
categories = sorted(products["category"].dropna().unique())
months = sorted(sales["month_key"].unique())

st.title(T("Control de rentabilidad mayorista", "Wholesale Management Cockpit"))
st.caption(T(
    "Ejercicio cuantitativo con cuatro sucursales y un centro de distribución ficticios, año 2025",
    "Quantitative case with four fictional branches and one fictional distribution center, 2025"
))
st.info(T(
    "Los datos son enteramente sintéticos. Los presupuestos y gastos corresponden a sucursales completas y no se distribuyen por categoría.",
    "All data are synthetic. Budgets and expenses apply to entire branches and are not allocated to categories."
))

with st.sidebar:
    st.header(T("Alcance del análisis", "Analysis scope"))
    chosen_branches = st.multiselect(T("Sucursales", "Branches"), branches, default=branches)
    start, end = st.select_slider(
        T("Periodo", "Reporting period"), options=months,
        value=(months[0], months[-1])
    )
    chosen_categories = st.multiselect(T("Categorías", "Categories"), categories, default=categories)
    st.divider()
    st.subheader(T("Umbrales gerenciales", "Management thresholds"))
    sales_threshold = st.slider(T("Cumplimiento de presupuesto (%)", "Budget attainment (%)"), 80, 120, 100) / 100
    fill_threshold = st.slider(T("Nivel de surtido (%)", "Fill rate (%)"), 85, 100, 97) / 100
    st.caption(T(
        "Los umbrales sirven para identificar alertas. No son metas reales aprobadas por una empresa.",
        "These thresholds screen for exceptions. They are not real company-approved targets."
    ))

if not chosen_branches or not chosen_categories:
    st.info(T("Selecciona al menos una sucursal y una categoría.", "Select at least one branch and one category."))
    st.stop()

branch_scope = lambda x: x["location_id"].isin(chosen_branches) & x["month_key"].between(start, end)
s = sales.loc[branch_scope(sales) & sales["category"].isin(chosen_categories)].copy()
d = demand.loc[branch_scope(demand) & demand["category"].isin(chosen_categories)].copy()
b = budget.loc[branch_scope(budget)].copy()
e = expenses.loc[branch_scope(expenses)].copy()
v = traffic.loc[branch_scope(traffic)].copy()
stock_scope = stock.loc[branch_scope(stock) & stock["sku"].isin(products.loc[products["category"].isin(chosen_categories), "sku"])].copy()
all_categories = set(chosen_categories) == set(categories)
st.caption(T(
    f"Periodo: {start} a {end}. Sucursales: {len(chosen_branches)}. " +
    ("Cobertura completa de categorías." if all_categories else "Cobertura parcial por categoría."),
    f"Period: {start} to {end}. Branches: {len(chosen_branches)}. " +
    ("All categories." if all_categories else "Partial category scope.")
))

def chart(fig):
    fig.update_layout(margin=dict(l=10, r=10, t=45, b=15), height=400, legend_title_text="")
    st.plotly_chart(fig, use_container_width=True)

def cards(items):
    cs = st.columns(len(items))
    for col, (label, value) in zip(cs, items):
        col.metric(label, value)

module = st.radio(
    T("Módulo", "Module"),
    ["summary", "commercial", "inventory", "scenario"],
    format_func=lambda x: {
        "summary": T("Resumen ejecutivo", "Executive overview"),
        "commercial": T("Desempeño comercial", "Commercial performance"),
        "inventory": T("Inventario y disponibilidad", "Inventory and availability"),
        "scenario": T("Laboratorio de escenarios", "Scenario lab"),
    }[x],
    horizontal=True
)

if module == "summary":
    revenue = s["net_sales"].sum()
    gp = s["gross_profit"].sum()
    expense = e["amount"].sum()
    cards([
        (T("Ventas netas", "Net sales"), money(revenue)),
        (T("Margen bruto", "Gross margin"), percent(gp, revenue)),
        (T("Contribución operativa", "Operating contribution"), money(gp-expense) if all_categories else T("No comparable", "Not comparable")),
        (T("Ventas contra presupuesto", "Sales against budget"), percent(revenue, b["sales_budget"].sum()) if all_categories else T("No comparable", "Not comparable")),
    ])
    monthly = s.groupby("month_key", as_index=False).agg(net_sales=("net_sales", "sum"), gross_profit=("gross_profit", "sum"))
    chart(px.line(monthly, x="month_key", y=["net_sales", "gross_profit"], markers=True,
                  title=T("Ventas y utilidad bruta por mes", "Monthly sales and gross profit")))
    branch = s.groupby("location_id", as_index=False).agg(net_sales=("net_sales", "sum"), gross_profit=("gross_profit", "sum"))
    if all_categories:
        costs = e.groupby("location_id", as_index=False)["amount"].sum()
        branch = branch.merge(costs, on="location_id", how="left")
        branch["contribution"] = branch["gross_profit"] - branch["amount"]
        chart(px.bar(branch, x="location_id", y=["net_sales", "gross_profit", "contribution"],
                     barmode="group", title=T("Comparativo financiero de sucursales", "Branch financial comparison")))
    else:
        chart(px.bar(branch, x="location_id", y=["net_sales", "gross_profit"],
                     barmode="group", title=T("Desempeño de las categorías seleccionadas", "Selected-category performance")))
        st.warning(T(
            "No se calcula contribución por categoría sin un criterio justificable de asignación de gastos.",
            "Category-level contribution is withheld because operating expenses cannot be allocated defensibly."
        ))
    st.subheader(T("Alertas de gestión", "Management alerts"))
    whole = sales.loc[branch_scope(sales)]
    whole_demand = demand.loc[branch_scope(demand)]
    alerts = []
    for br in chosen_branches:
        bs = whole.loc[whole["location_id"] == br]
        bd = whole_demand.loc[whole_demand["location_id"] == br]
        bb = b.loc[b["location_id"] == br]
        a = bs["net_sales"].sum() / bb["sales_budget"].sum() if bb["sales_budget"].sum() else float("nan")
        f = bd["units_fulfilled"].sum() / bd["units_requested"].sum() if bd["units_requested"].sum() else float("nan")
        if pd.notna(a) and a < sales_threshold:
            alerts.append((br, T("Ventas bajo presupuesto", "Sales below budget"), f"{a:.1%}", f"{sales_threshold:.0%}"))
        if pd.notna(f) and f < fill_threshold:
            alerts.append((br, T("Surtido bajo meta", "Fill rate below target"), f"{f:.1%}", f"{fill_threshold:.0%}"))
    if alerts:
        st.dataframe(pd.DataFrame(alerts, columns=[
            T("Sucursal", "Branch"), T("Indicador", "Indicator"),
            T("Resultado", "Actual"), T("Umbral", "Threshold")
        ]), hide_index=True, use_container_width=True)
    else:
        st.success(T("No se encontraron alertas con estos umbrales.", "No exceptions under these thresholds."))
    st.caption(T(
        "Las alertas utilizan ventas de todas las categorías para evitar comparar ventas parciales con presupuestos de sucursal.",
        "Signals use all-category sales so partial category totals are never compared against entire-branch budgets."
    ))
    o = ops.loc[branch_scope(ops)]
    if len(o):
        st.subheader(T("Disciplina operativa", "Operational discipline"))
        cards([
            (T("Capacitación completada", "Training completed"), f"{o['training_completion_rate'].mean():.1%}"),
            (T("Mantenimiento completado", "Maintenance completed"), percent(o["maintenance_tasks_completed"].sum(), o["maintenance_tasks_due"].sum())),
            (T("Acciones de auditoría cerradas", "Audit actions closed"), percent(o["audit_actions_closed"].sum(), o["audit_actions_due"].sum()))
        ])

elif module == "commercial":
    revenue = s["net_sales"].sum()
    gross = s["gross_profit"].sum()
    n_tickets = s["ticket_id"].nunique()
    visits = v["visits"].sum()
    cards([
        (T("Ventas del alcance seleccionado", "Selected-scope sales"), money(revenue)),
        (T("Gasto por ticket con producto seleccionado", "Spend per ticket containing selected items"), money(revenue/n_tickets) if n_tickets else T("Sin datos", "No data")),
        (T("Conversión general de sucursales", "Branch-wide conversion"), percent(v["purchasing_visits"].sum(), visits)),
        (T("Margen bruto seleccionado", "Selected gross margin"), percent(gross, revenue))
    ])
    st.caption(T(
        "El gasto por ticket usa solo los productos seleccionados. La conversión utiliza el tráfico completo de la sucursal. Los denominadores son distintos.",
        "Spend per ticket counts only selected items. Conversion uses full-branch footfall. These measures have different denominators."
    ))
    by_cat = s.groupby("category", as_index=False).agg(net_sales=("net_sales", "sum"))
    chart(px.bar(by_cat.sort_values("net_sales"), x="net_sales", y="category", orientation="h",
                 title=T("Ventas por categoría", "Sales by category")))
    by_sku = s.groupby(["sku", "product_name", "category"], as_index=False).agg(
        net_sales=("net_sales", "sum"), gross_profit=("gross_profit", "sum"), units=("units", "sum"))
    by_sku["gross_margin_pct"] = by_sku["gross_profit"] / by_sku["net_sales"].replace(0, float("nan"))
    st.subheader(T("Detalle por producto", "Product-level performance"))
    st.dataframe(by_sku.sort_values("net_sales", ascending=False), use_container_width=True, hide_index=True)

elif module == "inventory":
    requested = d["units_requested"].sum()
    fulfilled = d["units_fulfilled"].sum()
    missing_units = d["units_unfulfilled"].sum()
    closing_date = stock_scope["date"].max()
    closing = stock_scope.loc[stock_scope["date"] == closing_date]
    cards([
        (T("Nivel de surtido", "Demand fill rate"), percent(fulfilled, requested)),
        (T("Unidades no surtidas", "Unfulfilled units"), f"{missing_units:,.0f}"),
        (T("Valor del inventario al cierre", "Closing inventory value"), money(closing["closing_inventory_value"].sum())),
        (T("Unidades en inventario al cierre", "Closing inventory units"), f"{closing['closing_units'].sum():,.0f}")
    ])
    causes = d.loc[d["units_unfulfilled"] > 0].groupby("shortage_reason", as_index=False)["units_unfulfilled"].sum()
    if len(causes):
        chart(px.bar(causes, x="shortage_reason", y="units_unfulfilled",
                     title=T("Demanda no surtida por motivo registrado", "Unfulfilled demand by recorded reason")))
    months_d = d.groupby("month_key", as_index=False).agg(
        requested=("units_requested", "sum"), fulfilled=("units_fulfilled", "sum"))
    months_d["fill_rate"] = months_d["fulfilled"] / months_d["requested"]
    chart(px.line(months_d, x="month_key", y="fill_rate", markers=True,
                  title=T("Nivel de surtido mensual", "Monthly demand fill rate")))
    st.caption(T(
        "El inventario es una fotografía de cierre diario. No mide disponibilidad intradía. El centro de distribución queda fuera del valor de existencias de sucursales.",
        "Inventory is an end-of-day snapshot, not intraday availability. The distribution center is excluded from branch closing balances."
    ))

else:
    st.warning(T(
        "Análisis de sensibilidad económica con resultados precalculados. Los controles no ejecutan una nueva simulación logística.",
        "Economic sensitivity using precomputed results. The controls do not run a new logistics simulation."
    ))
    scenario = deltas.loc[branch_scope(deltas) & deltas["sku"].isin(
        products.loc[products["category"].isin(chosen_categories), "sku"])].copy()
    if scenario.empty:
        st.info(T("No hay observaciones para este alcance.", "No scenario observations for this scope."))
        st.stop()
    recovered = scenario.loc[scenario["delta_units"] > 0, "delta_units"].sum()
    displaced = -scenario.loc[scenario["delta_units"] < 0, "delta_units"].sum()
    full_scope = (
        set(chosen_branches) == set(branches) and start == months[0] and
        end == months[-1] and all_categories
    )
    gross_reference = 166128.79 if full_scope else scenario["incremental_gross_profit"].sum()
    handling = scenario["incremental_handling_cost"].sum()
    factor = st.slider(T("Factor de realización del margen (%)", "Gross profit realization factor (%)"), 0, 100, 100) / 100
    unit_cost = st.slider(T("Costo adicional por unidad recuperada (MXN)", "Additional cost per recovered unit (MXN)"), 0.0, 100.0, 0.0)
    fixed_cost = st.number_input(T("Costo fijo adicional (MXN)", "Additional fixed cost (MXN)"), min_value=0.0, value=0.0, step=1000.0)
    result = gross_reference * factor - handling - unit_cost * recovered - fixed_cost
    cards([
        (T("Unidades recuperadas", "Recovered units"), f"{recovered:,.0f}"),
        (T("Unidades desplazadas", "Displaced units"), f"{displaced:,.0f}"),
        (T("Unidades netas", "Net units"), f"{recovered-displaced:,.0f}"),
        (T("Contribución incremental ilustrativa", "Illustrative incremental contribution"), money(result))
    ])
    if full_scope:
        st.success(T(
            "Alcance anual completo: ventas incrementales de MXN 539,708.11, costo de venta incremental de MXN 373,579.32 y manejo de MXN 67,621.34. Contribución base: MXN 98,507.45 antes de costos no modelados.",
            "Full-year scope: MXN 539,708.11 additional sales, MXN 373,579.32 additional cost of goods sold, and MXN 67,621.34 handling. Base contribution: MXN 98,507.45 before unmodeled costs."
        ))
    else:
        st.info(T(
            "El resultado filtrado es una aproximación por transacciones. No dispone de una conciliación independiente del costo de venta para este subconjunto.",
            "The filtered result is a transaction-level proxy. It has no independent cost-of-goods-sold reconciliation for this subset."
        ))
    st.caption(T(
        "No representa una ganancia observada ni un pronóstico. Los costos adicionales pueden volver negativa la contribución.",
        "This is not observed profit or a forecast. Additional costs may make the contribution negative."
    ))

st.divider()
st.caption(T(
    "Caso técnico con datos ficticios. Sin afiliación con Casa Santos Lugo ni otra empresa. Sin conexión con un sistema de ventas en tiempo real.",
    "Technical case using fictional data. Not affiliated with Casa Santos Lugo or any other business. No live point-of-sale connection."
))
