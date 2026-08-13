# AlumiSight AI

**AI Decision Support System for Energy & Production Cost Optimization in Aluminium Manufacturing**

AlumiSight AI membantu pabrik dan smelter aluminium mengubah data operasional menjadi keputusan yang lebih cerdas: memprediksi konsumsi energi, mengestimasi biaya produksi, mendeteksi pemborosan energi, dan menyusun rekomendasi operasional berbahasa Indonesia melalui LLM lokal hasil fine-tune.

Dikembangkan untuk **AI Innovation Challenge (AIC) COMPFEST 18**, subtema **Smart Manufacturing**.

---

## Prasyarat

Untuk menjalankan dengan Docker (cara yang disarankan), cukup:

- **Git**
- **Docker Desktop** (pastikan status *Engine running*)
- Alokasi memori Docker minimal **6 GB** (LLM lokal membutuhkan ruang inferensi)
- Ruang disk kosong **±4 GB** untuk image dan bobot model

Tidak perlu memasang Python, Node.js, PostgreSQL, maupun runtime model secara manual — seluruh dependensi dibungkus dalam container.

---

## Arsitektur

Proyek terdiri atas empat komponen modular yang berjalan sebagai service Docker terpisah:

- **`ml-engine/`** — Mesin AI: Smart Data Adapter (dictionary + fuzzy matching), Forecast Engine tiga-model (Random Forest, XGBoost, LightGBM), Cost Estimator berbasis rumus terbuka, Anomaly Detection (Isolation Forest), Recommendation Engine berbasis LLM lokal (Qwen2.5-1.5B-Instruct GGUF), dan Insight Generator.
- **`backend/`** — REST API berbasis FastAPI yang mengorkestrasi ML Engine secara sinkron.
- **`frontend/`** — Antarmuka Next.js + TypeScript + Tailwind CSS dengan alur input tunggal → output AI.
- **`db`** — PostgreSQL 16 untuk menyimpan metadata dataset (tanpa riwayat penggunaan atau hasil analisis).

---

## Batasan Ruang Lingkup MVP

Sesuai batasan penyisihan AIC COMPFEST 18, sistem ini secara sengaja **hanya** mengimplementasikan fungsi inti:

- Frontend: alur interaksi input tunggal → output AI. Tanpa halaman riwayat penggunaan, tanpa dashboard analitik tingkat lanjut, tanpa sistem otentikasi kompleks.
- Backend: pemrosesan sinkron. Tanpa background jobs, tanpa automated data logging, tanpa infrastruktur database terdistribusi.
- Model AI: core inference dengan parameter statis saat demo. Tanpa auto-tuning, tanpa bulk testing scripts, tanpa feedback loop otomatis.
- LLM: model open-source (Qwen2.5-1.5B-Instruct) hasil fine-tune sendiri dengan LoRA, dijalankan sepenuhnya lokal via `llama-cpp-python` tanpa API eksternal maupun kunci API.

---

## Menjalankan dengan Docker (disarankan)

1. Clone repositori:

```bash
    git clone https://github.com/Daffa12777/AIC.git
    cd AIC
```

2. Siapkan berkas environment untuk backend:

```bash
    # Windows (PowerShell):
    Copy-Item backend\.env.example backend\.env

    # macOS/Linux:
    cp backend/.env.example backend/.env
```

3. Pastikan Docker Desktop berjalan, lalu:

```bash
    docker compose up --build
```

    Build pertama memakan waktu beberapa menit (mengunduh image dasar dan memasang seluruh dependensi termasuk pustaka LLM lokal).

Setelah seluruh service siap:

- Dashboard: <http://localhost:3000>
- API (dokumentasi Swagger): <http://localhost:8000/docs>
- ML Engine (opsional): <http://localhost:8001/docs>

Untuk menghentikan:

```bash
# Tekan Ctrl + C di terminal, lalu:
docker compose down
```

Untuk build ulang bersih (mis. setelah menarik commit baru):

```bash
docker compose down
docker compose up --build -d
```

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
# Windows (PowerShell):
$env:DATABASE_URL="sqlite:///./dev.db"
$env:PYTHONPATH="..\ml-engine;..\backend"
$env:UPLOAD_DIR="./storage"
$env:ML_ENGINE_URL="http://localhost:8001"

# macOS/Linux:
export DATABASE_URL="sqlite:///./dev.db"
export PYTHONPATH="../ml-engine:../backend"
export UPLOAD_DIR="./storage"
export ML_ENGINE_URL="http://localhost:8001"

python -m uvicorn app.main:app --reload
```

Backend berjalan di <http://localhost:8000>

### ML Engine (service terpisah untuk LLM Rekomendasi)

Pada terminal terpisah:

```bash
cd ml-engine
pip install -r requirements.txt
python main.py
```

ML Engine berjalan di <http://localhost:8001>

> Bobot model `unsloth.Q4_K_M.gguf` harus tersedia di `ml-engine/models/`. Pastikan sudah ter-clone bersama repositori.

### Frontend

Pada terminal terpisah:

```bash
cd frontend
npm install

