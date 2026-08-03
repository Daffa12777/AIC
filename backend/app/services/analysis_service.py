"""Service layer untuk Cost, Anomaly, Recommendation, dan Dashboard."""
import pandas as pd
from sqlalchemy.orm import Session

from preprocessing.cleaner import clean_dataset
from forecast_engine.cost_estimator import estimate_production_cost
from anomaly_detection.detector import detect_energy_anomalies
from decision_report.insight_generator import generate_cost_insight
from recommendation_engine.recommender import build_recommendation
from decision_report.insight_generator import generate_energy_insight

from app.core.config import settings
from app.core.exceptions import DatasetValidationError
from app.services.forecast_service import get_energy_forecast_series, _load_dataset
from app.db.models import (
    Dataset, ForecastResult, CostResult, AnomalyResult,
    RecommendationResult, ActivityHistory,
)


def run_cost_analysis(db: Session, dataset_id: str, period: str, horizon_days: int, energy_tariff: float | None) -> dict:
    forecast_energy, clean = get_energy_forecast_series(db, dataset_id, period, horizon_days)
    sub = clean[clean["period"] == period]

    avg_volume = float(sub["production_volume"].mean()) if "production_volume" in sub.columns else 1.0
    avg_material = float(sub["raw_material_cost"].mean()) if "raw_material_cost" in sub.columns else 0.0
    tariff = energy_tariff if energy_tariff else settings.DEFAULT_ENERGY_TARIFF

    cost = estimate_production_cost(forecast_energy, avg_volume, avg_material, tariff)
    insight = generate_cost_insight(cost)

    db.add(CostResult(dataset_id=dataset_id, period=period, cost_data=cost))
    db.add(ActivityHistory(dataset_id=dataset_id, action="cost", detail={"period": period}))
    db.commit()

    return {"dataset_id": dataset_id, "period": period, **cost, "insight": insight}


def run_anomaly_scan(db: Session, dataset_id: str, period: str | None) -> dict:
    raw = _load_dataset(db, dataset_id)
    clean = clean_dataset(raw)

    anomalies = detect_energy_anomalies(clean, period)
    anomaly_dicts = [
        {"date": a.date, "period": a.period, "energy": a.energy, "deviation_pct": a.deviation_pct}
        for a in anomalies
    ]

    if len(anomalies) == 0:
        narrative = "Tidak terdeteksi anomali konsumsi energi yang signifikan pada data ini."
    else:
        scope = f"pada {period}" if period else "pada seluruh lini produksi"
        narrative = (
            f"Terdeteksi {len(anomalies)} titik konsumsi energi anomali {scope}. Anomali dengan deviasi "
            f"terbesar mencapai {anomalies[0].deviation_pct:+.1f}% dari rata-rata historis, yang perlu "
            f"ditelusuri sebagai indikasi potensi pemborosan energi atau gangguan operasional."
        )

    db.add(AnomalyResult(dataset_id=dataset_id, period=period, anomalies=anomaly_dicts))
    db.add(ActivityHistory(dataset_id=dataset_id, action="anomaly", detail={"period": period}))
    db.commit()

    return {
        "dataset_id": dataset_id,
        "period": period,
        "total_anomalies": len(anomalies),
        "anomalies": anomaly_dicts,
        "narrative": narrative,
    }


def run_recommendation(db: Session, dataset_id: str, period: str, horizon_days: int) -> dict:
    forecast_energy, clean = get_energy_forecast_series(db, dataset_id, period, horizon_days)
    sub = clean[clean["period"] == period]

    energy_insight = generate_energy_insight(pd.Series(forecast_energy).values, None, None)

    avg_volume = float(sub["production_volume"].mean()) if "production_volume" in sub.columns else 1.0
    avg_material = float(sub["raw_material_cost"].mean()) if "raw_material_cost" in sub.columns else 0.0
    cost = estimate_production_cost(forecast_energy, avg_volume, avg_material, settings.DEFAULT_ENERGY_TARIFF)

    anomalies = detect_energy_anomalies(clean, period)

    # Baseline: rata-rata unit_cost historis bila tersedia.
    baseline = None
    if "unit_cost" in sub.columns and sub["unit_cost"].notna().any():
        baseline = float(sub["unit_cost"].mean())

    rec = build_recommendation(energy_insight, cost, len(anomalies), baseline_cost_per_unit=baseline)

    db.add(RecommendationResult(
        dataset_id=dataset_id, period=period, priority_level=rec.priority_level,
        summary=rec.summary, reasoning=rec.reasoning, action_items=rec.action_items,
    ))
    db.add(ActivityHistory(dataset_id=dataset_id, action="recommend", detail={"period": period}))
    db.commit()

    return {
        "dataset_id": dataset_id,
        "period": period,
        "priority_level": rec.priority_level,
        "summary": rec.summary,
        "reasoning": rec.reasoning,
        "action_items": rec.action_items,
        "caveat": rec.caveat,
    }


def get_dashboard_summary(db: Session) -> dict:
    recent = (
        db.query(ActivityHistory)
        .order_by(ActivityHistory.created_at.desc())
        .limit(8)
        .all()
    )
    return {
        "total_datasets": db.query(Dataset).count(),
        "total_forecasts_run": db.query(ForecastResult).count(),
        "total_cost_analyses": db.query(CostResult).count(),
        "total_anomaly_scans": db.query(AnomalyResult).count(),
        "total_recommendations": db.query(RecommendationResult).count(),
        "recent_activity": [
            {"action": a.action, "created_at": a.created_at.strftime("%Y-%m-%d %H:%M")}
            for a in recent
        ],
    }
