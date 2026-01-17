"""Generate executive memo in Markdown format."""

from typing import List, Dict, Any
from datetime import datetime


def generate_memo(
    pnl_data: List[Dict[str, Any]],
    diagnostics: Dict[str, Any],
    initiatives: List[Dict[str, Any]],
    data_completeness: Dict[str, Any],
    company_context: Dict[str, Any] = None,
) -> str:
    """Generate executive memo in Markdown format."""
    memo = []
    memo.append("# Executive Memo: Financial Diagnostics & Improvement Initiatives\n")
    if company_context and company_context.get("company_name"):
        memo.append(f"**Company:** {company_context.get('company_name')}\n")
    memo.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n")
    memo.append("---\n\n")
    
    # Add company context section if available
    if company_context:
        context_parts = []
        if company_context.get("industry"):
            context_parts.append(f"**Industry:** {company_context.get('industry')}")
        if company_context.get("company_size"):
            context_parts.append(f"**Company Size:** {company_context.get('company_size')}")
        if company_context.get("business_model"):
            context_parts.append(f"**Business Model:** {company_context.get('business_model')}")
        if company_context.get("growth_stage"):
            context_parts.append(f"**Growth Stage:** {company_context.get('growth_stage')}")
        
        if context_parts:
            memo.append("## Company Overview\n\n")
            memo.append(" | ".join(context_parts))
            memo.append("\n\n")
            if company_context.get("key_challenges"):
                memo.append(f"**Key Challenges:** {company_context.get('key_challenges')}\n\n")
            if company_context.get("strategic_priorities"):
                memo.append(f"**Strategic Priorities:** {company_context.get('strategic_priorities')}\n\n")

    # Summary
    memo.append("## Executive Summary\n\n")
    if pnl_data:
        latest = pnl_data[-1]
        memo.append(
            f"Our analysis identifies **{len(initiatives)} actionable initiatives** with potential to "
            f"improve EBITDA by ${sum(i.get('impact_low', 0) for i in initiatives[:5]):,.0f} - "
            f"${sum(i.get('impact_high', 0) for i in initiatives[:5]):,.0f} annually (based on top 5 initiatives).\n\n"
        )
        memo.append(
            f"Current EBITDA margin: **{latest.get('ebitda_margin_pct', 0):.1f}%** "
            f"(${latest.get('ebitda', 0):,.0f})\n\n"
        )

    # What's driving EBITDA
    memo.append("## What's Driving EBITDA\n\n")
    if diagnostics.get("trends"):
        trends = diagnostics["trends"]
        memo.append("**Key Trends:**\n\n")
        if "revenue" in trends:
            direction = trends["revenue"]["direction"]
            memo.append(f"- Revenue is **{direction}** (R² = {trends['revenue']['r_squared']:.2f})\n")
        if "ebitda" in trends:
            direction = trends["ebitda"]["direction"]
            memo.append(f"- EBITDA is **{direction}** (R² = {trends['ebitda']['r_squared']:.2f})\n")
        memo.append("\n")

    if diagnostics.get("fixed_vs_variable"):
        memo.append("**Cost Structure:**\n\n")
        fv = diagnostics["fixed_vs_variable"]
        for category, data in fv.items():
            memo.append(
                f"- {category.replace('_', ' ').title()}: "
                f"{data['fixed_pct']*100:.0f}% fixed, {data['variable_pct']*100:.0f}% variable "
                f"(confidence: {data['confidence']:.0%})\n"
            )
        memo.append("\n")

    # Top initiatives
    memo.append("## Top 5 Initiatives\n\n")
    if initiatives:
        top_5 = sorted(initiatives, key=lambda x: x.get("rank", 999))[:5]
        memo.append("| Rank | Initiative | Impact (Annual) | Confidence | Time | Risk |\n")
        memo.append("|------|------------|-----------------|------------|------|------|\n")

        for init in top_5:
            impact_str = f"${init.get('impact_low', 0):,.0f} - ${init.get('impact_high', 0):,.0f}"
            confidence_str = f"{init.get('confidence', 0)*100:.0f}%"
            time_str = f"{init.get('time_to_value_weeks', 0)} weeks"
            risk = init.get("risk_level", "Med")
            memo.append(
                f"| {init.get('rank', 'N/A')} | {init.get('title', 'N/A')} | {impact_str} | "
                f"{confidence_str} | {time_str} | {risk} |\n"
            )
        memo.append("\n")
    else:
        memo.append("**No new initiatives recommended this quarter.**\n\n")
        memo.append("This may be due to:\n")
        memo.append("- Insufficient data to generate high-confidence recommendations\n")
        memo.append("- Estimated impact of potential initiatives is below threshold\n")
        memo.append("- Data gaps preventing accurate sizing (see Data Gaps section below)\n\n")

    # Data gaps / what would improve confidence
    memo.append("## Data Gaps / What Would Improve Confidence\n\n")
    data_gaps = data_completeness.get("data_gaps", [])
    if data_gaps:
        memo.append("**Missing or Incomplete Data:**\n\n")
        for gap in data_gaps:
            memo.append(f"- {gap}\n")
        memo.append("\n")
        memo.append("**Impact on Analysis:**\n\n")
        memo.append("- Missing optional datasets reduce confidence in initiative sizing\n")
        memo.append("- Some initiative types may be disabled or have wider impact ranges\n")
        memo.append("- Completeness score: {:.0f}%\n\n".format(data_completeness.get("completeness_score", 0) * 100))
    else:
        memo.append("No significant data gaps identified. All required and optional datasets are present.\n\n")
    
    # What would improve confidence
    memo.append("**To Improve Confidence:**\n\n")
    if not data_completeness.get("has_payroll"):
        memo.append("- Upload payroll_summary.csv to enable headcount optimization initiatives\n")
    if not data_completeness.get("has_vendor"):
        memo.append("- Upload vendor_spend.csv to enable vendor consolidation initiatives\n")
    if not data_completeness.get("has_revenue_segments"):
        memo.append("- Upload revenue_by_segment.csv to enable segment-specific analysis\n")
    if data_completeness.get("payroll_cost_coverage", 1.0) < 0.8:
        memo.append("- Provide fully_loaded_cost data in payroll_summary.csv for accurate headcount sizing\n")
    if not data_gaps and data_completeness.get("has_payroll") and data_completeness.get("has_vendor"):
        memo.append("- All optional datasets are present. Consider extending historical data range for better trend analysis.\n")
    memo.append("\n")

    memo.append("---\n")
    memo.append("*This memo was generated automatically. Review all assumptions and sizing before implementation.*\n")

    return "".join(memo)


