import csv
import os
import sys
from typing import Dict, List, Set, Tuple

import pandas as pd


WORKDIR = "/workspace"
INPUT_A = os.path.join(WORKDIR, "TAI_EDIT_Voice2text_claude_gpt_human.csv")
INPUT_B = os.path.join(WORKDIR, "TAGI_BC_ODZ.csv")
OUTPUT = os.path.join(WORKDIR, "BC_TAI_combined_with_pipelines.csv")


def normalize_space(text: str) -> str:
    if not isinstance(text, str):
        return text
    # Replace non-breaking spaces and strange whitespaces
    return (
        text.replace("\u00A0", " ")
        .replace("\u2009", " ")
        .replace("\u202F", " ")
        .strip()
    )


def canonicalize_column_name(col: str) -> str:
    col = normalize_space(col)
    # Unify similar column names into a canonical set
    mapping = {
        "TAI - refined_zadania": "TAI_refined_zadania",
        "TAI-refined zadania": "TAI_refined_zadania",
        "TAI - tagi": "TAI_tagi",
        "TAI-tagi": "TAI_tagi",
        "TAI - uwagi": "TAI_uwagi",
        "TAI-uwagi": "TAI_uwagi",
        "TAI - tok myslenia": "TAI_tok_myslenia",
        "dodatkowe": "dodatkowe",
        # Business columns - keep their names, but trim spaces
        "OPIS- CO BADAMY": "OPIS_CO_BADAMY",
        "OPIS- CO BADAMY ": "OPIS_CO_BADAMY",
        "KORZYŚCIE DLA BANKU/OBSZARU/ZESPOŁU": "KORZYSCIE_DLA_BANKU_OBSZARU_ZESPOLU",
        "KORZYŚCIE DLA BANKU/OBSZARU/ZESPOŁU ": "KORZYSCIE_DLA_BANKU_OBSZARU_ZESPOLU",
        "NAZWA - PROJEKT": "NAZWA_PROJEKT",
        "Zespół zgłaszający potrzebę": "Zespol_zglaszajacy_potrzebe",
        "Projekt": "Projekt",
        "Cel biznesowy": "Cel_biznesowy",
        "KPI": "KPI",
        "Opis": "Opis",
        "Korzyść dla Banku/Obszaru/Zespołu": "Korzyść_dla_Banku_Obszaru_Zespołu",
        "STRUMIEŃ": "STRUMIEN",
        "STATUS": "STATUS",
        "TYP (BIZNES/PROCES/KONTROLA)": "TYP",
        "WHISPER/NEXIDIA": "WHISPER_NEXIDIA",
        "PRIORYTET": "PRIORYTET",
        "PROBLEM": "PROBLEM",
        "NUMER": "NUMER",
    }
    col2 = mapping.get(col)
    if col2:
        return col2
    return col


def normalize_tag(tag: str) -> str:
    if not isinstance(tag, str):
        return ""
    t = normalize_space(tag)
    t = t.strip('"\'\u2019\u201c\u201d ')
    t = t.lower()
    # Replace separators with hyphen
    for ch in [" ", "_", "/", "\\", "—", "–"]:
        t = t.replace(ch, "-")
    # Collapse multiple hyphens
    while "--" in t:
        t = t.replace("--", "-")
    # Specific canonical mappings for known variants
    canonical_map = {
        # clustering/extraction/binary variants
        "clusterowanie-fraz": "frazy-clustering",
        "clustering-frazy": "frazy-clustering",
        "frazy-clustering": "frazy-clustering",
        "ekstrakcja-fraz": "frazy-ekstrakcja",
        "frazy-ekstrakcja": "frazy-ekstrakcja",
        "ekstrakcja-frazy": "frazy-ekstrakcja",
        "binary": "frazy-binary",
        "frazy-binary": "frazy-binary",
        "binary-frazy": "frazy-binary",
        # other frequent tags normalization
        "kategoryzacja-rozmów": "kategoryzacja-rozmow",
        "poczta-głosowa": "poczta-glosowa",
        "llm-ocena-argumentów": "llm-ocena-argumentow",
        "scoring-jakości": "scoring-jakosci",
        "baza-wektorowa-tematy": "baza-wektorowa-tematy",
    }
    t = canonical_map.get(t, t)
    return t


