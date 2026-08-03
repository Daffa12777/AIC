"""
Production Cost Estimator
Mengestimasi biaya produksi per satuan berdasarkan proyeksi konsumsi energi,
harga bahan baku, dan volume produksi. Menggunakan pendekatan berbasis rumus
biaya yang transparan (bukan black-box) agar mudah dijelaskan ke stakeholder.
"""
import numpy as np
import pandas as pd

# Asumsi tarif energi default (Rp/kWh) bila tidak tersedia pada data.
DEFAULT_ENERGY_TARIFF = 1400.0


def estimate_production_cost(
    forecast_energy: list[float],
    avg_production_volume: float,
    avg_raw_material_cost: float,
    energy_tariff: float = DEFAULT_ENERGY_TARIFF,
) -> dict:
    """
    Estimasi biaya produksi berdasarkan proyeksi energi.

    forecast_energy       : deret prediksi konsumsi energi (kWh) per periode ke depan
    avg_production_volume : rata-rata volume produksi (ton) per periode
    avg_raw_material_cost : rata-rata biaya bahan baku (Rp) per periode
    energy_tariff         : tarif energi (Rp/kWh)
    """
    total_energy = float(np.sum(forecast_energy))
    n_periods = max(len(forecast_energy), 1)

    energy_cost = total_energy * energy_tariff
    material_cost_total = avg_raw_material_cost * n_periods
    total_cost = energy_cost + material_cost_total

    total_volume = max(avg_production_volume * n_periods, 1e-6)
    cost_per_unit = total_cost / total_volume
    energy_share = energy_cost / total_cost if total_cost > 0 else 0.0

    return {
        "total_energy_kwh": round(total_energy, 2),
        "energy_cost": round(energy_cost, 2),
        "material_cost": round(material_cost_total, 2),
        "total_production_cost": round(total_cost, 2),
        "estimated_cost_per_unit": round(cost_per_unit, 2),
        "energy_cost_share": round(energy_share, 4),
        "periods": n_periods,
    }
