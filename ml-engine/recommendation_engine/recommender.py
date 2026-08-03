"""
Recommendation Engine
Menggabungkan hasil proyeksi energi, estimasi biaya produksi, dan deteksi
anomali menjadi satu rekomendasi operasional yang kritis dan actionable
dalam Bahasa Indonesia (berbasis rule, tanpa LLM agar ringan & deterministik).
"""
from dataclasses import dataclass

from config.settings import COST_THRESHOLD_LOW, COST_THRESHOLD_HIGH


@dataclass
class Recommendation:
    priority_level: str  # "rendah" | "sedang" | "tinggi"
    summary: str
    reasoning: str
    action_items: list[str]
    caveat: str


def _categorize_cost_deviation(deviation_ratio: float) -> str:
    if deviation_ratio <= COST_THRESHOLD_LOW:
        return "rendah"
    if deviation_ratio <= COST_THRESHOLD_HIGH:
        return "sedang"
    return "tinggi"


def build_recommendation(
    energy_insight: dict,
    cost: dict,
    anomaly_count: int,
    baseline_cost_per_unit: float | None = None,
) -> Recommendation:
    """
    Bangun rekomendasi operasional berdasarkan gabungan sinyal.
    """
    cost_per_unit = cost.get("estimated_cost_per_unit", 0.0)

    if baseline_cost_per_unit and baseline_cost_per_unit > 0:
        deviation_ratio = abs(cost_per_unit - baseline_cost_per_unit) / baseline_cost_per_unit
    else:
        deviation_ratio = 0.0
    priority = _categorize_cost_deviation(deviation_ratio)

    # Naikkan prioritas bila terdapat anomali energi.
    if anomaly_count >= 3 and priority == "rendah":
        priority = "sedang"
    if anomaly_count >= 5:
        priority = "tinggi"

    trend = energy_insight.get("trend_label", "stabil")
    summary = (
        f"Estimasi biaya produksi sekitar Rp{cost_per_unit:,.0f} per satuan, dengan proyeksi konsumsi "
        f"energi cenderung {trend}. Tingkat prioritas tindakan: {priority}."
    ).replace(",", ".")

    reasoning_parts = [
        f"Proyeksi energi menunjukkan pola {trend} dengan volatilitas "
        f"{energy_insight.get('volatility_label', 'sedang')}.",
        f"Biaya energi menyumbang {cost.get('energy_cost_share', 0) * 100:.0f}% dari total biaya produksi.",
    ]
    if anomaly_count > 0:
        reasoning_parts.append(
            f"Terdeteksi {anomaly_count} titik konsumsi energi anomali yang perlu ditelusuri."
        )
    reasoning = " ".join(reasoning_parts)

    action_items = []
    if trend == "meningkat":
        action_items.append("Evaluasi efisiensi lini produksi dengan konsumsi energi tertinggi.")
        action_items.append("Pertimbangkan penjadwalan produksi pada jam tarif listrik lebih rendah.")
    if anomaly_count > 0:
        action_items.append("Telusuri titik anomali energi untuk mengidentifikasi pemborosan atau gangguan mesin.")
    if cost.get("energy_cost_share", 0) >= 0.5:
        action_items.append("Prioritaskan program efisiensi energi karena mendominasi struktur biaya.")
    if not action_items:
        action_items.append("Pertahankan pola operasional saat ini dan lanjutkan pemantauan berkala.")

    caveat = (
        "Rekomendasi ini didasarkan pada proyeksi data historis dan tidak memperhitungkan faktor "
        "eksternal seperti perubahan tarif listrik mendadak, gangguan pasokan bahan baku, atau kebijakan "
        "energi. Evaluasi ulang disarankan secara berkala seiring tersedianya data terbaru."
    )

    return Recommendation(
        priority_level=priority,
        summary=summary,
        reasoning=reasoning,
        action_items=action_items,
        caveat=caveat,
    )
