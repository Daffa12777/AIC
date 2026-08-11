"""Service layer untuk Cost, Anomaly, dan Recommendation.

Seluruh pemrosesan bersifat sinkron. Hasil dikembalikan langsung ke pemanggil
tanpa dipersistkan ke database maupun dicatat sebagai riwayat penggunaan
(sesuai batasan ruang lingkup MVP penyisihan).
"""
import os

import requests
import pandas as pd
from sqlalchemy.orm import Session

from forecast_engine.cost_estimator import estimate_production_cost, build_daily_cost_series
from anomaly_detection.detector import detect_energy_anomalies
from decision_report.insight_generator import generate_cost_insight, generate_energy_insight
from preprocessing.cleaner import clean_dataset

from app.core.config import settings
from app.core.exceptions import DatasetValidationError
from app.services.forecast_service import get_energy_forecast_series, _load_dataset


def run_cost_analysis(db: Session, dataset_id: str, period: str, horizon_days: int, energy_tariff: float | None) -> dict:
    forecast_df, clean = get_energy_forecast_series(db, dataset_id, period, horizon_days)
    sub = clean[clean["period"] == period]

    avg_volume = float(sub["production_volume"].mean()) if "production_volume" in sub.columns else 1.0
    avg_material = float(sub["raw_material_cost"].mean()) if "raw_material_cost" in sub.columns else 0.0
    tariff = energy_tariff if energy_tariff else settings.DEFAULT_ENERGY_TARIFF

    forecast_energy = forecast_df["energy"].tolist()
    cost = estimate_production_cost(forecast_energy, avg_volume, avg_material, tariff)
    insight = generate_cost_insight(cost)

    historical_cost, forecast_cost = build_daily_cost_series(
        sub, forecast_energy, forecast_df["date"].tolist(), tariff, avg_material,
    )

    return {
        "dataset_id": dataset_id,
        "period": period,
        **cost,
        "historical_cost": historical_cost,
        "forecast_cost": forecast_cost,
        "insight": insight,
    }


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

    return {
        "dataset_id": dataset_id,
        "period": period,
        "total_anomalies": len(anomalies),
        "anomalies": anomaly_dicts,
        "narrative": narrative,
    }


def run_recommendation(db: Session, dataset_id: str, period: str, horizon_days: int) -> dict:
    forecast_df, clean = get_energy_forecast_series(db, dataset_id, period, horizon_days)
    sub = clean[clean["period"] == period]

    forecast_energy = forecast_df["energy"].tolist()
    energy_insight = generate_energy_insight(pd.Series(forecast_energy).values, None, None)

    if hasattr(energy_insight, "model_dump"):
        energy_insight_dict = energy_insight.model_dump()
    elif hasattr(energy_insight, "dict"):
        energy_insight_dict = energy_insight.dict()
    else:
        energy_insight_dict = dict(energy_insight)

    avg_volume = float(sub["production_volume"].mean()) if "production_volume" in sub.columns else 1.0
    avg_material = float(sub["raw_material_cost"].mean()) if "raw_material_cost" in sub.columns else 0.0
    cost = estimate_production_cost(forecast_energy, avg_volume, avg_material, settings.DEFAULT_ENERGY_TARIFF)

    anomalies = detect_energy_anomalies(clean, period)

    baseline = 0.0
    if "unit_cost" in sub.columns and sub["unit_cost"].notna().any():
        baseline = float(sub["unit_cost"].mean())

    # Rekomendasi dihasilkan oleh model bahasa hasil fine-tune (Qwen2.5-1.5B-Instruct,
    # dijalankan pada service ml-engine terpisah via HTTP). Inferensi LLM lokal memakan
    # waktu, sehingga diberi toleransi timeout 120 detik.
    ml_engine_url = os.getenv("ML_ENGINE_URL", "http://ml-engine:8000")

    try:
        response = requests.post(
            f"{ml_engine_url}/api/recommendation",
            json={
                "energy_insight": energy_insight_dict,
                "cost": cost,
                "anomaly_count": len(anomalies),
                "baseline": baseline,
            },
            timeout=120,
        )
        response.raise_for_status()
        rec_data = response.json()
    except requests.exceptions.RequestException as e:
        rec_data = {
            "priority_level": "Sedang",
            "summary": "AI Recommendation Engine gagal merespons.",
            "reasoning": f"Sistem tidak dapat terhubung ke ml-engine: {str(e)}",
            "action_items": ["Pastikan container ml-engine menyala", "Periksa log ml-engine"],
            "caveat": "Ini adalah pesan error fallback otomatis.",
        }

    return {
        "dataset_id": dataset_id,
        "period": period,
        "priority_level": rec_data.get("priority_level", "Sedang"),
        "summary": rec_data.get("summary", ""),
        "reasoning": rec_data.get("reasoning", ""),
        "action_items": rec_data.get("action_items", []),
        "caveat": rec_data.get("caveat", ""),
    }
