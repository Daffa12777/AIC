"""
Fuzzy matching kolom menggunakan RapidFuzz.
Dipakai bila dictionary mapping tidak menemukan kecocokan persis.
"""
from rapidfuzz import fuzz, process

from data_adapter.dictionary_mapping import COLUMN_SYNONYMS
from config.settings import FUZZY_MATCH_THRESHOLD


def _all_candidates() -> list[tuple[str, str]]:
    """Kembalikan daftar (sinonim, kolom_standar) untuk seluruh kamus."""
    candidates = []
    for standard, synonyms in COLUMN_SYNONYMS.items():
        for syn in synonyms:
            candidates.append((syn.lower().strip(), standard))
    return candidates


def fuzzy_match_column(column_name: str) -> tuple[str | None, float]:
    """
    Cari kolom standar terdekat untuk column_name via fuzzy matching.
    Return (kolom_standar | None, confidence 0-100).
    """
    candidates = _all_candidates()
    synonym_list = [c[0] for c in candidates]

    match = process.extractOne(
        column_name.lower().strip(),
        synonym_list,
        scorer=fuzz.token_sort_ratio,
    )
    if match is None:
        return None, 0.0

    matched_synonym, score, idx = match
    if score >= FUZZY_MATCH_THRESHOLD:
        return candidates[idx][1], float(score)
    return None, float(score)
