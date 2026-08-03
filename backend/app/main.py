"""
AlumiSight AI — Backend API
AI Decision Support System for Energy & Production Cost Optimization
in Aluminium Manufacturing.
"""
import sys
from pathlib import Path

# --- Pastikan ml-engine (tempat data_adapter) ada di sys.path ---
_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[2]                    # E:\RISETCPS\AlumiSight-AI
for _p in (_HERE.parents[1], _ROOT / "ml-engine"):   # backend\  &  ml-engine\
    _p = str(_p)
    if _p not in sys.path:
        sys.path.insert(0, _p)
# ----------------------------------------------------------------

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import Base, engine
from app.api.routes import upload, analysis

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("alumisight.backend")

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(analysis.router)


@app.on_event("startup")
def on_startup():
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} ({settings.ENVIRONMENT})")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables siap.")


@app.get("/")
def root():
    return {"app": settings.APP_NAME, "version": settings.APP_VERSION, "status": "running"}


@app.get("/health")
def health():
    return {"status": "ok"}