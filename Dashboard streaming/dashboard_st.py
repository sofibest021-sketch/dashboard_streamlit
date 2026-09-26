# -*- coding: utf-8 -*-
"""
Dashboard Pharmaandina S.A.S. - Produccion de medicamentos genericos
Curso: DataViz & BI - Semana 3 - Valerien Muñoz Munar
Como ejecutar:  streamlit run app.py
"""
from pathlib import Path

#Instalar librerias necesarias

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Dashboard Pharmaandina - Valerie Muñoz Munar",
    page_icon="💊",
    layout="wide",
)

CARPETA_DATOS = Path(__file__).parent / "data"

@st.cache_data
def cargar_datos():
    produccion = pd.read_excel(CARPETA_DATOS / "1_Produccion_Farmaceutica_2025_2026.xlsx")
    calidad = pd.read_excel(CARPETA_DATOS / "2_Control_Calidad_Lotes_2025_2026.xlsx")
    ventas = pd.read_excel(CARPETA_DATOS / "3_Ventas_Distribucion_2025_2026.xlsx")
    return produccion, calidad, ventas


produccion, calidad, ventas = cargar_datos()

def promedio_seguro(serie):
    """Calcula el promedio de una serie; si esta vacia devuelve 0."""
    return round(serie.mean(), 1) if len(serie) > 0 else 0


def formato_millones(valor):
    """Convierte un numero grande a texto tipo 1.735,7 millones."""
    return f"${valor / 1_000_000:,.1f} M COP"

def formato_miles(valor):
    return f"${valor / 1_000:,.0f} mil"

st.sidebar.header("🔎 Filtros")
st.sidebar.caption("Los filtros actualizan todo el dashboard")

lista_plantas = ["Todas"] + sorted(produccion["Planta"].unique().tolist())
planta_seleccionada = st.sidebar.selectbox("Planta de producción", lista_plantas)

lista_medicamentos = ["Todos"] + sorted(produccion["Medicamento"].unique().tolist())
medicamento_seleccionado = st.sidebar.selectbox("Medicamento", lista_medicamentos)

prod = produccion.copy()
cal = calidad.copy()
ven = ventas.copy()

if planta_seleccionada != "Todas":
    prod = prod[prod["Planta"] == planta_seleccionada]
    cal = cal[cal["Planta"] == planta_seleccionada]
    # Nota: la tabla de ventas no tiene columna Planta

if medicamento_seleccionado != "Todos":
    prod = prod[prod["Medicamento"] == medicamento_seleccionado]
    cal = cal[cal["Medicamento"] == medicamento_seleccionado]
    ven = ven[ven["Medicamento"] == medicamento_seleccionado]

st.title("💊 Tablero estratégico — Pharmaandina S.A.S.")
st.caption("Producción de medicamentos genéricos · Colombia · Enero 2025 – Agosto 2026")

unidades_producidas = prod["Unidades_Producidas"].sum()
pct_aprobados = promedio_seguro(100 * cal["Aprobado"]) if len(cal) > 0 else 0
costo_reproceso = cal["Costo_Reproceso_COP"].sum()
ingresos_totales = ven["Ingresos_COP"].sum()
margen_promedio = promedio_seguro(ven["Margen_Bruto_%"])

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("🏭 Unidades producidas", f"{unidades_producidas:,.0f}")
c2.metric("✅ Lotes aprobados", f"{pct_aprobados} %")
c3.metric("🔧 Costo de reproceso", formato_miles(costo_reproceso))
c4.metric("💰 Ingresos totales", formato_millones(ingresos_totales))
c5.metric("📈 Margen bruto prom.", f"{margen_promedio} %")

st.divider()

tab_prod, tab_cal, tab_ven, tab_int = st.tabs(
    ["🏭 Producción", "🔬 Calidad", "💰 Ventas", "🧭 Integración"]
)

