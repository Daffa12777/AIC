# Arsitektur AlumiSight AI

## Tiga Lapis Modular

### 1. ML Engine (`ml-engine/`)
- **data_adapter/** — Smart Data Adapter (dictionary + fuzzy matching, tanpa LLM)
- **preprocessing/** — pembersihan & persiapan data
- **feature_engineering/** — lag, rolling statistics, fitur kalender
- **forecast_engine/** — training 3 model (RF/XGB/LGBM), pemilihan terbaik via RMSE, prediksi rekursif; cost_estimator untuk biaya produksi
- **anomaly_detection/** — Isolation Forest untuk deteksi pemborosan energi
- **recommendation_engine/** — penggabungan sinyal menjadi rekomendasi berbasis rule
- **decision_report/** — insight_generator (narasi Bahasa Indonesia)

### 2. Backend (`backend/`)
FastAPI dengan 6 endpoint: `/upload`, `/forecast`, `/cost`, `/anomaly`, `/recommend`, `/dashboard`.
Service layer memisahkan logika bisnis dari route. SQLAlchemy untuk persistensi riwayat.

### 3. Frontend (`frontend/`)
Next.js App Router. Satu halaman per kapabilitas inti, memanggil API melalui `src/lib/api.ts`.

## Keputusan Desain

- **Tanpa LLM di Smart Data Adapter** — agar ringan dan dapat dijalankan sepenuhnya secara lokal tanpa API eksternal.
- **Training difilter per lini produksi** — training hanya pada period yang diminta, bukan seluruh dataset, agar performa tetap cepat di CPU biasa.
- **Model di-cache per (dataset, period)** — inferensi berikutnya tidak melatih ulang model.
