# Data Cleaning & Validation Pack (Portfolio Demo)

## Business case (why this matters)
Teams lose time and credibility when reports are built on inconsistent spreadsheets: duplicated IDs, invalid dates, missing values, and mismatched totals. This demo shows a lightweight **data-quality pipeline** that:

- Reduces rework by **catching issues before reporting**
- Improves auditability with **repeatable checks + execution logs**
- Enables SLA-style governance with **metrics and traceability** per run

Typical impact in real projects:
- Fewer manual fixes in Excel/Sheets
- Fewer reporting errors (KPIs, revenue, funnel conversion)
- Faster onboarding for new analysts due to documented rules

## What this repo includes
- `data/` — 2 “dirty” CSVs (sales + leads) with realistic issues
- `src/` — cleaning + validation pipeline (pure Python/pandas)
- `outputs/` — generated `clean.csv`, `data-quality report` (Markdown + HTML), and `execution logs`

## Quickstart

### 1) Create a virtual environment
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Run the pipeline on the demo data
Sales:
```bash
python -m src.clean_validate --input data/sample_sales_raw.csv --dataset sales
```

Leads:
```bash
python -m src.clean_validate --input data/sample_leads_raw.csv --dataset leads
```

### 4) Inspect outputs
- Clean CSV: `outputs/clean/*_clean_*.csv`
- Data quality report:
  - `outputs/reports/*_dq_report_*.md`
  - `outputs/reports/*_dq_report_*.html`
- Execution log: `outputs/logs/run_*.log`

## Rules covered (examples)
Sales:
- qty must be >= 1
- unit_price must be within reasonable range
- order_id uniqueness
- revenue ≈ qty × unit_price

Leads:
- email format
- phone length
- created_at must parse
- score between 0 and 100
- lead_id uniqueness

## Portfolio notes (Upwork)
Suggested screenshots:
- Open the HTML report and capture:
  1) the **Validation results** table
  2) a **Failed samples** section with examples

Suggested hosting:
- Repo: GitHub
- Optional: publish the HTML report via **GitHub Pages** (static hosting)

## License
MIT (for portfolio use)
