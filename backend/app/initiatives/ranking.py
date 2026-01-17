"""Initiative ranking and scoring logic."""

from typing import List, Dict, Any
import json
import os


def load_ranking_config() -> Dict[str, float]:
    """Load ranking multipliers from config file."""
    config_path = os.path.join(os.path.dirname(__file__), "ranking_config.json")
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)
    # Default multipliers
    return {
        "risk_multiplier_low": 1.0,
        "risk_multiplier_med": 1.2,
        "risk_multiplier_high": 1.5,
        "time_multiplier_base": 1.0,
        "time_multiplier_per_week": 0.01,  # Additional multiplier per week
    }


def rank_initiatives(initiatives: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Rank initiatives using formula: score = impact_mid * confidence / (risk_multiplier * time_multiplier)."""
    config = load_ranking_config()

    # Score each initiative
    for initiative in initiatives:
        # Get impact (use midpoint)
        impact_mid = (initiative["impact_low"] + initiative["impact_high"]) / 2

        # Confidence (0-1)
        confidence = initiative.get("confidence", 0.5)

        # Risk multiplier
        risk_level = initiative.get("risk_level", "Med")
        risk_multiplier = calculate_risk_multiplier(risk_level, config)

        # Time multiplier
        time_weeks = initiative.get("time_to_value_weeks", 12)
        time_multiplier = calculate_time_multiplier(time_weeks, config)

        # Calculate score: impact_mid * confidence / (risk_multiplier * time_multiplier)
        denominator = risk_multiplier * time_multiplier
        if denominator > 0:
            weighted_score = (impact_mid * confidence) / denominator
        else:
            weighted_score = 0.0

        initiative["weighted_score"] = round(weighted_score, 2)

    # Sort by weighted score (descending)
    initiatives_sorted = sorted(initiatives, key=lambda x: x.get("weighted_score", 0), reverse=True)

    # Assign ranks
    for idx, initiative in enumerate(initiatives_sorted, 1):
        initiative["rank"] = idx

    return initiatives_sorted


def calculate_risk_multiplier(risk_level: str, config: Dict[str, float]) -> float:
    """Convert risk level to multiplier for scoring."""
    risk_map = {
        "Low": config.get("risk_multiplier_low", 1.0),
        "Med": config.get("risk_multiplier_med", 1.2),
        "High": config.get("risk_multiplier_high", 1.5),
    }
    return risk_map.get(risk_level, config.get("risk_multiplier_med", 1.2))


def calculate_time_multiplier(time_weeks: int, config: Dict[str, float]) -> float:
    """Convert time to value to multiplier for scoring."""
    base = config.get("time_multiplier_base", 1.0)
    per_week = config.get("time_multiplier_per_week", 0.01)
    # Time multiplier increases with weeks: base + (weeks * per_week)
    return base + (time_weeks * per_week)


