"""
Smart Data Adapter
Menormalkan berbagai format dataset perusahaan aluminium ke skema standar
melalui tiga lapis: dictionary mapping -> fuzzy matching -> konfirmasi manual.
Tidak menggunakan LLM agar ringan dijalankan secara lokal.
"""
from dataclasses import dataclass, field

import pandas as pd

from data_adapter.dictionary_mapping import build_reverse_lookup
from data_adapter.fuzzy_matching import fuzzy_match_column
from config.settings import REQUIRED_COLUMNS, OPTIONAL_COLUMNS


@dataclass
class ColumnMapping:
    original_column: str
    mapped_to: str | None
    method: str  # "dictionary" | "fuzzy" | "unmatched"
    confidence: float


@dataclass
class AdapterResult:
    dataframe: pd.DataFrame
    mapping: list[ColumnMapping]
    missing_required_columns: list[str]
    needs_manual_confirmation: bool
    is_valid: bool = field(init=False)

    def __post_init__(self):
        self.is_valid = len(self.missing_required_columns) == 0


def _load_dataframe(file_path: str) -> pd.DataFrame:
    if file_path.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(file_path)
    if file_path.lower().endswith((".csv", ".tsv")):
        sep = "\t" if file_path.lower().endswith(".tsv") else ","
        return pd.read_csv(file_path, sep=sep)
    raise ValueError("Format file tidak didukung. Gunakan .xlsx, .xls, .csv, atau .tsv.")


def map_columns(columns: list[str]) -> list[ColumnMapping]:
    """Petakan daftar kolom asli ke skema standar (dictionary lalu fuzzy)."""
    reverse = build_reverse_lookup()
    mappings: list[ColumnMapping] = []
    used_targets: set[str] = set()

    for col in columns:
        key = col.lower().strip()
        if key in reverse and reverse[key] not in used_targets:
            target = reverse[key]
            used_targets.add(target)
            mappings.append(ColumnMapping(col, target, "dictionary", 100.0))
            continue

        target, score = fuzzy_match_column(col)
        if target is not None and target not in used_targets:
            used_targets.add(target)
            mappings.append(ColumnMapping(col, target, "fuzzy", round(score, 1)))
        else:
            mappings.append(ColumnMapping(col, None, "unmatched", round(score, 1)))

    return mappings


def run_smart_data_adapter(file_path: str) -> AdapterResult:
    df = _load_dataframe(file_path)
    mappings = map_columns(list(df.columns))

    rename_map = {m.original_column: m.mapped_to for m in mappings if m.mapped_to}
    standardized = df.rename(columns=rename_map)

    keep_cols = [c for c in (REQUIRED_COLUMNS + OPTIONAL_COLUMNS) if c in standardized.columns]
    standardized = standardized[keep_cols].copy()

    mapped_targets = {m.mapped_to for m in mappings if m.mapped_to}
    missing_required = [c for c in REQUIRED_COLUMNS if c not in mapped_targets]

    has_unmatched = any(m.method == "unmatched" for m in mappings)

    return AdapterResult(
        dataframe=standardized,
        mapping=mappings,
        missing_required_columns=missing_required,
        needs_manual_confirmation=has_unmatched,
    )
