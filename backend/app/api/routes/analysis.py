"""Endpoint analisis sinkron: forecast energi, cost, anomaly, recommendation."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.schemas import (
    ForecastRequest, ForecastResponse,
    CostRequest, CostResponse,
    AnomalyRequest, AnomalyResponse,
    RecommendationRequest, RecommendationResponse,
)
from app.services.forecast_service import run_forecast
from app.services.analysis_service import (
    run_cost_analysis, run_anomaly_scan, run_recommendation,
)
from app.core.exceptions import DatasetValidationError, ModelNotTrainedError

router = APIRouter(tags=["analysis"])


@router.post("/forecast/", response_model=ForecastResponse)
def forecast(req: ForecastRequest, db: Session = Depends(get_db)):
    try:
        return run_forecast(db, req.dataset_id, req.periods, req.horizon_days, req.retrain)
    except (DatasetValidationError, ModelNotTrainedError) as e:
        raise HTTPException(status_code=422, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cost/", response_model=CostResponse)
def cost(req: CostRequest, db: Session = Depends(get_db)):
    try:
        return run_cost_analysis(db, req.dataset_id, req.period, req.horizon_days, req.energy_tariff)
    except DatasetValidationError as e:
        raise HTTPException(status_code=422, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/anomaly/", response_model=AnomalyResponse)
def anomaly(req: AnomalyRequest, db: Session = Depends(get_db)):
    try:
        return run_anomaly_scan(db, req.dataset_id, req.period)
    except DatasetValidationError as e:
        raise HTTPException(status_code=422, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommend/", response_model=RecommendationResponse)
def recommend(req: RecommendationRequest, db: Session = Depends(get_db)):
    try:
        return run_recommendation(db, req.dataset_id, req.period, req.horizon_days)
    except DatasetValidationError as e:
        raise HTTPException(status_code=422, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
