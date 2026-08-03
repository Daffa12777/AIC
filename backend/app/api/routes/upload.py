"""Endpoint upload dataset."""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.schemas import UploadResponse
from app.services.upload_service import save_and_process_upload
from app.core.exceptions import DatasetValidationError

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/", response_model=UploadResponse)
async def upload_dataset(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith((".xlsx", ".xls", ".csv", ".tsv")):
        raise HTTPException(status_code=400, detail="Format file harus .xlsx, .xls, .csv, atau .tsv")
    try:
        content = await file.read()
        return save_and_process_upload(db, file.filename, content)
    except DatasetValidationError as e:
        raise HTTPException(status_code=422, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memproses file: {str(e)}")
