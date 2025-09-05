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
