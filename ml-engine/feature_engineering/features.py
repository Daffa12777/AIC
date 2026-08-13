"""
Feature Engineering: membangun fitur prediktif dari deret waktu energi
(lag feature, rolling statistics, fitur kalender) untuk model konsumsi energi.
"""

import numpy as np
import pandas as pd

LAG_STEPS = [1, 2, 3, 7]
ROLLING_WINDOWS = [3, 7]


def build_features(df: pd.DataFrame, target: str = "energy") -> pd.DataFrame:
    """
    Bangun fitur untuk satu deret produk/period.
    Diasumsikan df sudah difilter ke satu period dan terurut berdasarkan date.
    """
    data = df.copy().sort_values("date").reset_index(drop=True)

    # Fitur kalender
    data["day_of_week"] = data["date"].dt.dayofweek
    data["day_of_month"] = data["date"].dt.day
    data["month"] = data["date"].dt.month
    data["is_weekend"] = (data["day_of_week"] >= 5).astype(int)

    # Lag features
    for lag in LAG_STEPS:
        data[f"{target}_lag_{lag}"] = data[target].shift(lag)

    # Rolling statistics
    # shift(1) agar tidak menggunakan target hari ini
    for w in ROLLING_WINDOWS:
        shifted = data[target].shift(1)

        data[f"{target}_roll_mean_{w}"] = (
            shifted
            .rolling(window=w, min_periods=1)
            .mean()
        )

        data[f"{target}_roll_std_{w}"] = (
            shifted
            .rolling(window=w, min_periods=1)
            .std()
            .fillna(0)
        )

    return data


def feature_columns(
    df: pd.DataFrame,
    target: str = "energy"
) -> list[str]:
    """
    Daftar kolom fitur numerik.
    Target, identitas, dan kolom biaya dikeluarkan dari fitur.
    """

    exclude = {
        target,
        "date",
        "period",
        "raw_material_cost",
        "unit_cost",
    }

    return [
        c
        for c in df.columns
        if c not in exclude
        and pd.api.types.is_numeric_dtype(df[c])
    ]