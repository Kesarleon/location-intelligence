import pandas as pd
from hexgrid import build_hex_agg, distance_to_sites


def service_level(
    demand_hex: pd.DataFrame, competitors_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Calcula el nivel de servicio para cada hexágono de demanda, basado en la distancia
    al competidor más cercano.

    Args:
        demand_hex: DataFrame con los datos de demanda agregados por hexágono.
        competitors_df: DataFrame con los datos de los competidores.

    Returns:
        El DataFrame de demanda por hexágono con una nueva columna "dist_to_competitor".
    """
    demand_hex = demand_hex.copy()
    dists_to_competitors = []
    for _, h in demand_hex.iterrows():
        dists = distance_to_sites(h.hex_lat, h.hex_lon, competitors_df)
        dists_to_competitors.append(dists.min())
    demand_hex["dist_to_competitor"] = dists_to_competitors
    return demand_hex


def white_space_analysis(
    demand_df: pd.DataFrame, competitors_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Realiza un análisis de white space para identificar áreas con alta demanda y baja
    presencia de competidores.

    Args:
        demand_df: DataFrame con los datos de demanda.
        competitors_df: DataFrame con los datos de los competidores.

    Returns:
        Un DataFrame de demanda por hexágono con una columna "white_space_score".
    """
    demand_hex = build_hex_agg(demand_df)
    demand_hex = service_level(demand_hex, competitors_df)

    # El score es una simple combinación de valor de demanda y distancia al competidor.
    # Se puede normalizar o usar una fórmula más compleja.
    demand_hex["white_space_score"] = (
        demand_hex["demand_value"] * demand_hex["dist_to_competitor"]
    )
    return demand_hex
