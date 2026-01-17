"""Database models for storing financial data and analysis results."""

from sqlalchemy import Column, Integer, Float, String, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.storage.database import Base


class DataUpload(Base):
    """Stores metadata about uploaded CSV files."""

    __tablename__ = "data_uploads"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # 'gl_pnl', 'payroll', 'vendor', 'revenue'
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    row_count = Column(Integer, nullable=False)
    validation_status = Column(String, default="pending")  # 'pending', 'valid', 'invalid'
    validation_errors = Column(JSON, default=list)


class GLPnLMonthly(Base):
    """Stores normalized GL/P&L monthly data."""

    __tablename__ = "gl_pnl_monthly"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(String, nullable=False, index=True)  # YYYY-MM
    revenue = Column(Float, nullable=False)
    cogs = Column(Float, nullable=False)
    opex_sales_marketing = Column(Float, default=0.0)
    opex_rnd = Column(Float, default=0.0)
    opex_gna = Column(Float, default=0.0)
    opex_other = Column(Float, default=0.0)


class PayrollSummary(Base):
    """Stores normalized payroll summary data."""

    __tablename__ = "payroll_summary"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(String, nullable=False, index=True)
    function = Column(String, nullable=False)  # Sales, Marketing, R&D, G&A, Ops
    headcount = Column(Integer, nullable=False)
    fully_loaded_cost = Column(Float, nullable=True)


class VendorSpend(Base):
    """Stores normalized vendor spend data."""

    __tablename__ = "vendor_spend"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(String, nullable=False, index=True)
    vendor = Column(String, nullable=False)
    category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)


class RevenueBySegment(Base):
    """Stores normalized revenue by segment data."""

    __tablename__ = "revenue_by_segment"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(String, nullable=False, index=True)
    segment = Column(String, nullable=False)
    revenue = Column(Float, nullable=False)


class AnalysisRun(Base):
    """Stores metadata about analysis runs."""

    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")  # 'pending', 'completed', 'failed'
    pnl_data = Column(JSON, nullable=True)
    diagnostics_data = Column(JSON, nullable=True)
    initiatives_data = Column(JSON, nullable=True)


class Initiative(Base):
    """Stores generated initiatives."""

    __tablename__ = "initiatives"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(String, ForeignKey("analysis_runs.run_id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)  # 'Cost', 'Efficiency', 'Structural'
    owner = Column(String, nullable=True)
    description = Column(Text, nullable=False)
    data_evidence = Column(JSON, default=list)
    impact_low = Column(Float, nullable=False)
    impact_high = Column(Float, nullable=False)
    time_to_value_weeks = Column(Integer, nullable=False)
    implementation_cost_estimate = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)  # 'Low', 'Med', 'High'
    confidence = Column(Float, nullable=False)  # 0-1
    assumptions = Column(JSON, default=list)
    next_steps = Column(JSON, default=list)
    rank = Column(Integer, nullable=True)
    weighted_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CompanyContext(Base):
    """Stores company context information."""

    __tablename__ = "company_context"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    company_size = Column(String, nullable=True)  # 'Startup', 'SMB', 'Mid-Market', 'Enterprise'
    revenue_range = Column(String, nullable=True)  # e.g., '$10M-$50M', '$50M-$100M'
    employee_count_range = Column(String, nullable=True)  # e.g., '50-100', '100-500'
    business_model = Column(String, nullable=True)  # 'SaaS', 'E-commerce', 'Services', etc.
    growth_stage = Column(String, nullable=True)  # 'Early', 'Growth', 'Mature', 'Declining'
    geographic_presence = Column(String, nullable=True)  # 'US Only', 'North America', 'Global', etc.
    key_challenges = Column(Text, nullable=True)  # Free text
    strategic_priorities = Column(Text, nullable=True)  # Free text
    additional_context = Column(Text, nullable=True)  # Free text for any other relevant info
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

