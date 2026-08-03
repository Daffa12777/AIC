"""
Training Forecast Engine untuk prediksi konsumsi energi.
Melatih tiga kandidat model (RandomForest, XGBoost, LightGBM), memilih terbaik
berdasarkan RMSE pada split berbasis waktu (tanpa kebocoran data).
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
    if name == "random_forest":
        return RandomForestRegressor(**MODEL_CONFIGS[name])
    if name == "xgboost":
        return XGBRegressor(**MODEL_CONFIGS[name])
    if name == "lightgbm":
        return LGBMRegressor(**MODEL_CONFIGS[name])
    raise ValueError(f"Model tidak dikenali: {name}")


def _prepare_training_frame(df: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for period, group in df.groupby("period"):
        feat = build_features(group, target="energy")
        frames.append(feat)
    combined = pd.concat(frames, ignore_index=True)
    combined = combined.dropna().reset_index(drop=True)
    return combined


def train_and_select_best_model(df: pd.DataFrame, model_output_path: Path) -> dict:
    """
    Latih & pilih model terbaik untuk prediksi energi.
    Menyimpan bundle model ke model_output_path.
    """
    prepared = _prepare_training_frame(df)
    if len(prepared) < 10:
        raise ValueError("Data tidak cukup untuk melatih model (minimal ~10 baris setelah feature engineering).")

    feat_cols = feature_columns(prepared, target="energy")
    X = prepared[feat_cols].values
    y = prepared["energy"].values

    split_idx = int(len(prepared) * (1 - TEST_SIZE_RATIO))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    metrics = {}
    trained = {}
    for name in MODEL_CONFIGS:
        model = _build_model(name)
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        rmse = float(np.sqrt(mean_squared_error(y_test, pred)))
        mae = float(mean_absolute_error(y_test, pred))
        metrics[name] = {"mae": round(mae, 3), "rmse": round(rmse, 3)}
        trained[name] = model

    best_model_name = min(metrics, key=lambda k: metrics[k]["rmse"])

    # Latih ulang model terbaik pada seluruh data agar optimal untuk inferensi.
    best_model = _build_model(best_model_name)
    best_model.fit(X, y)

    Path(model_output_path).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {"model": best_model, "model_name": best_model_name, "feature_columns": feat_cols},
        model_output_path,
    )

    return {"best_model": best_model_name, "metrics": metrics}
