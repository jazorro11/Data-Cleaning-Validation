from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Any, Dict, List
import re
import pandas as pd

@dataclass
class Rule:
    rule_id: str
    description: str
    severity: str  # "error" | "warn"
    check: Callable[[pd.DataFrame], pd.Series]  # returns boolean mask where True = FAIL

    def run(self, df: pd.DataFrame) -> Dict[str, Any]:
        fail_mask = self.check(df)
        failed_count = int(fail_mask.sum()) if hasattr(fail_mask, "sum") else 0
        status = "PASS" if failed_count == 0 else "FAIL"
        sample = df.loc[fail_mask].head(5).to_dict(orient="records") if failed_count else []
        return {
            "rule_id": self.rule_id,
            "description": self.description,
            "severity": self.severity,
            "status": status,
            "failed_count": failed_count,
            "failed_sample": sample,
        }

def get_rules_for_dataset(dataset: str) -> List[Rule]:
    if dataset == "sales":
        return [
            Rule(
                rule_id="S001_qty_positive",
                description="qty must be >= 1",
                severity="error",
                check=lambda d: (d["qty"].isna()) | (d["qty"] < 1),
            ),
            Rule(
                rule_id="S002_unit_price_reasonable",
                description="unit_price must be between 1,000 and 200,000",
                severity="error",
                check=lambda d: (d["unit_price"].isna()) | (d["unit_price"] < 1000) | (d["unit_price"] > 200000),
            ),
            Rule(
                rule_id="S003_order_date_present",
                description="order_date must be a valid parsed date",
                severity="error",
                check=lambda d: d["order_date"].isna(),
            ),
            Rule(
                rule_id="S004_revenue_consistency",
                description="revenue should equal qty * unit_price (tolerance 1 peso)",
                severity="warn",
                check=lambda d: (d["revenue"].isna()) | ((d["qty"] * d["unit_price"] - d["revenue"]).abs() > 1),
            ),
            Rule(
                rule_id="S005_region_not_null",
                description="region must not be null",
                severity="warn",
                check=lambda d: d["region"].isna() | (d["region"].astype(str).str.strip() == ""),
            ),
            Rule(
                rule_id="S006_order_id_unique",
                description="order_id must be unique after cleaning",
                severity="error",
                check=lambda d: d["order_id"].duplicated(keep=False),
            ),
        ]

    if dataset == "leads":
        email_re = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
        return [
            Rule(
                rule_id="L001_email_format",
                description="email must be valid format",
                severity="error",
                check=lambda d: ~d["email"].astype(str).str.match(email_re),
            ),
            Rule(
                rule_id="L002_phone_length",
                description="phone must have 10 digits (Colombia mobile standard)",
                severity="warn",
                check=lambda d: d["phone"].astype(str).str.len() != 10,
            ),
            Rule(
                rule_id="L003_created_at_valid",
                description="created_at must be a valid parsed date",
                severity="error",
                check=lambda d: d["created_at"].isna(),
            ),
            Rule(
                rule_id="L004_score_range",
                description="score must be between 0 and 100",
                severity="warn",
                check=lambda d: d["score"].isna() | (d["score"] < 0) | (d["score"] > 100),
            ),
            Rule(
                rule_id="L005_lead_id_unique",
                description="lead_id must be unique after cleaning",
                severity="error",
                check=lambda d: d["lead_id"].duplicated(keep=False),
            ),
        ]

    raise ValueError(f"Unknown dataset: {dataset}")
