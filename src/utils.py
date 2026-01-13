from __future__ import annotations
import os
import logging
from datetime import datetime
from typing import List
import pandas as pd

def build_run_id(dataset: str) -> str:
    return datetime.now().strftime(f"{dataset}_%Y%m%d_%H%M%S")

def ensure_dirs(paths: List[str]) -> None:
    for p in paths:
        os.makedirs(p, exist_ok=True)

def read_csv_safely(path: str, logger: logging.Logger | None = None) -> pd.DataFrame:
    # Read everything as string first to avoid implicit type bugs.
    df = pd.read_csv(path, dtype=str, keep_default_na=False, na_values=["", "NA", "N/A", "null", "None"])
    if logger:
        logger.info("Loaded %s rows from %s", len(df), path)
    return df

def normalize_strings(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    for c in cols:
        if c in df.columns:
            df[c] = (
                df[c].astype("string")
                    .str.strip()
                    .str.replace(r"\s+", " ", regex=True)
            )
            # common normalizations
            if c in {"channel", "source", "status"}:
                df[c] = df[c].str.lower()
            if c in {"city", "region", "product"}:
                # title-case but preserve accents
                df[c] = df[c].str.lower().str.title()
    return df

def parse_dates_flex(df: pd.DataFrame, col: str, logger: logging.Logger | None = None) -> pd.DataFrame:
    if col not in df.columns:
        return df
    # Try multiple dayfirst settings; keep best parse rate
    s = df[col].astype("string")
    parsed_dayfirst = pd.to_datetime(s, errors="coerce", dayfirst=True, infer_datetime_format=True)
    parsed_monthfirst = pd.to_datetime(s, errors="coerce", dayfirst=False, infer_datetime_format=True)

    dayfirst_ok = parsed_dayfirst.notna().mean()
    monthfirst_ok = parsed_monthfirst.notna().mean()
    chosen = parsed_dayfirst if dayfirst_ok >= monthfirst_ok else parsed_monthfirst

    df[col] = chosen
    if logger:
        logger.info("Parsed dates in %s: success_rate=%.1f%% (dayfirst=%.1f%% monthfirst=%.1f%%)",
                    col, 100*chosen.notna().mean(), 100*dayfirst_ok, 100*monthfirst_ok)
    return df

def coerce_numeric(df: pd.DataFrame, cols: List[str], logger: logging.Logger | None = None) -> pd.DataFrame:
    for c in cols:
        if c not in df.columns:
            continue
        before_na = df[c].isna().mean()
        # remove currency symbols and spaces
        df[c] = (
            df[c].astype("string")
                 .str.replace(r"[^\d\-\.,]", "", regex=True)
        )
        # Standardize decimal separator: if both dot and comma exist, assume dot is thousands sep
        # (handled elsewhere for revenue if needed)
        df[c] = df[c].str.replace(",", ".", regex=False)
        df[c] = pd.to_numeric(df[c], errors="coerce")
        after_na = df[c].isna().mean()
        if logger:
            logger.info("Coerced numeric %s: na_rate %.1f%% -> %.1f%%", c, 100*before_na, 100*after_na)
    return df

def deduplicate(df: pd.DataFrame, subset: List[str], logger: logging.Logger | None = None) -> pd.DataFrame:
    before = len(df)
    df2 = df.drop_duplicates(subset=subset, keep="first").copy()
    dropped = before - len(df2)
    if logger:
        logger.info("Deduplicated on %s: dropped=%s", subset, dropped)
    return df2

def write_dataframe(df: pd.DataFrame, path: str, logger: logging.Logger | None = None) -> None:
    df.to_csv(path, index=False)
    if logger:
        logger.info("Wrote %s rows to %s", len(df), path)
