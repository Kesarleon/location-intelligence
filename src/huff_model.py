from typing import Tuple

import numpy as np
import pandas as pd
from hexgrid import build_hex_agg, distance_to_sites


def huff_probabilities(
    demand_hex: pd.DataFrame,
    sites_df: pd.DataFrame,
    alpha: float = 1.0,
    beta: float = 1.6,
    max_km: float = 8.0,
) -> np.ndarray:
    """
    Calcula las probabilidades del modelo de Huff.
    P_ij = (A_j^alpha * d_ij^-beta) / sum_j ...  (con cutoff por distancia)

    Args:
        demand_hex: DataFrame con los datos de demanda agregados por hexágono.
        sites_df: DataFrame con los datos de los sitios (competidores y candidatos).
        alpha: Parámetro de atractividad.
        beta: Parámetro de distancia.
        max_km: Distancia máxima de captación.

    Returns:
        Un array de numpy con las probabilidades de captación para cada hexágono y sitio.
    """
    demand_hex = demand_hex.copy()
    probs = []
    for _, h in demand_hex.iterrows():
        dists = distance_to_sites(h.hex_lat, h.hex_lon, sites_df)
        # filtro por distancia máxima (captación realista)
        mask = dists <= max_km
        if not mask.any():
            probs.append(np.zeros(len(sites_df)))
            continue
        A = sites_df["attractiveness"].values
        num = (A**alpha) * np.power(np.maximum(dists, 0.2), -beta)  # evitar div/0
        num = np.where(mask, num, 0.0)
        denom = num.sum()
        probs.append(num / denom if denom > 0 else np.zeros_like(num))
    return np.vstack(probs)  # shape: [n_hex, n_sites]


def hex_capture(
    demand_df: pd.DataFrame,
    candidates_df: pd.DataFrame,
    competitors_df: pd.DataFrame,
    alpha: float = 1.0,
    beta: float = 1.6,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Calcula la captación de mercado por hexágono utilizando el modelo de Huff.

    Args:
        demand_df: DataFrame con los datos de demanda.
        candidates_df: DataFrame con los datos de los candidatos.
        competitors_df: DataFrame con los datos de los competidores.
        alpha: Parámetro de atractividad.
        beta: Parámetro de distancia.

    Returns:
        Una tupla con tres DataFrames:
        - Captación por sitio.
        - Resumen de captación por grupo.
        - Demanda por hexágono con información del ganador.
    """
    sites = pd.concat(
        [
            competitors_df.assign(group="competitor"),
            candidates_df.assign(group="candidate"),
        ],
        ignore_index=True,
    )

    demand_hex = build_hex_agg(demand_df, res=8)
    P = huff_probabilities(demand_hex, sites, alpha=alpha, beta=beta, max_km=8.0)

    cap = P * demand_hex["demand_value"].values[:, None]
    sites_capture = sites.copy()
    sites_capture["capture"] = cap.sum(axis=0)

    # Resumen por grupo
    summary = sites_capture.groupby("group")["capture"].sum().reset_index()

    # Añadimos captura esperada al demand_hex por “ganador” (argmax)
    winner_idx = np.argmax(P, axis=1) if P.size else np.array([])
    demand_hex["winner_site_id"] = [
        int(sites.iloc[i].id) if len(sites) > 0 else -1 for i in winner_idx
    ]
    demand_hex["winner_group"] = [
        sites.iloc[i].group if len(sites) > 0 else "" for i in winner_idx
    ]

    return sites_capture, summary, demand_hex
