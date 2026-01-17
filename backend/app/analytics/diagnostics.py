"""Deterministic diagnostics: fixed vs variable costs, outliers, trends."""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from app.storage.models import GLPnLMonthly, PayrollSummary, VendorSpend, RevenueBySegment
from app.analytics.pnl import calculate_margin_bridge


def run_diagnostics(db: Session, pnl_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Run comprehensive diagnostics on financial data."""
    diagnostics = {
        "fixed_vs_variable": estimate_fixed_variable_costs(pnl_data),
        "outliers": detect_outliers(db),
        "trends": calculate_trends(pnl_data),
        "margin_bridge": calculate_margin_bridge(pnl_data),
        "data_completeness": assess_data_completeness(db),
    }
    return diagnostics


def estimate_fixed_variable_costs(pnl_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Estimate fixed vs variable cost split using heuristics + simple correlation."""
    if len(pnl_data) < 3:
        # Insufficient data, use heuristics
        return {
            "sales_marketing": {"fixed_pct": 0.6, "variable_pct": 0.4, "confidence": 0.3},
            "rnd": {"fixed_pct": 0.8, "variable_pct": 0.2, "confidence": 0.3},
            "gna": {"fixed_pct": 0.9, "variable_pct": 0.1, "confidence": 0.3},
            "other": {"fixed_pct": 0.7, "variable_pct": 0.3, "confidence": 0.3},
        }

    df = pd.DataFrame(pnl_data)
    revenue = df["revenue"].values

    results = {}
    opex_categories = ["opex_sales_marketing", "opex_rnd", "opex_gna", "opex_other"]

    for category in opex_categories:
        costs = df[category].values

        # Use simple correlation check (numpy only)
        try:
            # Calculate correlation coefficient
            if len(revenue) > 1 and np.std(revenue) > 0 and np.std(costs) > 0:
                correlation = np.corrcoef(revenue, costs)[0, 1]
                # Use correlation as a proxy for variable cost strength
                # Higher correlation = more variable
                variable_strength = abs(correlation) if not np.isnan(correlation) else 0.3
                
                # Base heuristics by category
                if "sales" in category:
                    base_fixed = 0.6
                    base_variable = 0.4
                elif "rnd" in category:
                    base_fixed = 0.8
                    base_variable = 0.2
                elif "gna" in category:
                    base_fixed = 0.9
                    base_variable = 0.1
                else:
                    base_fixed = 0.7
                    base_variable = 0.3
                
                # Adjust based on correlation (but keep conservative)
                variable_pct = min(0.5, base_variable + (variable_strength - 0.3) * 0.2)
                fixed_pct = 1.0 - variable_pct
                
                # Confidence based on correlation strength and data quality
                confidence = min(0.7, max(0.3, abs(correlation) * 0.8)) if not np.isnan(correlation) else 0.3
            else:
                # Fallback to heuristics
                if "sales" in category:
                    fixed_pct, variable_pct = 0.6, 0.4
                elif "rnd" in category:
                    fixed_pct, variable_pct = 0.8, 0.2
                elif "gna" in category:
                    fixed_pct, variable_pct = 0.9, 0.1
                else:
                    fixed_pct, variable_pct = 0.7, 0.3
                confidence = 0.3

            results[category.replace("opex_", "")] = {
                "fixed_pct": round(fixed_pct, 2),
                "variable_pct": round(variable_pct, 2),
                "confidence": round(confidence, 2),
            }
        except Exception:
            # Fallback to heuristics
            if "sales" in category:
                results[category.replace("opex_", "")] = {"fixed_pct": 0.6, "variable_pct": 0.4, "confidence": 0.3}
            elif "rnd" in category:
                results[category.replace("opex_", "")] = {"fixed_pct": 0.8, "variable_pct": 0.2, "confidence": 0.3}
            elif "gna" in category:
                results[category.replace("opex_", "")] = {"fixed_pct": 0.9, "variable_pct": 0.1, "confidence": 0.3}
            else:
                results[category.replace("opex_", "")] = {"fixed_pct": 0.7, "variable_pct": 0.3, "confidence": 0.3}

    return results


def detect_outliers(db: Session) -> Dict[str, List[Dict[str, Any]]]:
    """Detect outliers in vendor spend, opex, and revenue."""
    outliers = {
        "vendor_spikes": [],
        "opex_spikes": [],
        "revenue_declines": [],
    }

    # Vendor spikes (Z-score > 2) - only if vendor data exists
    vendor_data = db.query(VendorSpend).all()
    if vendor_data:
        vendor_df = pd.DataFrame([{"vendor": v.vendor, "amount": v.amount, "month": v.month} for v in vendor_data])
        vendor_totals = vendor_df.groupby("month")["amount"].sum().reset_index()

        if len(vendor_totals) > 2:
            amounts = vendor_totals["amount"].values
            # Calculate Z-scores manually (numpy only)
            mean = np.mean(amounts)
            std = np.std(amounts)
            if std > 0:
                z_scores = np.abs((amounts - mean) / std)
                for idx, z_score in enumerate(z_scores):
                    if z_score > 2:
                        outliers["vendor_spikes"].append({
                            "month": vendor_totals.iloc[idx]["month"],
                            "amount": float(vendor_totals.iloc[idx]["amount"]),
                            "z_score": float(z_score),
                        })

    # Opex spikes
    gl_data = db.query(GLPnLMonthly).order_by(GLPnLMonthly.month).all()
    if len(gl_data) > 2:
        opex_totals = np.array([
            gl.opex_sales_marketing + gl.opex_rnd + gl.opex_gna + gl.opex_other for gl in gl_data
        ])
        # Calculate Z-scores manually
        mean = np.mean(opex_totals)
        std = np.std(opex_totals)
        if std > 0:
            z_scores = np.abs((opex_totals - mean) / std)
            for idx, z_score in enumerate(z_scores):
                if z_score > 2:
                    outliers["opex_spikes"].append({
                        "month": gl_data[idx].month,
                        "total_opex": float(opex_totals[idx]),
                        "z_score": float(z_score),
                    })

    # Revenue declines (month-over-month > 20%)
    if len(gl_data) > 1:
        for i in range(1, len(gl_data)):
            prev_rev = gl_data[i - 1].revenue
            curr_rev = gl_data[i].revenue
            if prev_rev > 0:
                decline_pct = (prev_rev - curr_rev) / prev_rev * 100
                if decline_pct > 20:
                    outliers["revenue_declines"].append({
                        "month": gl_data[i].month,
                        "prev_revenue": float(prev_rev),
                        "current_revenue": float(curr_rev),
                        "decline_pct": round(decline_pct, 2),
                    })

    return outliers


def calculate_trends(pnl_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate trends in key metrics using simple linear regression (numpy only)."""
    if len(pnl_data) < 3:
        return {}

    df = pd.DataFrame(pnl_data)
    df = df.sort_values("month")

    trends = {}
    metrics = ["revenue", "ebitda", "ebitda_margin_pct", "total_opex"]

    for metric in metrics:
        values = df[metric].values
        if len(values) > 1:
            # Simple linear regression using numpy
            x = np.arange(len(values))
            n = len(x)
            
            # Calculate slope and intercept manually
            sum_x = np.sum(x)
            sum_y = np.sum(values)
            sum_xy = np.sum(x * values)
            sum_x2 = np.sum(x * x)
            
            denominator = n * sum_x2 - sum_x * sum_x
            if denominator != 0:
                slope = (n * sum_xy - sum_x * sum_y) / denominator
                intercept = (sum_y - slope * sum_x) / n
                
                # Calculate R-squared
                y_pred = slope * x + intercept
                ss_res = np.sum((values - y_pred) ** 2)
                ss_tot = np.sum((values - np.mean(values)) ** 2)
                r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            else:
                slope = 0
                intercept = np.mean(values)
                r_squared = 0
            
            trends[metric] = {
                "slope": float(slope),
                "direction": "increasing" if slope > 0 else "decreasing",
                "r_squared": float(r_squared),
            }

    return trends


def assess_data_completeness(db: Session) -> Dict[str, Any]:
    """Assess data completeness and quality. Returns data gaps list."""
    gl_data = db.query(GLPnLMonthly).all()
    payroll_data = db.query(PayrollSummary).all()
    vendor_data = db.query(VendorSpend).all()
    revenue_data = db.query(RevenueBySegment).all()

    # Get expected month range from GL data (required)
    if gl_data:
        months = sorted([gl.month for gl in gl_data])
        expected_months = set(months)
    else:
        expected_months = set()

    # Check GL completeness (required)
    gl_months = set([gl.month for gl in gl_data])
    missing_gl_months = expected_months - gl_months

    # Check optional data completeness
    payroll_months = set([p.month for p in payroll_data]) if payroll_data else set()
    missing_payroll_months = expected_months - payroll_months if expected_months else set()
    
    # Check if payroll costs are provided
    payroll_with_costs = sum(1 for p in payroll_data if p.fully_loaded_cost is not None) if payroll_data else 0
    payroll_cost_coverage = payroll_with_costs / len(payroll_data) if payroll_data else 0

    # Build data gaps list
    data_gaps = []
    if missing_gl_months:
        data_gaps.append(f"Missing GL/P&L data for {len(missing_gl_months)} months")
    if not payroll_data:
        data_gaps.append("Payroll summary data not provided (optional)")
    elif missing_payroll_months:
        data_gaps.append(f"Missing payroll data for {len(missing_payroll_months)} months")
    if payroll_cost_coverage < 0.8 and payroll_data:
        data_gaps.append(f"Payroll cost data coverage: {payroll_cost_coverage*100:.0f}% (target: 100%)")
    if not vendor_data:
        data_gaps.append("Vendor spend data not provided (optional)")
    if not revenue_data:
        data_gaps.append("Revenue by segment data not provided (optional)")

    # Calculate overall completeness score
    required_score = 1.0 if gl_data and not missing_gl_months else 0.5
    optional_score = 0.0
    optional_count = 0
    if payroll_data:
        optional_score += 0.25 * (1.0 if not missing_payroll_months else 0.5)
        optional_count += 1
    if vendor_data:
        optional_score += 0.25
        optional_count += 1
    if revenue_data:
        optional_score += 0.25
        optional_count += 1
    
    completeness_score = required_score + optional_score

    return {
        "total_months": len(expected_months),
        "missing_gl_months": list(missing_gl_months),
        "missing_payroll_months": list(missing_payroll_months),
        "payroll_cost_coverage": round(payroll_cost_coverage, 2),
        "gl_records": len(gl_data),
        "payroll_records": len(payroll_data),
        "vendor_records": len(vendor_data),
        "revenue_segment_records": len(revenue_data) if revenue_data else 0,
        "data_gaps": data_gaps,
        "completeness_score": round(completeness_score, 2),
        "has_payroll": bool(payroll_data),
        "has_vendor": bool(vendor_data),
        "has_revenue_segments": bool(revenue_data),
    }


