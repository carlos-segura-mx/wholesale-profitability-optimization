"""Lightweight public snapshot of PORT-01. Entirely synthetic data."""
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Wholesale Profitability | Executive Preview",page_icon="📊",layout="wide")
st.title("Wholesale Profitability Optimization")
st.caption("CS Intelligence · Interactive executive preview · 2025 · 100% synthetic · Not affiliated with a real wholesaler")
st.warning("This is an aggregated snapshot preview, not the full four-module Management Cockpit. Original transaction-level filtering, stock snapshots and operational simulation are not available in this preview.")

# Annual figures reconciled from the approved synthetic v0.7 model.
data=[
("B1",12358385.84,8252533.43,31134,29708,11976374.13,887760),
("B2",12971236.25,8655052.97,32796,31212,12877821.63,924750),
("B3",14157888.95,9427360.28,35634,33739,13779269.15,961740),
("B4",14927631.73,9967517.18,37831,35726,14680716.65,998730)]
df=pd.DataFrame(data,columns=["Branch","Net sales","COGS","Requested units","Fulfilled units","Sales budget","Operating expenses"])
df["Gross profit"]=df["Net sales"]-df["COGS"]
df["Operating contribution"]=df["Gross profit"]-df["Operating expenses"]
df["Fill rate"]=df["Fulfilled units"]/df["Requested units"]
df["Attainment"]=df["Net sales"]/df["Sales budget"]

with st.sidebar:
    st.header("Executive filters")
    choices=st.multiselect("Fictional branches",list(df.Branch),default=list(df.Branch))
    target=st.slider("Sales attainment target (%)",80,120,100)
    fill=st.slider("Fill-rate target (%)",85,100,97)
    st.caption("Changing targets changes screening alerts only; financial figures are precomputed synthetic annual totals.")
s=df[df.Branch.isin(choices)].copy()
if s.empty:
    st.info("Select at least one branch.")
    st.stop()
sales=s["Net sales"].sum()
gp=s["Gross profit"].sum()
requested=s["Requested units"].sum()
fulfilled=s["Fulfilled units"].sum()
c1,c2,c3,c4=st.columns(4)
c1.metric("Net sales",f"MXN {sales/1e6:,.2f}M")
c2.metric("Gross margin",f"{gp/sales:.1%}")
c3.metric("Operating contribution",f"MXN {s['Operating contribution'].sum()/1e6:,.2f}M")
c4.metric("Demand fill rate",f"{fulfilled/requested:.2%}")
tab1,tab2,tab3=st.tabs(["Branch performance","Management signals","Scenario sensitivity"])
with tab1:
    st.plotly_chart(px.bar(s,x="Branch",y=["Net sales","Gross profit","Operating contribution"],barmode="group",title="Synthetic annual financial performance"),use_container_width=True)
    st.dataframe(s[["Branch","Net sales","Gross profit","Operating contribution","Attainment","Fill rate"]],hide_index=True,use_container_width=True)
    st.caption("Operating contribution = net sales − synthetic cost of goods sold − modeled operating expenses. This is not cash flow or audited profit.")
with tab2:
    alerts=[]
    for r in s.itertuples(index=False):
        if r.Attainment < target/100: alerts.append((r.Branch,"Sales below budget target",round(r.Attainment*100,2),target))
        if getattr(r,"Fill_rate") < fill/100: alerts.append((r.Branch,"Fill rate below threshold",round(getattr(r,"Fill_rate")*100,2),fill))
    st.write(f"{len(alerts)} screening alert(s) under your targets.")
    if alerts: st.dataframe(pd.DataFrame(alerts,columns=["Branch","Signal","Observed %","Threshold %"]),hide_index=True,use_container_width=True)
    else: st.success("No selected branch breached these two thresholds.")
    st.caption("Screening only: alerts are not root-cause or financial-impact estimates.")
with tab3:
    st.info("The sensitivity below uses the approved **full-network, full-year** shelf-only counterfactual. It is intentionally NOT recalculated for branch filters.")
    realized=st.slider("Gross-profit realization",0,100,100)/100
    extra_per_unit=st.slider("Additional handling cost / recovered unit (MXN)",0.0,100.0,0.0)
    fixed=st.number_input("Additional fixed cost (MXN)",min_value=0.0,value=0.0,step=1000.0)
    contribution=166128.79*realized-67621.34-4004*extra_per_unit-fixed
    a,b,c=st.columns(3)
    a.metric("Recovered units","4,004")
    b.metric("Displaced units","2,525")
    c.metric("Illustrative incremental contribution",f"MXN {contribution:,.2f}")
    st.caption("Conditional synthetic accounting bridge: MXN 166,128.79 incremental gross profit, MXN 67,621.34 modeled handling before extra costs. Original baseline MXN 98,507.45. Excludes unmodeled costs, does not rerun inventory and is not observed savings.")
st.divider()
st.caption("Portfolio demonstration · Fictional branches and products · No company affiliation · No live ERP/POS feed · Full technical case available separately.")
