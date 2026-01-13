#!/usr/bin/env python3
"""
Generate publication-quality plots from outputs/clean/*.csv using seaborn.

Charts generated:
1) Leads: Monthly lead volume segmented by status (Grouped Bar Chart)
2) Sales: Monthly revenue trend segmented by channel (Line Chart)

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
import matplotlib.ticker as ticker
import matplotlib.dates as mdates

# --- Configuration & Constants ---
ROOT = Path(__file__).resolve().parents[1]
CLEAN_DIR = ROOT / "outputs" / "clean"
PLOTS_DIR = ROOT / "outputs" / "plots"

# Set a professional "Paper" style theme globally
sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)


def setup_plot_style():
    """Helper to ensure consistent figure styling."""
    plt.rcParams["figure.dpi"] = 300
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.labelsize"] = 12
    plt.rcParams["xtick.labelsize"] = 10
    plt.rcParams["ytick.labelsize"] = 10
    plt.rcParams["legend.fontsize"] = 10
    plt.rcParams["font.family"] = "sans-serif"


def latest_file(pattern: str) -> str | None:
    files = glob.glob(str(CLEAN_DIR / pattern))
    if not files:
        return None
    # Most recent by modified time
    files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return files[0]


def plot_leads_monthly_by_status(leads_csv: str) -> str | None:
    df = pd.read_csv(leads_csv)

    # Validate Columns
    if "created_at" not in df.columns or "status" not in df.columns:
        print("[WARN] Leads file missing 'created_at' or 'status'. Skipping.")
        return None

    # Data Processing
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
    df = df.dropna(subset=["created_at"]).copy()
    
    if df.empty:
        print("[WARN] No valid dates in leads. Skipping.")
        return None

    # Create a month identifier for sorting/grouping
    df["month_dt"] = df["created_at"].dt.to_period("M").dt.to_timestamp()
    
    # Aggregation
    agg = (
        df.groupby(["month_dt", "status"], as_index=False)
        .size()
        .rename(columns={"size": "leads"})
    )
    
    # Format month for display (Category styling for Bar Plot)
    agg["month_str"] = agg["month_dt"].dt.strftime("%Y-%m")
    agg = agg.sort_values("month_dt")

    # Plotting
    setup_plot_style()
    fig, ax = plt.subplots(figsize=(12, 7))

    # Grouped Bar Chart
    sns.barplot(
        data=agg,
        x="month_str",
        y="leads",
        hue="status",
        palette="viridis",
        edgecolor="white",
        linewidth=1,
        ax=ax
    )

    # Aesthetics
    ax.set_title("Monthly Leads Volume by Status", fontweight="bold", pad=20)
    ax.set_xlabel("Month")
    ax.set_ylabel("Number of Leads")
    
    # Legend placement (Outside to prevent overlap)
    ax.legend(title="Status", bbox_to_anchor=(1.02, 1), loc="upper left", borderaxespad=0)

    # Clean spines
    sns.despine(left=True)
    
    # Rotate X labels slightly for readability
    plt.xticks(rotation=45, ha="right")

    # Annotation (Translated & Moved below chart)
    note_text = "Note: Only includes records with valid 'created_at' timestamps."
    plt.figtext(
        0.05, 0.02,  # Coordinates (x, y) relative to figure
        note_text,
        fontsize=9,
        color="gray",
        style="italic"
    )

    # Adjust layout to accommodate external legend and bottom note
    plt.tight_layout(rect=[0, 0.05, 1, 1]) 

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PLOTS_DIR / "leads_monthly_by_status.png"
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)

    return str(out_path)


def plot_sales_monthly_revenue(sales_csv: str) -> str | None:
    df = pd.read_csv(sales_csv)

    # 1. Validation & Pre-processing
    required_cols = ["order_date", "revenue"]
    if not all(col in df.columns for col in required_cols):
        print(f"[WARN] Sales file missing required columns {required_cols}. Skipping.")
        return None

    if "channel" not in df.columns:
        df["channel"] = "Unknown"

    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")
    df = df.dropna(subset=["order_date", "revenue"]).copy()

    if df.empty:
        print("[WARN] No valid sales data found. Skipping.")
        return None

    df["month"] = df["order_date"].dt.to_period("M").dt.to_timestamp()

    # 2. Logic to force consecutive months (Gap Filling)
    grouped = df.groupby(["month", "channel"])["revenue"].sum().reset_index()

    all_months = pd.date_range(start=grouped["month"].min(), end=grouped["month"].max(), freq="MS")
    unique_channels = grouped["channel"].unique()
    # Sort channels alphabetically for consistent plotting order
    unique_channels.sort()
    
    full_idx = pd.MultiIndex.from_product([all_months, unique_channels], names=["month", "channel"])
    grouped = (
        grouped.set_index(["month", "channel"])
        .reindex(full_idx, fill_value=0)
        .reset_index()
    )

    # 3. Setup Plotting Environment (Small Multiples)
    setup_plot_style()
    
    # Determine layout based on number of channels (Targeting 3 as requested)
    n_channels = len(unique_channels)
    # We use sharex and sharey to force identical limits
    fig, axes = plt.subplots(nrows=1, ncols=n_channels, figsize=(18, 6), 
                             sharey=True, sharex=True)

    # Ensure axes is always a list (even if there is only 1 channel)
    if n_channels == 1:
        axes = [axes]

    # Currency Formatter Definition
    def currency_fmt(x, pos):
        # M = Millions, K = Thousands. Adjust logic as needed.
        if x >= 1_000_000:
            return f"${x*1e-6:.1f}M"
        return f"${x:,.0f}"

    # 4. Iterative Plotting per Channel
    for ax, channel in zip(axes, unique_channels):
        subset = grouped[grouped["channel"] == channel]
        
        # Plot Line
        sns.lineplot(
            data=subset,
            x="month",
            y="revenue",
            marker="o",
            linewidth=2.5,
            color="#2c3e50", # Professional dark blue/grey
            ax=ax
        )
        
        # Fill area under line for better visual weight (optional, looks very scientific)
        ax.fill_between(subset["month"], subset["revenue"], alpha=0.1, color="#2c3e50")

        # Specific subplot styling
        ax.set_title(channel, fontweight="bold", fontsize=14)
        ax.set_xlabel("") # Remove individual x-labels for cleanliness
        ax.set_ylabel("") # Remove individual y-labels
        
        # Grid settings
        ax.grid(True, which='major', linestyle='--', linewidth=0.5, alpha=0.7)
        
        # Format X-Axis (Dates)
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.tick_params(axis='x', rotation=45)

    # 5. Global Formatting (The "Frame")
    
    # Add a global Y-axis formatter to the first plot (since they are shared)
    axes[0].yaxis.set_major_formatter(ticker.FuncFormatter(currency_fmt))
    axes[0].set_ylabel("Revenue (COP)", fontsize=13, fontweight='bold')
    
    # Global Title
    fig.suptitle("Monthly Revenue Trend by Channel", fontsize=16, fontweight='bold', y=1.05)
    
    # Global X Label
    fig.text(0.5, -0.05, 'Month', ha='center', fontsize=13)

    # Clean styling
    sns.despine()
    
    # Tight layout with extra rect to accommodate global labels
    plt.tight_layout()

    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PLOTS_DIR / "sales_monthly_revenue.png"
    fig.savefig(out_path, bbox_inches="tight")
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
        return 2

    print(f"[INFO] Processing files from: {CLEAN_DIR}")

    if leads_csv:
        print(f"[INFO] Generating Leads plot from: {leads_csv}")
        out = plot_leads_monthly_by_status(leads_csv)
        if out:
            print(f"[OK] Saved: {out}")

    if sales_csv:
        print(f"[INFO] Generating Sales plot from: {sales_csv}")
        out = plot_sales_monthly_revenue(sales_csv)
        if out:
            print(f"[OK] Saved: {out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())