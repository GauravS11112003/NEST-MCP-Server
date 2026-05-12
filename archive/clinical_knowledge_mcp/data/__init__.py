"""Static clinical reference datasets bundled with the MCP server."""

from .anticholinergic_burden import (
    ACB_SCORE,
    acb_score_for,
    calculate_total_acb,
)
from .beers_criteria import BEERS_CRITERIA_2023, lookup_beers
from .renal_dose_adjustments import (
    RENAL_ADJUSTMENTS,
    get_renal_recommendation,
)

__all__ = [
    "ACB_SCORE",
    "BEERS_CRITERIA_2023",
    "RENAL_ADJUSTMENTS",
    "acb_score_for",
    "calculate_total_acb",
    "get_renal_recommendation",
    "lookup_beers",
]
