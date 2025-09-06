from typing import List, Optional

import folium
import numpy as np
import pandas as pd
from folium.plugins import HeatMap


def kde_weighted_points(df: pd.DataFrame, weight_col: str = "value") -> List[List]:
    """
    Prepara los datos para el heatmap ponderado.

    Args:
        df: DataFrame con los datos de ubicación y ponderación.
        weight_col: Nombre de la columna de ponderación.

    Returns:
        Una lista de listas con latitud, longitud y ponderación.
    """
    return df[["lat", "lon", weight_col]].values.tolist()


def plot_heatmap(
    df: Optional[pd.DataFrame] = None, csv_path: str = "data/locations.csv"
) -> folium.Map:
    """
    Crea un mapa de calor (heatmap) ponderado por valor de consumo.

    Args:
        df: DataFrame con los datos de ubicación. Si es None, se carga desde csv_path.
        csv_path: Ruta al archivo CSV con los datos de ubicación.

    Returns:
        Un objeto folium.Map con el mapa.
    """
    if df is None:
        df = pd.read_csv(csv_path)
    demand = df[df["type"] == "demand"].copy()
    center = [demand["lat"].mean(), demand["lon"].mean()]
    m = folium.Map(location=center, zoom_start=12, tiles="CartoDB dark_matter")

    heat_data = kde_weighted_points(demand, "value")
    HeatMap(heat_data, radius=18, blur=24, max_zoom=13).add_to(m)

    # Marcamos competencia y candidatos
    for _, r in df[df["type"].isin(["competitor", "candidate"])].iterrows():
        folium.CircleMarker(
            [r.lat, r.lon],
            radius=5,
            color="red" if r.type == "competitor" else "green",
            fill=True,
            fill_opacity=0.8,
            popup=f"{r.type.title()} #{int(r.id)} | A={r.get('attractiveness', '-')}",
        ).add_to(m)

    return m


if __name__ == "__main__":
    m = plot_heatmap()
    m.save("heatmap.html")
    print("✅ Heatmap guardado en heatmap.html")
