"""
Konfigurasi global untuk ML Engine AlumiSight AI.
Seluruh path dan parameter dapat dioverride lewat environment variable.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_DIR = Path(os.getenv("MODEL_DIR", BASE_DIR / "forecast_engine" / "artifacts"))
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Kolom standar yang wajib ada setelah Smart Data Adapter.
# date    : tanggal pencatatan produksi
# period  : identitas periode/lini produksi (mis. "line-1", "2026-01")
# energy  : konsumsi energi listrik (kWh)
REQUIRED_COLUMNS = ["date", "period", "energy"]
# Kolom opsional yang memperkaya analisis bila tersedia.
OPTIONAL_COLUMNS = ["production_volume", "raw_material_cost", "unit_cost"]

# Ambang batas fuzzy matching (0-100). Di bawah ini dianggap tidak cocok.
FUZZY_MATCH_THRESHOLD = 75

# Ambang deviasi (skor anomali IsolationForest) untuk klasifikasi.
ANOMALY_CONTAMINATION = 0.08

# Ambang kategori efisiensi biaya (rasio deviasi terhadap baseline).
COST_THRESHOLD_LOW = 0.05
COST_THRESHOLD_HIGH = 0.15

RANDOM_SEED = 42
