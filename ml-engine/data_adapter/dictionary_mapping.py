"""
Kamus sinonim kolom untuk Smart Data Adapter (domain: manufaktur aluminium).
Memetakan berbagai variasi penamaan kolom (ID/EN) ke skema standar.
"""

COLUMN_SYNONYMS = {
    "date": [
        "date", "tanggal", "tgl", "waktu", "periode tanggal", "tanggal produksi",
        "tanggal pencatatan", "production date", "record date", "day",
    ],
    "period": [
        "period", "periode", "lini", "line", "lini produksi", "production line",
        "kode periode", "id periode", "unit", "pot line", "potline",
    ],
    "energy": [
        "energy", "energi", "konsumsi energi", "energy consumption", "kwh",
        "pemakaian listrik", "konsumsi listrik", "power", "power consumption",
        "listrik", "energi listrik", "energy_kwh", "daya",
    ],
    "production_volume": [
        "production_volume", "produksi", "volume produksi", "output", "tonase",
        "jumlah produksi", "hasil produksi", "production", "volume", "ton",
        "output ton", "produksi ton",
    ],
    "raw_material_cost": [
        "raw_material_cost", "biaya bahan baku", "biaya alumina", "biaya bauksit",
        "material cost", "harga bahan baku", "cost bahan baku", "biaya material",
    ],
    "unit_cost": [
        "unit_cost", "biaya per unit", "biaya produksi", "hpp", "cost per ton",
        "biaya per ton", "production cost", "harga pokok", "harga pokok produksi",
    ],
}


def build_reverse_lookup() -> dict:
    """Bangun mapping {sinonim_lowercase: kolom_standar}."""
    reverse = {}
    for standard, synonyms in COLUMN_SYNONYMS.items():
        for syn in synonyms:
            reverse[syn.lower().strip()] = standard
    return reverse
