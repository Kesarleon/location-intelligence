import pandas as pd
import h3
from utils import haversine_km

def latlon_to_h3(lat, lon, res=8):
    return h3.geo_to_h3(lat, lon, res)

def build_hex_agg(df, res=8):
    df = df.copy()
    df["h3"] = df.apply(lambda r: latlon_to_h3(r.lat, r.lon, res), axis=1)

    demand = df[df["type"]=="demand"].groupby("h3").agg(
        demand_value=("value", "sum"),
        lat=("lat","mean"),
        lon=("lon","mean"),
        n_points=("value","count")
    ).reset_index()

    # Centros hex
    demand["hex_lat"] = demand["h3"].apply(lambda h: h3.h3_to_geo(h)[0])
    demand["hex_lon"] = demand["h3"].apply(lambda h: h3.h3_to_geo(h)[1])

    return demand

def distance_to_sites(hex_lat, hex_lon, sites_df):
    return sites_df.apply(lambda r: haversine_km(hex_lat, hex_lon, r.lat, r.lon), axis=1)
