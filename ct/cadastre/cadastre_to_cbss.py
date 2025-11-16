#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch-map several fields from a cadastre CSV to CBSS by fuzzy cave-name match (no averaging).
- Fuzzy name matching (accents/spaces/punctuation normalized)
- Auto-detect CBSS delimiter (;, , or tab) and write back with the same
- Fill **only blank** cells in targets; preserve existing data
- Preserve original CBSS row/column order (append targets if needed)

Default fields mapped (cadastre → CBSS target):
  - Main entrance width (Dimenzije glavnog ulaza (širina))
  - Main entrance height (Dimenzije glavnog ulaza (visina))  [also matches 'hught']
  - Cave length (Duljina (m))
  - Horizontal cave length (Horizontalna duljina (m))
  - Cave depth (Dubina (m))
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Tuple, Dict
import unicodedata
import pandas as pd


# ---------- helpers ----------

def _strip(s: str) -> str:
    return str(s).strip().strip("\ufeff").strip()


def _normalize(s: str) -> str:
    if s is None:
        return ""
    s = _strip(s).lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = " ".join(s.replace("\t", " ").split())
    return s


def _keyify_value(v: str) -> str:
    if v is None:
        return ""
    v = _strip(v).lower()
    v = unicodedata.normalize("NFKD", v)
    v = "".join(ch for ch in v if not unicodedata.combining(ch))
    out = []
    for ch in v:
        out.append(ch if ch.isalnum() else " ")
    return " ".join("".join(out).split())


def _col_lookup(cols, *needles):
    norm_map = {c: _normalize(c) for c in cols}
    targets = [_normalize(n) for n in needles]
    # exact normalized match
    for orig, norm in norm_map.items():
        if norm in targets:
            return orig
    # substring normalized match
    for orig, norm in norm_map.items():
        if any(t in norm for t in targets):
            return orig
    return None


def _read_csv_smart(path: Path, default_sep=";") -> Tuple[pd.DataFrame, str]:
    """Try ; , and tab. Return df and sep used."""
    for sep in [";", ",", "\t"]:
        try:
            df = pd.read_csv(path, sep=sep, dtype=str, engine="python", encoding=None)
            if df.shape[1] > 1:
                return df, sep
        except Exception:
            continue
    df = pd.read_csv(path, sep=default_sep, dtype=str, engine="python", encoding=None)
    return df, default_sep


def _to_scalar_value(s: pd.Series) -> pd.Series:
    """Clean a string series: prefer numeric token; otherwise keep trimmed string."""
    if s is None:
        return pd.Series(dtype=str)
    ss = s.astype(str).str.strip()
    # strip % and convert comma decimals
    cleaned = ss.str.replace("%", "", regex=False).str.replace(",", ".", regex=False)
    extracted = cleaned.str.extract(r"([-+]?\d*\.?\d+)")[0]
    out = ss.where(extracted.isna(), extracted)
    return out


# ---------- batch mapping ----------

DEFAULT_FIELDS: List[Tuple[str, str]] = [
    ("Main entrance width (Dimenzije glavnog ulaza (širina))", "Main entrance width (Dimenzije glavnog ulaza (širina))"),
    ("Main entrance hught (Dimenzije glavnog ulaza (visina))", "Main entrance hught (Dimenzije glavnog ulaza (visina))"),
    ("Main entrance height (Dimenzije glavnog ulaza (visina))", "Main entrance hught (Dimenzije glavnog ulaza (visina))"),
    ("Number of entrances (Broj ulaza)", "Number of entrances (Broj ulaza)"),
    ("Cave length (Duljina (m))", "Cave length (Duljina (m))"),
    ("Horizontal cave length (Horizontalna duljina (m))", "Horizontal cave length (Horizontalna duljina (m))"),
    ("Cave depth (Dubina (m))", "Cave depth (Dubina (m))"),
]





