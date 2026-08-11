import type {
  UploadResult, ForecastResult, CostResult, AnomalyResult,
  RecommendationResult,
} from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function handle<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = "Terjadi kesalahan pada server.";
    try {
      const body = await res.json();
      detail = body.detail || detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return res.json();
}

export async function uploadDataset(file: File): Promise<UploadResult> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_URL}/upload/`, { method: "POST", body: form });
  return handle<UploadResult>(res);
}

export async function runForecast(
  datasetId: string,
  periods: string[],
  horizonDays: number
): Promise<ForecastResult> {
  const res = await fetch(`${API_URL}/forecast/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dataset_id: datasetId, periods, horizon_days: horizonDays }),
  });
  return handle<ForecastResult>(res);
}

export async function runCostAnalysis(
  datasetId: string,
  period: string,
  horizonDays: number
): Promise<CostResult> {
  const res = await fetch(`${API_URL}/cost/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dataset_id: datasetId, period, horizon_days: horizonDays }),
  });
  return handle<CostResult>(res);
}

export async function runAnomalyScan(
  datasetId: string,
  period: string | null
): Promise<AnomalyResult> {
  const res = await fetch(`${API_URL}/anomaly/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dataset_id: datasetId, period }),
  });
  return handle<AnomalyResult>(res);
}

export async function runRecommendation(
  datasetId: string,
  period: string,
  horizonDays: number
): Promise<RecommendationResult> {
  const res = await fetch(`${API_URL}/recommend/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ dataset_id: datasetId, period, horizon_days: horizonDays }),
  });
  return handle<RecommendationResult>(res);
}
