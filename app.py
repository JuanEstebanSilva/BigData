import os
import pandas as pd
import streamlit as st
import plotly.express as px

# Configuración de página
st.set_page_config(
    page_title="Monitor de Tarifas · APIs de IA",
    page_icon="📊",
    layout="wide"
)

# Carga de datos con cache
@st.cache_data
def cargar_datos():
    rutas = [
        "ai_models_limpio.csv.gz",
        "ai_models_limpio.csv",
        os.path.join("ai-models-and-api-pricing-2026-price-history", "ai_model_price_history.csv"),
        "ai_model_price_history.csv"
    ]
    for r in rutas:
        if os.path.exists(r):
            df = pd.read_csv(r)
            if "week_start" in df.columns:
                df["week_start"] = pd.to_datetime(df["week_start"])
            df = df.dropna(subset=["input_price_per_1m_tokens", "output_price_per_1m_tokens"])
            return df
    return None

df = cargar_datos()

if df is None:
    st.error("No se encontró el archivo de datos. Verifica la ubicación del dataset.")
    st.stop()

VARIABLES_NUM = [
    "input_price_per_1m_tokens",
    "output_price_per_1m_tokens",
    "max_input_tokens"
]
for col_extra in ["ratio_precio_salida_entrada", "costo_contexto_maximo", "diferencia_precio_tokens"]:
    if col_extra in df.columns:
        VARIABLES_NUM.append(col_extra)

# ---------- Barra lateral: Filtros ----------
st.sidebar.header("Filtros de Análisis")
proveedores_unicos = sorted(df["provider"].dropna().unique().tolist())
top_default = ["openai", "meta", "anthropic", "google", "deepinfra", "azure_ai"]
seleccion_prov = [p for p in top_default if p in proveedores_unicos]

prov_filtro = st.sidebar.multiselect(
    "Proveedor:",
    options=proveedores_unicos,
    default=seleccion_prov if seleccion_prov else proveedores_unicos[:5],
    placeholder="Todos"
)

modalidades = sorted(df["mode"].dropna().unique().tolist())
modo_filtro = st.sidebar.multiselect(
    "Modalidad:",
    options=modalidades,
    default=modalidades,
    placeholder="Todas"
)

metodo_corr = st.sidebar.radio("Método de correlación", ["pearson", "spearman"])

# Filtrado dinámico
datos = df.copy()
if prov_filtro:
    datos = datos[datos["provider"].isin(prov_filtro)]
if modo_filtro:
    datos = datos[datos["mode"].isin(modo_filtro)]

st.title("📊 Monitor de Tarifas de APIs de Modelos de IA (2023–2026)")
st.caption("Proyecto Integrador de Big Data · Universidad Santo Tomás Seccional Tunja")

if len(datos) < 10:
    st.warning("Hay muy pocos datos con estos filtros. Amplía la selección en la barra lateral.")
    st.stop()

# ---------- Indicadores Principales (KPIs) ----------
st.markdown("---")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
mediana_in = datos["input_price_per_1m_tokens"].median()
mediana_out = datos["output_price_per_1m_tokens"].median()
ratio_med = (mediana_out / mediana_in) if mediana_in > 0 else 0
corr_io = datos["input_price_per_1m_tokens"].corr(datos["output_price_per_1m_tokens"], method=metodo_corr)

kpi1.metric("💵 Precio Entrada Mediano", f"${mediana_in:.2f} USD", help="Por 1M de tokens de entrada")
kpi2.metric("📝 Precio Salida Mediano", f"${mediana_out:.2f} USD", help="Por 1M de tokens de salida")
kpi3.metric("⚖️ Ratio Salida / Entrada", f"{ratio_med:.2f}x", help="Multiplicador de sobrecosto de generar vs leer")
kpi4.metric(f"📈 Correlación ({metodo_corr.capitalize()})", f"{corr_io:.2f}", help="Correlación entre precio de entrada y salida")
st.markdown("---")

# ---------- Pestañas de Visualización ----------
tab1, tab2, tab3, tab4 = st.tabs([
    "Matriz de Correlación",
    "Evolución y Disparidad Multicloud",
    "Explorar Variables por Tramos",
    "Calculadora de Presupuesto"
])

with tab1:
    col_c1, col_c2 = st.columns([1.2, 1])
    with col_c1:
        corr_matrix = datos[VARIABLES_NUM].corr(method=metodo_corr).round(2)
        fig_matriz = px.imshow(
            corr_matrix,
            text_auto=True,
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1,
            title=f"Matriz de Correlación ({metodo_corr.capitalize()})"
        )
        fig_matriz.update_layout(height=480, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_matriz, use_container_width=True)
    with col_c2:
        con_salida = corr_matrix["output_price_per_1m_tokens"].drop("output_price_per_1m_tokens").sort_values()
        fig_bar_corr = px.bar(
            con_salida,
            orientation="h",
            title="Correlación con el Precio de Salida",
            labels={"value": f"Correlación ({metodo_corr})", "index": "Variable"},
            color=con_salida.values,
            color_continuous_scale="Blues"
        )
        fig_bar_corr.update_layout(height=480, showlegend=False, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_bar_corr, use_container_width=True)

