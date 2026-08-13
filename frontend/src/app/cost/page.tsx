"use client";

import { useEffect, useState } from "react";
import { runCostAnalysis } from "@/lib/api";
import HistoricalForecastChart from "@/components/HistoricalForecastChart";
import type { CostResult } from "@/types";

function rupiah(n: number): string {
  return "Rp" + Math.round(n).toLocaleString("id-ID");
}

function rupiahShort(n: number): string {
  if (n >= 1e9) return `${(n / 1e9).toFixed(1)}M`;
  if (n >= 1e6) return `${(n / 1e6).toFixed(0)}jt`;
  if (n >= 1e3) return `${(n / 1e3).toFixed(0)}rb`;
  return String(Math.round(n));
}

export default function CostPage() {
  const [datasetId, setDatasetId] = useState("");
  const [period, setPeriod] = useState("POT-A");
  const [horizon, setHorizon] = useState(30);
  const [result, setResult] = useState<CostResult | null>(null);
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
      setResult(await runCostAnalysis(datasetId, period, horizon));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const metrics = result
    ? [
        { label: "Total Konsumsi Energi", value: `${result.total_energy_kwh.toLocaleString("id-ID")} kWh` },
        { label: "Biaya Energi", value: rupiah(result.energy_cost) },
        { label: "Biaya Bahan Baku", value: rupiah(result.material_cost) },
        { label: "Total Biaya Produksi", value: rupiah(result.total_production_cost) },
      ]
    : [];

  const historicalCost = result?.historical_cost?.map((h) => ({
    date: h.date,
    value: h.cost,
  })) ?? [];

  const forecastCost = result?.forecast_cost?.map((f) => ({
    date: f.date,
    value: f.cost,
  })) ?? [];

  return (
    <div className="max-w-4xl">
      <p className="eyebrow mb-3">Langkah 3</p>
      <h1 className="text-4xl text-navy-900 mb-3">Estimasi Biaya Produksi</h1>
      <p className="text-[16px] text-steel-400 max-w-2xl mb-10 leading-relaxed">
        Proyeksi biaya produksi per satuan berdasarkan prediksi konsumsi energi, tarif listrik,
        dan biaya bahan baku.
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
              placeholder="mis. POT-A" className="input-field" />
          </div>
          <div>
            <label className="field-label">Horizon Proyeksi (hari)</label>
            <input type="number" value={horizon} onChange={(e) => setHorizon(Number(e.target.value))} className="input-field" />
          </div>
        </div>
        <button onClick={run} disabled={!datasetId || loading} className="btn-primary mt-6">
          {loading ? "Menghitung…" : "Hitung Biaya Produksi"}
        </button>
        {error && <p className="text-[14px] text-red-700 mt-4">{error}</p>}
      </div>

      {result && (
        <>
          <div className="card p-8 mb-6">
            <div className="flex items-baseline justify-between mb-6">
              <h2 className="text-xl text-navy-900">Estimasi {period}</h2>
              <span className="badge border-navy-200 text-navy-600 bg-navy-50">
                {result.periods} periode proyeksi
              </span>
            </div>

            <div className="mb-8">
              <p className="eyebrow mb-2">Biaya Produksi per Satuan</p>
              <p className="text-5xl text-navy-900 tabular-nums">
                {rupiah(result.estimated_cost_per_unit)}
              </p>
              <p className="text-[13px] text-steel-300 mt-1.5">estimasi biaya per ton produksi</p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-px bg-cream-300 border border-cream-300 rounded-lg overflow-hidden">
              {metrics.map((m) => (
                <div key={m.label} className="bg-white px-4 py-4">
                  <p className="text-[11px] uppercase tracking-wide text-steel-400 mb-1">{m.label}</p>
                  <p className="text-[15px] text-navy-800 tabular-nums">{m.value}</p>
                </div>
              ))}
            </div>

            <div className="mt-6">
              <div className="flex items-center justify-between text-[13px] text-steel-400 mb-1.5">
                <span>Porsi biaya energi terhadap total</span>
                <span className="tabular-nums">{(result.energy_cost_share * 100).toFixed(0)}%</span>
              </div>
              <div className="h-2 bg-cream-200 rounded-full overflow-hidden">
                <div className="h-full bg-navy-700 rounded-full"
                  style={{ width: `${Math.min(result.energy_cost_share * 100, 100)}%` }} />
              </div>
            </div>
          </div>

          {(historicalCost.length > 0 || forecastCost.length > 0) && (
            <div className="card p-8 mb-6">
              <h2 className="text-xl text-navy-900 mb-6">Historis & Proyeksi Biaya Harian</h2>
              <HistoricalForecastChart
                historical={historicalCost}
                forecast={forecastCost}
                valueLabel="Biaya Produksi"
                formatValue={(v) => rupiah(v)}
                yAxisFormatter={rupiahShort}
              />
            </div>
          )}

          {result.insight && (
            <div className="card p-8">
              <p className="eyebrow mb-3">Analisis Struktur Biaya</p>
              <p className="text-[15px] text-navy-700 leading-relaxed mb-5">{result.insight.narrative}</p>
              <div className="card-tint p-5">
                <p className="eyebrow mb-1.5">Catatan Strategis</p>
                <p className="text-[14px] text-navy-700 leading-relaxed">{result.insight.recommendation_note}</p>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}