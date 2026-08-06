"""
Forecast Service (konsumsi energi)
Model dilatih per dataset+period (cached di disk). Training difilter hanya pada
period yang diminta agar performa tidak terbebani period yang tidak relevan.
"""
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from preprocessing.cleaner import clean_dataset
from forecast_engine.train import train_and_select_best_model
from forecast_engine.predict import predict, ModelNotFoundError
from decision_report.insight_generator import generate_energy_insight
from app.core.config import settings
from app.core.exceptions import DatasetValidationError, ModelNotTrainedError
from app.db.models import Dataset, ForecastResult, ActivityHistory

MODEL_DIR = Path(settings.UPLOAD_DIR).parent / "models"


def _load_dataset(db: Session, dataset_id: str) -> pd.DataFrame:
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if dataset is None:
        raise DatasetValidationError(f"Dataset dengan id {dataset_id} tidak ditemukan.")
    if not dataset.is_valid:
        raise DatasetValidationError("Dataset belum valid (kolom wajib belum lengkap).")
    return pd.read_csv(dataset.storage_path, parse_dates=["date"])


def _model_path_for(dataset_id: str, periods: list[str] | None) -> Path:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    if periods:
        scope = "-".join(sorted(periods))[:80]
        return MODEL_DIR / f"{dataset_id}_{scope}.joblib"
    return MODEL_DIR / f"{dataset_id}_all.joblib"


def run_forecast(db: Session, dataset_id: str, periods: list[str] | None, horizon_days: int, retrain: bool = False) -> dict:
    raw = _load_dataset(db, dataset_id)
    clean = clean_dataset(raw)

    training_df = clean
    if periods:
        training_df = clean[clean["period"].isin(periods)].copy()
        if training_df.empty:
            raise DatasetValidationError(f"Period {periods} tidak ditemukan pada dataset ini.")

    model_path = _model_path_for(dataset_id, periods)
    train_metrics = None
    best_model_name = None

    if retrain or not model_path.exists():
        tr = train_and_select_best_model(training_df, model_output_path=model_path)
        train_metrics = tr["metrics"]
        best_model_name = tr["best_model"]

    try:
        forecast_df = predict(training_df, periods=periods, horizon_days=horizon_days, model_path=model_path)
    except ModelNotFoundError as e:
        raise ModelNotTrainedError(str(e))

    if train_metrics is None:
        import joblib
        cached = joblib.load(model_path)
        best_model_name = cached.get("model_name")
        train_metrics = cached.get("metrics")

    insight = generate_energy_insight(forecast_df["energy"].values, best_model_name, train_metrics)

    historical_df = training_df[["date", "period", "energy"]].sort_values("date")

    db.add(ForecastResult(
        dataset_id=dataset_id, best_model=best_model_name, metrics=train_metrics,
        horizon_days=horizon_days,
        forecast_data=forecast_df.assign(date=forecast_df["date"].astype(str)).to_dict(orient="records"),
    ))
    db.add(ActivityHistory(dataset_id=dataset_id, action="forecast", detail={"horizon_days": horizon_days}))
    db.commit()

    return {
        "dataset_id": dataset_id,
        "best_model": best_model_name,
        "metrics": train_metrics,
        "horizon_days": horizon_days,
        "historical": historical_df.to_dict(orient="records"),
        "forecast": forecast_df.to_dict(orient="records"),
        "insight": insight,
    }


def get_energy_forecast_series(db: Session, dataset_id: str, period: str, horizon_days: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Ambil deret forecast energi untuk satu period (dipakai cost & recommendation)."""
    raw = _load_dataset(db, dataset_id)
    clean = clean_dataset(raw)
    training_df = clean[clean["period"] == period].copy()
    if training_df.empty:
        raise DatasetValidationError(f"Period '{period}' tidak ditemukan pada dataset ini.")

    model_path = _model_path_for(dataset_id, [period])
    if not model_path.exists():
        train_and_select_best_model(training_df, model_output_path=model_path)

    forecast_df = predict(training_df, periods=[period], horizon_days=horizon_days, model_path=model_path)
    return forecast_df, clean
