from typing import Optional, Tuple

import folium
import pandas as pd
from utils import COLORS


def plot_buffers(
    df: Optional[pd.DataFrame] = None,
    csv_path: str = "data/locations.csv",
    radii_m: Tuple[int, int, int] = (300, 500, 800),
) -> folium.Map:
    """
    Crea un mapa con buffers alrededor de los puntos de interés.

    Args:
        df: DataFrame con los datos de ubicación. Si es None, se carga desde csv_path.
        csv_path: Ruta al archivo CSV con los datos de ubicación.
        radii_m: Tupla con los radios de los buffers en metros.

    Returns:
        Un objeto folium.Map con el mapa.
    """
    if df is None:
        df = pd.read_csv(csv_path)
    lat_c = df["lat"].mean()
    lon_c = df["lon"].mean()

    m = folium.Map(location=[lat_c, lon_c], zoom_start=12, tiles="CartoDB positron")

    # Puntos
    for _, r in df.iterrows():
        folium.CircleMarker(
            [r.lat, r.lon],
            radius=4,
            color=COLORS.get(r.type, "gray"),
            fill=True,
            fill_opacity=0.7,
            popup=f"{r.type.title()} #{r.get('id', '')}",
        ).add_to(m)

    # Buffers para candidatos
    for _, r in df[df["type"] == "candidate"].iterrows():
        for rad in radii_m:
            folium.Circle(
                [r.lat, r.lon],
                radius=rad,
                color="green",
                fill=False,
                weight=1,
                opacity=0.5,
                popup=f"Candidate #{int(r.id)} - {rad} m",
            ).add_to(m)

    folium.LayerControl().add_to(m)
    return m


if __name__ == "__main__":
    m = plot_buffers()
    m.save("buffers.html")
    print("✅ Buffers guardados en buffers.html")