# Windows (PowerShell):
$env:NEXT_PUBLIC_API_URL="http://localhost:8000"

# macOS/Linux:
export NEXT_PUBLIC_API_URL="http://localhost:8000"

npm run dev
```

Dashboard berjalan di <http://localhost:3000>

---

## Coba Cepat (Quick Demo)

1. Jalankan seluruh service (`docker compose up --build`).
2. Buka <http://localhost:3000>.
3. Ke halaman **Unggah Data**, pilih berkas `demo/datasetDemo.xlsx`.
4. Setelah diproses, Dataset ID otomatis tersimpan dan diteruskan ke halaman berikutnya.
5. Ke halaman **Prediksi Energi** — field Lini Produksi akan otomatis terisi `POT-A`. Klik **Jalankan Prediksi**.
6. Lanjutkan ke **Biaya Produksi**, **Deteksi Anomali**, dan **Rekomendasi** dengan lini produksi yang sama.

> Dataset demo berisi tiga lini produksi (`POT-A`, `POT-B`, `POT-C`), data harian selama satu tahun. Untuk mencoba lini lain, cukup ubah field Lini Produksi di setiap halaman.

---

## Dataset

Untuk kebutuhan demo dan reprodusibilitas, disediakan dataset sintetik yang dikalibrasi terhadap parameter proses nyata industri peleburan aluminium:

- **Berkas**: `demo/datasetDemo.xlsx`
- **Cakupan**: 3 pot line × 365 hari operasi
- **Kolom wajib**: `Tanggal Pencatatan`, `Pot Line`, `Konsumsi Listrik (kWh)`
- **Kolom opsional**: `Volume Produksi (ton)`, `Biaya Bahan Baku (Rp)`, `Biaya per Ton (Rp)`
- **Parameter kalibrasi**: mengacu pada rasio energi spesifik (~14 kWh/kg Al) dan stoikiometri proses Hall-Héroult sebagaimana dilaporkan International Aluminium Institute.
- **Injeksi realisme**: nilai kosong (NaN) acak, anomali energi terinjeksi, hari maintenance, dan variasi musiman.

Smart Data Adapter mampu memetakan nama kolom dari berbagai gaya penulisan (`Pot Line`, `pot-a`, `Line 1`, `Konsumsi Listrik`, `Energy Consumption`, dst.) ke skema internal secara otomatis melalui kombinasi kamus istilah domain dan fuzzy matching.

---

## LLM Fine-Tuning

Recommendation Engine menggunakan model **Qwen2.5-1.5B-Instruct** yang di-fine-tune sendiri pada data domain peleburan aluminium dengan metode **LoRA** (Low-Rank Adaptation) berbasis kerangka kerja **unsloth**. Model kemudian dikuantisasi ke format **GGUF q4_k_m** untuk efisiensi memori dan dijalankan sepenuhnya lokal via `llama-cpp-python`.

**Notebook fine-tuning (Google Colab):**

🔗 **[Buka Notebook Fine-Tune Qwen2.5-1.5B di Google Colab](https://colab.research.google.com/drive/1pG8t98mACKTAWGptybKLw237AkOPod3l)**

Notebook mencakup:

1. Pemuatan model dasar `Qwen/Qwen2.5-1.5B-Instruct` dengan unsloth.
2. Penyusunan dataset instruction-tuning berformat prompt-response domain aluminium.
3. Konfigurasi LoRA (rank, alpha, dropout, target modules).
4. Proses pelatihan dengan `TRL SFTTrainer`.
5. Ekspor bobot hasil fine-tune ke format GGUF q4_k_m.
6. Verifikasi inferensi lokal.

Bobot hasil fine-tune tersimpan di `ml-engine/models/unsloth.Q4_K_M.gguf` dan menjadi bagian dari repositori untuk menjamin reprodusibilitas — panitia dapat menjalankan seluruh sistem lokal tanpa memerlukan proses pelatihan ulang maupun akses API eksternal.

---

## Tech Stack

| Lapisan | Teknologi |
|---------|-----------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| Basis data | PostgreSQL 16 (metadata dataset) |
| ML klasik | scikit-learn, XGBoost, LightGBM |
| Deteksi anomali | Isolation Forest (scikit-learn) |
| Adapter data | rapidfuzz (fuzzy matching), pandas |
| LLM lokal | Qwen2.5-1.5B-Instruct GGUF q4_k_m, llama-cpp-python |
| Fine-tune | unsloth, PEFT (LoRA), TRL SFTTrainer |
| Orkestrasi | Docker Compose |