"use client";

import { useEffect, useState } from "react";
import { runAnomalyScan } from "@/lib/api";
import type { AnomalyResult } from "@/types";

export default function AnomalyPage() {
  const [datasetId, setDatasetId] = useState("");
  const [period, setPeriod] = useState("POT-A");
  const [result, setResult] = useState<AnomalyResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const saved = localStorage.getItem("alumisight_dataset_id");
    if (saved) setDatasetId(saved);
  }, []);

  const run = async () => {
    if (!datasetId) return;
    setLoading(true);
    setError(null);
    try {
      setResult(await runAnomalyScan(datasetId, period || null));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl">
      <p className="eyebrow mb-3">Langkah 4</p>
      <h1 className="text-4xl text-navy-900 mb-3">Deteksi Anomali Energi</h1>
      <p className="text-[16px] text-steel-400 max-w-2xl mb-10 leading-relaxed">
        Identifikasi titik konsumsi energi yang menyimpang dari pola normal sinyal dini
        pemborosan atau gangguan operasional.
      </p>

      <div className="card p-8 mb-6">
        <div className="grid grid-cols-2 gap-5">
          <div>
            <label className="field-label">Dataset ID</label>
            <input value={datasetId} onChange={(e) => setDatasetId(e.target.value)}
              placeholder="ID dataset" className="input-field" />
          </div>
          <div>
            <label className="field-label">Lini Produksi (opsional)</label>
            <input value={period} onChange={(e) => setPeriod(e.target.value)}
              placeholder="kosongkan untuk semua lini" className="input-field" />
          </div>
        </div>
        <button onClick={run} disabled={!datasetId || loading} className="btn-primary mt-6">
          {loading ? "Memindai…" : "Pindai Anomali"}
        </button>
        {error && <p className="text-[14px] text-red-700 mt-4">{error}</p>}
      </div>

      {result && (
        <div className="card p-8">
          <div className="flex items-baseline justify-between mb-5">
            <h2 className="text-xl text-navy-900">Hasil Pemindaian</h2>
            <span className={`badge ${result.total_anomalies > 0 ? "border-amber-200 text-amber-700 bg-amber-50" : "border-navy-200 text-navy-600 bg-navy-50"}`}>
              {result.total_anomalies} anomali
            </span>
          </div>
          <p className="text-[15px] text-navy-700 leading-relaxed mb-6">{result.narrative}</p>

          {result.anomalies.length > 0 && (
            <div className="overflow-hidden border border-cream-300 rounded-lg">
              <table className="w-full text-[14px]">
                <thead>
                  <tr className="bg-navy-800 text-cream-50 text-left text-[12px] uppercase tracking-wide">
                    <th className="py-2.5 px-4 font-normal">Tanggal</th>
                    <th className="py-2.5 px-4 font-normal">Lini</th>
                    <th className="py-2.5 px-4 font-normal">Konsumsi (kWh)</th>
                    <th className="py-2.5 px-4 font-normal">Deviasi</th>
                  </tr>
                </thead>
                <tbody>
                  {result.anomalies.map((a, idx) => (
                    <tr key={idx} className={idx % 2 ? "bg-cream-50" : "bg-white"}>
                      <td className="py-2.5 px-4 text-navy-800 tabular-nums">{a.date}</td>
                      <td className="py-2.5 px-4 text-navy-800">{a.period}</td>
                      <td className="py-2.5 px-4 text-navy-800 tabular-nums">
                        {a.energy.toLocaleString("id-ID")}
                      </td>
                      <td className={`py-2.5 px-4 tabular-nums ${a.deviation_pct >= 0 ? "text-red-700" : "text-navy-600"}`}>
                        {a.deviation_pct > 0 ? "+" : ""}{a.deviation_pct}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
}