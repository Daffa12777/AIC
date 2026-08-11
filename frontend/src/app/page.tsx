import Link from "next/link";

const CAPABILITIES = [
  { title: "Prediksi Konsumsi Energi", desc: "Proyeksi pemakaian listrik per lini produksi berdasarkan pola historis." },
  { title: "Estimasi Biaya Produksi", desc: "Perhitungan biaya per satuan dari proyeksi energi dan bahan baku." },
  { title: "Deteksi Anomali Energi", desc: "Identifikasi lonjakan konsumsi listrik yang mengindikasikan pemborosan." },
  { title: "Rekomendasi Operasional", desc: "Ringkasan keputusan dan langkah tindakan berbasis seluruh analisis." },
];

export default function HomePage() {
  return (
    <div>
      {/* Hero */}
      <section className="mb-16">
        <p className="eyebrow mb-4">AI Decision Support · Aluminium Manufacturing</p>
        <h1 className="text-5xl md:text-6xl leading-[1.05] text-navy-900 max-w-3xl mb-6">
          Mengubah data energi menjadi keputusan produksi yang lebih cerdas.
        </h1>
        <p className="text-[17px] text-steel-400 max-w-2xl leading-relaxed mb-8">
          AlumiSight AI membantu pabrik dan smelter aluminium memprediksi konsumsi energi,
          mengestimasi biaya produksi, dan mendeteksi pemborosan lalu menyusunnya menjadi
          rekomendasi operasional yang jelas.
        </p>
        <div className="flex gap-3">
          <Link href="/upload" className="btn-primary">Mulai dengan Unggah Data</Link>
          <Link href="/forecast" className="btn-ghost">Lihat Prediksi Energi</Link>
        </div>
      </section>

      {/* Kapabilitas */}
      <section className="mb-16">
        <p className="eyebrow mb-6">Kapabilitas Sistem</p>
        <div className="grid md:grid-cols-2 gap-px bg-cream-300 border border-cream-300 rounded-xl overflow-hidden">
          {CAPABILITIES.map((c, i) => (
            <div key={c.title} className="bg-white p-7">
              <div className="flex items-baseline gap-3 mb-2">
                <span className="text-[13px] text-steel-300 tabular-nums">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <h3 className="text-xl text-navy-900">{c.title}</h3>
              </div>
              <p className="text-[15px] text-steel-400 leading-relaxed pl-8">{c.desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
