import pandas as pd
import numpy as np

np.random.seed(42)

# Simulamos 50 ubicaciones de clientes y 20 de competencia en CDMX
n_clients = 50
n_competitors = 20

# Coordenadas aproximadas CDMX
lat_center, lon_center = 19.4326, -99.1332

clients = pd.DataFrame({
    "id": range(1, n_clients+1),
    "type": "client",
    "lat": np.random.uniform(lat_center-0.05, lat_center+0.05, n_clients),
    "lon": np.random.uniform(lon_center-0.05, lon_center+0.05, n_clients),
})

competitors = pd.DataFrame({
    "id": range(1, n_competitors+1),
    "type": "competitor",
    "lat": np.random.uniform(lat_center-0.05, lat_center+0.05, n_competitors),
    "lon": np.random.uniform(lon_center-0.05, lon_center+0.05, n_competitors),
})

df = pd.concat([clients, competitors], ignore_index=True)
df.to_csv("data/locations.csv", index=False)
print("✅ Dataset generado en data/locations.csv")
