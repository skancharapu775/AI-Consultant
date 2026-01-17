"""Deterministic sizing logic for initiatives."""

from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from app.storage.models import VendorSpend, PayrollSummary, GLPnLMonthly


def size_initiative(initiative: Dict[str, Any], db: Session, diagnostics: Dict[str, Any]) -> Dict[str, Any]:
    """Size an initiative deterministically based on available data."""
    title_lower = initiative["title"].lower()
    category = initiative.get("category", "")

    # Default values
    impact_low = 0.0
    impact_high = 0.0
    time_to_value_weeks = 12
    implementation_cost = 0.0
    risk_level = "Med"
    confidence = 0.5
    assumptions = []
    next_steps = []
    needs_data = False

    # Vendor consolidation / optimization
    if "vendor" in title_lower or "saas" in title_lower or "software" in title_lower:
        vendor_data = db.query(VendorSpend).all()
        if vendor_data:
            vendor_totals = {}
            for v in vendor_data:
                vendor_totals[v.vendor] = vendor_totals.get(v.vendor, 0) + v.amount

            total_vendor_spend = sum(vendor_totals.values())
            vendor_count = len(vendor_totals)

            # Estimate 5-15% savings from consolidation
            savings_pct_low = 0.05
            savings_pct_high = 0.15
            impact_low = total_vendor_spend * savings_pct_low
            impact_high = total_vendor_spend * savings_pct_high
            time_to_value_weeks = 8
            implementation_cost = total_vendor_spend * 0.02  # 2% of annual spend
            risk_level = "Low"
            confidence = 0.7 if vendor_count > 10 else 0.5
            assumptions = [f"Assumes {vendor_count} vendors can be consolidated"]
            next_steps = ["Inventory all vendor contracts", "Identify consolidation candidates"]
        else:
            # Missing vendor data - use heuristics based on opex_other
            gl_data = db.query(GLPnLMonthly).all()
            if gl_data:
                avg_opex_other = sum(gl.opex_other for gl in gl_data) / len(gl_data)
                # Assume 20-40% of opex_other is vendor spend, 5-15% savings
                estimated_vendor_spend = avg_opex_other * 0.3 * 12  # Annualized
                impact_low = estimated_vendor_spend * 0.05
                impact_high = estimated_vendor_spend * 0.15
                time_to_value_weeks = 8
                implementation_cost = estimated_vendor_spend * 0.02
                risk_level = "Med"
                confidence = 0.3  # Low confidence due to missing data
                assumptions = ["Vendor data not available - estimate based on opex_other"]
                next_steps = ["Collect vendor spend data", "Inventory all vendor contracts"]
            else:
                # No data at all - very low confidence
                confidence = 0.2
                needs_data = True

    # Cloud cost optimization
    elif "cloud" in title_lower or "infrastructure" in title_lower or "aws" in title_lower or "azure" in title_lower:
        # Estimate based on opex
        gl_data = db.query(GLPnLMonthly).all()
        if gl_data:
            avg_opex = sum(gl.opex_other for gl in gl_data) / len(gl_data)
            # Assume 10-25% of infrastructure costs are optimizable
            impact_low = avg_opex * 0.10 * 12  # Annualized
            impact_high = avg_opex * 0.25 * 12
            time_to_value_weeks = 16
            implementation_cost = avg_opex * 0.05 * 12
            risk_level = "Med"
            confidence = 0.6
            assumptions = ["Infrastructure costs are ~30% of opex_other"]
            next_steps = ["Right-size instances", "Reserved instance analysis"]

    # Headcount optimization / reallocation
    elif "headcount" in title_lower or "staffing" in title_lower or "workforce" in title_lower:
        payroll_data = db.query(PayrollSummary).all()
        if payroll_data:
            latest_month = max(p.month for p in payroll_data)
            total_headcount = sum(p.headcount for p in payroll_data if p.month == latest_month)
            total_cost = sum(p.fully_loaded_cost for p in payroll_data if p.fully_loaded_cost and p.fully_loaded_cost is not None)
            avg_cost_per_head = total_cost / total_headcount if total_headcount > 0 else 150000

            # Estimate 5-10% headcount optimization
            optimization_pct_low = 0.05
            optimization_pct_high = 0.10
            impact_low = total_headcount * avg_cost_per_head * optimization_pct_low
            impact_high = total_headcount * avg_cost_per_head * optimization_pct_high
            time_to_value_weeks = 24  # Longer for headcount changes
            implementation_cost = avg_cost_per_head * 0.5  # Severance/transition costs
            risk_level = "High"
            confidence = 0.5 if total_cost > 0 else 0.3
            assumptions = [f"Assumes {total_headcount} total headcount"]
            next_steps = ["Workforce analysis", "Identify optimization opportunities"]
        else:
            # Missing payroll data - use heuristics based on opex
            gl_data = db.query(GLPnLMonthly).all()
            if gl_data:
                avg_total_opex = sum(
                    gl.opex_sales_marketing + gl.opex_rnd + gl.opex_gna + gl.opex_other
                    for gl in gl_data
                ) / len(gl_data)
                # Assume 60% of opex is payroll, 5-10% optimization
                estimated_payroll = avg_total_opex * 0.6 * 12  # Annualized
                impact_low = estimated_payroll * 0.05
                impact_high = estimated_payroll * 0.10
                time_to_value_weeks = 24
                implementation_cost = estimated_payroll * 0.02
                risk_level = "High"
                confidence = 0.3  # Low confidence due to missing data
                assumptions = ["Payroll data not available - estimate based on opex"]
                next_steps = ["Collect payroll data", "Workforce analysis"]
            else:
                confidence = 0.2
                needs_data = True

    # Sales & Marketing efficiency
    elif "sales" in title_lower or "marketing" in title_lower or "cac" in title_lower:
        gl_data = db.query(GLPnLMonthly).all()
        if gl_data:
            avg_sales_marketing = sum(gl.opex_sales_marketing for gl in gl_data) / len(gl_data)
            # Estimate 10-20% efficiency improvement
            impact_low = avg_sales_marketing * 0.10 * 12
            impact_high = avg_sales_marketing * 0.20 * 12
            time_to_value_weeks = 12
            implementation_cost = avg_sales_marketing * 0.05 * 12
            risk_level = "Med"
            confidence = 0.6
            assumptions = ["Sales & Marketing spend can be optimized"]
            next_steps = ["CAC analysis", "Channel efficiency review"]

    # Tool sprawl / software rationalization
    elif "tool" in title_lower or "software" in title_lower or "sprawl" in title_lower:
        vendor_data = db.query(VendorSpend).all()
        software_vendors = [v for v in vendor_data if "software" in v.category.lower() or "saas" in v.category.lower()]
        if software_vendors:
            total_software_spend = sum(v.amount for v in software_vendors)
            # Estimate 15-25% savings
            impact_low = total_software_spend * 0.15
            impact_high = total_software_spend * 0.25
            time_to_value_weeks = 8
            implementation_cost = total_software_spend * 0.03
            risk_level = "Low"
            confidence = 0.7
            assumptions = [f"{len(software_vendors)} software vendors identified"]
            next_steps = ["Software inventory", "Usage analysis"]

    # Generic cost reduction (fallback)
    else:
        gl_data = db.query(GLPnLMonthly).all()
        if gl_data:
            avg_opex = (
                sum(
                    gl.opex_sales_marketing + gl.opex_rnd + gl.opex_gna + gl.opex_other
                    for gl in gl_data
                )
                / len(gl_data)
            )
            # Conservative 3-8% estimate
            impact_low = avg_opex * 0.03 * 12
            impact_high = avg_opex * 0.08 * 12
            time_to_value_weeks = 16
            implementation_cost = avg_opex * 0.02 * 12
            risk_level = "Med"
            confidence = 0.4
            assumptions = ["Generic cost reduction estimate"]
            next_steps = ["Detailed analysis required"]

    # Round to reasonable precision
    impact_low = round(impact_low, -3)  # Round to nearest 1000
    impact_high = round(impact_high, -3)

    return {
        "impact_low": impact_low,
        "impact_high": impact_high,
        "time_to_value_weeks": time_to_value_weeks,
        "implementation_cost_estimate": round(implementation_cost, -3),
        "risk_level": risk_level,
        "confidence": min(0.9, max(0.2, confidence)),
        "assumptions": assumptions,
        "next_steps": next_steps,
        "needs_data": needs_data,
    }

