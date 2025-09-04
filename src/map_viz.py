import folium
import pandas as pd

def create_map(data_path="data/locations.csv", output_path="map.html"):
    df = pd.read_csv(data_path)

    # Mapa centrado en CDMX
    m = folium.Map(location=[19.4326, -99.1332], zoom_start=12, tiles="CartoDB positron")

    # Demanda
    for _, row in df[df["type"]=="demand"].iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=5,
            color="blue",
            fill=True,
            fill_opacity=0.7,
            popup=f"Demanda {row['id']}"
        ).add_to(m)

    # Competencia
    for _, row in df[df["type"]=="competitor"].iterrows():
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=f"Competidor {row['id']}",
            icon=folium.Icon(color="red", icon="briefcase")
        ).add_to(m)

    # Candidatos
    for _, row in df[df["type"]=="candidate"].iterrows():
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=f"Candidato {row['id']} (Att: {row['attractiveness']})",
            icon=folium.Icon(color="green", icon="star")
        ).add_to(m)

    # Guardar
    m.save(output_path)
    print(f"✅ Mapa generado en {output_path}")

if __name__ == "__main__":
    create_map()
