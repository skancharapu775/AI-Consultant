"""Analysis API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.storage.database import get_db
from app.analytics.pnl import reconstruct_pnl, calculate_margin_bridge
from app.analytics.diagnostics import run_diagnostics

router = APIRouter()


@router.post("/pnl")
async def analyze_pnl(db: Session = Depends(get_db)):
    """Reconstruct and return canonical P&L."""
    pnl_data = reconstruct_pnl(db)

    if not pnl_data:
        raise HTTPException(status_code=404, detail="No P&L data found. Please upload GL/P&L data first.")

    margin_bridge = calculate_margin_bridge(pnl_data)

    return {
        "pnl": pnl_data,
        "margin_bridge": margin_bridge,
    }


@router.post("/diagnostics")
async def analyze_diagnostics(db: Session = Depends(get_db)):
    """Run diagnostics and return results."""
    pnl_data = reconstruct_pnl(db)

    if not pnl_data:
        raise HTTPException(status_code=404, detail="No P&L data found. Please upload GL/P&L data first.")

    diagnostics = run_diagnostics(db, pnl_data)

    return diagnostics


