"""
Generator dataset demo untuk AlumiSight AI.
Mensimulasikan export data operasional pabrik aluminium: 3 lini produksi,
1 tahun data harian, dengan kolom bernama gaya perusahaan (agar sekaligus
mendemonstrasikan Smart Data Adapter).
"""
import numpy as np
import pandas as pd

RNG = np.random.default_rng(2026)


def generate() -> pd.DataFrame:
    dates = pd.date_range("2025-01-01", periods=365, freq="D")
    lines = ["line-1", "line-2", "line-3"]
    rows = []

    for line in lines:
        base_energy = RNG.uniform(12000, 16000)
        base_volume = RNG.uniform(90, 110)
        for i, d in enumerate(dates):
            trend = i * RNG.uniform(3, 7)
            weekly = 700 * np.sin(i / 7 * 2 * np.pi)
            noise = RNG.normal(0, 350)
            energy = max(base_energy + trend + weekly + noise, 2000)

            volume = max(base_volume + RNG.normal(0, 8), 40)
            material = RNG.uniform(2.1e8, 2.9e8)
            unit_cost = (energy * 1400 + material) / max(volume, 1)

            rows.append({
                "Tanggal": d.strftime("%Y-%m-%d"),
                "Lini Produksi": line,
                "Konsumsi Energi (kWh)": round(energy, 1),
                "Volume Produksi (ton)": round(volume, 1),
                "Biaya Bahan Baku (Rp)": round(material, 0),
                "Biaya per Ton (Rp)": round(unit_cost, 0),
            })

    df = pd.DataFrame(rows).sort_values(["Tanggal", "Lini Produksi"]).reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = generate()
    out = "alumisight_demo_dataset.xlsx"
    df.to_excel(out, index=False)
    print(f"Dataset dibuat: {len(df)} baris, {len(df.columns)} kolom -> {out}")
    print("Kolom:", list(df.columns))
