# AlumiSight AI

**AI Decision Support System for Energy & Production Cost Optimization in Aluminium Manufacturing**

AlumiSight AI membantu pabrik dan smelter aluminium mengubah data operasional menjadi keputusan yang lebih cerdas: memprediksi konsumsi energi, mengestimasi biaya produksi, mendeteksi pemborosan energi, dan menyusun rekomendasi operasional — seluruhnya dalam Bahasa Indonesia.

Dikembangkan untuk **AI Innovation Challenge (AIC) COMPFEST 18**, subtema **Smart Manufacturing**.

---

## Arsitektur

Proyek terdiri atas tiga komponen modular:

- **`ml-engine/`** — Mesin AI: Smart Data Adapter, Forecast Engine (energi), Cost Estimator, Anomaly Detection (Isolation Forest), Recommendation Engine, dan Insight Generator.
- **`backend/`** — REST API berbasis FastAPI yang mengorkestrasi ML Engine dan menyimpan riwayat analisis.
- **`frontend/`** — Dashboard berbasis Next.js + TypeScript + Tailwind CSS.

---

## Menjalankan dengan Docker (disarankan)

Pastikan Docker Desktop berjalan, lalu:

```bash
docker compose up --build
```

Setelah seluruh service siap:

- Dashboard: http://localhost:3000
- API (dokumentasi Swagger): http://localhost:8000/docs

---

## Menjalankan secara manual (tanpa Docker)

### Backend

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt

# Konfigurasi environment (contoh untuk SQLite lokal)
export DATABASE_URL="sqlite:///./dev.db"
export PYTHONPATH="../ml-engine:../backend"
export UPLOAD_DIR="./storage"

python -m uvicorn app.main:app --reload
```

Backend berjalan di http://localhost:8000

### Frontend

Pada terminal terpisah:

```bash
cd frontend
npm install
export NEXT_PUBLIC_API_URL="http://localhost:8000"
npm run dev
```

Dashboard berjalan di http://localhost:3000

---

## Coba Cepat (Quick Demo)

1. Jalankan backend dan frontend (atau `docker compose up --build`).
2. Buka http://localhost:3000.
3. Ke halaman **Unggah Data**, pilih berkas `demo/alumisight_demo_dataset.xlsx`.
4. Setelah diproses, Dataset ID tersimpan otomatis.
5. Ke halaman **Prediksi Energi**, isi Lini Produksi `line-1`, klik **Jalankan Prediksi**.
6. Lanjutkan ke **Biaya Produksi**, **Deteksi Anomali**, dan **Rekomendasi** dengan lini produksi yang sama.

> Dataset demo berisi 3 lini produksi (`line-1`, `line-2`, `line-3`), data harian selama satu tahun.

---

## Alur Data

```
Upload → Smart Data Adapter → Preprocessing → Feature Engineering
      → Forecast Engine (energi) → Cost Estimator
      → Anomaly Detection → Recommendation Engine → Dashboard
```

## Teknologi

| Bagian | Teknologi |
|---|---|
| Frontend | Next.js, TypeScript, Tailwind CSS |
| Backend | FastAPI, SQLAlchemy |
| Machine Learning | scikit-learn, XGBoost, LightGBM |
| Anomaly Detection | Isolation Forest |
| Database | PostgreSQL (Docker) / SQLite (lokal) |
| Deployment | Docker, Docker Compose |

## Skema Kolom

Setelah Smart Data Adapter, dataset dipetakan ke skema standar:

- **Wajib:** `date` (tanggal), `period` (lini produksi), `energy` (konsumsi energi kWh)
- **Opsional:** `production_volume`, `raw_material_cost`, `unit_cost`

Smart Data Adapter memetakan nama kolom apa pun secara otomatis melalui dictionary mapping dan fuzzy matching, sehingga berkas dari berbagai perusahaan tetap dapat diproses tanpa penyesuaian manual.
