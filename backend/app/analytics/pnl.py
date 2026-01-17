"""P&L reconstruction and canonical P&L generation."""

import pandas as pd
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.storage.models import GLPnLMonthly, PayrollSummary, VendorSpend, RevenueBySegment


def reconstruct_pnl(db: Session) -> List[Dict[str, Any]]:
    """Reconstruct canonical P&L from normalized tables."""
    # Get all data
    gl_data = db.query(GLPnLMonthly).order_by(GLPnLMonthly.month).all()
    payroll_data = db.query(PayrollSummary).all()
    vendor_data = db.query(VendorSpend).all()
    revenue_data = db.query(RevenueBySegment).all()

    # Build dataframe from GL data
    records = []
    for gl in gl_data:
        records.append({
            "month": gl.month,
            "revenue": gl.revenue,
            "cogs": gl.cogs,
            "opex_sales_marketing": gl.opex_sales_marketing,
            "opex_rnd": gl.opex_rnd,
            "opex_gna": gl.opex_gna,
            "opex_other": gl.opex_other,
        })

    if not records:
        return []

    df = pd.DataFrame(records)
    df = df.sort_values("month")

    # Calculate derived metrics
    df["gross_margin"] = df["revenue"] - df["cogs"]
    # Avoid division by zero
    df["gross_margin_pct"] = df.apply(
        lambda row: round(row["gross_margin"] / row["revenue"] * 100, 2) if row["revenue"] != 0 else 0.0,
        axis=1
    )
    df["total_opex"] = (
        df["opex_sales_marketing"] + df["opex_rnd"] + df["opex_gna"] + df["opex_other"]
    )
    df["ebitda"] = df["gross_margin"] - df["total_opex"]
    df["ebitda_margin_pct"] = df.apply(
        lambda row: round(row["ebitda"] / row["revenue"] * 100, 2) if row["revenue"] != 0 else 0.0,
        axis=1
    )

    # Convert to list of dicts
    result = df.to_dict("records")
    return result


def calculate_margin_bridge(pnl_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Calculate month-over-month margin bridge."""
    if len(pnl_data) < 2:
        return []

    bridge = []
    for i in range(1, len(pnl_data)):
        prev = pnl_data[i - 1]
        curr = pnl_data[i]

        ebitda_change = curr["ebitda"] - prev["ebitda"]
        revenue_impact = (curr["revenue"] - prev["revenue"]) * (prev["gross_margin_pct"] / 100)
        cogs_impact = -(curr["cogs"] - prev["cogs"])
        opex_impact = -(curr["total_opex"] - prev["total_opex"])

        bridge.append({
            "month": curr["month"],
            "prev_month": prev["month"],
            "ebitda_change": ebitda_change,
            "revenue_impact": revenue_impact,
            "cogs_impact": cogs_impact,
            "opex_impact": opex_impact,
            "other_impact": ebitda_change - revenue_impact - cogs_impact - opex_impact,
        })

    return bridge


