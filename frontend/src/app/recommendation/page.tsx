"use client";

import { useEffect, useState } from "react";
import { runRecommendation } from "@/lib/api";
import type { RecommendationResult } from "@/types";

const PRIORITY: Record<string, string> = {
  rendah: "border-navy-200 text-navy-600 bg-navy-50",
  sedang: "border-amber-200 text-amber-700 bg-amber-50",
  tinggi: "border-red-200 text-red-700 bg-red-50",
};

export default function RecommendationPage() {
  const [datasetId, setDatasetId] = useState("");
  const [period, setPeriod] = useState("line-1");
  const [horizon, setHorizon] = useState(30);
  const [result, setResult] = useState<RecommendationResult | null>(null);
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
      setResult(await runRecommendation(datasetId, period, horizon));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl">
      <p className="eyebrow mb-3">Langkah 5</p>
      <h1 className="text-4xl text-navy-900 mb-3">Rekomendasi Operasional</h1>
      <p className="text-[16px] text-steel-400 max-w-2xl mb-10 leading-relaxed">
        Ringkasan keputusan yang menggabungkan proyeksi energi, estimasi biaya, dan deteksi
        anomali menjadi langkah tindakan yang dapat langsung dieksekusi.
      </p>

      <div className="card p-8 mb-6">
        <div className="mb-5">
          <label className="field-label">Dataset ID</label>
          <input value={datasetId} onChange={(e) => setDatasetId(e.target.value)}
            placeholder="ID dataset dari halaman Unggah Data" className="input-field" />
        </div>
        <div className="grid grid-cols-2 gap-5">
          <div>
            <label className="field-label">Lini Produksi</label>
            <input value={period} onChange={(e) => setPeriod(e.target.value)} className="input-field" />
          </div>
          <div>
            <label className="field-label">Horizon Proyeksi (hari)</label>
            <input type="number" value={horizon} onChange={(e) => setHorizon(Number(e.target.value))} className="input-field" />
          </div>
        </div>
        <button onClick={run} disabled={!datasetId || loading} className="btn-primary mt-6">
          {loading ? "Menganalisis…" : "Susun Rekomendasi"}
        </button>
        {error && <p className="text-[14px] text-red-700 mt-4">{error}</p>}
      </div>

      {result && (
        <div className="space-y-5">
          <div className="card p-8">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-xl text-navy-900">Keputusan {result.period}</h2>
              <span className={`badge ${PRIORITY[result.priority_level]}`}>
                Prioritas {result.priority_level}
              </span>
            </div>
            <p className="text-[16px] text-navy-800 leading-relaxed">{result.summary}</p>
          </div>

          <div className="card p-8">
            <p className="eyebrow mb-2.5">Dasar Pertimbangan</p>
            <p className="text-[15px] text-navy-700 leading-relaxed">{result.reasoning}</p>
          </div>

          <div className="card p-8">
            <p className="eyebrow mb-4">Langkah Tindakan</p>
            <ul className="space-y-3">
              {result.action_items.map((item, idx) => (
                <li key={idx} className="flex gap-3 text-[15px] text-navy-800">
                  <span className="text-steel-300 tabular-nums">{String(idx + 1).padStart(2, "0")}</span>
                  <span className="leading-relaxed">{item}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="border border-amber-200 bg-amber-50/60 rounded-xl p-6">
            <p className="eyebrow mb-2 text-amber-700">Catatan & Batasan</p>
            <p className="text-[14px] text-amber-800 leading-relaxed">{result.caveat}</p>
          </div>
        </div>
      )}
    </div>
  );
}
