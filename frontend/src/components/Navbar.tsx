"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV = [
  { href: "/", label: "Ringkasan" },
  { href: "/upload", label: "Unggah Data" },
  { href: "/forecast", label: "Prediksi Energi" },
  { href: "/cost", label: "Biaya Produksi" },
  { href: "/anomaly", label: "Deteksi Anomali" },
  { href: "/recommendation", label: "Rekomendasi" },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <header className="bg-cream-50/95 backdrop-blur border-b border-cream-300 sticky top-0 z-20">
      <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5">
          <Image src="/Alumisight (1).png" alt="AlumiSight AI" width={28} height={28} priority />
          <span className="flex items-baseline gap-2.5">
            <span className="text-[22px] text-navy-900 tracking-tight">AlumiSight AI</span>
            <span className="hidden md:inline text-[11px] uppercase tracking-eyebrow text-steel-300">
              Energy Intelligence
            </span>
          </span>
        </Link>
        <nav className="flex items-center gap-0.5 overflow-x-auto">
          {NAV.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`px-3.5 py-2 text-[13px] whitespace-nowrap border-b-2 transition-colors ${
                  active
                    ? "text-navy-900 border-navy-800"
                    : "text-steel-400 border-transparent hover:text-navy-700"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}