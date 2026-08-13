# Arsitektur AlumiSight AI

## Tiga Lapis Modular + Basis Data

### 1. ML Engine (`ml-engine/`) — service Docker terpisah
- **data_adapter/** — Smart Data Adapter (dictionary + fuzzy matching berbasis rapidfuzz, tanpa LLM)
- **preprocessing/** — pembersihan & persiapan data (dropna required, interpolasi opsional)
- **feature_engineering/** — lag, rolling statistics, fitur kalender
- **forecast_engine/** — training 3 model (Random Forest, XGBoost, LightGBM), pemilihan terbaik via MAE, prediksi rekursif; `cost_estimator` untuk biaya produksi berbasis rumus terbuka
- **anomaly_detection/** — Isolation Forest untuk deteksi pemborosan energi
- **recommendation_engine/** — LLM lokal Qwen2.5-1.5B-Instruct hasil fine-tune (LoRA + unsloth, GGUF q4_k_m) via `llama-cpp-python`; menerima ringkasan hasil analisis dan mengembalikan rekomendasi JSON terstruktur (priority_level, reasoning, action_items)
- **decision_report/** — insight_generator (narasi Bahasa Indonesia untuk tren, volatilitas, dan biaya)

### 2. Backend (`backend/`) — FastAPI
5 endpoint sinkron: `/upload/`, `/forecast/`, `/cost/`, `/anomaly/`, `/recommend/`.
Service layer memisahkan logika bisnis dari route. SQLAlchemy hanya menyimpan **metadata dataset** (id, filename, storage_path, row_count, column_mapping, is_valid). Tidak ada persistensi riwayat penggunaan maupun hasil analisis — sesuai batasan MVP rulebook hlm 15.

### 3. Frontend (`frontend/`) — Next.js
App Router dengan satu halaman per kapabilitas inti (upload, forecast, cost, anomaly, recommendation), memanggil API melalui `src/lib/api.ts`. Alur interaksi: input tunggal → output AI.

### 4. Basis Data (`db`) — PostgreSQL 16
Menyimpan metadata dataset agar dapat direferensikan lewat dataset_id antar langkah analisis.

## Keputusan Desain

- **Tanpa LLM di Smart Data Adapter** — kombinasi kamus + fuzzy matching cukup untuk pemetaan kolom dan lebih deterministik.
- **Training difilter per lini produksi** — training hanya pada period yang diminta, bukan seluruh dataset, agar cepat di CPU biasa.
- **Trend & volatility dihitung dari data historis** — bukan dari forecast, karena model tree-based cenderung konvergen ke mean pada horizon panjang.
- **LLM Rekomendasi dijalankan lokal** — bobot GGUF q4_k_m tersimpan di repo, dijalankan via `llama-cpp-python` di service ml-engine terpisah. Tanpa API eksternal, menjamin reprodusibilitas saat panitia melakukan verifikasi silang.
- **Parser JSON berlapis** — output LLM diproses dengan tiga lapis parser (regex block, closing bracket fix, ekstraktor manual) sehingga sistem tetap berfungsi meskipun output model tidak sempurna.
- **Batasan MVP** — tanpa scheduler, background jobs, halaman riwayat, dashboard analitik lanjut, atau auto-tuning, sesuai rulebook hlm 15.