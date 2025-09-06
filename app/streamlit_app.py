import sys
from pathlib import Path

# Add src to path to be able to import local modules
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import folium

from map_viz import plot_overview, plot_huff_hex, hexlayer_from_df
from heatmap import plot_heatmap
from buffers import plot_buffers
from huff_model import hex_capture
from white_space import white_space_analysis
from analysis import calculate_cannibalization

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
    "Herramienta avanzada para análisis de ubicaciones, competencia y potencial de mercado."
)


# --------------------------
# Cargar datos
# --------------------------
@st.cache_data
def load_data(path: str = "data/locations.csv") -> pd.DataFrame:
    return pd.read_csv(path)


df = load_data()
demand_df = df[df["type"] == "demand"].copy()
competitors_df = df[df["type"] == "competitor"].copy()
candidates_df = df[df["type"] == "candidate"].copy()

# --------------------------
# Dashboard con Pestañas
# --------------------------
tab1, tab2, tab3 = st.tabs(
    ["🗺️ Vista General", "🔍 Análisis de Competencia", "📈 Modelo de Huff"]
)

with tab1:
    st.header("Vista General del Mercado")
    st.markdown(
        "Mapa con todos los puntos de interés: demanda, competidores y candidatos."
    )
    m = plot_overview(df=df)
    st_folium(m, width=1200, height=700)

with tab2:
    st.header("Análisis de Competencia y Oportunidades")
    analysis_type = st.radio(
        "Selecciona un tipo de análisis:",
        ["Heatmap de Demanda", "Análisis de White Space"],
    )

    if analysis_type == "Heatmap de Demanda":
        st.markdown(
            "Mapa de calor que muestra la concentración de la demanda ponderada por su valor."
        )
        m = plot_heatmap(df=df)
        st_folium(m, width=1200, height=700)
    elif analysis_type == "Análisis de White Space":
        st.markdown(
            "Identificación de áreas con alta demanda y baja presencia de competidores."
        )
        white_space_df = white_space_analysis(demand_df, competitors_df)

        m = folium.Map(
            location=[df["lat"].mean(), df["lon"].mean()],
            zoom_start=12,
            tiles="CartoDB dark_matter",
        )

        # Capa de hexágonos coloreada por white space score
        gj = hexlayer_from_df(white_space_df, color_by="white_space_score")

        def style_fn(feat):
            score = feat["properties"]["white_space_score"]
            # Escala de color simple de blanco a verde
            green = int(255 * (score / white_space_df["white_space_score"].max()))
            color = f"#{255-green:02x}{green:02x}{255-green:02x}"
            return {
                "fillColor": color,
                "color": "#333333",
                "weight": 0.3,
                "fillOpacity": 0.6,
            }

        folium.GeoJson(gj, style_function=style_fn, name="White Space Score").add_to(m)
        st_folium(m, width=1200, height=700)

with tab3:
    st.header("Simulación de Captación de Mercado (Modelo de Huff)")
    st.markdown("Análisis 'what-if' para evaluar el potencial de nuevas ubicaciones.")

    st.sidebar.header("Parámetros del Modelo de Huff")
    alpha = st.sidebar.slider("Atractividad (alpha)", 0.1, 3.0, 1.0, 0.1)
    beta = st.sidebar.slider("Distancia (beta)", 0.1, 3.0, 1.6, 0.1)

    selected_candidates = st.sidebar.multiselect(
        "Selecciona candidatos a incluir en la simulación:",
        options=candidates_df["id"].tolist(),
        default=candidates_df["id"].tolist(),
    )

    if not selected_candidates:
        st.warning("Por favor, selecciona al menos un candidato.")
    else:
        active_candidates = candidates_df[
            candidates_df["id"].isin(selected_candidates)
        ]
        sites_cap, summary, demand_hex = hex_capture(
            demand_df, active_candidates, competitors_df, alpha=alpha, beta=beta
        )

        m = plot_huff_hex(sites_cap, demand_hex, df)
        st_folium(m, width=1200, height=700)

        st.subheader("Resultados de la Simulación")
        st.write("Captación de mercado por grupo:")
        st.dataframe(summary)

        st.write("Ranking de candidatos por captación:")
        st.dataframe(
            sites_cap[sites_cap["group"] == "candidate"]
            .sort_values("capture", ascending=False)
            .reset_index(drop=True)
        )

        if len(active_candidates) > 1:
            st.subheader("Análisis de Canibalización")
            st.write(
                "Área de canibalización (km²) entre los buffers de los candidatos (radio de 1km):"
            )
            cannibalization_df = calculate_cannibalization(
                active_candidates, radius_km=1.0
            )
            st.dataframe(cannibalization_df)
