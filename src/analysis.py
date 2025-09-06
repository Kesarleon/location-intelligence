import folium
import geopandas as gpd
import pandas as pd
from folium.plugins import HeatMap
from shapely.geometry import Point


def load_data(path: str = "data/locations.csv") -> gpd.GeoDataFrame:
    """
    Carga datos de ubicación desde un archivo CSV o GeoJSON a un GeoDataFrame.

    Args:
        path: Ruta al archivo.

    Returns:
        Un GeoDataFrame con los datos de ubicación.
    """
    if path.endswith(".geojson"):
        gdf = gpd.read_file(path)
    else:
        df = pd.read_csv(path)
        gdf = gpd.GeoDataFrame(
            df, geometry=gpd.points_from_xy(df.lon, df.lat), crs="EPSG:4326"
        )
    return gdf


def create_buffer(df: pd.DataFrame, radius: float = 0.01) -> gpd.GeoDataFrame:
    """
    Crea un buffer alrededor de los puntos en un DataFrame.
    radius ~0.01 grados ≈ 1 km dependiendo de lat/lon

    Args:
        df: DataFrame con los datos de ubicación.
        radius: Radio del buffer en grados.

    Returns:
        Un GeoDataFrame con una columna "buffer" que contiene los polígonos del buffer.
    """
    gdf = gpd.GeoDataFrame(
        df, geometry=[Point(xy) for xy in zip(df.lon, df.lat)], crs="EPSG:4326"
    )
    gdf["buffer"] = gdf.geometry.buffer(radius)
    return gdf


def create_heatmap(df: pd.DataFrame, output: str = "analysis_heatmap.html") -> str:
    """
    Crea un mapa de calor (heatmap) a partir de un DataFrame.

    Args:
        df: DataFrame con los datos de ubicación.
        output: Ruta donde se guardará el mapa HTML.

    Returns:
        La ruta al archivo HTML del mapa.
    """
    m = folium.Map(location=[19.4326, -99.1332], zoom_start=12)
    heat_data = df[["lat", "lon"]].values.tolist()
    HeatMap(heat_data, radius=12).add_to(m)
    m.save(output)
    return output


def calculate_cannibalization(
    candidates_df: pd.DataFrame, radius_km: float = 1.0
) -> pd.DataFrame:
    """
    Calcula la canibalización entre tiendas candidatas basada en la superposición de buffers.

    Args:
        candidates_df: DataFrame con los datos de los candidatos.
        radius_km: Radio de los buffers en kilómetros.

    Returns:
        Un DataFrame con el área de canibalización para cada par de tiendas.
    """
    gdf = gpd.GeoDataFrame(
        candidates_df,
        geometry=gpd.points_from_xy(candidates_df.lon, candidates_df.lat),
        crs="EPSG:4326",
    )
    gdf_proj = gdf.to_crs(epsg=3857)
    gdf_proj["buffer"] = gdf_proj.geometry.buffer(radius_km * 1000)

    intersections = []
    for i, poly1 in gdf_proj.iterrows():
        for j, poly2 in gdf_proj.iterrows():
            if i >= j:
                continue
            if poly1["buffer"].intersects(poly2["buffer"]):
                intersection_area = poly1["buffer"].intersection(poly2["buffer"]).area / 1e6
                intersections.append(
                    {
                        "candidate1": poly1["id"],
                        "candidate2": poly2["id"],
                        "cannibalization_area_km2": intersection_area,
                    }
                )
    return pd.DataFrame(intersections)
