import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import folium
from folium.plugins import HeatMap

def load_data(path="data/locations.csv"):
    if path.endswith(".geojson"):
        gdf = gpd.read_file(path)
    else:
        df = pd.read_csv(path)
        gdf = gpd.GeoDataFrame(
            df, geometry=gpd.points_from_xy(df.lon, df.lat), crs="EPSG:4326"
        )
    return gdf

def create_buffer(df, radius=0.01):
    """
    radius ~0.01 grados ≈ 1 km dependiendo de lat/lon
    """
    gdf = gpd.GeoDataFrame(
        df, geometry=[Point(xy) for xy in zip(df.lon, df.lat)], crs="EPSG:4326"
    )
    gdf["buffer"] = gdf.geometry.buffer(radius)
    return gdf

def create_heatmap(df, output="analysis_heatmap.html"):
    m = folium.Map(location=[19.4326, -99.1332], zoom_start=12)
    heat_data = df[["lat", "lon"]].values.tolist()
    HeatMap(heat_data, radius=12).add_to(m)
    m.save(output)
    return output
