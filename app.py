import os
import pandas as pd
import streamlit as st
import plotly.express as px

# Configuración de página
st.set_page_config(
    page_title="Dashboard Precios APIs IA",
    page_icon="📊",
    layout="wide"
)

# Título y encabezado
st.title("📊 Monitor de Tarifas de APIs de Modelos de IA (2023–2026)")
st.markdown("### Proyecto Integrador de Big Data · Universidad Santo Tomás Seccional Tunja")
st.markdown("Herramienta analítica interactiva para el seguimiento de costos de inferencia y arbitraje multicloud.")

# Carga de datos
@st.cache_data
def cargar_datos():
    posibles_rutas = [
        os.path.join("ai-models-and-api-pricing-2026-price-history", "ai_model_price_history.csv"),
        "ai_model_price_history.csv"
    ]
    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            df = pd.read_csv(ruta)
            df["week_start"] = pd.to_datetime(df["week_start"])
            df = df.dropna(subset=["input_price_per_1m_tokens", "output_price_per_1m_tokens"])
            return df
    return None

df = cargar_datos()

if df is None:
    st.error("No se encontró el archivo 'ai_model_price_history.csv'. Verifica la ruta del dataset.")
    st.stop()

# Barra lateral: Filtros interactivos
st.sidebar.header("⚙️ Filtros de Análisis")
proveedores_unicos = sorted(df["provider"].dropna().unique().tolist())
top_default = ["openai", "meta", "anthropic", "google", "deepinfra", "azure_ai"]
seleccion_prov = [p for p in top_default if p in proveedores_unicos]

prov_filtro = st.sidebar.multiselect(
    "Selecciona Proveedores:",
    options=proveedores_unicos,
    default=seleccion_prov if seleccion_prov else proveedores_unicos[:5]
)

modalidades = sorted(df["mode"].dropna().unique().tolist())
modo_filtro = st.sidebar.multiselect(
    "Modalidad del Modelo:",
    options=modalidades,
    default=modalidades
)

# Filtrado dinámico
df_filtrado = df[
    (df["provider"].isin(prov_filtro)) &
    (df["mode"].isin(modo_filtro))
]

# 1. Tarjetas de Indicadores Principales (KPIs)
st.markdown("---")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

mediana_in = df_filtrado["input_price_per_1m_tokens"].median()
mediana_out = df_filtrado["output_price_per_1m_tokens"].median()
ratio_med = (mediana_out / mediana_in) if mediana_in > 0 else 0
total_obs = len(df_filtrado)

kpi1.metric("💵 Precio Mediano Entrada", f"${mediana_in:.2f} USD", help="Por 1M de tokens de prompt")
kpi2.metric("📝 Precio Mediano Salida", f"${mediana_out:.2f} USD", help="Por 1M de tokens generados")
kpi3.metric("⚖️ Multiplicador Salida/Entrada", f"{ratio_med:.2f}x", help="Sobrecosto de generar vs leer")
kpi4.metric("📈 Modelos Analizados", f"{total_obs:,}", help="Total de observaciones con filtros aplicados")

st.markdown("---")

# 2. Visualizaciones Analíticas
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("1. Evolución Temporal de Precios (Deflación Histórica)")
    serie_tiempo = df_filtrado.groupby(["week_start", "developer"], observed=True)["input_price_per_1m_tokens"].median().reset_index()
    fig_linea = px.line(
        serie_tiempo,
        x="week_start",
        y="input_price_per_1m_tokens",
        color="developer",
        labels={"week_start": "Fecha (Semana)", "input_price_per_1m_tokens": "USD / 1M Tokens Entrada"},
        title="Precio Mediano por Semana según Desarrollador",
        template="plotly_white"
    )
    fig_linea.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=380)
    st.plotly_chart(fig_linea, use_container_width=True)

with col_graf2:
    st.subheader("2. Comparativa de Nubes para Meta Llama 3 (Disparidad)")
    df_llama = df[df["model_name"].str.contains("llama-3", case=False, na=False)]
    llama_stats = df_llama.groupby("provider")["input_price_per_1m_tokens"].agg(["mean", "min", "max", "count"]).reset_index()
    llama_stats = llama_stats[llama_stats["count"] >= 30].sort_values("mean")

    fig_barras = px.bar(
        llama_stats,
        x="provider",
        y="mean",
        labels={"provider": "Plataforma de Nube", "mean": "Precio Promedio Entrada (USD)"},
        title="Diferencia de Tarifa para el Mismo Modelo (Meta Llama 3)",
        color="mean",
        color_continuous_scale="Blues",
        template="plotly_white"
    )
    fig_barras.update_layout(margin=dict(l=20, r=20, t=40, b=20), height=380)
    st.plotly_chart(fig_barras, use_container_width=True)

# 3. Calculadora de Costos
st.markdown("---")
st.subheader("💡 Calculadora Rápida de Presupuesto Empresarial")
calc_c1, calc_c2 = st.columns(2)
with calc_c1:
    vol_consultas = st.slider("Consultas mensuales estimadas:", min_value=1000, max_value=500000, value=50000, step=5000)
with calc_c2:
    costo_est_barato = (vol_consultas * (1000 * 0.15 + 500 * 0.60)) / 1_000_000
    costo_est_caro = (vol_consultas * (1000 * 3.00 + 500 * 15.00)) / 1_000_000
    st.write(f"• Costo mensual con proveedores económicos (DeepInfra/Groq): **${costo_est_barato:.2f} USD**")
    st.write(f"• Costo mensual con proveedores corporativos tradicionales: **${costo_est_caro:.2f} USD**")
    st.success(f"Ahorro potencial estimado: **${costo_est_caro - costo_est_barato:.2f} USD al mes ({((costo_est_caro - costo_est_barato)/costo_est_caro)*100:.1f}%)**")

