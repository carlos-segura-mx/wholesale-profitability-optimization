"""Bilingual executive preview of a fictional wholesale business.
Vista ejecutiva bilingue de una distribuidora ficticia.
"""
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Wholesale Profitability | Rentabilidad mayorista",page_icon="📊",layout="wide")
lang=st.sidebar.radio("Idioma / Language",["Español","English"],horizontal=True)
def L(es,en):
    return es if lang=="Español" else en

st.title(L("Optimización de rentabilidad mayorista","Wholesale Profitability Optimization"))
st.caption(L(
    "Carlos Segura | Vista ejecutiva | Modelo sintético de 2025",
    "Carlos Segura | Executive view | Synthetic 2025 model"
))
st.caption(L(
    "Vista ejecutiva con cifras anuales por sucursal. El detalle de productos e inventario forma parte de la versión completa.",
    "Executive view with annual branch figures. Product and inventory details are part of the full version."
))

rows=[
("B1",12358385.84,8252533.43,31134,29708,11976374.13,887760),
("B2",12971236.25,8655052.97,32796,31212,12877821.63,924750),
("B3",14157888.95,9427360.28,35634,33739,13779269.15,961740),
("B4",14927631.73,9967517.18,37831,35726,14680716.65,998730)]
df=pd.DataFrame(rows,columns=["Sucursal","Ventas netas","Costo de venta","Unidades solicitadas","Unidades surtidas","Presupuesto de ventas","Gasto operativo"])
df["Utilidad bruta"]=df["Ventas netas"]-df["Costo de venta"]
df["Contribución operativa"]=df["Utilidad bruta"]-df["Gasto operativo"]
df["Nivel de surtido"]=df["Unidades surtidas"]/df["Unidades solicitadas"]
df["Cumplimiento"]=df["Ventas netas"]/df["Presupuesto de ventas"]

with st.sidebar:
    st.header(L("Filtros ejecutivos","Executive filters"))
    branches=st.multiselect(L("Sucursales ficticias","Fictional branches"),df["Sucursal"].tolist(),default=df["Sucursal"].tolist())
    target=st.slider(L("Meta de cumplimiento de ventas (%)","Sales attainment target (%)"),80,120,100)
    fill=st.slider(L("Meta de nivel de surtido (%)","Demand fill-rate target (%)"),85,100,97)
    st.caption(L(
        "Las metas modifican las alertas, no los importes financieros precalculados.",
        "Targets affect screening alerts, not the precomputed financial figures."
    ))

selected=df[df["Sucursal"].isin(branches)]
if selected.empty:
    st.info(L("Selecciona al menos una sucursal.","Select at least one branch."))
    st.stop()

sales=selected["Ventas netas"].sum()
gp=selected["Utilidad bruta"].sum()
requested=selected["Unidades solicitadas"].sum()
fulfilled=selected["Unidades surtidas"].sum()
c1,c2,c3,c4=st.columns(4)
c1.metric(L("Ventas netas","Net sales"),f"MXN {sales/1e6:,.2f}M")
c2.metric(L("Margen bruto","Gross margin"),f"{gp/sales:.1%}")
c3.metric(L("Contribución operativa","Operating contribution"),f"MXN {selected['Contribución operativa'].sum()/1e6:,.2f}M")
c4.metric(L("Nivel de surtido","Demand fill rate"),f"{fulfilled/requested:.2%}")

