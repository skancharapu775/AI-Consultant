"""Pydantic schemas for CSV data validation."""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class GLPnLMonthlyRow(BaseModel):
    """Schema for GL/P&L monthly CSV row."""

    month: str = Field(..., description="Month in YYYY-MM format")
    revenue: float = Field(..., ge=0)
    cogs: float = Field(..., ge=0)
    opex_sales_marketing: float = Field(default=0.0, ge=0)
    opex_rnd: float = Field(default=0.0, ge=0)
    opex_gna: float = Field(default=0.0, ge=0)
    opex_other: float = Field(default=0.0, ge=0)

    @validator("month")
    def validate_month_format(cls, v):
        try:
            datetime.strptime(v, "%Y-%m")
            return v
        except ValueError:
            raise ValueError("Month must be in YYYY-MM format")


class PayrollSummaryRow(BaseModel):
    """Schema for payroll summary CSV row."""

    month: str = Field(..., description="Month in YYYY-MM format")
    function: str = Field(..., description="Function: Sales, Marketing, R&D, G&A, Ops")
    headcount: int = Field(..., ge=0)
    fully_loaded_cost: Optional[float] = Field(default=None, ge=0)

    @validator("month")
    def validate_month_format(cls, v):
        try:
            datetime.strptime(v, "%Y-%m")
            return v
        except ValueError:
            raise ValueError("Month must be in YYYY-MM format")

    @validator("function")
    def validate_function(cls, v):
        valid_functions = ["Sales", "Marketing", "R&D", "G&A", "Ops"]
        if v not in valid_functions:
            raise ValueError(f"Function must be one of: {', '.join(valid_functions)}")
        return v


class VendorSpendRow(BaseModel):
    """Schema for vendor spend CSV row."""

    month: str = Field(..., description="Month in YYYY-MM format")
    vendor: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1)
    amount: float = Field(..., ge=0)

    @validator("month")
    def validate_month_format(cls, v):
        try:
            datetime.strptime(v, "%Y-%m")
            return v
        except ValueError:
            raise ValueError("Month must be in YYYY-MM format")


class RevenueBySegmentRow(BaseModel):
    """Schema for revenue by segment CSV row."""

    month: str = Field(..., description="Month in YYYY-MM format")
    segment: str = Field(..., min_length=1)
    revenue: float = Field(..., ge=0)

    @validator("month")
    def validate_month_format(cls, v):
        try:
            datetime.strptime(v, "%Y-%m")
            return v
        except ValueError:
            raise ValueError("Month must be in YYYY-MM format")