def map_fields(cad_path: Path, cbss_path: Path, out_path: Path,
               cad_join_col: str = "Cave name (Ime objekta)",
               cbss_join_col: str = "cave name",
               fields: list = DEFAULT_FIELDS) -> None:
    # Read input files (cadastre is typically comma-separated, CBSS autodetected)
    cad_df, _ = _read_csv_smart(cad_path, default_sep=",")
    cbss_df, cbss_sep = _read_csv_smart(cbss_path)

    # ---- work out which columns to join on ----
    cad_join_actual = (
        _col_lookup(cad_df.columns, cad_join_col, "cave name", "cave name (Ime objekta)", "locality")
        or cad_join_col
    )
    if cad_join_actual not in cad_df.columns:
        token_cols = [c for c in cad_df.columns if all(tok in _normalize(c) for tok in ("cave", "name"))]
        if token_cols:
            cad_join_actual = token_cols[0]
        elif _col_lookup(cad_df.columns, "locality"):
            cad_join_actual = _col_lookup(cad_df.columns, "locality")

    cbss_join_actual = (
        _col_lookup(cbss_df.columns, cbss_join_col, "cave name", "locality")
        or cbss_join_col
    )

    if cad_join_actual not in cad_df.columns:
        raise SystemExit(
            f"Cadastre join column not found: {cad_join_col} (tried: 'cave name' / 'locality')"
        )
    if cbss_join_actual not in cbss_df.columns:
        raise SystemExit(f"CBSS join column not found: {cbss_join_col}")

    # Normalised keys used for matching between the two tables
    cad_keys = cad_df[cad_join_actual].astype(str).map(_keyify_value)
    cbss_df["__join_key__"] = cbss_df[cbss_join_actual].astype(str).map(_keyify_value)

    # Preserve original CBSS column and row order
    cbss_cols_order = list(cbss_df.columns)
    cbss_df["__row_order__"] = range(len(cbss_df))

    # ---- build cadastre → value maps for each requested field ----
    maps: Dict[str, Dict[str, str]] = {}
    for src_name, tgt_name in fields:
        # Basic lookup by the provided source name
        src_actual = _col_lookup(cad_df.columns, src_name)

        # Special-case: sometimes 'height' vs. 'hught' is misspelled; try to be forgiving
        if src_actual is None and "hught" in _normalize(src_name):
            src_actual = _col_lookup(
                cad_df.columns,
                "Main entrance height (Dimenzije glavnog ulaza (visina))",
                "Main entrance hught (Dimenzije glavnog ulaza (visina))",
            )

        if src_actual is None:
            src_actual = src_name

        if src_actual not in cad_df.columns:
            print(f"[WARN] Cadastre column not found: {src_name}")
            continue

        vals = _to_scalar_value(cad_df[src_actual])
        maps[tgt_name] = dict(zip(cad_keys, vals))

    # What counts as a blank cell in CBSS (only these will be overwritten)
    def is_blank(s: pd.Series) -> pd.Series:
        blanks = {"", "-", "—", "na", "n/a", "null", "none"}
        return s.isna() | s.astype(str).str.strip().str.lower().isin(blanks)
        # If you also want literal '0' to be overwritten, add "0" to the blanks set above.

    # ---- actually apply fills into the CBSS dataframe ----
    for tgt_name, value_map in maps.items():
        tgt_actual = _col_lookup(cbss_df.columns, tgt_name) or tgt_name
        if tgt_actual not in cbss_df.columns:
            cbss_df[tgt_actual] = ""

        # Values from the cadastre, aligned to CBSS rows via the join key
        fills = cbss_df["__join_key__"].map(value_map)

        mask = is_blank(cbss_df[tgt_actual]) & fills.notna()
        n_candidates = int(fills.notna().sum())
        n_blank = int(is_blank(cbss_df[tgt_actual]).sum())
        n_applied = int(mask.sum())

        print(
            f"[INFO] Field '{tgt_actual}': candidates from cadastre={n_candidates}, "
            f"blank cells in CBSS={n_blank}, filled={n_applied}"
        )

        # ✅ This is the crucial part that was missing before
        cbss_df.loc[mask, tgt_actual] = fills[mask]

    # Clean up helper columns and restore original order
    cbss_df.drop(columns=["__row_order__", "__join_key__"], errors="ignore", inplace=True)
    base_order = [c for c in cbss_cols_order if c in cbss_df.columns]
    extra = [c for c in cbss_df.columns if c not in base_order]
    cbss_df = cbss_df[base_order + extra]

    # Write out with the same delimiter CBSS originally had
    cbss_df.to_csv(out_path, sep=cbss_sep, index=False)

    # Simple debug summary
    try:
        inter = len(set(cad_keys) & set(cbss_df[cbss_join_actual].astype(str).map(_keyify_value)))
        print(
            f"[DEBUG] cadastre rows: {len(cad_df)}  CBSS rows: {len(cbss_df)}  matched keys: {inter}"
        )
    except Exception:
        pass


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Batch map cadastre fields onto CBSS (no averaging)." )
    ap.add_argument("--cadastre", required=True, type=Path, help="Path to cadastre CSV (e.g., Croatian_cave_cadastre.csv)")
    ap.add_argument("--cbss", required=True, type=Path, help="Path to CBSS CSV to update (e.g., CBSS.updated.csv)")
    ap.add_argument("--out", required=True, type=Path, help="Output CSV path for updated CBSS")
    ap.add_argument("--cad-join-col", default="Cave name (Ime objekta)", help="Cadastre cave name column")
    ap.add_argument("--cbss-join-col", default="cave name", help="CBSS cave name column")
    args = ap.parse_args(argv)

    map_fields(args.cadastre, args.cbss, args.out,
               cad_join_col=args.cad_join_col,
               cbss_join_col=args.cbss_join_col)
    print(f"Updated CBSS written to: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
