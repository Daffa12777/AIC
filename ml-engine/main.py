from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, Any
from recommendation_engine.recommender import build_final_recommendation

app = FastAPI()

# Bikin format data yang fleksibel
class FactoryData(BaseModel):
    energy_insight: Dict[str, Any]
    cost: Dict[str, Any]
    anomaly_count: int
    baseline: Optional[float] = 0.0  # <--- INI KUNCI PERBAIKANNYA (Ubah jadi float)

@app.post("/api/recommendation")
def get_recommendation(data: FactoryData):
    # Panggil fungsi yang ada di recommender.py
    hasil = build_final_recommendation(
        energy_insight=data.energy_insight,
        cost=data.cost,
        anomaly_count=data.anomaly_count,
        baseline=data.baseline
    )
    return hasil