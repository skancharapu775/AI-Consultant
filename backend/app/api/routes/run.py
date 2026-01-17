"""Full pipeline run API route."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
from app.storage.database import get_db
from app.storage.models import AnalysisRun, CompanyContext
from app.analytics.pnl import reconstruct_pnl
from app.analytics.diagnostics import run_diagnostics
from app.ai.client import generate_initiatives
from app.initiatives.sizing import size_initiative
from app.initiatives.ranking import rank_initiatives
# Helper functions (duplicated from initiatives.py to avoid circular imports)
def format_diagnostics_summary(diagnostics):
    """Format diagnostics into a summary string for LLM."""
    summary_parts = []
    if diagnostics.get("fixed_vs_variable"):
        summary_parts.append("Fixed vs Variable Cost Analysis:")
        for cat, data in diagnostics["fixed_vs_variable"].items():
            summary_parts.append(
                f"  - {cat}: {data['fixed_pct']*100:.0f}% fixed, {data['variable_pct']*100:.0f}% variable"
            )
    if diagnostics.get("outliers"):
        outliers = diagnostics["outliers"]
        if outliers.get("vendor_spikes"):
            summary_parts.append(f"Vendor spend spikes detected: {len(outliers['vendor_spikes'])} months")
        if outliers.get("opex_spikes"):
            summary_parts.append(f"Operating expense spikes detected: {len(outliers['opex_spikes'])} months")
        if outliers.get("revenue_declines"):
            summary_parts.append(f"Revenue declines detected: {len(outliers['revenue_declines'])} months")
    if diagnostics.get("trends"):
        trends = diagnostics["trends"]
        if "revenue" in trends:
            summary_parts.append(f"Revenue trend: {trends['revenue']['direction']}")
        if "ebitda" in trends:
            summary_parts.append(f"EBITDA trend: {trends['ebitda']['direction']}")
    return "\n".join(summary_parts)


def format_pnl_summary(pnl_data):
    """Format P&L data into a summary string for LLM."""
    if not pnl_data:
        return "No P&L data available."
    latest = pnl_data[-1]
    summary = f"Latest period ({latest['month']}):\n"
    summary += f"  Revenue: ${latest['revenue']:,.0f}\n"
    summary += f"  COGS: ${latest['cogs']:,.0f}\n"
    summary += f"  Gross Margin: ${latest['gross_margin']:,.0f} ({latest['gross_margin_pct']:.1f}%)\n"
    summary += f"  Total OpEx: ${latest['total_opex']:,.0f}\n"
    summary += f"  EBITDA: ${latest['ebitda']:,.0f} ({latest['ebitda_margin_pct']:.1f}%)\n"
    if len(pnl_data) > 1:
        summary += f"\nTrend over {len(pnl_data)} months:\n"
        first = pnl_data[0]
        revenue_growth = ((latest['revenue'] - first['revenue']) / first['revenue'] * 100) if first['revenue'] > 0 else 0
        ebitda_growth = ((latest['ebitda'] - first['ebitda']) / abs(first['ebitda']) * 100) if first['ebitda'] != 0 else 0
        summary += f"  Revenue growth: {revenue_growth:.1f}%\n"
        summary += f"  EBITDA change: {ebitda_growth:.1f}%\n"
    return summary


def format_company_context(db: Session) -> str:
    """Format company context into a summary string for LLM."""
    context = db.query(CompanyContext).first()
    if not context:
        return "No company context provided."
    
    parts = []
    if context.company_name:
        parts.append(f"Company Name: {context.company_name}")
    if context.industry:
        parts.append(f"Industry: {context.industry}")
    if context.company_size:
        parts.append(f"Company Size: {context.company_size}")
    if context.revenue_range:
        parts.append(f"Revenue Range: {context.revenue_range}")
    if context.employee_count_range:
        parts.append(f"Employee Count: {context.employee_count_range}")
    if context.business_model:
        parts.append(f"Business Model: {context.business_model}")
    if context.growth_stage:
        parts.append(f"Growth Stage: {context.growth_stage}")
    if context.geographic_presence:
        parts.append(f"Geographic Presence: {context.geographic_presence}")
    if context.key_challenges:
        parts.append(f"\nKey Challenges:\n{context.key_challenges}")
    if context.strategic_priorities:
        parts.append(f"\nStrategic Priorities:\n{context.strategic_priorities}")
    if context.additional_context:
        parts.append(f"\nAdditional Context:\n{context.additional_context}")
    
    return "\n".join(parts) if parts else "No company context provided."

router = APIRouter()


@router.post("/full")
async def run_full_pipeline(db: Session = Depends(get_db)):
    """Run the full pipeline: ingestion -> analysis -> initiatives -> ranking."""
    run_id = str(uuid.uuid4())

    try:
        # Step 1: Reconstruct P&L (required)
        pnl_data = reconstruct_pnl(db)
        if not pnl_data:
            raise HTTPException(status_code=404, detail="No GL/P&L data found. Please upload gl_pnl_monthly.csv first.")

        # Step 2: Run diagnostics
        diagnostics = run_diagnostics(db, pnl_data)

        # Step 3: Generate initiatives (LLM)
        diagnostics_summary = format_diagnostics_summary(diagnostics)
        pnl_summary = format_pnl_summary(pnl_data)
        company_context = format_company_context(db)

        try:
            initiatives = generate_initiatives(diagnostics_summary, pnl_summary, company_context)
        except Exception as e:
            # If LLM fails, return error but don't fail entire pipeline
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"LLM generation failed: {str(e)}", exc_info=True)
            initiatives = []
            diagnostics["llm_error"] = str(e)

        # Step 4: Size initiatives (deterministic)
        sized_initiatives = []
        for initiative in initiatives:
            sized = size_initiative(initiative, db, diagnostics)
            sized_initiatives.append({**initiative, **sized})

        # Step 5: Rank initiatives
        ranked_initiatives = rank_initiatives(sized_initiatives)

        # Step 6: Store run
        analysis_run = AnalysisRun(
            run_id=run_id,
            status="completed",
            pnl_data=pnl_data,
            diagnostics_data=diagnostics,
            initiatives_data=ranked_initiatives,
        )
        db.add(analysis_run)
        db.commit()

        result = {
            "run_id": run_id,
            "status": "completed",
            "pnl_records": len(pnl_data),
            "initiatives_count": len(ranked_initiatives),
            "initiatives": ranked_initiatives,
        }
        # Include LLM error if it occurred
        if "llm_error" in diagnostics:
            result["llm_error"] = diagnostics["llm_error"]
        return result

    except HTTPException:
        raise
    except Exception as e:
        # Store failed run
        analysis_run = AnalysisRun(
            run_id=run_id,
            status="failed",
        )
        db.add(analysis_run)
        db.commit()

        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")