with tab2:
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("1. Evolución Temporal de Tarifas (Deflación)")
        if "week_start" in datos.columns and "developer" in datos.columns:
            serie_tiempo = datos.groupby(["week_start", "developer"], observed=True)["input_price_per_1m_tokens"].median().reset_index()
            fig_linea = px.line(
                serie_tiempo,
                x="week_start",
                y="input_price_per_1m_tokens",
                color="developer",
                labels={"week_start": "Fecha", "input_price_per_1m_tokens": "USD / 1M Tokens Entrada"},
                title="Precio Mediano por Semana según Desarrollador"
            )
            fig_linea.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_linea, use_container_width=True)
        else:
            st.info("Columna temporal no disponible en el subconjunto.")

    with col_g2:
        st.subheader("2. Comparativa Multicloud (Meta Llama 3)")
        df_llama = df[df["model_name"].str.contains("llama-3", case=False, na=False)] if "model_name" in df.columns else df
        llama_stats = df_llama.groupby("provider")["input_price_per_1m_tokens"].agg(["mean", "count"]).reset_index()
        llama_stats = llama_stats[llama_stats["count"] >= 15].sort_values("mean")
        fig_barras = px.bar(
            llama_stats,
            x="provider",
            y="mean",
            labels={"provider": "Proveedor de Nube", "mean": "Precio Promedio Entrada (USD)"},
            title="Diferencia de Tarifa para el Mismo Modelo (Meta Llama 3)",
            color="mean",
            color_continuous_scale="Blues"
        )
        fig_barras.update_layout(height=400, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_barras, use_container_width=True)

with tab3:
    st.subheader("Distribución de Precios por Tramos (Cuantiles)")
    var_analizar = st.selectbox(
        "Variable a explorar por tramos:",
        [v for v in VARIABLES_NUM if v != "output_price_per_1m_tokens"]
    )
    serie_var = datos[var_analizar].dropna()
    if len(serie_var) > 10:
        tramos = pd.qcut(datos[var_analizar], q=5, duplicates="drop")
        if len(tramos.cat.categories) < 3:
            tramos = pd.cut(datos[var_analizar], bins=5)
        resumen_tramos = datos.groupby(tramos, observed=True).agg(
            modelos=("output_price_per_1m_tokens", "count"),
            precio_salida_mediano=("output_price_per_1m_tokens", "median")
        ).reset_index()
        resumen_tramos[var_analizar] = resumen_tramos[var_analizar].astype(str)
        fig_tramos = px.bar(
            resumen_tramos,
            x=var_analizar,
            y="precio_salida_mediano",
            text="precio_salida_mediano",
            labels={var_analizar: f"Rango de {var_analizar}", "precio_salida_mediano": "Precio Mediano Salida (USD)"},
            title=f"Precio Mediano de Salida según tramos de {var_analizar}",
            color="precio_salida_mediano",
            color_continuous_scale="Blues"
        )
        fig_tramos.update_traces(texttemplate="$%{text:.2f}", textposition="outside")
        fig_tramos.update_layout(height=420)
        st.plotly_chart(fig_tramos, use_container_width=True)

with tab4:
    st.subheader("💡 Calculadora Rápida de Presupuesto Empresarial")
    calc_c1, calc_c2 = st.columns(2)
    with calc_c1:
        vol_consultas = st.slider("Consultas mensuales estimadas:", min_value=1000, max_value=500000, value=50000, step=5000)
        tokens_in = st.number_input("Tokens promedio de entrada por consulta:", value=1000, step=100)
        tokens_out = st.number_input("Tokens promedio de salida por consulta:", value=500, step=50)
    with calc_c2:
        costo_est_barato = (vol_consultas * (tokens_in * 0.15 + tokens_out * 0.60)) / 1_000_000
        costo_est_caro = (vol_consultas * (tokens_in * 3.00 + tokens_out * 15.00)) / 1_000_000
        ahorro = costo_est_caro - costo_est_barato
        pct_ahorro = (ahorro / costo_est_caro * 100) if costo_est_caro > 0 else 0
        st.write(f"• Costo mensual con proveedores económicos (DeepInfra/Groq): **${costo_est_barato:.2f} USD**")
        st.write(f"• Costo mensual con proveedores corporativos tradicionales: **${costo_est_caro:.2f} USD**")
        st.success(f"Ahorro potencial estimado: **${ahorro:.2f} USD al mes ({pct_ahorro:.1f}%)**")

# ---------- Inspección y Descarga de Datos ----------
st.markdown("---")
with st.expander("🔍 Explorar Datos Filtrados"):
    st.dataframe(datos.head(500), use_container_width=True)
    st.download_button(
        "📥 Descargar CSV Filtrado",
        datos.to_csv(index=False).encode("utf-8"),
        file_name="ai_models_filtrado.csv",
        mime="text/csv"
    )
