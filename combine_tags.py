#!/usr/bin/env python3
import csv
import os
from typing import List, Dict, Set

BC_FILE = "/workspace/TAGI_BC_nexidia.xlsx - Nexidia ODZ.csv"
V2T_FILE = "/workspace/TAI_EDIT_Voice2text.xlsx - Kodowanie.csv"
OUT_FILE = "/workspace/TAI_combined_with_tag_columns.csv"

# Possible tag column names across sources
TAG_COL_NAMES = [
    "TAI-tagi",
    "TAI - tagi",
    "TAI- tagi",
    "Tagi",
    "tagi",
]

def read_csv_rows(path: str) -> List[Dict[str, str]]:
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = [dict(r) for r in reader]
    return rows


def get_tag_column_name(headers: List[str]) -> str:
    # Prefer explicit names by order
    for candidate in TAG_COL_NAMES:
        if candidate in headers:
            return candidate
    # Fallback: any header containing 'tagi'
    for h in headers:
        if "tagi" in h.lower():
            return h
    return ""


def parse_tags(tag_str: str) -> List[str]:
    if not tag_str:
        return []
    # Split by comma and strip
    parts = [p.strip() for p in tag_str.split(",")]
    # Drop empties and deduplicate preserving order
    seen: Set[str] = set()
    result: List[str] = []
    for p in parts:
        if not p:
            continue
        if p not in seen:
            seen.add(p)
            result.append(p)
    return result


def main():
    sources = [
        (BC_FILE, "bc_nexidia"),
        (V2T_FILE, "voice2text"),
    ]
    all_rows: List[Dict[str, str]] = []
    all_headers: List[str] = []
    unique_tags: Set[str] = set()

    for path, source in sources:
        rows = read_csv_rows(path)
        headers = list(rows[0].keys()) if rows else []
        all_headers = list(set(all_headers).union(headers))
        tag_col = get_tag_column_name(headers)
        for r in rows:
            r_copy = dict(r)
            r_copy["source"] = source
            tags_raw = r.get(tag_col, "") if tag_col else ""
            r_copy["tags_raw"] = tags_raw
            tags_list = parse_tags(tags_raw)
            # store temporary list for later
            r_copy["__tags_list"] = "||".join(tags_list)  # temp serialization
            unique_tags.update(tags_list)
            all_rows.append(r_copy)

    # Prepare output headers: union of all original headers + computed fields + one-hot tag columns
    base_headers = list(all_headers)
    # Ensure deterministic order: sort base headers except computed
    base_headers = sorted(h for h in base_headers)
    computed_headers = ["source", "tags_raw", "tags_combo"]
    # One-hot tag columns with a prefix to avoid collisions
    tag_columns = [f"tag:{t}" for t in sorted(unique_tags)]

    out_headers = base_headers + computed_headers + tag_columns

    # Build output rows
    out_rows: List[Dict[str, str]] = []
    for r in all_rows:
        out_r: Dict[str, str] = {h: r.get(h, "") for h in base_headers}
        out_r["source"] = r.get("source", "")
        tags_list = r.get("__tags_list", "").split("||") if r.get("__tags_list") else []
        # tags combo: sorted, pipe-separated for easy pivoting
        out_r["tags_combo"] = " | ".join(sorted(tags_list)) if tags_list else ""
        out_r["tags_raw"] = r.get("tags_raw", "")
        # One-hot
        present = set(tags_list)
        for t in unique_tags:
            out_r[f"tag:{t}"] = "1" if t in present else "0"
        out_rows.append(out_r)

    # Write
    with open(OUT_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_headers)
        writer.writeheader()
        for r in out_rows:
            writer.writerow(r)

    print(f"Wrote {len(out_rows)} rows to {OUT_FILE} with {len(tag_columns)} tag columns.")


if __name__ == "__main__":
    main()