def split_and_normalize_tags(tag_str: str) -> List[str]:
    if not isinstance(tag_str, str) or not tag_str.strip():
        return []
    raw = [normalize_space(x) for x in tag_str.split(",")]
    norm = [normalize_tag(x) for x in raw if normalize_tag(x)]
    # Remove empties and duplicates while preserving order
    seen: Set[str] = set()
    out: List[str] = []
    for x in norm:
        if x and x not in seen:
            out.append(x)
            seen.add(x)
    return out


def read_csv_with_canonical_columns(path: str) -> pd.DataFrame:
    # Try utf-8-sig first; fallback to latin-1 if needed
    for enc in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            df = pd.read_csv(path, encoding=enc, dtype=str, keep_default_na=False)
            break
        except Exception:
            df = None
    if df is None:
        raise RuntimeError(f"Failed to read CSV: {path}")
    # Strip NBSP and whitespace from headers
    df.columns = [canonicalize_column_name(c) for c in df.columns]
    # Normalize cell whitespace
    for c in df.columns:
        df[c] = df[c].map(normalize_space)
    return df


def build_pipeline_key_from_tags(tags: List[str]) -> Tuple[str, Tuple[str, ...]]:
    # Consider only methodological tags; by default anything starting with 'frazy-'
    method_tags = [t for t in tags if t.startswith("frazy-")]
    if not method_tags:
        return "", tuple()
    method_tags_sorted = tuple(sorted(method_tags))
    key = ", ".join(method_tags_sorted)
    return key, method_tags_sorted


def main() -> int:
    df_a = read_csv_with_canonical_columns(INPUT_A)
    df_b = read_csv_with_canonical_columns(INPUT_B)

    # Align the refined columns presence in both
    # Ensure canonical refined columns exist
    for col in [
        "TAI_refined_zadania",
        "TAI_tagi",
        "TAI_uwagi",
        "TAI_tok_myslenia",
        "dodatkowe",
    ]:
        if col not in df_a.columns:
            df_a[col] = ""
        if col not in df_b.columns:
            df_b[col] = ""

    # Normalize tags and store normalized list and string
    for df in (df_a, df_b):
        df["TAI_tagi_list"] = df["TAI_tagi"].apply(split_and_normalize_tags)
        df["TAI_tagi_normalized"] = df["TAI_tagi_list"].apply(lambda lst: ", ".join(lst))
        # Build pipeline keys based on methodological tags
        keys_and_sets = df["TAI_tagi_list"].apply(build_pipeline_key_from_tags)
        df["pipeline_key"] = keys_and_sets.apply(lambda ks: ks[0])
        df["pipeline_tags"] = keys_and_sets.apply(lambda ks: ", ".join(ks[1]))

    # Select core columns to keep from each dataset
    # We keep all columns, but ensure the normalized/derived columns are included
    common_cols = sorted(set(df_a.columns).union(df_b.columns))
    df_a = df_a.reindex(columns=common_cols)
    df_b = df_b.reindex(columns=common_cols)

    combined = pd.concat([df_b, df_a], ignore_index=True)

    # Create pipeline binary columns for each unique non-empty pipeline_key
    unique_pipelines = [k for k in sorted(combined["pipeline_key"].unique()) if k]
    for k in unique_pipelines:
        combined[f"pipeline::{k}"] = (combined["pipeline_key"] == k).astype(int)

    # Write output
    combined.to_csv(OUTPUT, index=False, encoding="utf-8-sig", quoting=csv.QUOTE_MINIMAL)

    # Also write a small report to stdout
    print(f"Wrote combined CSV to: {OUTPUT}")
    print(f"Rows: {len(combined)}")
    print("Pipelines (columns created):")
    for k in unique_pipelines:
        count = int((combined["pipeline_key"] == k).sum())
        print(f" - {k} -> {count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())