"use client";

import { useEffect, useState } from "react";
import { runForecast } from "@/lib/api";
import HistoricalForecastChart from "@/components/HistoricalForecastChart";
import type { ForecastResult } from "@/types";

const TREND_BADGE: Record<string, string> = {
  meningkat: "border-navy-200 text-navy-700 bg-navy-50",
  menurun: "border-amber-200 text-amber-700 bg-amber-50",
  stabil: "border-cream-300 text-steel-400 bg-cream-100",
};
const VOL_BADGE: Record<string, string> = {
  rendah: "border-cream-300 text-steel-400 bg-cream-100",
  sedang: "border-amber-200 text-amber-700 bg-amber-50",
  tinggi: "border-red-200 text-red-700 bg-red-50",
};

export default function ForecastPage() {
  const [datasetId, setDatasetId] = useState("");
  const [period, setPeriod] = useState("line-1");
  const [horizon, setHorizon] = useState(30);
  const [result, setResult] = useState<ForecastResult | null>(null);
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
      setResult(await runForecast(datasetId, [period], horizon));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const historicalEnergy = result?.historical?.map((h) => ({
    date: h.date,
    value: h.energy,
  })) ?? [];

  const forecastEnergy = result?.forecast?.map((f) => ({
    date: f.date,
    value: f.energy,
  })) ?? [];

  const insight = result?.insight;

  return (
    <div className="max-w-4xl">
      <p className="eyebrow mb-3">Langkah 2</p>
      <h1 className="text-4xl text-navy-900 mb-3">Prediksi Konsumsi Energi</h1>
      <p className="text-[16px] text-steel-400 max-w-2xl mb-10 leading-relaxed">
        Proyeksi pemakaian listrik ke depan menggunakan model terbaik (Random Forest, XGBoost,
        atau LightGBM) yang dipilih otomatis berdasarkan akurasi.
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
            <input value={period} onChange={(e) => setPeriod(e.target.value)}
              placeholder="mis. line-1" className="input-field" />
          </div>
          <div>
            <label className="field-label">Horizon Proyeksi (hari)</label>
            <input type="number" value={horizon} onChange={(e) => setHorizon(Number(e.target.value))}
              className="input-field" />
          </div>
        </div>
        <button onClick={run} disabled={!datasetId || loading} className="btn-primary mt-6">
          {loading ? "Melatih model…" : "Jalankan Prediksi"}
        </button>
        {error && <p className="text-[14px] text-red-700 mt-4">{error}</p>}
      </div>

      {result && (
        <>
          <div className="card p-8 mb-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl text-navy-900">Historis & Proyeksi {period}</h2>
              {result.best_model && (
                <span className="badge border-navy-200 text-navy-600 bg-navy-50">
                  Model: {result.best_model}
                </span>
              )}
            </div>
            <HistoricalForecastChart
              historical={historicalEnergy}
              forecast={forecastEnergy}
              valueLabel="Energi (kWh)"
              formatValue={(v) => `${v.toLocaleString("id-ID")} kWh`}
              yAxisFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
            />
            {result.metrics && (
              <div className="grid grid-cols-3 gap-3 mt-6 text-[13px]">
                {Object.entries(result.metrics).map(([m, v]) => (
                  <div key={m} className={`border rounded-lg p-3.5 ${m === result.best_model ? "border-navy-300 bg-navy-50" : "border-cream-300"}`}>
                    <p className="capitalize text-navy-800 mb-1">{m.replace("_", " ")}</p>
                    <p className="text-steel-400 tabular-nums">MAE {v.mae.toFixed(1)}</p>
                    <p className="text-steel-400 tabular-nums">RMSE {v.rmse.toFixed(1)}</p>
                  </div>
                ))}
              </div>
            )}
          </div>

          {insight && (
            <div className="card p-8">
              <p className="eyebrow mb-4">Interpretasi</p>
              <div className="flex flex-wrap gap-2 mb-5">
                <span className={`badge ${TREND_BADGE[insight.trend_label]}`}>
                  Tren {insight.trend_label}
                  {insight.trend_label !== "stabil" && ` (${insight.change_pct > 0 ? "+" : ""}${insight.change_pct}%)`}
                </span>
                <span className={`badge ${VOL_BADGE[insight.volatility_label]}`}>
                  Volatilitas {insight.volatility_label} ({insight.coefficient_of_variation}%)
                </span>
                <span className="badge border-cream-300 text-steel-400 bg-cream-100">
                  Rata-rata {insight.average_energy.toLocaleString("id-ID")} kWh
                </span>
              </div>
              <p className="text-[15px] text-navy-700 leading-relaxed mb-5">{insight.narrative}</p>
              <div className="card-tint p-5 mb-4">
                <p className="eyebrow mb-1.5">Catatan Strategis</p>
                <p className="text-[14px] text-navy-700 leading-relaxed">{insight.recommendation_note}</p>
              </div>
              {insight.model_note && (
                <div className="border border-cream-300 rounded-lg p-5">
                  <p className="eyebrow mb-1.5">Pemilihan Model</p>
                  <p className="text-[14px] text-steel-400 leading-relaxed">{insight.model_note}</p>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
