import json
import re
from llama_cpp import Llama
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../models/unsloth.Q4_K_M.gguf")

llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=2048,       
    n_threads=4,      
    verbose=False     
)

def extract_data_manually(text):
    """Fungsi Pemburu Teks: Ekstrak data secara paksa dari JSON yang rusak parah"""
    priority = "Sedang"
    if re.search(r'(?i)tinggi', text): priority = "Tinggi"
    elif re.search(r'(?i)rendah', text): priority = "Rendah"
    
    # 2. Cari Reasoning
    reasoning = "Sistem AI berhasil menganalisis data, namun kesulitan menyusun kalimat baku."
    res_match = re.search(r'"reasoning"\s*:\s*"([^"]+)', text, re.IGNORECASE)
    if res_match:
        reasoning = res_match.group(1)
    
    action_items = []
    act_match = re.search(r'"action_items"\s*:\s*\[(.*)', text, re.IGNORECASE | re.DOTALL)
    if act_match:
        items_text = act_match.group(1)
        action_items = re.findall(r'"([^"]+)"', items_text)
        
    if not action_items:
         action_items = ["Lakukan evaluasi ulang pada lini produksi berdasarkan data terbaru.", "Periksa potensi anomali energi secara manual."]
         
    return {
        "priority_level": priority,
        "reasoning": reasoning,
        "action_items": action_items
    }

def fix_and_parse_json(text):
    """Sistem Parsing Berlapis"""
    text = text.strip()
    
    try:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except:
        pass
        
    try:
        match = re.search(r'\{.*', text, re.DOTALL)
        if match:
            json_str = match.group(0).rstrip(', \n\t')
            for suffix in ["}", "]}", "\"]}"]:
                try: return json.loads(json_str + suffix)
                except: pass
    except:
        pass
        
    return extract_data_manually(text)

def generate_recommendation_from_llm(input_text):
    inference_prompt = """<|im_start|>system
Anda adalah konsultan AI industri kelas atas yang sangat analitis. Analisis data operasional pabrik berikut.
BERIKAN ANALISIS YANG MENDALAM:
- Pada "reasoning", jelaskan alasan Anda secara detail, komprehensif, dan kreatif (minimal 3 kalimat yang saling berhubungan). 
- Pada "action_items", berikan langkah tindakan strategis yang spesifik, tidak standar, dan dapat langsung dieksekusi.

ATURAN MUTLAK: Kamu harus mengekstrak angka metrik dan anomali persis 100% seperti yang tertera pada data input. DILARANG KERAS mengarang, membulatkan, atau mengubah angka apa pun dalam alasanmu.

Output WAJIB persis seperti template JSON ini, tanpa awalan/akhiran apapun:
{
  "priority_level": "Tinggi",
  "reasoning": "Tuliskan analisis komprehensif yang panjang dan mendalam di sini...",
  "action_items": ["Langkah strategis 1 yang spesifik", "Langkah strategis 2 yang spesifik"]
}<|im_end|>
<|im_start|>user
{}<|im_end|>
<|im_start|>assistant
"""
    
    prompt = inference_prompt.replace("{}", input_text)
    
    response = llm(
        prompt, 
        max_tokens=512, 
        temperature=0.1,      
        top_p=0.9,            
        repeat_penalty=1.15,  
        stop=["<|im_end|>"] 
    )
    
    output_text = response["choices"][0]["text"].strip()
    print(f"--- OUTPUT MENTAH LLM ---\n{output_text}\n-------------------------")
    
    return fix_and_parse_json(output_text)

def build_final_recommendation(energy_insight, cost, anomaly_count, baseline):
    baseline_str = f"Rp{baseline:,.0f}".replace(",", ".") if baseline else "Tidak tersedia"
    cost_per_unit = cost.get("estimated_cost_per_unit", 0)
    cost_str = f"Rp{cost_per_unit:,.0f}".replace(",", ".")

    input_text = (
        f"Data Operasional:\n"
        f"- Tren Konsumsi Energi: {energy_insight.get('trend_label', 'stabil')}\n"
        f"- Volatilitas Energi: {energy_insight.get('volatility_label', 'rendah')}\n"
        f"- Estimasi Biaya/Unit: {cost_str}\n"
        f"- Baseline Biaya/Unit: {baseline_str}\n"
        f"- Pangsa Biaya Energi Terhadap Total Produksi: {int(cost.get('energy_cost_share', 0) * 100)}%\n"
        f"- Jumlah Anomali Konsumsi Energi Terdeteksi: {anomaly_count}"
    )

    try:
        parsed_json = generate_recommendation_from_llm(input_text)
    except Exception as e:
        print(f"LLM Parsing Error Fatal: {e}")
        parsed_json = {"priority_level": "Sedang", "reasoning": "Mesin AI mengalami gangguan internal saat memproses output.", "action_items": ["Hubungi administrator sistem."]}

    trend = energy_insight.get("trend_label", "cenderung stabil")
    summary_text = (
        f"Estimasi biaya produksi sekitar {cost_str} per satuan, dengan proyeksi konsumsi "
        f"energi {trend}. Tingkat prioritas tindakan: {parsed_json.get('priority_level', 'Sedang')}."
    )
    
    caveat_text = (
        "Rekomendasi ini didasarkan pada proyeksi data historis dan tidak memperhitungkan faktor "
        "eksternal seperti perubahan tarif listrik mendadak, gangguan pasokan bahan baku, atau kebijakan "
        "energi. Evaluasi ulang disarankan secara berkala seiring tersedianya data terbaru."
    )
    
    return {
        "priority_level": parsed_json.get("priority_level"),
        "summary": summary_text,
        "reasoning": parsed_json.get("reasoning"),
        "action_items": parsed_json.get("action_items", []),
        "caveat": caveat_text
    }