"""Model database (tabel) AlumiSight AI."""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text

from app.db.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String, primary_key=True, default=gen_uuid)
    filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    row_count = Column(Integer, default=0)
    column_mapping = Column(JSON, default=list)
    is_valid = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ForecastResult(Base):
    __tablename__ = "forecast_results"

    id = Column(String, primary_key=True, default=gen_uuid)
    dataset_id = Column(String, nullable=False)
    best_model = Column(String, nullable=True)
    metrics = Column(JSON, nullable=True)
    horizon_days = Column(Integer, default=30)
    forecast_data = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)


class CostResult(Base):
    __tablename__ = "cost_results"

    id = Column(String, primary_key=True, default=gen_uuid)
    dataset_id = Column(String, nullable=False)
    period = Column(String, nullable=False)
    cost_data = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)


class AnomalyResult(Base):
    __tablename__ = "anomaly_results"

    id = Column(String, primary_key=True, default=gen_uuid)
    dataset_id = Column(String, nullable=False)
    period = Column(String, nullable=True)
    anomalies = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)


class RecommendationResult(Base):
    __tablename__ = "recommendation_results"

    id = Column(String, primary_key=True, default=gen_uuid)
    dataset_id = Column(String, nullable=False)
    period = Column(String, nullable=False)
    priority_level = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    reasoning = Column(Text, nullable=True)
    action_items = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)


class ActivityHistory(Base):
    __tablename__ = "activity_history"

    id = Column(String, primary_key=True, default=gen_uuid)
    dataset_id = Column(String, nullable=True)
    action = Column(String, nullable=False)
    detail = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
