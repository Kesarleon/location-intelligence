from typing import Any, Dict, List

import folium
import pandas as pd
from folium.features import GeoJson
from h3 import h3
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
    boundary = h3.h3_to_geo_boundary(h, geo_json=True)
    return [[lat, lon] for lat, lon in boundary]


def hexlayer_from_df(
    demand_hex: pd.DataFrame, color_by: str = "winner_group"
) -> Dict[str, Any]:
    """
    Crea una capa GeoJson de hexágonos a partir de un DataFrame.

    Args:
        demand_hex: DataFrame con los datos de demanda agregados por hexágono.
        color_by: Nombre de la columna para colorear los hexágonos.

    Returns:
        Un diccionario GeoJson con los hexágonos.
    """
    features = []
    for _, r in demand_hex.iterrows():
        poly = {
            "type": "Feature",
            "properties": {
                "h3": r.h3,
                "demand_value": float(r.demand_value),
                "winner_group": r.get("winner_group", ""),
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [lon, lat]
                        for lat, lon in h3.h3_to_geo_boundary(r.h3, geo_json=True)
                    ]
                ],
            },
        }
        features.append(poly)
    return {"type": "FeatureCollection", "features": features}


def plot_overview(
    csv_path: str = "data/locations.csv", output: str = "overview.html"
) -> None:
    """
    Crea un mapa con una vista general de todos los puntos de interés.

    Args:
        csv_path: Ruta al archivo CSV con los datos de ubicación.
        output: Ruta donde se guardará el mapa HTML.
    """
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
    m.save(output)
    print(f"✅ Overview map → {output}")


def plot_huff_hex(
    csv_path: str = "data/locations.csv", output: str = "h3_hex_huff.html"
) -> None:
    """
    Crea un mapa con los resultados del modelo de Huff visualizados por hexágono.

    Args:
        csv_path: Ruta al archivo CSV con los datos de ubicación.
        output: Ruta donde se guardará el mapa HTML.
    """
    df = pd.read_csv(csv_path)
    demand = df[df["type"] == "demand"].copy()
    candidates = df[df["type"] == "candidate"].copy()
    competitors = df[df["type"] == "competitor"].copy()

    sites_cap, summary, demand_hex = hex_capture(
        demand, candidates, competitors, alpha=1.0, beta=1.6
    )

    m = folium.Map(
        location=[df["lat"].mean(), df["lon"].mean()],
        zoom_start=12,
        tiles="CartoDB positron",
    )

    # Capa H3 coloreada por ganador (candidate vs competitor)
    gj = hexlayer_from_df(demand_hex, color_by="winner_group")

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
    m.save(output)
    print(f"✅ Huff hex map → {output}")
