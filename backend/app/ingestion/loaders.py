"""CSV file loaders and validators."""

import pandas as pd
from typing import List, Dict, Any, Tuple
from io import BytesIO
from app.ingestion.schemas import (
    GLPnLMonthlyRow,
    PayrollSummaryRow,
    VendorSpendRow,
    RevenueBySegmentRow,
)


def load_gl_pnl_csv(file_content: bytes) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Load and validate GL/P&L monthly CSV."""
    errors = []
    records = []

    try:
        df = pd.read_csv(BytesIO(file_content))
        df = df.fillna(0)

        # Validate required columns
        required_cols = ["month", "revenue", "cogs"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {', '.join(missing_cols)}")
            return records, errors

        for idx, row in df.iterrows():
            try:
                record = GLPnLMonthlyRow(
                    month=str(row["month"]),
                    revenue=float(row["revenue"]),
                    cogs=float(row["cogs"]),
                    opex_sales_marketing=float(row.get("opex_sales_marketing", 0)),
                    opex_rnd=float(row.get("opex_rnd", 0)),
                    opex_gna=float(row.get("opex_gna", 0)),
                    opex_other=float(row.get("opex_other", 0)),
                )
                records.append(record.dict())
            except Exception as e:
                errors.append(f"Row {idx + 1}: {str(e)}")

    except Exception as e:
        errors.append(f"File parsing error: {str(e)}")

    return records, errors


def load_payroll_csv(file_content: bytes) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Load and validate payroll summary CSV."""
    errors = []
    records = []

    try:
        df = pd.read_csv(BytesIO(file_content))
        df = df.fillna({"fully_loaded_cost": None})

        required_cols = ["month", "function", "headcount"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {', '.join(missing_cols)}")
            return records, errors

        for idx, row in df.iterrows():
            try:
                record = PayrollSummaryRow(
                    month=str(row["month"]),
                    function=str(row["function"]),
                    headcount=int(row["headcount"]),
                    fully_loaded_cost=float(row["fully_loaded_cost"]) if pd.notna(row.get("fully_loaded_cost")) else None,
                )
                records.append(record.dict())
            except Exception as e:
                errors.append(f"Row {idx + 1}: {str(e)}")

    except Exception as e:
        errors.append(f"File parsing error: {str(e)}")

    return records, errors


def load_vendor_csv(file_content: bytes) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Load and validate vendor spend CSV."""
    errors = []
    records = []

    try:
        df = pd.read_csv(BytesIO(file_content))

        required_cols = ["month", "vendor", "category", "amount"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {', '.join(missing_cols)}")
            return records, errors

        for idx, row in df.iterrows():
            try:
                record = VendorSpendRow(
                    month=str(row["month"]),
                    vendor=str(row["vendor"]),
                    category=str(row["category"]),
                    amount=float(row["amount"]),
                )
                records.append(record.dict())
            except Exception as e:
                errors.append(f"Row {idx + 1}: {str(e)}")

    except Exception as e:
        errors.append(f"File parsing error: {str(e)}")

    return records, errors


def load_revenue_csv(file_content: bytes) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Load and validate revenue by segment CSV."""
    errors = []
    records = []

    try:
        df = pd.read_csv(BytesIO(file_content))

        required_cols = ["month", "segment", "revenue"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns: {', '.join(missing_cols)}")
            return records, errors

        for idx, row in df.iterrows():
            try:
                record = RevenueBySegmentRow(
                    month=str(row["month"]),
                    segment=str(row["segment"]),
                    revenue=float(row["revenue"]),
                )
                records.append(record.dict())
            except Exception as e:
                errors.append(f"Row {idx + 1}: {str(e)}")

    except Exception as e:
        errors.append(f"File parsing error: {str(e)}")

    return records, errors


