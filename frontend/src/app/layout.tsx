import "@/styles/globals.css";
import type { Metadata } from "next";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "AlumiSight AI — Energy & Cost Intelligence",
  description:
    "AI Decision Support System for Energy & Production Cost Optimization in Aluminium Manufacturing",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="id">
      <body>
        <Navbar />
        <main className="max-w-6xl mx-auto px-6 py-12">{children}</main>
        <footer className="border-t border-cream-300 mt-20">
          <div className="max-w-6xl mx-auto px-6 py-8 flex items-center justify-between text-[12px] text-steel-300">
            <span>AlumiSight AI — AI for the Backbone of the Economy</span>
            <span>Smart Manufacturing</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
