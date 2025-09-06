import sys
from pathlib import Path

# Add src to path to be able to import local modules
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

import streamlit as st
import pandas as pd
from streamlit_folium import st_folium

from map_viz import plot_overview, plot_huff_hex
from heatmap import plot_heatmap
from buffers import plot_buffers
from huff_model import hex_capture

# --------------------------
# Configuración inicial
# --------------------------
st.set_page_config(
    page_title="🌍 Location Intelligence Dashboard",
    page_icon="🗺️",
    layout="wide",
)

st.title("🌍 Location Intelligence Dashboard")
st.markdown(
    "Análisis de clientes, competencia y áreas de influencia para toma de decisiones."
)


# --------------------------
# Cargar datos
# --------------------------
@st.cache_data
def load_data(path: str = "data/locations.csv") -> pd.DataFrame:
    return pd.read_csv(path)


df = load_data()

# --------------------------
# Sidebar
# --------------------------
st.sidebar.header("⚙️ Configuración de Visualización")
view_option = st.sidebar.selectbox(
    "Selecciona una visualización:",
    ["Vista General", "Heatmap de Demanda", "Buffers de Candidatos", "Modelo de Huff"],
)

# --------------------------
# Crear y renderizar mapa
# --------------------------
st.header(f"Visualización: {view_option}")

if view_option == "Vista General":
    st.markdown("Mapa con todos los puntos de interés: demanda, competidores y candidatos.")
    m = plot_overview(df=df)
    st_folium(m, width=1200, height=700)

elif view_option == "Heatmap de Demanda":
    st.markdown(
        "Mapa de calor que muestra la concentración de la demanda ponderada por su valor."
    )
    m = plot_heatmap(df=df)
    st_folium(m, width=1200, height=700)

elif view_option == "Buffers de Candidatos":
    st.markdown(
        "Áreas de influencia (buffers) alrededor de las ubicaciones candidatas."
    )
    radii_m = st.sidebar.multiselect(
        "Radios de los buffers (m):",
        [300, 500, 800, 1000, 1500],
        default=[300, 500, 800],
    )
    m = plot_buffers(df=df, radii_m=tuple(radii_m))
    st_folium(m, width=1200, height=700)

elif view_option == "Modelo de Huff":
    st.markdown(
        "Resultados del modelo de Huff, mostrando la captación de mercado por hexágono."
    )
    alpha = st.sidebar.slider("Parámetro de atractividad (alpha)", 0.1, 3.0, 1.0, 0.1)
    beta = st.sidebar.slider("Parámetro de distancia (beta)", 0.1, 3.0, 1.6, 0.1)

    demand = df[df["type"] == "demand"].copy()
    candidates = df[df["type"] == "candidate"].copy()
    competitors = df[df["type"] == "competitor"].copy()

    sites_cap, summary, demand_hex = hex_capture(
        demand, candidates, competitors, alpha=alpha, beta=beta
    )

    m = plot_huff_hex(df=df)
    st_folium(m, width=1200, height=700)

    st.subheader("Resultados del Modelo de Huff")
    st.write("Captación de mercado por grupo:")
    st.dataframe(summary)

    st.write("Top 5 candidatos con mayor captación:")
    st.dataframe(
        sites_cap[sites_cap["group"] == "candidate"]
        .sort_values("capture", ascending=False)
        .head(5)
    )

# --------------------------
# Insights
# --------------------------
st.sidebar.header("📊 Resumen de Datos")
st.sidebar.markdown(
    f"- **{df[df['type'] == 'demand'].shape[0]}** puntos de demanda"
)
st.sidebar.markdown(
    f"- **{df[df['type'] == 'competitor'].shape[0]}** competidores"
)
st.sidebar.markdown(
    f"- **{df[df['type'] == 'candidate'].shape[0]}** candidatos"
)