# ------------------------------------------------------------
# PESTANA 1: PRODUCCION
# ------------------------------------------------------------
with tab_prod:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Evolución mensual de la producción")
        serie_mes = prod.groupby("Periodo", as_index=False)["Unidades_Producidas"].sum()
        fig = px.line(
            serie_mes, x="Periodo", y="Unidades_Producidas", markers=True,
            labels={"Unidades_Producidas": "Unidades", "Periodo": "Mes"},
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        st.subheader("Producción por planta")
        por_planta = prod.groupby("Planta", as_index=False)["Unidades_Producidas"].sum()
        fig = px.bar(
            por_planta, x="Planta", y="Unidades_Producidas", color="Planta",
            text_auto=".3s",
            labels={"Unidades_Producidas": "Unidades", "Planta": "Planta"},
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, width="stretch")

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Cumplimiento del plan por planta")
        cumplimiento = prod.groupby("Planta", as_index=False)["Cumplimiento_Plan_%"].mean()
        fig = px.bar(
            cumplimiento, x="Planta", y="Cumplimiento_Plan_%",
            text_auto=True,
            labels={"Cumplimiento_Plan_%": "% cumplimiento"},
        )
        fig.update_yaxes(range=[80, 100])
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, width="stretch")

    with col4:
        st.subheader("Top 10 medicamentos más producidos")
        top_prod = (
            prod.groupby("Medicamento", as_index=False)["Unidades_Producidas"].sum()
            .sort_values("Unidades_Producidas", ascending=False)
            .head(10)
        )
        fig = px.bar(
            top_prod, x="Unidades_Producidas", y="Medicamento", orientation="h",
            text_auto=".3s",
            labels={"Unidades_Producidas": "Unidades", "Medicamento": ""},
        ).update_yaxes(autorange="reversed")
        st.plotly_chart(fig, width="stretch")

# ------------------------------------------------------------
# PESTANA 2: CALIDAD
# ------------------------------------------------------------
with tab_cal:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Resultado de la inspección de lotes")
        conteo_resultado = cal["Resultado"].value_counts().reset_index()
        conteo_resultado.columns = ["Resultado", "Lotes"]
        fig = px.pie(
            conteo_resultado, names="Resultado", values="Lotes", hole=0.55,
            color="Resultado",
            color_discrete_map={"Aprobado": "#92b6f1", "Observaciones": "#baa2ee", "Rechazado": "#704fd3"},
        )
        st.plotly_chart(fig, width="stretch")
        
    with col2:
        st.subheader("Tasa de defecto promedio por planta")
        tasa_planta = cal.groupby("Planta", as_index=False)["Tasa_Defecto_%"].mean()
        fig = px.bar(
            tasa_planta, x="Planta", y="Tasa_Defecto_%", color="Planta", text_auto=True,
            labels={"Tasa_Defecto_%": "Tasa de defecto (%)"},
        )

        fig.update_traces(textposition="outside")

        st.plotly_chart(fig, width="stretch")

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Causas más frecuentes de defectos")
        defectos = cal[cal["Tipo_Defeccion"] != "Ninguna"]["Tipo_Defeccion"].value_counts().reset_index()
        defectos.columns = ["Tipo de defecto", "Lotes"]
        fig = px.bar(
            defectos, x="Lotes", y="Tipo de defecto", orientation="h", text_auto=True,
        ).update_yaxes(autorange="reversed")
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, width="stretch")

    with col4:
        st.subheader("Costo de reproceso por planta")
        reproceso_planta = cal.groupby("Planta", as_index=False)["Costo_Reproceso_COP"].sum()
        fig = px.bar(
            reproceso_planta, x="Planta", y="Costo_Reproceso_COP", color="Planta",
            text_auto=".3s",
            labels={"Costo_Reproceso_COP": "COP"},
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, width="stretch")

