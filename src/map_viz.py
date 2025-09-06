from typing import Any, Dict, List, Optional

import folium
import pandas as pd
from folium.features import GeoJson
import h3
from huff_model import hex_capture
from utils import COLORS


def h3_polygon(h: str) -> List[List[float]]:
    """
    Obtiene los vértices de un hexágono H3.

    Args:
        h: ID del hexágono H3.

    Returns:
        Una lista de listas con las coordenadas de los vértices del hexágono.
    """
    boundary = h3.cell_to_boundary(h)
    return [[lat, lon] for lat, lon in boundary]


def hexlayer_from_df(demand_hex: pd.DataFrame) -> Dict[str, Any]:
    """
    Crea una capa GeoJson de hexágonos a partir de un DataFrame.

    Args:
        demand_hex: DataFrame con los datos de demanda agregados por hexágono.

    Returns:
        Un diccionario GeoJson con los hexágonos.
    """
    features = []
    for _, r in demand_hex.iterrows():
        properties = r.to_dict()
        poly = {
            "type": "Feature",
            "properties": properties,
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [lon, lat]
                        for lat, lon in h3.cell_to_boundary(r.h3)
                    ]
                ],
            },
        }
        features.append(poly)
    return {"type": "FeatureCollection", "features": features}


def plot_overview(
    df: Optional[pd.DataFrame] = None, csv_path: str = "data/locations.csv"
) -> folium.Map:
    """
    Crea un mapa con una vista general de todos los puntos de interés.

    Args:
        df: DataFrame con los datos de ubicación. Si es None, se carga desde csv_path.
        csv_path: Ruta al archivo CSV con los datos de ubicación.

    Returns:
        Un objeto folium.Map con el mapa.
    """
    if df is None:
        df = pd.read_csv(csv_path)
    center = [df["lat"].mean(), df["lon"].mean()]
    m = folium.Map(location=center, zoom_start=12, tiles="CartoDB positron")

    for t in ["demand", "competitor", "candidate"]:
        sub = df[df["type"] == t]
        for _, r in sub.iterrows():
            folium.CircleMarker(
                [r.lat, r.lon],
                radius=4 if t == "demand" else 6,
                color=COLORS.get(t, "gray"),
                fill=True,
                fill_opacity=0.7,
                popup=f"{t.title()} #{int(r.id)} | A={r.get('attractiveness', '-')}",
            ).add_to(m)

    folium.LayerControl().add_to(m)
    return m


def plot_huff_hex(
    sites_cap: pd.DataFrame, demand_hex: pd.DataFrame, df: pd.DataFrame
) -> folium.Map:
    """
    Crea un mapa con los resultados del modelo de Huff visualizados por hexágono.

    Args:
        sites_cap: DataFrame con la captación por sitio.
        demand_hex: DataFrame con la demanda por hexágono y el ganador.
        df: DataFrame con los datos de ubicación originales.

    Returns:
        Un objeto folium.Map con el mapa.
    """
    m = folium.Map(
        location=[df["lat"].mean(), df["lon"].mean()],
        zoom_start=12,
        tiles="CartoDB positron",
    )

    # Capa H3 coloreada por ganador (candidate vs competitor)
    gj = hexlayer_from_df(demand_hex)

    def style_fn(feat: Dict[str, Any]) -> Dict[str, Any]:
        group = feat["properties"]["winner_group"]
        color = (
            "#2ECC71"
            if group == "candidate"
            else ("#E74C3C" if group == "competitor" else "#95A5A6")
        )
        return {
            "fillColor": color,
            "color": "#333333",
            "weight": 0.3,
            "fillOpacity": 0.45,
        }

    GeoJson(gj, style_function=style_fn, name="Huff winner").add_to(m)

    # Marcadores de sitios con tamaño ~ captura
    max_cap = max(sites_cap["capture"].max(), 1.0)
    for _, r in sites_cap.iterrows():
        rad = 4 + 16 * (r.capture / max_cap)
        color = "green" if r.group == "candidate" else "red"
        folium.CircleMarker(
            [r.lat, r.lon],
            radius=rad,
            color=color,
            fill=True,
            fill_opacity=0.85,
            popup=f"{r.group.title()} #{int(r.id)} | Capture={r.capture:.1f}",
        ).add_to(m)

    folium.LayerControl().add_to(m)
    return m
