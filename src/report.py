from __future__ import annotations
import logging
from datetime import datetime
from typing import Dict, Any
import pandas as pd

def summarize_df(df: pd.DataFrame) -> pd.DataFrame:
    # Per-column stats that are helpful for data quality
    rows = []
    n = len(df)
    for c in df.columns:
        s = df[c]
        rows.append({
            "column": c,
            "dtype": str(s.dtype),
            "null_rate": float(s.isna().mean()),
            "distinct": int(s.nunique(dropna=True)),
            "sample_values": ", ".join([str(x) for x in s.dropna().astype(str).head(3).tolist()])
        })
    return pd.DataFrame(rows).sort_values(["null_rate","distinct"], ascending=[False, True])

def build_quality_report(
    dataset: str,
    run_id: str,
    input_path: str,
    clean_path: str,
    df_raw: pd.DataFrame,
    df_clean: pd.DataFrame,
    validation_results: Dict[str, Any],
    out_md_path: str,
    out_html_path: str,
    logger: logging.Logger | None = None,
) -> None:
    raw_summary = summarize_df(df_raw)
    clean_summary = summarize_df(df_clean)

    # high-level metrics
    metrics = {
        "dataset": dataset,
        "run_id": run_id,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "raw_rows": len(df_raw),
        "clean_rows": len(df_clean),
        "raw_cols": df_raw.shape[1],
        "clean_cols": df_clean.shape[1],
    }
    failed = [r for r in validation_results.values() if r["status"] == "FAIL"]
    metrics["failed_rules"] = len(failed)
    metrics["total_rules"] = len(validation_results)

    # Markdown report
    md = []
    md.append(f"# Data Quality Report — {dataset}")
    md.append("")
    md.append("## Run metadata")
    md.append("")
    for k,v in metrics.items():
        md.append(f"- **{k}**: {v}")
    md.append("")
    md.append("## Validation results")
    md.append("")
    md.append("| Rule | Severity | Status | Failed | Description |")
    md.append("|---|---|---:|---:|---|")
    for r in validation_results.values():
        md.append(f"| {r['rule_id']} | {r['severity']} | {r['status']} | {r['failed_count']} | {r['description']} |")
    md.append("")
    md.append("### Failed samples (up to 5 rows per rule)")
    md.append("")
    for r in failed:
        md.append(f"#### {r['rule_id']} — {r['description']} ({r['severity']})")
        if r["failed_sample"]:
            md.append("")
            md.append(pd.DataFrame(r["failed_sample"]).to_markdown(index=False))
            md.append("")
        else:
            md.append("")
            md.append("_No sample available._")
            md.append("")
    md.append("## Column profile (raw)")
    md.append("")
    md.append(raw_summary.to_markdown(index=False))
    md.append("")
    md.append("## Column profile (clean)")
    md.append("")
    md.append(clean_summary.to_markdown(index=False))
    md.append("")
    md.append("## Artifacts")
    md.append("")
    md.append(f"- Raw input: `{input_path}`")
    md.append(f"- Clean output: `{clean_path}`")
    md.append(f"- Log: see `outputs/logs/run_{run_id}.log`")
    md_text = "\n".join(md)

    with open(out_md_path, "w", encoding="utf-8") as f:
        f.write(md_text)

    # Simple HTML wrapper around Markdown-like content (preformatted tables)
    # For portability (no external assets)
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Data Quality Report — {dataset}</title>
<style>
body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif; margin: 24px; line-height: 1.45; }}
h1,h2,h3,h4 {{ margin-top: 1.2em; }}
code, pre {{ background: #f6f8fa; padding: 2px 4px; border-radius: 4px; }}
table {{ border-collapse: collapse; width: 100%; margin: 12px 0; }}
th, td {{ border: 1px solid #e5e7eb; padding: 8px; font-size: 13px; vertical-align: top; }}
th {{ background: #f3f4f6; text-align: left; }}
.badge-pass {{ color: #065f46; font-weight: 600; }}
.badge-fail {{ color: #991b1b; font-weight: 600; }}
.small {{ color: #6b7280; font-size: 12px; }}
</style>
</head>
<body>
<h1>Data Quality Report — {dataset}</h1>
<p class="small">Run ID: <code>{run_id}</code> • Generated: {metrics['generated_at']}</p>

<h2>Run metadata</h2>
<ul>
{''.join([f"<li><b>{k}</b>: {v}</li>" for k,v in metrics.items()])}
</ul>

<h2>Validation results</h2>
<table>
<thead><tr><th>Rule</th><th>Severity</th><th>Status</th><th>Failed</th><th>Description</th></tr></thead>
<tbody>
{''.join([f"<tr><td><code>{r['rule_id']}</code></td><td>{r['severity']}</td><td class={'badge-pass' if r['status']=='PASS' else 'badge-fail'}>{r['status']}</td><td>{r['failed_count']}</td><td>{r['description']}</td></tr>" for r in validation_results.values()])}
</tbody>
</table>

<h3>Failed samples (up to 5 rows per rule)</h3>
{''.join([f"<h4><code>{r['rule_id']}</code> — {r['description']} ({r['severity']})</h4>" + (pd.DataFrame(r['failed_sample']).to_html(index=False, escape=True) if r['failed_sample'] else "<p><i>No sample available.</i></p>") for r in failed])}

<h2>Column profile (raw)</h2>
{raw_summary.to_html(index=False, escape=True)}

<h2>Column profile (clean)</h2>
{clean_summary.to_html(index=False, escape=True)}

<h2>Artifacts</h2>
<ul>
<li>Raw input: <code>{input_path}</code></li>
<li>Clean output: <code>{clean_path}</code></li>
<li>Log: <code>outputs/logs/run_{run_id}.log</code></li>
</ul>
</body>
</html>
"""
    with open(out_html_path, "w", encoding="utf-8") as f:
        f.write(html)

    if logger:
        logger.info("Wrote report: %s and %s", out_md_path, out_html_path)
