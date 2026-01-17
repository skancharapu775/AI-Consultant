"""Tests for initiative ranking."""

import pytest
from app.initiatives.ranking import rank_initiatives


def test_rank_initiatives():
    """Test initiative ranking."""
    initiatives = [
        {
            "title": "Test Initiative 1",
            "impact_low": 100000,
            "impact_high": 200000,
            "confidence": 0.8,
            "risk_level": "Low",
            "time_to_value_weeks": 8,
        },
        {
            "title": "Test Initiative 2",
            "impact_low": 50000,
            "impact_high": 100000,
            "confidence": 0.6,
            "risk_level": "High",
            "time_to_value_weeks": 24,
        },
    ]
    
    ranked = rank_initiatives(initiatives)
    
    assert len(ranked) == 2
    assert ranked[0]["rank"] == 1
    assert ranked[1]["rank"] == 2
    assert "weighted_score" in ranked[0]
    # Higher impact, confidence, lower risk should rank higher
    assert ranked[0]["weighted_score"] >= ranked[1]["weighted_score"]