tab1,tab2,tab3=st.tabs([
    L("Desempeño por sucursal","Branch performance"),
    L("Alertas de gestión","Management signals"),
    L("Sensibilidad del escenario","Scenario sensitivity")
])
with tab1:
    labels=["Ventas netas","Utilidad bruta","Contribución operativa"]
    en={"Ventas netas":"Net sales","Utilidad bruta":"Gross profit","Contribución operativa":"Operating contribution"}
    display=selected.rename(columns=en) if lang=="English" else selected
    fields=[en[x] for x in labels] if lang=="English" else labels
    fig=px.bar(display,x="Sucursal",y=fields,barmode="group",title=L(
        "Desempeño financiero anual de cuatro sucursales ficticias",
        "Annual financial performance of four fictional branches"
    ),labels={"Sucursal":L("Sucursal","Branch"),"value":L("MXN","MXN"),"variable":L("Indicador","Metric")})
    st.plotly_chart(fig,use_container_width=True)
    columns=["Sucursal","Ventas netas","Utilidad bruta","Contribución operativa","Cumplimiento","Nivel de surtido"]
    report=selected[columns].copy()
    if lang=="English":
        report=report.rename(columns={
            "Sucursal":"Branch","Ventas netas":"Net sales","Utilidad bruta":"Gross profit",
            "Contribución operativa":"Operating contribution","Cumplimiento":"Attainment",
            "Nivel de surtido":"Fill rate"})
    st.dataframe(report,hide_index=True,use_container_width=True)
    st.caption(L(
        "La contribución operativa es ventas menos costo de venta y gastos operativos simulados. No representa flujo de caja ni utilidad auditada.",
        "Operating contribution is sales less synthetic cost of goods sold and operating expenses. It is not cash flow or audited profit."
    ))

with tab2:
    alerts=[]
    for _,r in selected.iterrows():
        if r["Cumplimiento"]<target/100:
            alerts.append((r["Sucursal"],L("Ventas bajo la meta","Sales below target"),round(100*r["Cumplimiento"],2),target))
        if r["Nivel de surtido"]<fill/100:
            alerts.append((r["Sucursal"],L("Surtido bajo la meta","Fill rate below target"),round(100*r["Nivel de surtido"],2),fill))
    st.write(L(f"{len(alerts)} alertas según los umbrales seleccionados.",f"{len(alerts)} alerts under the selected thresholds."))
    if alerts:
        st.dataframe(pd.DataFrame(alerts,columns=[
            L("Sucursal","Branch"),L("Indicador","Indicator"),L("Valor observado (%)","Observed (%)"),
            L("Umbral (%)","Threshold (%)")
        ]),hide_index=True,use_container_width=True)
    else:
        st.success(L("Sin alertas para las sucursales seleccionadas.","No alerts for the selected branches."))
    st.caption(L(
        "Las alertas señalan diferencias frente a metas ajustables. No identifican causas ni cuantifican impactos causales.",
        "Alerts flag deviations from adjustable targets. They do not establish causes or quantify causal effects."
    ))

with tab3:
    st.info(L(
        "Escenario de reposición de anaquel, calculado para toda la red y todo 2025. Los filtros por sucursal no modifican este resultado.",
        "Shelf replenishment scenario for the full network and all of 2025. Branch filters do not change this result."
    ))
    realized=st.slider(L("Factor de realización de utilidad bruta (%)","Gross profit realization factor (%)"),0,100,100)/100
    extra=st.slider(L("Costo adicional por unidad recuperada (MXN)","Extra cost per recovered unit (MXN)"),0.0,100.0,0.0)
    fixed=st.number_input(L("Costo fijo adicional (MXN)","Additional fixed cost (MXN)"),min_value=0.0,value=0.0,step=1000.0)
    contribution=166128.79*realized-67621.34-4004*extra-fixed
    a,b,c=st.columns(3)
    a.metric(L("Unidades recuperadas","Recovered units"),"4,004")
    b.metric(L("Unidades desplazadas","Displaced units"),"2,525")
    c.metric(L("Contribución incremental ilustrativa","Illustrative incremental contribution"),f"MXN {contribution:,.2f}")
    st.caption(L(
        "Puente contable sintético: MXN 166,128.79 de utilidad bruta incremental menos MXN 67,621.34 de manejo, antes de costos adicionales. La contribución base es MXN 98,507.45. No equivale a un ahorro observado ni vuelve a simular inventarios.",
        "Synthetic accounting bridge: MXN 166,128.79 incremental gross profit less MXN 67,621.34 modeled handling, before additional costs. Base contribution is MXN 98,507.45. This is not observed savings and does not rerun inventory."
    ))
st.divider()
st.caption(L(
    "Datos sintéticos de 2025. Los escenarios dependen de los supuestos utilizados.",
    "Synthetic 2025 data. Scenario outcomes depend on the assumptions used."
))
