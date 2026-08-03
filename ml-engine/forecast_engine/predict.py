"""
Inference Forecast Engine: prediksi konsumsi energi multi-langkah ke depan
secara rekursif untuk satu atau beberapa period.
"""
from pathlib import Path

import joblib
import pandas as pd

from feature_engineering.features import build_features, feature_columns


class ModelNotFoundError(Exception):
    pass


def _load_bundle(model_path: Path) -> dict:
    if not Path(model_path).exists():
        raise ModelNotFoundError(f"Model belum dilatih untuk konfigurasi ini: {model_path}")
    return joblib.load(model_path)


def _forecast_one_period(period_df: pd.DataFrame, model, feat_cols: list[str], horizon: int) -> list[dict]:
    history = period_df.sort_values("date").copy()
    period_name = history["period"].iloc[0]
    results = []

    last_date = history["date"].max()
    freq_days = 1

    for step in range(horizon):
        feat = build_features(history, target="energy")
        latest = feat.iloc[[-1]]
        X = latest.reindex(columns=feat_cols, fill_value=0).values
        pred = float(model.predict(X)[0])
        pred = max(pred, 0.0)

        next_date = last_date + pd.Timedelta(days=freq_days * (step + 1))
        results.append({"date": next_date, "period": period_name, "energy": pred})

        new_row = {"date": next_date, "period": period_name, "energy": pred}
        for opt in ["production_volume", "raw_material_cost", "unit_cost"]:
            if opt in history.columns:
                new_row[opt] = history[opt].iloc[-1]
        history = pd.concat([history, pd.DataFrame([new_row])], ignore_index=True)

    return results


def predict(df: pd.DataFrame, periods: list[str] | None, horizon_days: int, model_path: Path) -> pd.DataFrame:
    bundle = _load_bundle(model_path)
    model = bundle["model"]
    feat_cols = bundle["feature_columns"]

    target_periods = periods if periods else list(df["period"].unique())
    all_results = []
    for period in target_periods:
        period_df = df[df["period"] == period]
        if period_df.empty:
            continue
        all_results.extend(_forecast_one_period(period_df, model, feat_cols, horizon_days))

    return pd.DataFrame(all_results)
