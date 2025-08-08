#!/usr/bin/env python3
import csv
import re
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple

BC_FILE = "/workspace/TAGI_BC_nexidia.xlsx - Nexidia ODZ.csv"
V2T_FILE = "/workspace/TAI_EDIT_Voice2text.xlsx - Kodowanie.csv"
COMBINED_FILE = "/workspace/TAI_combined_with_tag_columns.csv"

MAP_OUT = "/workspace/TAI_tag_normalization_proposals.csv"
LEGEND_OUT = "/workspace/TAI_tag_canonical_legend.csv"
COMBINED_CANON_OUT = "/workspace/TAI_combined_with_canonical_tags.csv"

TAG_COL_NAMES = ["TAI-tagi", "TAI - tagi", "TAI- tagi", "Tagi", "tagi", "tags_raw"]

# Known manual fixes (common typos/variants → canonical)
MANUAL_MAP = {
    "pair-classfication-client-agent": "pair-classification-agent-client",
    "karta kredytowa": "karta-kredytowa",
    "karta kredytowych": "karta-kredytowa",
    "kredyt-got": "kredyt-gotówkowy",
    "frazy-binaryx2": "frazy-binary (2x)",
    "baza-wektorowa-oswiadczenia(procedury)": "baza-wektorowa-oświadczenia",
    "baza-wektorowa-oswiadczenia": "baza-wektorowa-oświadczenia",
    "llm-opis-ocena": "llm-ocena-argumentów",
    "llm-opis-segment": "llm-ocena-segmentu",
    "limit": "limit-w-koncie",
}

# PARENS_RE left unused on purpose to avoid stripping meaningful qualifiers like (2x)


def read_rows(path: str) -> Tuple[List[Dict[str, str]], List[str]]:
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        rdr = csv.DictReader(f)
        rows = [dict(r) for r in rdr]
    return rows, list(rows[0].keys()) if rows else []


def get_tag_col(headers: List[str]) -> str:
    for c in TAG_COL_NAMES:
        if c in headers:
            return c
    for h in headers:
        if "tag" in h.lower():
            return h
    return ""


def normalize_tag_basic(tag: str) -> str:
    t = tag.strip()
    if not t:
        return t
    # Manual overrides first
    if t in MANUAL_MAP:
        t = MANUAL_MAP[t]
    # Normalize separators and case
    t = t.replace("_", "-")
    t = re.sub(r"\s+", "-", t)
    t = re.sub(r"-+", "-", t)
    t = t.strip("- ")
    t = t.lower()
    # Re-apply manual overrides post-normalization just in case
    if t in MANUAL_MAP:
        t = MANUAL_MAP[t]
    return t


def split_tags(s: str) -> List[str]:
    if not s:
        return []
    return [p.strip() for p in s.split(",") if p.strip()]


def main():
    sources = [(BC_FILE, "bc_nexidia"), (V2T_FILE, "voice2text"), (COMBINED_FILE, "combined")]
    tag_counts: Counter = Counter()
    tag_sources: Dict[str, Counter] = defaultdict(Counter)

    all_rows: List[Dict[str, str]] = []

    for path, src in sources:
        try:
            rows, headers = read_rows(path)
        except FileNotFoundError:
            continue
        tag_col = get_tag_col(headers)
        for r in rows:
            tags = split_tags(r.get(tag_col, "")) if tag_col else []
            for t in tags:
                tag_counts[t] += 1
                tag_sources[t][src] += 1
        all_rows.extend({**r, "__source": src} for r in rows)

    # Build canonical mapping by normalization
    canon_map: Dict[str, str] = {}
    for t in tag_counts:
        norm = normalize_tag_basic(t)
        canon_map[t] = norm

    # Aggregate by canonical
    by_canon: Dict[str, List[str]] = defaultdict(list)
    canon_counts: Counter = Counter()
    canon_sources: Dict[str, Counter] = defaultdict(Counter)

    for orig, cnt in tag_counts.items():
        c = canon_map[orig]
        by_canon[c].append(orig)
        canon_counts[c] += cnt
        for s, sc in tag_sources[orig].items():
            canon_sources[c][s] += sc

    # Write normalization proposals
    with open(MAP_OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["original_tag", "canonical_tag", "count", "sources"])
        for orig in sorted(tag_counts.keys(), key=lambda x: x.lower()):
            w.writerow([orig, canon_map[orig], tag_counts[orig], "; ".join(f"{s}:{c}" for s, c in tag_sources[orig].items())])

    # Write canonical legend
    with open(LEGEND_OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["canonical_tag", "total_count", "sources", "variants"])
        for c in sorted(by_canon.keys(), key=lambda x: (x.lower(), x)):
            w.writerow([
                c,
                canon_counts[c],
                "; ".join(f"{s}:{cnt}" for s, cnt in canon_sources[c].items()),
                ", ".join(sorted(by_canon[c], key=lambda x: x.lower())),
            ])

    # Produce combined canonical file with canonical one-hot columns
    try:
        rows, headers = read_rows(COMBINED_FILE)
        # First pass: gather all canonical tags across rows
        all_canonical_tags: Set[str] = set()
        for r in rows:
            tags_raw = r.get("tags_raw", "")
            for t in split_tags(tags_raw):
                all_canonical_tags.add(normalize_tag_basic(t))
        # Prepare headers
        ctag_cols = [f"ctag:{t}" for t in sorted(all_canonical_tags)]
        out_headers = headers + ["tags_raw_canonical", "tags_combo_canonical"] + ctag_cols
        # Write
        with open(COMBINED_CANON_OUT, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=out_headers)
            w.writeheader()
            for r in rows:
                tags_raw = r.get("tags_raw", "")
                tags = split_tags(tags_raw)
                canon_tags = [normalize_tag_basic(t) for t in tags]
                # unique, preserve order
                seen: Set[str] = set()
                canon_unique: List[str] = []
                for t in canon_tags:
                    if t and t not in seen:
                        seen.add(t)
                        canon_unique.append(t)
                r_out = dict(r)
                r_out["tags_raw_canonical"] = ", ".join(canon_unique)
                r_out["tags_combo_canonical"] = " | ".join(sorted(canon_unique))
                for ct in all_canonical_tags:
                    r_out[f"ctag:{ct}"] = "1" if ct in seen else "0"
                w.writerow(r_out)
    except FileNotFoundError:
        pass

    print(f"Wrote {MAP_OUT}, {LEGEND_OUT} and {COMBINED_CANON_OUT if 'rows' in locals() else '(no combined)'}")


if __name__ == "__main__":
    main()