"""
Preprocessing pipeline: pembersihan dan persiapan data terstandardisasi
sebelum masuk ke feature engineering dan model.
"""
import pandas as pd


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Bersihkan dataset terstandardisasi:
    - parse kolom date
    - buang baris tanpa date/period/energy
    - konversi tipe numerik
    - urutkan berdasarkan period lalu date
    - isi missing numerik opsional dengan interpolasi/median
    """
    clean = df.copy()

    clean["date"] = pd.to_datetime(clean["date"], errors="coerce")
    clean = clean.dropna(subset=["date", "period", "energy"])

    clean["energy"] = pd.to_numeric(clean["energy"], errors="coerce")
    clean = clean.dropna(subset=["energy"])

    for opt in ["production_volume", "raw_material_cost", "unit_cost"]:
        if opt in clean.columns:
            clean[opt] = pd.to_numeric(clean[opt], errors="coerce")

    clean = clean.sort_values(["period", "date"]).reset_index(drop=True)

    # Interpolasi missing opsional per period, sisanya isi median global.
    for opt in ["production_volume", "raw_material_cost", "unit_cost"]:
        if opt in clean.columns:
            clean[opt] = clean.groupby("period")[opt].transform(
                lambda s: s.interpolate(limit_direction="both")
            )
            if clean[opt].isna().any():
                clean[opt] = clean[opt].fillna(clean[opt].median())

    # Buang duplikat (period, date), pertahankan yang terakhir.
    clean = clean.drop_duplicates(subset=["period", "date"], keep="last").reset_index(drop=True)
    return clean
