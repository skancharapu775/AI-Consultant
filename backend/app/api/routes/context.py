"""Company context API routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.storage.database import get_db
from app.storage.models import CompanyContext


class CompanyContextInput(BaseModel):
    company_name: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    revenue_range: Optional[str] = None
    employee_count_range: Optional[str] = None
    business_model: Optional[str] = None
    growth_stage: Optional[str] = None
    geographic_presence: Optional[str] = None
    key_challenges: Optional[str] = None
    strategic_priorities: Optional[str] = None
    additional_context: Optional[str] = None


router = APIRouter()


@router.get("/")
async def get_company_context(db: Session = Depends(get_db)):
    """Get current company context."""
    context = db.query(CompanyContext).first()
    if not context:
        return {
            "company_name": None,
            "industry": None,
            "company_size": None,
            "revenue_range": None,
            "employee_count_range": None,
            "business_model": None,
            "growth_stage": None,
            "geographic_presence": None,
            "key_challenges": None,
            "strategic_priorities": None,
            "additional_context": None,
        }
    
    return {
        "company_name": context.company_name,
        "industry": context.industry,
        "company_size": context.company_size,
        "revenue_range": context.revenue_range,
        "employee_count_range": context.employee_count_range,
        "business_model": context.business_model,
        "growth_stage": context.growth_stage,
        "geographic_presence": context.geographic_presence,
        "key_challenges": context.key_challenges,
        "strategic_priorities": context.strategic_priorities,
        "additional_context": context.additional_context,
    }


@router.post("/")
async def save_company_context(
    context_data: CompanyContextInput,
    db: Session = Depends(get_db),
):
    """Save or update company context."""
    # Get existing context or create new
    context = db.query(CompanyContext).first()
    
    if context:
        # Update existing
        for field, value in context_data.dict(exclude_unset=True).items():
            setattr(context, field, value)
    else:
        # Create new
        context = CompanyContext(**context_data.dict(exclude_unset=True))
        db.add(context)
    
    db.commit()
    db.refresh(context)
    
    return {
        "message": "Company context saved successfully",
        "context": {
            "company_name": context.company_name,
            "industry": context.industry,
            "company_size": context.company_size,
            "revenue_range": context.revenue_range,
            "employee_count_range": context.employee_count_range,
            "business_model": context.business_model,
            "growth_stage": context.growth_stage,
            "geographic_presence": context.geographic_presence,
            "key_challenges": context.key_challenges,
            "strategic_priorities": context.strategic_priorities,
            "additional_context": context.additional_context,
        },
    }
