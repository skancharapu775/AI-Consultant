"""Ingestion API routes."""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.storage.database import get_db
from app.storage.models import DataUpload, GLPnLMonthly, PayrollSummary, VendorSpend, RevenueBySegment
from app.ingestion.loaders import (
    load_gl_pnl_csv,
    load_payroll_csv,
    load_vendor_csv,
    load_revenue_csv,
)
import uuid

router = APIRouter()


@router.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    """Upload one or more CSV files. gl_pnl_monthly.csv is required, others are optional."""
    results = []
    has_gl_pnl = False

    for file in files:
        # Get filename safely
        filename = file.filename or "unknown_file"
        filename_lower = filename.lower()
        file_type = None
        loader_func = None

        # Determine file type from filename
        if "gl" in filename_lower or "pnl" in filename_lower or "profit" in filename_lower or "loss" in filename_lower:
            file_type = "gl_pnl"
            loader_func = load_gl_pnl_csv
        elif "payroll" in filename_lower or "pay" in filename_lower or "headcount" in filename_lower:
            file_type = "payroll"
            loader_func = load_payroll_csv
        elif "vendor" in filename_lower or "spend" in filename_lower:
            file_type = "vendor"
            loader_func = load_vendor_csv
        elif "revenue" in filename_lower or "segment" in filename_lower:
            file_type = "revenue"
            loader_func = load_revenue_csv
        else:
            results.append({
                "file_name": filename,
                "status": "error",
                "error": f"Could not determine file type from filename '{filename}'. File name must contain one of: 'gl', 'pnl', 'payroll', 'vendor', or 'revenue'",
            })
            continue

        # Track if we have required GL/P&L file
        if file_type == "gl_pnl":
            has_gl_pnl = True

        # Read file content
        try:
            content = await file.read()
        except Exception as e:
            results.append({
                "file_name": filename,
                "status": "error",
                "error": f"Failed to read file: {str(e)}",
            })
            continue

        # Load and validate
        try:
            records, errors = loader_func(content)
        except Exception as e:
            results.append({
                "file_name": filename,
                "status": "error",
                "error": f"Failed to parse CSV file: {str(e)}",
            })
            continue

        # Store upload metadata
        try:
            upload = DataUpload(
                file_name=filename,
                file_type=file_type,
                row_count=len(records),
                validation_status="valid" if not errors else "invalid",
                validation_errors=errors,
            )
            db.add(upload)
            db.flush()
        except Exception as e:
            results.append({
                "file_name": filename,
                "status": "error",
                "error": f"Failed to store upload metadata: {str(e)}",
            })
            continue

        # Store data if valid
        if not errors:
            if file_type == "gl_pnl":
                # Delete existing records for same months
                existing_months = {r["month"] for r in records}
                db.query(GLPnLMonthly).filter(GLPnLMonthly.month.in_(existing_months)).delete()

                for record in records:
                    db.add(GLPnLMonthly(**record))

            elif file_type == "payroll":
                existing_months = {r["month"] for r in records}
                db.query(PayrollSummary).filter(
                    PayrollSummary.month.in_(existing_months)
                ).delete()

                for record in records:
                    db.add(PayrollSummary(**record))

            elif file_type == "vendor":
                existing_months = {r["month"] for r in records}
                db.query(VendorSpend).filter(VendorSpend.month.in_(existing_months)).delete()

                for record in records:
                    db.add(VendorSpend(**record))

            elif file_type == "revenue":
                existing_months = {r["month"] for r in records}
                db.query(RevenueBySegment).filter(
                    RevenueBySegment.month.in_(existing_months)
                ).delete()

                for record in records:
                    db.add(RevenueBySegment(**record))

            db.commit()

        results.append({
            "file_name": filename,
            "file_type": file_type,
            "status": "valid" if not errors else "invalid",
            "row_count": len(records),
            "errors": errors if errors else [],
        })

    # Validate that required file (gl_pnl) was uploaded
    if not has_gl_pnl:
        return {
            "results": results,
            "error": "gl_pnl_monthly.csv is required but was not found in uploaded files",
        }

    return {"results": results}


