import sys
import os
import pytest

# Add src to path to be able to import utils
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from utils import haversine_km, bbox_from_points


def test_haversine_km():
    # Test with known values
    # Paris to New York
    lat1, lon1 = 48.8566, 2.3522
    lat2, lon2 = 40.7128, -74.0060
    distance = haversine_km(lat1, lon1, lat2, lon2)
    assert 5800 < distance < 5900  # Approximately 5837 km

    # Same point should be 0
    distance = haversine_km(lat1, lon1, lat1, lon1)
    assert distance == 0


def test_bbox_from_points():
    lats = [10, 20, 30]
    lons = [-10, 0, 10]
    pad = 0.1
    bbox = bbox_from_points(lats, lons, pad)
    assert bbox == (10 - pad, -10 - pad, 30 + pad, 10 + pad)

    # Test with no padding
    bbox = bbox_from_points(lats, lons, 0)
    assert bbox == (10, -10, 30, 10)
