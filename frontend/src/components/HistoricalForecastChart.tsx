"use client";

import { useMemo, useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine, Legend,
} from "recharts";

export interface TimeSeriesInput {
  date: string;
  value: number;
}

type Granularity = "day" | "month";

interface Props {
  historical: TimeSeriesInput[];
  forecast: TimeSeriesInput[];
  valueLabel: string;
  formatValue?: (v: number) => string;
  yAxisFormatter?: (v: number) => string;
}

function monthKey(dateStr: string): string {
  const d = new Date(dateStr);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

function formatDateLabel(dateStr: string, granularity: Granularity): string {
  const d = new Date(dateStr);
  if (granularity === "month") {
    return d.toLocaleDateString("id-ID", { month: "short", year: "numeric" });
  }
  return d.toLocaleDateString("id-ID", { day: "2-digit", month: "short" });
}

function aggregateByMonth(points: TimeSeriesInput[]): TimeSeriesInput[] {
  const buckets = new Map<string, number>();
  for (const p of points) {
    const key = monthKey(p.date);
    buckets.set(key, (buckets.get(key) ?? 0) + p.value);
  }
  return Array.from(buckets.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([key, value]) => ({ date: `${key}-01`, value }));
}

function buildChartData(
  historical: TimeSeriesInput[],
  forecast: TimeSeriesInput[],
  granularity: Granularity,
) {
  const hist = granularity === "month" ? aggregateByMonth(historical) : historical;
  const fcst = granularity === "month" ? aggregateByMonth(forecast) : forecast;

  const dateMap = new Map<string, { date: string; actual: number | null; forecast: number | null }>();

  const normalizeDate = (d: string) => d.split("T")[0];

  for (const p of hist) {
    const key = normalizeDate(p.date);
    dateMap.set(key, { date: key, actual: Math.round(p.value), forecast: null });
  }
  for (const p of fcst) {
    const key = normalizeDate(p.date);
    const existing = dateMap.get(key);
    if (existing) {
      existing.forecast = Math.round(p.value);
    } else {
      dateMap.set(key, { date: key, actual: null, forecast: Math.round(p.value) });
    }
  }

  const sortedData = Array.from(dateMap.values()).sort(
    (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
  );

  let lastActualIdx = -1;
  for (let i = sortedData.length - 1; i >= 0; i--) {
    if (sortedData[i].actual !== null) {
      lastActualIdx = i;
      break;
    }
  }

  if (lastActualIdx !== -1 && lastActualIdx < sortedData.length - 1) {
    sortedData[lastActualIdx].forecast = sortedData[lastActualIdx].actual;
  }

  return sortedData;
}

export default function HistoricalForecastChart({
  historical,
  forecast,
  valueLabel,
  formatValue = (v) => v.toLocaleString("id-ID"),
  yAxisFormatter,
}: Props) {
  const [granularity, setGranularity] = useState<Granularity>("day");

  const chartData = useMemo(
    () => buildChartData(historical, forecast, granularity),
    [historical, forecast, granularity],
  );

  const boundaryLabel = useMemo(() => {
    if (historical.length === 0) return null;
    const hist = granularity === "month" ? aggregateByMonth(historical) : historical;
    const lastHist = hist[hist.length - 1];
    return lastHist.date.split("T")[0];
  }, [historical, granularity]);

  const yFmt = yAxisFormatter ?? ((v: number) => formatValue(v));

  if (historical.length === 0 && forecast.length === 0) {
    return <p className="text-[14px] text-steel-400">Tidak ada data untuk ditampilkan.</p>;
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4 text-[12px] text-steel-400">
          <span className="flex items-center gap-1.5">
            <span className="inline-block w-5 h-0.5 bg-navy-800 rounded" />
            Historis
          </span>
          <span className="flex items-center gap-1.5">
            <span className="inline-block w-5 h-0.5 border-t-2 border-dashed border-amber-600" />
            Proyeksi
          </span>
        </div>
        <div className="flex rounded-lg border border-cream-300 overflow-hidden text-[13px]">
          <button
            type="button"
            onClick={() => setGranularity("day")}
            className={`px-3.5 py-1.5 transition-colors ${
              granularity === "day"
                ? "bg-navy-800 text-cream-50"
                : "bg-white text-steel-400 hover:bg-cream-50"
            }`}
          >
            Harian
          </button>
          <button
            type="button"
            onClick={() => setGranularity("month")}
            className={`px-3.5 py-1.5 transition-colors border-l border-cream-300 ${
              granularity === "month"
                ? "bg-navy-800 text-cream-50"
                : "bg-white text-steel-400 hover:bg-cream-50"
            }`}
          >
            Bulanan
          </button>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={chartData} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#EDE7DA" />
          <XAxis
            dataKey="date"
            tickFormatter={(val) => formatDateLabel(val, granularity)}
            fontSize={11}
            stroke="#6B7883"
            interval="preserveStartEnd"
            angle={granularity === "day" && chartData.length > 20 ? -35 : 0}
            textAnchor={granularity === "day" && chartData.length > 20 ? "end" : "middle"}
            height={granularity === "day" && chartData.length > 20 ? 55 : 30}
          />
          <YAxis
            fontSize={12}
            stroke="#6B7883"
            width={75}
            tickFormatter={yFmt}
          />
          <Tooltip
            labelFormatter={(label) => formatDateLabel(label as string, granularity)}
            contentStyle={{
              fontFamily: "Times New Roman",
              borderColor: "#DDD4C2",
              borderRadius: 8,
            }}
            formatter={(v: number, name: string) => [
              formatValue(v),
              name === "actual" ? `${valueLabel} (Historis)` : `${valueLabel} (Proyeksi)`,
            ]}
          />
          <Legend
            wrapperStyle={{ fontSize: 12 }}
            formatter={(value) => (value === "actual" ? "Historis" : "Proyeksi")}
          />
          {boundaryLabel && (
            <ReferenceLine
              x={boundaryLabel}
              stroke="#C4A882"
              strokeDasharray="4 4"
              label={{ value: "Proyeksi →", position: "insideTopRight", fontSize: 11, fill: "#6B7883" }}
            />
          )}
          <Line
            type="monotone"
            dataKey="actual"
            stroke="#132135"
            strokeWidth={2}
            dot={false}
            connectNulls={false}
            name="actual"
          />
          <Line
            type="monotone"
            dataKey="forecast"
            stroke="#D97706"
            strokeWidth={2}
            strokeDasharray="6 4"
            dot={false}
            connectNulls={false}
            name="forecast"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
