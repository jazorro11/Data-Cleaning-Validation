#!/usr/bin/env python3
"""
Data Cleaning & Validation Pack (Portfolio demo)
- Reads 1..N CSV files
- Cleans: types, nulls, string normalization, date parsing, dedup
- Validates: business rules, cross-field consistency, ranges, uniqueness
- Outputs: clean.csv, report.md + report.html, execution log

Run:
  python -m src.clean_validate --input data/sample_sales_raw.csv --dataset sales
  python -m src.clean_validate --input data/sample_leads_raw.csv --dataset leads
"""

from __future__ import annotations
import argparse
import os
import sys
import time
import logging
from datetime import datetime
import pandas as pd

from .rules import get_rules_for_dataset
from .utils import (
    ensure_dirs, read_csv_safely, normalize_strings, parse_dates_flex,
    coerce_numeric, deduplicate, write_dataframe, build_run_id
)
from .report import build_quality_report


def configure_logger(log_path: str) -> logging.Logger:
    logger = logging.getLogger("dq_pack")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setFormatter(fmt)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(sh)
    return logger


def clean_dataset(df: pd.DataFrame, dataset: str, logger: logging.Logger) -> pd.DataFrame:
    logger.info("Cleaning dataset=%s, rows=%s, cols=%s", dataset, len(df), df.shape[1])

    # Dataset-specific cleaning hooks
    if dataset == "sales":
        df = normalize_strings(df, cols=["region", "channel", "product", "notes"])
        df = parse_dates_flex(df, col="order_date", logger=logger)
        df = coerce_numeric(df, cols=["order_id", "customer_id", "qty", "unit_price", "revenue"], logger=logger)
        # revenue sometimes uses dots as thousands separator; attempt to fix if object
        if df["revenue"].dtype == "object":
            df["revenue"] = (
                df["revenue"].astype(str)
                  .str.replace(".", "", regex=False)   # remove thousands sep
                  .str.replace(",", ".", regex=False)  # decimal comma
            )
            df = coerce_numeric(df, cols=["revenue"], logger=logger)

    elif dataset == "leads":
        df = normalize_strings(df, cols=["source", "status", "city", "notes", "email"])
        df = parse_dates_flex(df, col="created_at", logger=logger)
        df = coerce_numeric(df, cols=["lead_id", "score"], logger=logger)
        # phone as string but normalized (keep digits only)
        df["phone"] = df["phone"].astype(str).str.replace(r"\D+", "", regex=True)

    else:
        # generic fallbacks
        df = normalize_strings(df, cols=df.select_dtypes(include=["object"]).columns.tolist())
        for c in df.columns:
            if c.lower().endswith(("date", "_at", "timestamp")):
                df = parse_dates_flex(df, col=c, logger=logger)

    # Dedup on primary key if present
    pk = "order_id" if dataset == "sales" else "lead_id" if dataset == "leads" else None
    if pk and pk in df.columns:
        df = deduplicate(df, subset=[pk], logger=logger)

    return df


def run_validations(df: pd.DataFrame, dataset: str, logger: logging.Logger) -> dict:
    rules = get_rules_for_dataset(dataset)
    logger.info("Running %s validation rules for dataset=%s", len(rules), dataset)

    results = {}
    for rule in rules:
        r = rule.run(df)
        results[rule.rule_id] = r
        logger.info("Rule %s: status=%s, failed=%s", rule.rule_id, r["status"], r["failed_count"])
    return results


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="Path to raw CSV")
    p.add_argument("--dataset", required=True, choices=["sales", "leads"], help="Dataset type")
    p.add_argument("--outdir", default="outputs", help="Base outputs folder")
    args = p.parse_args()

    run_id = build_run_id(args.dataset)
    out_clean_dir = os.path.join(args.outdir, "clean")
    out_reports_dir = os.path.join(args.outdir, "reports")
    out_logs_dir = os.path.join(args.outdir, "logs")
    ensure_dirs([out_clean_dir, out_reports_dir, out_logs_dir])

    log_path = os.path.join(out_logs_dir, f"run_{run_id}.log")
    logger = configure_logger(log_path)
    logger.info("Starting run_id=%s input=%s dataset=%s", run_id, args.input, args.dataset)

    t0 = time.time()
    df_raw = read_csv_safely(args.input, logger=logger)
    df_clean = clean_dataset(df_raw, args.dataset, logger=logger)

    validation_results = run_validations(df_clean, args.dataset, logger=logger)

    clean_path = os.path.join(out_clean_dir, f"{args.dataset}_clean_{run_id}.csv")
    write_dataframe(df_clean, clean_path, logger=logger)

    report_md_path = os.path.join(out_reports_dir, f"{args.dataset}_dq_report_{run_id}.md")
    report_html_path = os.path.join(out_reports_dir, f"{args.dataset}_dq_report_{run_id}.html")
    build_quality_report(
        dataset=args.dataset,
        run_id=run_id,
        input_path=args.input,
        clean_path=clean_path,
        df_raw=df_raw,
        df_clean=df_clean,
        validation_results=validation_results,
        out_md_path=report_md_path,
        out_html_path=report_html_path,
        logger=logger,
    )

    elapsed = time.time() - t0
    logger.info("Finished run_id=%s in %.2fs", run_id, elapsed)
    logger.info("Outputs: clean=%s report_md=%s report_html=%s log=%s", clean_path, report_md_path, report_html_path, log_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
