import numpy as np

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p = np.pi / 180.0
    a = 0.5 - np.cos((lat2 - lat1)*p)/2 + np.cos(lat1*p)*np.cos(lat2*p)*(1 - np.cos((lon2 - lon1)*p))/2
    return 2 * R * np.arcsin(np.sqrt(a))

def bbox_from_points(lats, lons, pad=0.02):
    return (min(lats)-pad, min(lons)-pad, max(lats)+pad, max(lons)+pad)

# Paletas simples
COLORS = {
    "demand": "blue",
    "competitor": "red",
    "candidate": "green"
}
