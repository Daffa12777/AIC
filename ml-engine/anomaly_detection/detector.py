"""
Energy Anomaly Detection
Mendeteksi pola konsumsi energi yang tidak normal menggunakan IsolationForest,
sebagai sinyal dini pemborosan energi atau gangguan operasional.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

from config.settings import ANOMALY_CONTAMINATION, RANDOM_SEED


@dataclass
class AnomalyPoint:
    date: str
    period: str
    energy: float
    deviation_pct: float  # deviasi terhadap rata-rata historis period


def detect_energy_anomalies(df: pd.DataFrame, period: str | None = None) -> list[AnomalyPoint]:
    """
    Deteksi anomali konsumsi energi. Bila period diberikan, deteksi hanya untuk
    period tersebut; jika tidak, seluruh dataset.
    """
    data = df.copy()
    if period is not None:
        data = data[data["period"] == period]
    if len(data) < 8:
        return []

    features = data[["energy"]].copy()
    if "production_volume" in data.columns:
        features["energy_per_volume"] = (
            data["energy"] / data["production_volume"].replace(0, np.nan)
        ).fillna(data["energy"].median())

    model = IsolationForest(
        contamination=ANOMALY_CONTAMINATION,
        random_state=RANDOM_SEED,
        n_estimators=100,
    )
    labels = model.fit_predict(features.values)

    anomalies = []
    for i, (idx, row) in enumerate(data.iterrows()):
        if labels[i] == -1:
            period_mean = data[data["period"] == row["period"]]["energy"].mean()
            deviation = ((row["energy"] - period_mean) / period_mean * 100) if period_mean > 0 else 0.0
            anomalies.append(
                AnomalyPoint(
                    date=str(pd.to_datetime(row["date"]).date()),
                    period=str(row["period"]),
                    energy=round(float(row["energy"]), 2),
                    deviation_pct=round(float(deviation), 1),
                )
            )

    anomalies.sort(key=lambda a: abs(a.deviation_pct), reverse=True)
    return anomalies
