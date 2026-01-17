"""Reports API routes."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.storage.database import get_db
from app.storage.models import AnalysisRun, CompanyContext
from app.reports.memo import generate_memo
from app.reports.deck import generate_deck
from app.analytics.pnl import reconstruct_pnl
from app.analytics.diagnostics import run_diagnostics, assess_data_completeness
import json

router = APIRouter()


@router.get("/memo")
async def get_memo(db: Session = Depends(get_db)):
    """Generate and return executive memo as Markdown."""
    # Get latest run or use current data
    latest_run = db.query(AnalysisRun).order_by(desc(AnalysisRun.created_at)).first()

    if latest_run and latest_run.initiatives_data:
        initiatives = latest_run.initiatives_data
        pnl_data = latest_run.pnl_data or reconstruct_pnl(db)
        diagnostics = latest_run.diagnostics_data or run_diagnostics(db, pnl_data)
    else:
        pnl_data = reconstruct_pnl(db)
        if not pnl_data:
            raise HTTPException(status_code=404, detail="No analysis data found. Please run full analysis first.")
        diagnostics = run_diagnostics(db, pnl_data)
        initiatives = []

    data_completeness = assess_data_completeness(db)
    
    # Get company context
    company_context = db.query(CompanyContext).first()
    context_dict = None
    if company_context:
        context_dict = {
            "company_name": company_context.company_name,
            "industry": company_context.industry,
            "company_size": company_context.company_size,
            "revenue_range": company_context.revenue_range,
            "employee_count_range": company_context.employee_count_range,
            "business_model": company_context.business_model,
            "growth_stage": company_context.growth_stage,
            "geographic_presence": company_context.geographic_presence,
            "key_challenges": company_context.key_challenges,
            "strategic_priorities": company_context.strategic_priorities,
            "additional_context": company_context.additional_context,
        }

    memo = generate_memo(pnl_data, diagnostics, initiatives, data_completeness, context_dict)

    return Response(content=memo, media_type="text/markdown")


@router.get("/deck")
async def get_deck(db: Session = Depends(get_db)):
    """Generate and return PowerPoint deck."""
    # Get latest run or use current data
    latest_run = db.query(AnalysisRun).order_by(desc(AnalysisRun.created_at)).first()

    if latest_run and latest_run.initiatives_data:
        initiatives = latest_run.initiatives_data
        pnl_data = latest_run.pnl_data or reconstruct_pnl(db)
        diagnostics = latest_run.diagnostics_data or run_diagnostics(db, pnl_data)
    else:
        pnl_data = reconstruct_pnl(db)
        if not pnl_data:
            raise HTTPException(status_code=404, detail="No analysis data found. Please run full analysis first.")
        diagnostics = run_diagnostics(db, pnl_data)
        initiatives = []

    data_completeness = assess_data_completeness(db)
    deck_bytes = generate_deck(pnl_data, diagnostics, initiatives, data_completeness)

    return Response(
        content=deck_bytes,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": "attachment; filename=analysis_deck.pptx"},
    )


