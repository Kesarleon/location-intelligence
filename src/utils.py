from typing import Dict, List, Tuple

import numpy as np


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula la distancia haversine entre dos puntos en kilómetros.

    Args:
        lat1: Latitud del primer punto.
        lon1: Longitud del primer punto.
        lat2: Latitud del segundo punto.
        lon2: Longitud del segundo punto.

    Returns:
        La distancia entre los dos puntos en kilómetros.
    """
    R = 6371.0  # Radio de la Tierra en kilómetros
    p = np.pi / 180.0
    a = (
        0.5
        - np.cos((lat2 - lat1) * p) / 2
        + np.cos(lat1 * p) * np.cos(lat2 * p) * (1 - np.cos((lon2 - lon1) * p)) / 2
    )
    return 2 * R * np.arcsin(np.sqrt(a))


def bbox_from_points(
    lats: List[float], lons: List[float], pad: float = 0.02
) -> Tuple[float, float, float, float]:
    """
    Crea un bounding box a partir de una lista de latitudes y longitudes.

    Args:
        lats: Lista de latitudes.
        lons: Lista de longitudes.
        pad: Cantidad de padding para agregar al bounding box.

    Returns:
        Una tupla con las coordenadas del bounding box (min_lat, min_lon, max_lat, max_lon).
    """
    return (min(lats) - pad, min(lons) - pad, max(lats) + pad, max(lons) + pad)


# Paletas simples
COLORS: Dict[str, str] = {"demand": "blue", "competitor": "red", "candidate": "green"}
