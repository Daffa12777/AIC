"""Pydantic Schemas — validasi request & response seluruh endpoint API."""
from datetime import datetime
from pydantic import BaseModel, Field


# ---------- Upload ----------

class ColumnMappingSchema(BaseModel):
    original_column: str
    mapped_to: str | None
    method: str
    confidence: float


class UploadResponse(BaseModel):
    dataset_id: str
    filename: str
    row_count: int
    mapping: list[ColumnMappingSchema]
    missing_required_columns: list[str]
    needs_manual_confirmation: bool
    is_valid: bool
    preview: list[dict]


# ---------- Forecast (Energy) ----------

class ForecastRequest(BaseModel):
    dataset_id: str
    periods: list[str] | None = None
    horizon_days: int = Field(default=30, ge=1, le=180)
    retrain: bool = False


class ForecastPoint(BaseModel):
    date: datetime
    period: str
    energy: float


class EnergyInsight(BaseModel):
    trend_label: str
    change_pct: float
    volatility_label: str
    coefficient_of_variation: float
    average_energy: float
    narrative: str
    recommendation_note: str
    model_note: str | None = None


class ForecastResponse(BaseModel):
    dataset_id: str
    best_model: str | None = None
    metrics: dict | None = None
    horizon_days: int
    forecast: list[ForecastPoint]
    insight: EnergyInsight | None = None


# ---------- Cost ----------

class CostRequest(BaseModel):
    dataset_id: str
    period: str
    horizon_days: int = Field(default=30, ge=1, le=180)
    energy_tariff: float | None = None


class CostInsight(BaseModel):
    narrative: str
    recommendation_note: str


class CostResponse(BaseModel):
    dataset_id: str
    period: str
    total_energy_kwh: float
    energy_cost: float
    material_cost: float
    total_production_cost: float
    estimated_cost_per_unit: float
    energy_cost_share: float
    periods: int
    insight: CostInsight | None = None


# ---------- Anomaly ----------

class AnomalyRequest(BaseModel):
    dataset_id: str
    period: str | None = None


class AnomalyPointSchema(BaseModel):
    date: str
    period: str
    energy: float
    deviation_pct: float


class AnomalyResponse(BaseModel):
    dataset_id: str
    period: str | None
    total_anomalies: int
    anomalies: list[AnomalyPointSchema]
    narrative: str


# ---------- Recommendation ----------

class RecommendationRequest(BaseModel):
    dataset_id: str
    period: str
    horizon_days: int = Field(default=30, ge=1, le=180)


class RecommendationResponse(BaseModel):
    dataset_id: str
    period: str
    priority_level: str
    summary: str
    reasoning: str
    action_items: list[str]
    caveat: str


# ---------- Dashboard ----------

class DashboardSummary(BaseModel):
    total_datasets: int
    total_forecasts_run: int
    total_cost_analyses: int
    total_anomaly_scans: int
    total_recommendations: int
    recent_activity: list[dict]
