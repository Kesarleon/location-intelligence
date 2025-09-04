import pandas as pd
import numpy as np

np.random.seed(42)

# Centro CDMX
LAT_C, LON_C = 19.4326, -99.1332

def jitter(n, lat_c=LAT_C, lon_c=LON_C, span=0.06):
    lat = np.random.uniform(lat_c - span, lat_c + span, n)
    lon = np.random.uniform(lon_c - span, lon_c + span, n)
    return lat, lon

def main():
    n_clients = 800      # “demanda” (puntos de población/consumo)
    n_comp = 25          # competencia
    n_cand = 6           # candidatos a nuevas sucursales

    lat, lon = jitter(n_clients)
    clients = pd.DataFrame({
        "id": range(1, n_clients+1),
        "type": "demand",
        "lat": lat,
        "lon": lon,
        # ticket/propensión simulada (para ponderar KDE y hexes)
        "value": np.random.gamma(shape=2.0, scale=50.0, size=n_clients).round(2)
    })

    lat, lon = jitter(n_comp)
    competitors = pd.DataFrame({
        "id": range(1, n_comp+1),
        "type": "competitor",
        "lat": lat,
        "lon": lon,
        # “atractividad” (p.e. tamaño/ratings)
        "attractiveness": np.random.uniform(0.8, 1.3, n_comp).round(2)
    })

    # 3 candidatos con alta atracción (flagship) + 3 normales
    lat, lon = jitter(n_cand)
    attractiveness = np.concatenate([
        np.random.uniform(1.2, 1.6, 3), np.random.uniform(0.9, 1.2, 3)
    ])
    candidates = pd.DataFrame({
        "id": range(1, n_cand+1),
        "type": "candidate",
        "lat": lat,
        "lon": lon,
        "attractiveness": attractiveness.round(2)
    })

    df = pd.concat([clients, competitors, candidates], ignore_index=True)
    df.to_csv("data/locations.csv", index=False)
    print("✅ data/locations.csv generado.")

if __name__ == "__main__":
    main()
