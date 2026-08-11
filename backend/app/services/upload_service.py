"""Upload Service: menjembatani endpoint /upload dengan Smart Data Adapter."""
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from data_adapter.adapter import run_smart_data_adapter
from app.core.config import settings
from app.db.models import Dataset


def save_and_process_upload(db: Session, filename: str, file_bytes: bytes) -> dict:
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    raw_path = upload_dir / filename
    with open(raw_path, "wb") as f:
        f.write(file_bytes)

    result = run_smart_data_adapter(str(raw_path))

    # Simpan versi terstandardisasi sebagai CSV agar mudah dibaca ulang.
    standardized_path = upload_dir / f"{Path(filename).stem}_standardized.csv"
    result.dataframe.to_csv(standardized_path, index=False)

    mapping_dicts = [
        {
            "original_column": m.original_column,
            "mapped_to": m.mapped_to,
            "method": m.method,
            "confidence": m.confidence,
        }
        for m in result.mapping
    ]

    dataset = Dataset(
        filename=filename,
        storage_path=str(standardized_path),
        row_count=len(result.dataframe),
        column_mapping=mapping_dicts,
        is_valid=result.is_valid,
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    preview = result.dataframe.head(5).copy()
    for col in preview.columns:
        if pd.api.types.is_datetime64_any_dtype(preview[col]):
            preview[col] = preview[col].astype(str)

    return {
        "dataset_id": dataset.id,
        "filename": filename,
        "row_count": len(result.dataframe),
        "mapping": mapping_dicts,
        "missing_required_columns": result.missing_required_columns,
        "needs_manual_confirmation": result.needs_manual_confirmation,
        "is_valid": result.is_valid,
        "preview": preview.to_dict(orient="records"),
    }
