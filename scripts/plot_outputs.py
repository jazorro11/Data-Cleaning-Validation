#!/usr/bin/env python3
"""
Generate simple, portfolio-ready plots from outputs/clean/*.csv using seaborn.

Charts generated (if data is available):
1) Leads: monthly lead volume segmented by status (stacked bar)
2) Sales: monthly revenue trend (line)

Outputs:
- outputs/plots/leads_monthly_by_status.png
- outputs/plots/sales_monthly_revenue.png

Run:
  python scripts/plot_outputs.py
"""

from __future__ import annotations

import os
import glob
import sys
from pathlib import Path

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
CLEAN_DIR = ROOT / "outputs" / "clean"
PLOTS_DIR = ROOT / "outputs" / "plots"


def latest_file(pattern: str) -> str | None:
    files = glob.glob(str(CLEAN_DIR / pattern))
    if not files:
        return None
    # Most recent by modified time
    files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return files[0]


def plot_leads_monthly_by_status(leads_csv: str) -> str | None:
    df = pd.read_csv(leads_csv)

    # Ensure created_at parses (may already be datetime-like, but we enforce)
    df["created_at"] = pd.to_datetime(df.get("created_at"), errors="coerce")
    if "status" not in df.columns:
        print("[WARN] Leads file has no 'status' column. Skipping leads plot.")
        return None

    # Only keep rows with valid date
    df = df.dropna(subset=["created_at"]).copy()
    if df.empty:
        print("[WARN] No valid 'created_at' dates found in leads clean data. Skipping leads plot.")
        return None

    # Monthly bucket
    df["month"] = df["created_at"].dt.to_period("M").dt.to_timestamp()

    # Aggregate
    agg = (
        df.groupby(["month", "status"], as_index=False)
          .size()
          .rename(columns={"size": "leads"})
    )

    # Plot
    sns.set_theme(style="whitegrid", context="talk")
    fig, ax = plt.subplots(figsize=(12, 6))

    # stacked bars: pivot to wide then plot
    pivot = agg.pivot(index="month", columns="status", values="leads").fillna(0).sort_index()

    bottom = None
    for col in pivot.columns:
        if bottom is None:
            ax.bar(pivot.index, pivot[col].values, label=str(col))
            bottom = pivot[col].values
        else:
            ax.bar(pivot.index, pivot[col].values, bottom=bottom, label=str(col))
            bottom = bottom + pivot[col].values

    ax.set_title("Leads por mes (segmentado por status)")
    ax.set_xlabel("Mes")
    ax.set_ylabel("Cantidad de leads")
    ax.legend(title="status", frameon=True)

    # Improve x labels
    ax.set_xticks(pivot.index)
    ax.set_xticklabels([d.strftime("%Y-%m") for d in pivot.index], rotation=45, ha="right")

    # Footer note (useful for portfolio transparency)
    ax.text(
        0.01, -0.18,
        "Nota: Solo incluye filas con created_at válido (NaT excluido).",
        transform=ax.transAxes,
        fontsize=10
    )

    fig.tight_layout()

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PLOTS_DIR / "leads_monthly_by_status.png"
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    return str(out_path)


def plot_sales_monthly_revenue(sales_csv: str) -> str | None:
    df = pd.read_csv(sales_csv)

    if "order_date" not in df.columns or "revenue" not in df.columns:
        print("[WARN] Sales file missing 'order_date' or 'revenue'. Skipping sales plot.")
        return None

    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")

    df = df.dropna(subset=["order_date", "revenue"]).copy()
    if df.empty:
        print("[WARN] No valid 'order_date'/'revenue' rows found. Skipping sales plot.")
        return None

    df["month"] = df["order_date"].dt.to_period("M").dt.to_timestamp()

    agg = (
        df.groupby("month", as_index=False)["revenue"]
          .sum()
          .sort_values("month")
    )

    sns.set_theme(style="whitegrid", context="talk")
    fig, ax = plt.subplots(figsize=(12, 6))

    sns.lineplot(data=agg, x="month", y="revenue", marker="o", ax=ax)

    ax.set_title("Revenue mensual (Sales)")
    ax.set_xlabel("Mes")
    ax.set_ylabel("Revenue total")

    ax.set_xticks(agg["month"])
    ax.set_xticklabels([d.strftime("%Y-%m") for d in agg["month"]], rotation=45, ha="right")

    fig.tight_layout()

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PLOTS_DIR / "sales_monthly_revenue.png"
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    return str(out_path)


def main() -> int:
    if not CLEAN_DIR.exists():
        print(f"[ERROR] Clean outputs folder not found: {CLEAN_DIR}")
        print("Run the pipeline first to generate outputs/clean/*.csv")
        return 2

    leads_csv = latest_file("leads_clean_*.csv")
    sales_csv = latest_file("sales_clean_*.csv")

    if not leads_csv and not sales_csv:
        print("[ERROR] No clean CSVs found in outputs/clean/")
        print("Expected patterns: leads_clean_*.csv and/or sales_clean_*.csv")
        return 2

    print(f"[INFO] Using clean outputs from: {CLEAN_DIR}")

    if leads_csv:
        print(f"[INFO] Leads file: {leads_csv}")
        out = plot_leads_monthly_by_status(leads_csv)
        if out:
            print(f"[OK] Leads plot saved to: {out}")

    if sales_csv:
        print(f"[INFO] Sales file: {sales_csv}")
        out = plot_sales_monthly_revenue(sales_csv)
        if out:
            print(f"[OK] Sales plot saved to: {out}")

    print(f"[DONE] Plots (if generated) are in: {PLOTS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
