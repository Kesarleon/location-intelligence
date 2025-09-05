import h3
import pandas as pd
from utils import haversine_km


def latlon_to_h3(lat: float, lon: float, res: int = 8) -> str:
    """
    Convierte coordenadas de latitud y longitud a un hexágono H3.

    Args:
        lat: Latitud.
        lon: Longitud.
        res: Resolución del hexágono H3.

    Returns:
        El ID del hexágono H3.
    """
    return h3.geo_to_h3(lat, lon, res)


def build_hex_agg(df: pd.DataFrame, res: int = 8) -> pd.DataFrame:
    """
    Agrega datos de demanda en hexágonos H3.

    Args:
        df: DataFrame con los datos de ubicación.
        res: Resolución de los hexágonos H3.

    Returns:
        Un DataFrame con los datos de demanda agregados por hexágono.
    """
    df = df.copy()
    df["h3"] = df.apply(lambda r: latlon_to_h3(r.lat, r.lon, res), axis=1)

    demand = (
        df[df["type"] == "demand"]
        .groupby("h3")
        .agg(
            demand_value=("value", "sum"),
            lat=("lat", "mean"),
            lon=("lon", "mean"),
            n_points=("value", "count"),
        )
        .reset_index()
    )

    # Centros hex
    demand["hex_lat"] = demand["h3"].apply(lambda h: h3.h3_to_geo(h)[0])
    demand["hex_lon"] = demand["h3"].apply(lambda h: h3.h3_to_geo(h)[1])

    return demand


def distance_to_sites(
    hex_lat: float, hex_lon: float, sites_df: pd.DataFrame
) -> pd.Series:
    """
    Calcula la distancia desde un punto a todos los sitios en un DataFrame.

    Args:
        hex_lat: Latitud del punto.
        hex_lon: Longitud del punto.
        sites_df: DataFrame con los datos de los sitios.

    Returns:
        Una serie de pandas con las distancias a cada sitio.
    """
    return sites_df.apply(
        lambda r: haversine_km(hex_lat, hex_lon, r.lat, r.lon), axis=1
    )
