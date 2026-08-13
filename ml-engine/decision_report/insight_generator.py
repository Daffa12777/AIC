"""
Insight Generator
Menghasilkan analisis naratif berbahasa Indonesia yang kritis dan profesional
untuk mendampingi output numerik Forecast Engine, Cost Estimator, dan
Anomaly Detection.
"""
import numpy as np


def generate_energy_insight(quantities: np.ndarray, best_model: str, metrics: dict | None) -> dict:
    """Analisis tren & volatilitas proyeksi konsumsi energi."""
    n = len(quantities)
    mean_q = float(np.mean(quantities)) if n else 0.0
    std_q = float(np.std(quantities)) if n else 0.0
    cv = (std_q / mean_q) if mean_q > 0 else 0.0

    third = max(1, n // 3)
    first_avg = float(np.mean(quantities[:third])) if n else 0.0
    last_avg = float(np.mean(quantities[-third:])) if n else 0.0
    change_pct = ((last_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0.0

    if abs(change_pct) < 5:
        trend_label = "stabil"
    elif change_pct > 0:
        trend_label = "meningkat"
    else:
        trend_label = "menurun"

    if cv < 0.15:
        volatility_label = "rendah"
    elif cv < 0.35:
        volatility_label = "sedang"
    else:
        volatility_label = "tinggi"

    narrative = (
        f"Proyeksi konsumsi energi menunjukkan pola {trend_label}"
        + (f" ({change_pct:+.1f}% dari awal ke akhir periode proyeksi)" if trend_label != "stabil" else "")
        + f", dengan rata-rata {mean_q:.1f} kWh per periode dan tingkat volatilitas {volatility_label} "
        f"(koefisien variasi {cv * 100:.1f}%)."
    )

    if trend_label == "meningkat":
        recommendation_note = (
            "Tren konsumsi energi yang meningkat berpotensi menaikkan biaya produksi. Disarankan "
            "mengevaluasi efisiensi lini produksi dan mempertimbangkan penjadwalan beban pada jam "
            "tarif listrik yang lebih rendah."
        )
    elif trend_label == "menurun":
        recommendation_note = (
            "Tren konsumsi energi yang menurun mengindikasikan potensi efisiensi. Pastikan penurunan "
            "ini tidak disertai penurunan volume produksi yang tidak diinginkan."
        )
    elif volatility_label == "tinggi":
        recommendation_note = (
            "Volatilitas konsumsi energi yang tinggi menyulitkan perencanaan biaya. Disarankan menelusuri "
            "penyebab fluktuasi pada lini produksi untuk menstabilkan pemakaian energi."
        )
    else:
        recommendation_note = (
            "Pola konsumsi energi yang stabil memudahkan perencanaan biaya produksi dengan tingkat "
            "kepercayaan yang relatif tinggi terhadap proyeksi ini."
        )

    model_note = None
    if metrics and best_model:
        others = {k: v for k, v in metrics.items() if k != best_model}
        if others:
            best_rmse = metrics[best_model]["rmse"]
            worst_alt = max(v["rmse"] for v in others.values())
            if worst_alt > 0:
                improvement = (worst_alt - best_rmse) / worst_alt * 100
                if improvement > 10:
                    model_note = (
                        f"Model {best_model} dipilih karena akurasi signifikan lebih baik "
                        f"(RMSE lebih rendah {improvement:.0f}%) dibanding alternatif pada data historis ini."
                    )
                else:
                    model_note = (
                        f"Model {best_model} dipilih dengan margin akurasi tipis dibanding alternatif "
                        f"(selisih RMSE < 10%) — performa ketiga model relatif setara pada dataset ini."
                    )

    return {
        "trend_label": trend_label,
        "change_pct": round(change_pct, 1),
        "volatility_label": volatility_label,
        "coefficient_of_variation": round(cv * 100, 1),
        "average_energy": round(mean_q, 1),
        "narrative": narrative,
        "recommendation_note": recommendation_note,
        "model_note": model_note,
    }


def generate_cost_insight(cost: dict) -> dict:
    """Analisis komposisi biaya produksi."""
    energy_share = cost.get("energy_cost_share", 0.0)
    if energy_share >= 0.5:
        narrative = (
            f"Biaya energi mendominasi struktur biaya produksi ({energy_share * 100:.0f}% dari total). "
            f"Efisiensi energi menjadi faktor paling menentukan dalam menekan biaya per satuan produksi."
        )
        note = (
            "Karena energi menjadi komponen biaya terbesar, prioritaskan optimasi konsumsi energi"
            "sekecil apa pun penghematan akan berdampak besar secara akumulatif."
        )
    elif energy_share >= 0.3:
        narrative = (
            f"Biaya energi menyumbang porsi signifikan ({energy_share * 100:.0f}%) terhadap total biaya "
            f"produksi, sejajar dengan komponen bahan baku."
        )
        note = (
            "Optimasi seimbang antara efisiensi energi dan negosiasi harga bahan baku disarankan untuk "
            "menekan biaya produksi secara menyeluruh."
        )
    else:
        narrative = (
            f"Biaya energi menyumbang porsi relatif kecil ({energy_share * 100:.0f}%); struktur biaya "
            f"lebih dipengaruhi oleh komponen bahan baku."
        )
        note = (
            "Fokus efisiensi sebaiknya diarahkan pada pengelolaan biaya bahan baku, tanpa mengabaikan "
            "pemantauan konsumsi energi."
        )

    return {"narrative": narrative, "recommendation_note": note}
