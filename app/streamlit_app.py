import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
from shapely.geometry import Point
import geopandas as gpd

st.set_page_config(page_title="Location Intelligence Dashboard", layout="wide")

# =======================
# 1. Cargar datos
# =======================
df = pd.read_csv("../data/locations.csv")

# Convertir a GeoDataFrame
gdf = gpd.GeoDataFrame(
    df, geometry=[Point(xy) for xy in zip(df.lon, df.lat)], crs="EPSG:4326"
)

# =======================
# Sidebar
# =======================
st.sidebar.header("⚙️ Configuración")
view_option = st.sidebar.radio("Visualización:", ["Mapa de Puntos", "Heatmap", "Áreas de Influencia"])
radius_km = st.sidebar.slider("Radio de influencia (km)", 0.5, 5.0, 1.0, step=0.5)

st.title("🌍 Location Intelligence Dashboard")
st.markdown("Analiza clientes y competencia en un mapa interactivo.")

# =======================
# 2. Crear mapa
# =======================
m = folium.Map(location=[19.4326, -99.1332], zoom_start=12, tiles="CartoDB positron")

if view_option == "Mapa de Puntos":
    for _, row in df[df["type"]=="demand"].iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=5, color="blue", fill=True, popup=f"Cliente {row['id']}"
        ).add_to(m)

    for _, row in df[df["type"]=="competitor"].iterrows():
        folium.Marker(
            location=[row["lat"], row["lon"]],
            icon=folium.Icon(color="red", icon="briefcase"),
            popup=f"Competidor {row['id']}"
        ).add_to(m)

elif view_option == "Heatmap":
    HeatMap(df[df["type"]=="demand"][["lat","lon"]].values.tolist(), radius=12).add_to(m)

elif view_option == "Áreas de Influencia":
    # Buffers en metros
    gdf_utm = gdf.to_crs(epsg=3857)  # reproyectar a métrico
    gdf_utm["buffer"] = gdf_utm.buffer(radius_km*1000)
    gdf_buffers = gdf_utm.to_crs(epsg=4326)

    for _, row in gdf_buffers[gdf_buffers["type"]=="demand"].iterrows():
        folium.GeoJson(
            row["buffer"],
            style_function=lambda x: {"color":"blue", "fillColor":"blue", "fillOpacity":0.2}
        ).add_to(m)

    for _, row in gdf_buffers[gdf_buffers["type"]=="competitor"].iterrows():
        folium.GeoJson(
            row["buffer"],
            style_function=lambda x: {"color":"red", "fillColor":"red", "fillOpacity":0.2}
        ).add_to(m)

# =======================
# 3. Renderizar mapa
# =======================
st_data = st_folium(m, width=1200, height=700)

# =======================
# 4. Insights dinámicos
# =======================
st.subheader("📊 Insights")
clients = df[df["type"]=="demand"].shape[0]
competitors = df[df["type"]=="competitor"].shape[0]

st.markdown(f"- Número de puntos de demanda simulados: **{clients}**")
st.markdown(f"- Número de competidores simulados: **{competitors}**")

if view_option == "Áreas de Influencia":
    overlap = gpd.overlay(
        gdf_buffers[gdf_buffers["type"]=="demand"],
        gdf_buffers[gdf_buffers["type"]=="competitor"],
        how="intersection"
    )
    st.markdown(f"- Zonas de competencia directa detectadas: **{len(overlap)}**")
