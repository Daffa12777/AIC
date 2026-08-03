export interface ColumnMapping {
  original_column: string;
  mapped_to: string | null;
  method: "dictionary" | "fuzzy" | "unmatched";
  confidence: number;
}

export interface UploadResult {
  dataset_id: string;
  filename: string;
  row_count: number;
  mapping: ColumnMapping[];
  missing_required_columns: string[];
  needs_manual_confirmation: boolean;
  is_valid: boolean;
  preview: Record<string, unknown>[];
}

export interface ForecastPoint {
  date: string;
  period: string;
  energy: number;
}

export interface EnergyInsight {
  trend_label: "meningkat" | "menurun" | "stabil";
  change_pct: number;
  volatility_label: "rendah" | "sedang" | "tinggi";
  coefficient_of_variation: number;
  average_energy: number;
  narrative: string;
  recommendation_note: string;
  model_note: string | null;
}

export interface ForecastResult {
  dataset_id: string;
  best_model: string | null;
  metrics: Record<string, { mae: number; rmse: number }> | null;
  horizon_days: number;
  forecast: ForecastPoint[];
  insight: EnergyInsight | null;
}

export interface CostInsight {
  narrative: string;
  recommendation_note: string;
}

export interface CostResult {
  dataset_id: string;
  period: string;
  total_energy_kwh: number;
  energy_cost: number;
  material_cost: number;
  total_production_cost: number;
  estimated_cost_per_unit: number;
  energy_cost_share: number;
  periods: number;
  insight: CostInsight | null;
}

export interface AnomalyPoint {
  date: string;
  period: string;
  energy: number;
  deviation_pct: number;
}

export interface AnomalyResult {
  dataset_id: string;
  period: string | null;
  total_anomalies: number;
  anomalies: AnomalyPoint[];
  narrative: string;
}

export interface RecommendationResult {
  dataset_id: string;
  period: string;
  priority_level: "rendah" | "sedang" | "tinggi";
  summary: string;
  reasoning: string;
  action_items: string[];
  caveat: string;
}

export interface DashboardSummary {
  total_datasets: number;
  total_forecasts_run: number;
  total_cost_analyses: number;
  total_anomaly_scans: number;
  total_recommendations: number;
  recent_activity: Record<string, unknown>[];
}
