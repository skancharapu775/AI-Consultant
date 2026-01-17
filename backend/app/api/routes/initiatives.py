"""Initiatives API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.storage.database import get_db
from app.analytics.pnl import reconstruct_pnl
from app.analytics.diagnostics import run_diagnostics
from app.ai.client import generate_initiatives
from app.initiatives.sizing import size_initiative
from app.initiatives.ranking import rank_initiatives
import json

router = APIRouter()


def format_diagnostics_summary(diagnostics: Dict[str, Any]) -> str:
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


def format_pnl_summary(pnl_data: List[Dict[str, Any]]) -> str:
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


@router.post("/generate")
async def generate_initiatives_endpoint(db: Session = Depends(get_db)):
    """Generate initiative proposals using LLM."""
    # Get diagnostics and P&L
    pnl_data = reconstruct_pnl(db)
    if not pnl_data:
        raise HTTPException(status_code=404, detail="No P&L data found. Please run diagnostics first.")

    diagnostics = run_diagnostics(db, pnl_data)

    # Format summaries for LLM
    diagnostics_summary = format_diagnostics_summary(diagnostics)
    pnl_summary = format_pnl_summary(pnl_data)

    # Generate initiatives
    try:
        initiatives = generate_initiatives(diagnostics_summary, pnl_summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating initiatives: {str(e)}")

    return {"initiatives": initiatives}


@router.post("/score")
async def score_initiatives(
    initiatives: List[Dict[str, Any]],
    db: Session = Depends(get_db),
):
    """Deterministically size initiatives."""
    diagnostics = run_diagnostics(db, reconstruct_pnl(db))

    scored_initiatives = []
    for initiative in initiatives:
        sized = size_initiative(initiative, db, diagnostics)
        scored_initiatives.append({**initiative, **sized})

    return {"initiatives": scored_initiatives}


@router.post("/rank")
async def rank_initiatives_endpoint(initiatives: List[Dict[str, Any]]):
    """Rank initiatives by weighted score."""
    ranked = rank_initiatives(initiatives)
    return {"initiatives": ranked}


