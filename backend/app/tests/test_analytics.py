"""Tests for analytics engine."""

import pytest
from app.analytics.pnl import PLReconstructor, PLStatement


def test_pnl_reconstructor():
    """Test P&L reconstruction."""
    reconstructor = PLReconstructor()
    
    # Sample data
    gl_data = [{
        "account_code": "4",
        "account_name": "Revenue",
        "amount": 1000000,
        "date": "2023-01",
        "category": "Revenue"
    }]
    
    reconstructor.load_data(gl_data=gl_data)
    pnl = reconstructor.reconstruct("2023-01")
    
    assert pnl.revenue > 0
    assert isinstance(pnl, PLStatement)


def test_margin_calculation():
    """Test margin calculations."""
    reconstructor = PLReconstructor()
    gl_data = [{
        "account_code": "4",
        "account_name": "Revenue",
        "amount": 1000000,
        "date": "2023-01",
        "category": "Revenue"
    }]
    
    reconstructor.load_data(gl_data=gl_data)
    pnl = reconstructor.reconstruct("2023-01")
    
    assert pnl.gross_margin == pnl.revenue - pnl.cogs
    assert pnl.ebitda == pnl.gross_margin - pnl.operating_expenses.total()


