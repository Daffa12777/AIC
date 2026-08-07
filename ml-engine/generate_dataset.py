import json
import random
import os
import sys

# Memastikan Python bisa membaca folder recommendation_engine tanpa error path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from recommendation_engine.recommender import build_recommendation

def generate_synthetic_data(num_samples=200):
    dataset = []
    
    trends = ["menurun", "stabil", "meningkat"]
    volatilities = ["rendah", "sedang", "tinggi"]
    
    for _ in range(num_samples):
        # 1. Bikin data input acak 
        energy_insight = {
            "trend_label": random.choice(trends),
            "volatility_label": random.choice(volatilities)
        }
        
        # Angka di-set ke rentang 1 juta - 5 juta
        cost_per_unit = random.randint(1000000, 5000000)
        baseline = random.randint(1000000, 5000000)
        energy_share = random.uniform(0.1, 0.7)
        
        cost = {
            "estimated_cost_per_unit": cost_per_unit,
            "energy_cost_share": energy_share
        }
        
        anomaly_count = random.randint(0, 10)

        # 2. Dapatkan output otomatis dari sistem rule-based
        rec = build_recommendation(
            energy_insight=energy_insight, 
            cost=cost, 
            anomaly_count=anomaly_count, 
            baseline_cost_per_unit=baseline
        )
        
        # 3. Format Output hanya 3 
        output_json = {
            "priority_level": rec.priority_level,
            "reasoning": rec.reasoning,
            "action_items": rec.action_items
        }
        
        # 4. Susun Input string
        input_text = (
            f"Data Operasional:\n"
            f"- Tren Konsumsi Energi: {energy_insight['trend_label']}\n"
            f"- Volatilitas Energi: {energy_insight['volatility_label']}\n"
            f"- Estimasi Biaya/Unit: Rp{cost_per_unit}\n"
            f"- Baseline Biaya/Unit: Rp{baseline}\n"
            f"- Pangsa Biaya Energi Terhadap Total Produksi: {energy_share*100:.0f}%\n"
            f"- Jumlah Anomali Mesin Terdeteksi: {anomaly_count}"
        )

        # 5. Gabungkan jadi format Alpaca
        dataset.append({
            "instruction": "Anda adalah konsultan AI industri yang ahli di bidang efisiensi energi pabrik. Analisis data operasional berikut dan berikan rekomendasi aksi dalam Bahasa Indonesia. Output WAJIB berupa objek JSON murni tanpa awalan/akhiran apapun.",
            "input": input_text,
            "output": json.dumps(output_json, ensure_ascii=False)
        })

    # Simpan ke file JSONL
    output_path = os.path.join(os.getcwd(), "dataset.jsonl")
    with open(output_path, "w", encoding="utf-8") as f:
        for item in dataset:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
            
    print(f"Mantap! Berhasil membuat {num_samples} baris data sintetis baru yang sudah optimal di: {output_path}")

if __name__ == "__main__":
    generate_synthetic_data(200) 