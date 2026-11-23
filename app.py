# Mini-app de datos · APIs de IA: ¿Qué determina el costo de una API de IA?
# Ejecutar en local: streamlit run app.py
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="APIs de IA · Monitor de Costos",
    page_icon="🤖",
    layout="wide"
)

@st.cache_data
def cargar_datos():
    return pd.read_csv("ai_models_limpio.csv.gz")

df = cargar_datos()

VARIABLES = [
    "input_price_per_1m_tokens",
    "output_price_per_1m_tokens",
    "max_input_tokens",
    "ratio_precio_salida_entrada"
]

# ---------- Barra lateral: filtros ----------
st.sidebar.header("Filtros")
proveedores = st.sidebar.multiselect(
    "Proveedor de nube",
    sorted(df["provider"].dropna().unique()),
    placeholder="Todos"
)
modalidades = st.sidebar.multiselect(
    "Modalidad del modelo",
    sorted(df["mode"].dropna().unique()),
    placeholder="Todas"
)
metodo = st.sidebar.radio("Método de correlación", ["pearson", "spearman"])

datos = df.copy()
if proveedores:
    datos = datos[datos["provider"].isin(proveedores)]
if modalidades:
    datos = datos[datos["mode"].isin(modalidades)]

st.title("🤖 ¿Qué determina el costo de una API de IA?")
st.caption("Tarifas y arbitraje multicloud en 147.000 modelos (2023–2026). Deje los filtros vacíos para ver todo.")

if len(datos) < 30:
    st.warning("Hay muy pocos datos con estos filtros. Amplíe la selección.")
    st.stop()

# ---------- Indicadores ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Modelos / Obs.", f"{len(datos):,}".replace(",", "."))
c2.metric("Precio Entrada Mediano", f"${datos['input_price_per_1m_tokens'].median():.2f} USD")
c3.metric("Precio Salida Mediano", f"${datos['output_price_per_1m_tokens'].median():.2f} USD")
r = datos["input_price_per_1m_tokens"].corr(datos["output_price_per_1m_tokens"], method=metodo)
c4.metric(f"Correlación ({metodo})", f"{r:.2f}")

# ---------- Pestañas ----------
tab1, tab2, tab3 = st.tabs(["Matriz de correlación", "Proveedor y modalidad", "Explorar una variable"])

with tab1:
    cols_corr = [c for c in VARIABLES if c in datos.columns]
    corr = datos[cols_corr].corr(method=metodo).round(2)
    fig = px.imshow(
        corr,
        text_auto=True,
        color_continuous_scale="Blues",
        zmin=-1,
        zmax=1,
        title=f"Matriz de correlación ({metodo.capitalize()})"
    )
    fig.update_layout(height=550)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    izq, der = st.columns(2)
    # 1. Tarifa de salida por proveedor (igual a Power BI)
    top_prov = datos.groupby("provider")["output_price_per_1m_tokens"].median().sort_values(ascending=True).tail(12).reset_index()
    fig_prov = px.bar(
        top_prov,
        x="output_price_per_1m_tokens",
        y="provider",
        orientation="h",
        text_auto=".2f",
        color_discrete_sequence=["#1b5e20"],
        labels={"provider": "Proveedor", "output_price_per_1m_tokens": "Tarifa Mediana Salida (USD/1M)"},
        title="Tarifa de Salida Mediana por Proveedor (USD)"
    )
    fig_prov.update_layout(height=480)
    izq.plotly_chart(fig_prov, use_container_width=True)

    # 2. Tarifa según modalidad (igual a Power BI)
    modos = datos.groupby("mode")["output_price_per_1m_tokens"].median().sort_values(ascending=False).reset_index()
    fig_mod = px.bar(
        modos,
        x="mode",
        y="output_price_per_1m_tokens",
        text_auto=".2f",
        color_discrete_sequence=["#581845"],
        labels={"mode": "Modalidad", "output_price_per_1m_tokens": "Tarifa Mediana Salida (USD/1M)"},
        title="Tarifa Mediana según Modalidad (USD)"
    )
    fig_mod.update_layout(height=480)
    der.plotly_chart(fig_mod, use_container_width=True)
    st.info("Observe la disparidad: los modelos de chat y completion concentran el costo de salida, mientras que el proveedor genera variaciones de hasta 5x para el mismo servicio.")

with tab3:
    vars_disponibles = [v for v in VARIABLES if v != "output_price_per_1m_tokens"]
    x = st.selectbox("Variable a comparar frente al precio de salida", vars_disponibles)
    tramos = pd.qcut(datos[x], q=5, duplicates="drop")
    if len(tramos.cat.categories) < 3:
        tramos = pd.cut(datos[x], bins=5)
    resumen = datos.groupby(tramos, observed=True).agg(
        modelos=("output_price_per_1m_tokens", "count"),
        salida_mediana=("output_price_per_1m_tokens", "median")
    ).reset_index()
    resumen[x] = resumen[x].astype(str)
    fig_tramos = px.bar(
        resumen,
        x=x,
        y="salida_mediana",
        text_auto=".2f",
        hover_data=["modelos"],
        color_discrete_sequence=["#104F8B"],
        labels={x: f"{x} (tramos)", "salida_mediana": "Precio Salida Mediano (USD)"},
        title=f"Precio de salida mediano según tramos de {x}"
    )
    fig_tramos.update_layout(height=480)
    st.plotly_chart(fig_tramos, use_container_width=True)

with st.expander("Ver los datos filtrados"):
    st.dataframe(datos.head(500))
    st.download_button(
        "Descargar CSV filtrado",
        datos.to_csv(index=False).encode("utf-8"),
        file_name="ai_models_filtrado.csv",
        mime="text/csv"
    )
