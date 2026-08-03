"use client";

import { useState } from "react";
import { uploadDataset } from "@/lib/api";
import type { UploadResult } from "@/types";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<UploadResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const res = await uploadDataset(file);
      setResult(res);
      if (res.dataset_id) localStorage.setItem("alumisight_dataset_id", res.dataset_id);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl">
      <p className="eyebrow mb-3">Langkah 1</p>
      <h1 className="text-4xl text-navy-900 mb-3">Unggah Data</h1>
      <p className="text-[16px] text-steel-400 max-w-2xl mb-10 leading-relaxed">
        Unggah berkas Excel atau CSV berisi data produksi dan konsumsi energi. Sistem akan
        memetakan format kolom apa pun ke skema standar secara otomatis.
      </p>

      <div className="card p-8 mb-6">
        <label className="field-label">Berkas Dataset</label>
        <input
          type="file"
          accept=".xlsx,.xls,.csv,.tsv"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className="block w-full text-[14px] text-navy-700 file:mr-4 file:py-2.5 file:px-5 file:rounded-lg
          file:border file:border-navy-300 file:bg-transparent file:text-navy-800 file:text-[13px]
          file:cursor-pointer hover:file:bg-navy-800 hover:file:text-cream-50 hover:file:border-navy-800
          file:transition-colors"
        />
        <p className="field-hint">Format didukung: .xlsx, .xls, .csv. Kolom wajib: tanggal, lini produksi, konsumsi energi.</p>
        <button onClick={handleUpload} disabled={!file || loading} className="btn-primary mt-6">
          {loading ? "Memproses…" : "Unggah & Proses"}
        </button>
        {error && <p className="text-[14px] text-red-700 mt-4">{error}</p>}
      </div>

      {result && (
        <div className="card p-8">
          <div className="flex items-center gap-2.5 mb-6">
            <span className={`w-2 h-2 rounded-full ${result.is_valid ? "bg-navy-700" : "bg-amber-500"}`} />
            <h2 className="text-lg text-navy-900">
              {result.is_valid ? "Dataset valid dan siap dianalisis" : "Perlu konfirmasi pemetaan kolom"}
            </h2>
          </div>

          <div className="grid grid-cols-2 gap-6 mb-8">
            <div>
              <p className="eyebrow mb-1.5">Dataset ID</p>
              <code className="text-[13px] text-navy-700 bg-cream-100 px-2 py-1 rounded break-all">
                {result.dataset_id}
              </code>
            </div>
            <div>
              <p className="eyebrow mb-1.5">Jumlah Baris</p>
              <p className="text-[15px] text-navy-800 tabular-nums">
                {result.row_count.toLocaleString("id-ID")}
              </p>
            </div>
          </div>

          <p className="eyebrow mb-3">Hasil Pemetaan Kolom</p>
          <div className="overflow-hidden border border-cream-300 rounded-lg">
            <table className="w-full text-[14px]">
              <thead>
                <tr className="bg-navy-800 text-cream-50 text-left text-[12px] uppercase tracking-wide">
                  <th className="py-2.5 px-4 font-normal">Kolom Asli</th>
                  <th className="py-2.5 px-4 font-normal">Dipetakan Ke</th>
                  <th className="py-2.5 px-4 font-normal">Metode</th>
                  <th className="py-2.5 px-4 font-normal">Keyakinan</th>
                </tr>
              </thead>
              <tbody>
                {result.mapping.map((m, idx) => (
                  <tr key={idx} className={idx % 2 ? "bg-cream-50" : "bg-white"}>
                    <td className="py-2.5 px-4 text-navy-800">{m.original_column}</td>
                    <td className="py-2.5 px-4">
                      {m.mapped_to ?? <span className="text-amber-600 italic">tidak dikenali</span>}
                    </td>
                    <td className="py-2.5 px-4 capitalize text-steel-400">{m.method}</td>
                    <td className="py-2.5 px-4 text-steel-400 tabular-nums">{m.confidence.toFixed(0)}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {result.missing_required_columns.length > 0 && (
            <p className="text-[14px] text-red-700 mt-4">
              Kolom wajib belum lengkap: {result.missing_required_columns.join(", ")}
            </p>
          )}
          {result.is_valid && (
            <p className="text-[14px] text-steel-400 mt-5">
              Dataset ID tersimpan otomatis. Lanjutkan ke halaman Prediksi Energi.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
