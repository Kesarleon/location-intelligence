import folium
import pandas as pd
from utils import bbox_from_points, COLORS

def plot_buffers(csv_path="data/locations.csv", output="buffers.html",
                 radii_m=(300, 500, 800)):
    df = pd.read_csv(csv_path)
    lat_c = df["lat"].mean()
    lon_c = df["lon"].mean()

    m = folium.Map(location=[lat_c, lon_c], zoom_start=12, tiles="CartoDB positron")

    # Puntos
    for _, r in df.iterrows():
        folium.CircleMarker(
            [r.lat, r.lon], radius=4, color=COLORS.get(r.type, "gray"),
            fill=True, fill_opacity=0.7,
            popup=f"{r.type.title()} #{r.get('id', '')}"
        ).add_to(m)

    # Buffers para candidatos
    for _, r in df[df["type"]=="candidate"].iterrows():
        for rad in radii_m:
            folium.Circle(
                [r.lat, r.lon], radius=rad,
                color="green", fill=False, weight=1, opacity=0.5,
                popup=f"Candidate #{int(r.id)} - {rad} m"
            ).add_to(m)

    folium.LayerControl().add_to(m)
    m.save(output)
    print(f"✅ Buffers guardados en {output}")

if __name__ == "__main__":
    plot_buffers()
