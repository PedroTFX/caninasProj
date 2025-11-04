#!/usr/bin/env python3
"""
Cave temperature aggregator → updates CBSS file.

What it does, per cave name:
- Reads your “field diary” CSVs that have a 2-row header (group row + column row)
- Focuses on two signals only:
  • "air (zrak) temperature" in the group "exact place in the cave not specified"
  • "air temperature" from all groups except "cave entrance (ulaz)"
- Computes per-cave averages:
  • deepest_air_temperature = mean of "air temperature" inside the "deep cave" group
  • media_temperature      = mean of all non-entrance air temperatures (this includes
                             "exact place in the cave not specified", all the
                             "other part of the cave ..." groups, and also "deep cave")
- Writes these back into your CBSS CSV, filling/overwriting the columns
  "deepest air temperature" and "média temperature" (name matching is accent/space/ case-insensitive).

Notes
- We ignore the CBSS column "air temperature" as requested.
- The script is robust to messy spaces, accents, stray BOMs, and commas-as-decimals.
- If your CBSS doesn’t have a dedicated "cave name" column, you can point the join
  to any column (e.g. "locality") using --cbss-join-col.

Usage
------
python cave_temps_to_cbss.py \
  --diary paths/diary1.csv paths/diary2.csv \
  --cbss  paths/CBSS.csv \
  --out   paths/CBSS.updated.csv \
  --cbss-join-col "cave name"

If you only have one diary file, pass a single --diary argument.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Iterable, List, Optional, Tuple
import unicodedata

import pandas as pd

# ---------- Helpers ----------

def _strip(s: str) -> str:
    return s.strip().strip("﻿").strip()


def _normalize(s: str) -> str:
    """Lowercase, remove accents, compress spaces/semicolons for fuzzy matching of COLUMN NAMES."""
    if s is None:
        return ""
    s = str(s)
    s = _strip(s).lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.replace("	", " ").replace(";", ";")
    s = " ".join(s.split())
    return s

import re

def keyify_value(s: str) -> str:
    """Normalize CELL VALUES used for joining (handles Croatian letters).
    - lowercases, trims
    - removes accents
    - maps 'đ'/'Đ' -> 'd'
    - strips punctuation to spaces
    - collapses multiple spaces
    """
    if s is None:
        return ""
    s = str(s)
    s = _strip(s).lower()
    # NFKD accent strip
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    # map special Croatian letters that don't decompose well
    s = s.replace("đ", "d").replace("Đ", "D")
    # unify quotes/dashes
    s = s.replace("’", "'").replace("–", "-")
    # replace non-alphanumeric with space
    s = re.sub(r"[^a-z0-9]+", " ", s)
    # collapse spaces
    s = " ".join(s.split())
    return s


def _col_lookup(cols: Iterable[str], *needles: str) -> Optional[str]:
    """Find a column name in iterable `cols` that loosely matches any of `needles`.
    Matching is case/diacritic/whitespace-insensitive and allows substring inclusions.
    Returns the original column if found, else None.
    """
    norm_map = {c: _normalize(c) for c in cols}
    needle_norms = [_normalize(n) for n in needles]
    for orig, norm in norm_map.items():
        if norm in needle_norms:
            return orig
    for orig, norm in norm_map.items():
        if any(n in norm for n in needle_norms):
            return orig
    return None

def _col_lookup(cols: Iterable[str], *needles: str) -> Optional[str]:
    """Find a column name in iterable `cols` that loosely matches any of `needles`.
    Matching is case/diacritic/whitespace-insensitive and allows substring inclusions.
    Returns the original column if found, else None.
    """
    norm_map = {c: _normalize(c) for c in cols}
    needle_norms = [_normalize(n) for n in needles]
    # exact first
    for orig, norm in norm_map.items():
        if norm in needle_norms:
            return orig
    # then substring
    for orig, norm in norm_map.items():
        if any(n in norm for n in needle_norms):
            return orig
    return None


# ---------- Reading diary files (2-row header) ----------

def read_diary(path: Path) -> pd.DataFrame:
    """Read a diary CSV with two header rows (group row + field row).
    Returns a DF with a flattened MultiIndex header "group|field".

    This version is robust to Windows encodings. It tries several
    encodings automatically: UTF-8 (with/without BOM), CP1252, and Latin-1.
    """
    encodings_to_try = [
        "utf-8",
        "utf-8-sig",
        "cp1252",
        "latin1",
    ]
    last_err = None
    for enc in encodings_to_try:
        try:
            df = pd.read_csv(
                path,
                sep=";",
                header=[0, 1],
                engine="python",
                dtype=str,
                quoting=csv.QUOTE_MINIMAL,
                on_bad_lines="skip",
                encoding=enc,
            )
            break
        except UnicodeDecodeError as e:
            last_err = e
            continue
    else:
        # If all encodings fail, re-raise the last error
        raise last_err

    # Clean top and second header rows
    # If the file isn’t true multiindex everywhere, Pandas may fill NA header entries with 'Unnamed: ...'
    def clean_header(v: str) -> str:
        if pd.isna(v):
            return ""
        v = _strip(str(v))
        v = v.replace("Unnamed: 0_level_0", "").replace("Unnamed: 1_level_0", "")
        v = v.replace("Unnamed: 0_level_1", "").replace("Unnamed: 1_level_1", "")
        return v

    df.columns = pd.MultiIndex.from_tuples(
        [(clean_header(a), clean_header(b)) for a, b in df.columns]
    )

    # Flatten to single-level columns: "group|field" with trimmed pipes
    flat_cols = []
    for g, f in df.columns:
        g2 = _strip(g)
        f2 = _strip(f)
        if not g2 and not f2:
            flat_cols.append("")
        elif not g2:
            flat_cols.append(f2)
        elif not f2:
            flat_cols.append(g2)
        else:
            flat_cols.append(f"{g2}|{f2}")
    df.columns = flat_cols

    # Trim all cells
    for c in df.columns:
        if df[c].dtype == object:
            df[c] = df[c].astype(str).map(_strip)

    return df


def combine_diaries(paths: List[Path]) -> pd.DataFrame:
    """Combine one or more diary CSVs into a single DataFrame."""
    frames = [read_diary(p) for p in paths]
    if not frames:
        raise SystemExit("No diary CSVs were read.")
    return pd.concat(frames, ignore_index=True)


# ---------- Extract temperature columns ----------

GROUP_UNSPEC = "exact place in the cave not specified"
GROUP_ENTR   = "cave entrance"
GROUP_DEEP   = "deep cave"
GROUP_OTHER  = "other part of the cave"

FIELD_AIR_ZRAK = "air (zrak) temperature"
FIELD_AIR      = "air temperature"


def pick_columns(di: pd.DataFrame) -> Tuple[pd.Series, pd.Series, List[pd.Series]]:
    """Return series:
    - cave_name
    - air_unspecified (zrak) from UNSPEC group
    - list of air columns for MEDIA (all non-entrance air temps incl deep + others + unspecified)
    """
    # Cave name lives in the pre-group columns, so it should be a flat column named like "cave name"
    cave_col = _col_lookup(di.columns, "cave name")
    if cave_col is None:
        raise SystemExit(
            "Couldn't find a 'cave name' column in diary files. Please ensure your diary CSVs include it."
        )

    # Unspecified zrak
    # Look for a flattened header like "exact place in the cave not specified|air (zrak) temperature"
    unspec_candidates = [
        c for c in di.columns
        if GROUP_UNSPEC in _normalize(c) and _normalize(FIELD_AIR_ZRAK) in _normalize(c)
    ]
    air_unspec = di[unspec_candidates[0]] if unspec_candidates else pd.Series([None]*len(di))

    # Deep cave: standard air temperature
    deep_cols = [
        c for c in di.columns
        if GROUP_DEEP in _normalize(c) and _normalize(FIELD_AIR) in _normalize(c)
    ]

    # Cave entrance (we will EXCLUDE these from media)
    entrance_cols = [
        c for c in di.columns
        if GROUP_ENTR in _normalize(c) and _normalize(FIELD_AIR) in _normalize(c)
    ]

    # Other part(s): many repeating groups
    other_cols = [
        c for c in di.columns
        if GROUP_OTHER in _normalize(c) and _normalize(FIELD_AIR) in _normalize(c)
    ]

    # Build list of columns used in the MEDIA metric: unspecified zrak as well as deep + others (no entrance)
    media_cols: List[pd.Series] = []
    if not air_unspec.isna().all():
        media_cols.append(air_unspec)
    media_cols += [di[c] for c in deep_cols]
    media_cols += [di[c] for c in other_cols]

    return di[cave_col], air_unspec, media_cols


# ---------- Numeric cleaning ----------

def to_num(s: pd.Series) -> pd.Series:
    if s is None:
        return pd.Series(dtype=float)
    # Replace commas as decimal separator; ignore empty strings, non-numbers become NaN
    return pd.to_numeric(s.str.replace(",", ".", regex=False), errors="coerce")


# ---------- Aggregation per cave ----------

def aggregate_by_cave(di: pd.DataFrame) -> pd.DataFrame:
    """Aggregate temperatures per cave using GRAND MEANS across individual readings.

    - deepest air temperature: grand mean of all individual "deep cave | air temperature" readings
    - média temperature: grand mean of all individual non-entrance air temperature readings
      (unspecified zrak + deep cave + all "other part of the cave"; excludes entrance)
    """
    cave_name, air_unspec, media_cols = pick_columns(di)

    # deep-cave columns for the "deepest" metric
    deep_cols = [
        c for c in di.columns
        if GROUP_DEEP in _normalize(c) and _normalize(FIELD_AIR) in _normalize(c)
    ]

    def pooled_mean_by_cave(cave_s: pd.Series, series_list: List[pd.Series]) -> pd.DataFrame:
        """Return per-cave pooled mean over all numeric values in series_list."""
        if not series_list:
            return pd.DataFrame({"cave name": [], "val": []})
        long = pd.concat(
            [pd.DataFrame({"cave name": cave_s, "val": to_num(s)}) for s in series_list],
            ignore_index=True
        ).dropna(subset=["val"])
        return long.groupby("cave name", as_index=False)["val"].mean()

    # pooled mean over all non-entrance air temps
    media_df = (
        pooled_mean_by_cave(cave_name, media_cols)
        .rename(columns={"val": "média temperature"})
    )

    # pooled mean over deep-cave air temps only
    deep_df = (
        pooled_mean_by_cave(cave_name, [di[c] for c in deep_cols])
        .rename(columns={"val": "deepest air temperature"})
    )

    # combine results
    out = pd.merge(media_df, deep_df, on="cave name", how="outer")
    return out



# ---------- Update CBSS ----------
def update_cbss(cbss_path: Path, agg: pd.DataFrame, out_path: Path, join_col: str) -> None:
    # ---- Read CBSS with robust encodings ----
    encodings_to_try = ["utf-8", "utf-8-sig", "cp1252", "latin1"]
    last_err = None
    for enc in encodings_to_try:
        try:
            cbss = pd.read_csv(cbss_path, sep=";", dtype=str, engine="python", encoding=enc)
            break
        except UnicodeDecodeError as e:
            last_err = e
            continue
    else:
        raise last_err

    # ---- Find join column in CBSS (fuzzy) ----
    join_actual = _col_lookup(cbss.columns, join_col)
    if join_actual is None:
        join_actual = _col_lookup(cbss.columns, "cave name", "locality")
    if join_actual is None:
        raise SystemExit(
            f"Could not find a join column in CBSS matching '{join_col}' or common alternates ('cave name', 'locality')."
        )

    # ---- Helper for formatting back to comma decimals ----
    def fmt_float_col(s: pd.Series) -> pd.Series:
        def conv(x):
            if pd.isna(x) or x == "":
                return ""
            try:
                x2 = x.replace(",", ".").strip() if isinstance(x, str) else x
                return f"{float(x2):.3f}".replace(".", ",")
            except Exception:
                return str(x)
        return s.map(conv)

    # ---- Ensure target columns exist in CBSS ----
    tgt_deep  = _col_lookup(cbss.columns, "deepest air temperature") or "deepest air temperature"
    tgt_media = _col_lookup(cbss.columns, "média temperature", "media temperature") or "média temperature"
    for c in [tgt_deep, tgt_media]:
        if c not in cbss.columns:
            cbss[c] = ""

    # ---- Build normalized join keys on BOTH sides, collapse agg to 1 row per key ----
    def _key(s: pd.Series) -> pd.Series:
        # strong normalizer: lowercase + accents/punctuation removed
        return s.astype(str).map(keyify_value)

    # agg: one row per normalized cave, using pooled means from aggregate_by_cave
    if "cave name" not in agg.columns:
        raise SystemExit("aggregate_by_cave() output must include 'cave name'.")

    agg_work = agg.rename(columns={"cave name": "__cave_name__"}).copy()
    agg_work["__join_key__"] = _key(agg_work["__cave_name__"])

    # numeric means across variants that collapse to the same normalized name
    agg_grouped = (
        agg_work
        .groupby("__join_key__", as_index=False)[["deepest air temperature", "média temperature"]]
        .mean()
        .rename(columns={
            "deepest air temperature": "deepest__agg",
            "média temperature": "media__agg",
        })
    )

    # CBSS side with same key
    cbss_work = cbss.copy()
    cbss_work["__join_key__"] = _key(cbss_work[join_actual])

    # ---- 1:1 merge (pre-collapsed agg prevents cartesian duplicates) ----
    merged = cbss_work.merge(agg_grouped, on="__join_key__", how="left")

    # ---- Write back to target columns (prefer aggregate if present) ----
    merged[tgt_deep]  = merged["deepest__agg"].where(~merged["deepest__agg"].isna(), merged.get(tgt_deep, ""))
    merged[tgt_media] = merged["media__agg"].where(~merged["media__agg"].isna(),  merged.get(tgt_media, ""))

    # format as EU-style comma decimals
    merged[tgt_deep]  = fmt_float_col(merged[tgt_deep])
    merged[tgt_media] = fmt_float_col(merged[tgt_media])

    # ---- Cleanup and save ----
    merged.drop(columns=["__join_key__", "deepest__agg", "media__agg"], errors="ignore", inplace=True)
    merged.to_csv(out_path, sep=";", index=False)



# ---------- CLI ----------

def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Aggregate diary cave temperatures and update CBSS CSV")
    p.add_argument("--diary", nargs="+", required=True, type=Path, help="Path(s) to diary CSV(s) with 2-row headers")
    p.add_argument("--cbss", required=True, type=Path, help="Path to CBSS CSV to update")
    p.add_argument("--out", required=True, type=Path, help="Output CSV path for updated CBSS")
    p.add_argument("--cbss-join-col", default="cave name", help="CBSS column to match with diary 'cave name' (default: 'cave name')")

    args = p.parse_args(argv)

    # Read and aggregate diaries
    diary_df = combine_diaries(args.diary)
    agg = aggregate_by_cave(diary_df)

    # Update CBSS
    update_cbss(args.cbss, agg, args.out, args["cbss_join_col"] if isinstance(args, dict) else args.cbss_join_col)

    print(f"Updated CBSS written to: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
