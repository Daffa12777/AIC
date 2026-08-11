"""Model database (tabel) AlumiSight AI.

MVP penyisihan bersifat sinkron: hanya menyimpan metadata dataset yang diunggah
agar dapat direferensikan lewat dataset_id antar langkah analisis. Tidak ada
pencatatan riwayat penggunaan maupun penyimpanan hasil analisis (sesuai batasan
ruang lingkup MVP).
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON

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
