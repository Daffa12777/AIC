"""
Training Forecast Engine untuk prediksi konsumsi energi.

Melatih tiga kandidat model:
- RandomForest
- XGBoost
- LightGBM

Evaluasi menggunakan split berbasis waktu pada masing-masing period/lini.
Model terbaik dipilih berdasarkan MAE terkecil.
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor

from feature_engineering.features import build_features, feature_columns
from forecast_engine.config import MODEL_CONFIGS, TEST_SIZE_RATIO


def _build_model(name: str):
    """Bangun model berdasarkan nama konfigurasi."""

    if name == "random_forest":
        return RandomForestRegressor(**MODEL_CONFIGS[name])

    if name == "xgboost":
        return XGBRegressor(**MODEL_CONFIGS[name])

    if name == "lightgbm":
        return LGBMRegressor(**MODEL_CONFIGS[name])

    raise ValueError(f"Model tidak dikenali: {name}")


def _prepare_training_frame(df: pd.DataFrame) -> pd.DataFrame:
    """
    Bangun feature engineering untuk setiap period/lini.

    Setiap period diproses secara terpisah agar:
    - lag tidak tercampur antar lini
    - rolling statistics tidak tercampur antar lini
    - urutan waktu tetap terjaga
    """

    frames = []

    for period, group in df.groupby("period"):
        group = group.sort_values("date").reset_index(drop=True)

        feat = build_features(
            group,
            target="energy"
        )

        feat["period"] = period

        frames.append(feat)

    if not frames:
        raise ValueError("Tidak ada data yang dapat diproses.")

    combined = pd.concat(
        frames,
        ignore_index=True
    )

    combined = combined.sort_values(
        ["period", "date"]
    ).reset_index(drop=True)

    # Buang baris yang belum memiliki lag lengkap.
    combined = combined.dropna().reset_index(drop=True)

    return combined


def _time_series_split(
    df: pd.DataFrame,
    test_size_ratio: float
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split data secara kronologis untuk setiap period.

    Contoh:

    POT-A:
        80% awal -> train
        20% akhir -> test

    POT-B:
        80% awal -> train
        20% akhir -> test

    POT-C:
        80% awal -> train
        20% akhir -> test
    """

    train_frames = []
    test_frames = []

    for period, group in df.groupby("period"):
        group = group.sort_values("date").reset_index(drop=True)

        n = len(group)

        if n < 2:
            continue

        split_idx = int(n * (1 - test_size_ratio))

        # Pastikan train dan test tidak kosong.
        split_idx = max(1, min(split_idx, n - 1))

        train_group = group.iloc[:split_idx].copy()
        test_group = group.iloc[split_idx:].copy()

        train_frames.append(train_group)
        test_frames.append(test_group)

    if not train_frames or not test_frames:
        raise ValueError(
            "Data tidak cukup untuk melakukan time-series split."
        )

    train_df = pd.concat(
        train_frames,
        ignore_index=True
    )

    test_df = pd.concat(
        test_frames,
        ignore_index=True
    )

    return train_df, test_df


def train_and_select_best_model(
    df: pd.DataFrame,
    model_output_path: Path
) -> dict:
    """
    Latih tiga kandidat model dan pilih model terbaik berdasarkan MAE.

    Proses:

    Data
      ↓
    Feature Engineering
      ↓
    Time-Series Split per period
      ↓
    Random Forest
    XGBoost
    LightGBM
      ↓
    MAE + RMSE
      ↓
    MAE terkecil = model terbaik
      ↓
    Retraining model terbaik menggunakan seluruh data
      ↓
    Simpan model
    """

    # ============================================================
    # 1. FEATURE ENGINEERING
    # ============================================================

    prepared = _prepare_training_frame(df)

    if len(prepared) < 10:
        raise ValueError(
            "Data tidak cukup untuk melatih model "
            "(minimal ~10 baris setelah feature engineering)."
        )

    # ============================================================
    # 2. TENTUKAN FITUR
    # ============================================================

    feat_cols = feature_columns(
        prepared,
        target="energy"
    )

    if not feat_cols:
        raise ValueError(
            "Tidak ada fitur yang tersedia untuk training."
        )

    # ============================================================
    # 3. TIME-SERIES SPLIT PER PERIOD
    # ============================================================

    train_df, test_df = _time_series_split(
        prepared,
        TEST_SIZE_RATIO
    )

    X_train = train_df[feat_cols].values
    y_train = train_df["energy"].values

    X_test = test_df[feat_cols].values
    y_test = test_df["energy"].values

    if len(X_train) == 0 or len(X_test) == 0:
        raise ValueError(
            "Data train atau test kosong."
        )

    # ============================================================
    # 4. TRAIN + EVALUASI 3 MODEL
    # ============================================================

    metrics = {}

    for name in MODEL_CONFIGS:

        model = _build_model(name)

        model.fit(
            X_train,
            y_train
        )

        pred = model.predict(
            X_test
        )

        mae = float(
            mean_absolute_error(
                y_test,
                pred
            )
        )

        rmse = float(
            np.sqrt(
                mean_squared_error(
                    y_test,
                    pred
                )
            )
        )

        metrics[name] = {
            "mae": round(mae, 3),
            "rmse": round(rmse, 3),
        }

    # ============================================================
    # 5. PILIH MODEL TERBAIK BERDASARKAN MAE
    # ============================================================

    best_model_name = min(
        metrics,
        key=lambda name: metrics[name]["mae"]
    )

    # ============================================================
    # 6. RETRAIN MODEL TERBAIK DENGAN SELURUH DATA
    # ============================================================

    best_model = _build_model(
        best_model_name
    )

    X_all = prepared[feat_cols].values
    y_all = prepared["energy"].values

    best_model.fit(
        X_all,
        y_all
    )

    # ============================================================
    # 7. SIMPAN MODEL BUNDLE
    # ============================================================

    model_output_path = Path(
        model_output_path
    )

    model_output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        {
            "model": best_model,
            "model_name": best_model_name,
            "feature_columns": feat_cols,
            "metrics": metrics,
        },
        model_output_path,
    )

    # ============================================================
    # 8. RETURN HASIL
    # ============================================================

    return {
        "best_model": best_model_name,
        "metrics": metrics,
        "train_rows": len(train_df),
        "test_rows": len(test_df),
        "feature_columns": feat_cols,
    }