# ------------------------------------------------------------
# PESTANA 3: VENTAS
# ------------------------------------------------------------
with tab_ven:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Evolución mensual de los ingresos")
        serie_ventas = ven.groupby("Periodo", as_index=False)["Ingresos_COP"].sum()
        fig = px.line(
            serie_ventas, x="Periodo", y="Ingresos_COP", markers=True,
            labels={"Ingresos_COP": "Ingresos (COP)", "Periodo": "Mes"},
        )
        st.plotly_chart(fig, width="stretch")

    with col2:
        st.subheader("Ingresos por canal de distribución")
        por_canal = ven.groupby("Canal", as_index=False)["Ingresos_COP"].sum()
        fig = px.bar(
            por_canal, x="Canal", y="Ingresos_COP", color="Canal", text_auto=".3s",
            labels={"Ingresos_COP": "Ingresos (COP)", "Canal": ""},
        ).update_xaxes(tickangle=15)
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, width="stretch")

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Ingresos por ciudad")
        por_ciudad = ven.groupby("Ciudad", as_index=False)["Ingresos_COP"].sum()
        fig = px.bar(
            por_ciudad, x="Ciudad", y="Ingresos_COP", text_auto=".3s",
            labels={"Ingresos_COP": "Ingresos (COP)"},
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, width="stretch")

    with col4:
        st.subheader("Top 10 medicamentos por ingresos")
        top_ventas = (
            ven.groupby("Medicamento", as_index=False)["Ingresos_COP"].sum()
            .sort_values("Ingresos_COP", ascending=False)
            .head(10)
        )
        fig = px.bar(
            top_ventas, x="Ingresos_COP", y="Medicamento", orientation="h",
            text_auto=".3s",
            labels={"Ingresos_COP": "Ingresos (COP)", "Medicamento": ""},
        ).update_yaxes(autorange="reversed")
        st.plotly_chart(fig, width="stretch")
        fig.update_traces(textposition="outside")

# ------------------------------------------------------------
# PESTANA 4: INTEGRACION PRODUCCION vs VENTAS
# ------------------------------------------------------------
with tab_int:
    st.subheader("¿La producción está alineada con la demanda?")

    producido = prod.groupby("Medicamento", as_index=False)["Unidades_Producidas"].sum()
    vendido = ven.groupby("Medicamento", as_index=False)["Unidades_Vendidas"].sum()
    comparacion = producido.merge(vendido, on="Medicamento", how="outer").fillna(0)
    comparacion["Cobertura_%"] = (
        100 * comparacion["Unidades_Vendidas"] / comparacion["Unidades_Producidas"]
    ).round(1)

    top10 = comparacion.sort_values("Unidades_Vendidas", ascending=False).head(10)
    comparacion_larga = top10.melt(
        id_vars="Medicamento",
        value_vars=["Unidades_Producidas", "Unidades_Vendidas"],
        var_name="Concepto", value_name="Unidades",
    )

    fig = px.bar(
        comparacion_larga, x="Medicamento", y="Unidades", color="Concepto",
        barmode="group",
        color_discrete_map={"Unidades_Producidas": "#1f77b4", "Unidades_Vendidas": "#ff7f0e"},
    ).update_xaxes(tickangle=30)
    st.plotly_chart(fig, width="stretch")

    st.write("**Tabla: cobertura de demanda por medicamento** "
             "(% vendido respecto a lo producido; valores muy altos sugieren desabastecimiento, "
             "muy bajos sugieren sobreproducción)")
    st.dataframe(
        top10[["Medicamento", "Unidades_Producidas", "Unidades_Vendidas", "Cobertura_%"]],
        width="stretch",
        hide_index=True,
    )

    st.info(
        "🧭 **Cómo leer esta pestaña:** si un medicamento vende casi todo lo que produce "
        "(cobertura cercana o superior al 100 %), la empresa puede estar perdiendo ventas por falta de "
        "inventario. Si la cobertura es muy baja, hay producto acumulado que amarra capital de trabajo. "
        "Combine esta lectura con la pestaña de Calidad para decidir en qué planta invertir."
    )

# ------------------------------------------------------------
# PIE DE PAGINA
# ------------------------------------------------------------
st.divider()
st.caption(
    "Dashboard educativo · Curso DataViz & BI · Semana 2 · Datos sintéticos de la empresa "
    "ficticia Pharmaandina S.A.S."
)