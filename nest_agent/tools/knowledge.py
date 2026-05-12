"""
Knowledge-base tool wrappers for NEST specialists.

These are thin ADK-tool adapters around the curated guideline data in
`nest_agent.data`. Specialists call them per medication / per finding to
produce verdicts that always include a `source_id` for the audit log.
"""

from __future__ import annotations

import logging
from typing import Any

from google.adk.tools import ToolContext

from ..data.aap_newborn import (
    aap_newborn_visits,
    bhutani_phototherapy_threshold,
    feeding_milestone_check,
    newborn_red_flag_panel,
)
from ..data.acog_postpartum import (
    acog_postpartum_visits,
    bp_postpartum_assessment,
    postpartum_red_flag_panel,
)
from ..data.lactmed import lactation_safety_lookup
from ..data.mental_health import (
    edinburgh_score_interpretation,
    phq9_score_interpretation,
)
from ..data.sdoh import sdoh_screen_summary

logger = logging.getLogger(__name__)


def list_acog_postpartum_visits(
    delivery_date: str,
    has_hypertensive_disorder: bool,
    has_postpartum_hemorrhage: bool,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Return ACOG postpartum visit windows tailored to this patient.

    Args:
        delivery_date: ISO date YYYY-MM-DD.
        has_hypertensive_disorder: True if preeclampsia / gestational HTN /
            chronic HTN (triggers earlier BP visit window).
        has_postpartum_hemorrhage: True if PPH (triggers 1-week bleeding visit).
    """
    logger.info(
        "tool_list_acog_postpartum_visits htn=%s pph=%s",
        has_hypertensive_disorder, has_postpartum_hemorrhage,
    )
    return acog_postpartum_visits(
        delivery_date=delivery_date,
        has_hypertensive_disorder=bool(has_hypertensive_disorder),
        has_postpartum_hemorrhage=bool(has_postpartum_hemorrhage),
    )


def classify_bp_postpartum(
    systolic: float,
    diastolic: float,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Classify a postpartum BP reading per ACOG severity bands.

    Args:
        systolic: Systolic BP, mmHg.
        diastolic: Diastolic BP, mmHg.
    """
    logger.info("tool_classify_bp_postpartum sys=%s dia=%s", systolic, diastolic)
    return bp_postpartum_assessment(systolic=float(systolic), diastolic=float(diastolic))


def check_postpartum_red_flags(tool_context: ToolContext) -> dict[str, Any]:
    """Return the curated ACOG / CDC postpartum red-flag panel for the report.

    These are the exact warning signs that should be on the mother's red-flag
    card in the discharge handoff (CDC "Hear Her" + ACOG urgent maternal
    warning signs).
    """
    logger.info("tool_check_postpartum_red_flags")
    return {"status": "success", "red_flags": postpartum_red_flag_panel()}


def list_aap_newborn_visits(
    infant_age_days: int,
    hospital_discharge_day: int,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Return the AAP / Bright Futures newborn visit schedule."""
    logger.info(
        "tool_list_aap_newborn_visits age_days=%s discharge=%s",
        infant_age_days, hospital_discharge_day,
    )
    return aap_newborn_visits(
        infant_age_days=int(infant_age_days),
        hospital_discharge_day=int(hospital_discharge_day),
    )


def classify_jaundice_risk(
    age_hours: float,
    total_bilirubin_mg_dl: float,
    risk_band: str,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Compare a newborn TSB to the AAP 2022 phototherapy threshold.

    Args:
        age_hours: Infant age in HOURS at the bilirubin measurement.
        total_bilirubin_mg_dl: TSB in mg/dL.
        risk_band: 'low' | 'medium' | 'high' (per AAP risk factors).
    """
    logger.info(
        "tool_classify_jaundice_risk age_h=%s tsb=%s band=%s",
        age_hours, total_bilirubin_mg_dl, risk_band,
    )
    return bhutani_phototherapy_threshold(
        age_hours=float(age_hours),
        total_bilirubin_mg_dl=float(total_bilirubin_mg_dl),
        risk_band=risk_band,
    )


def check_newborn_red_flags(tool_context: ToolContext) -> dict[str, Any]:
    """Return the curated AAP newborn red-flag panel for the discharge handoff."""
    logger.info("tool_check_newborn_red_flags")
    return {"status": "success", "red_flags": newborn_red_flag_panel()}


def lookup_lactation_safety(medication: str, tool_context: ToolContext) -> dict[str, Any]:
    """Look up a maternal medication's LactMed safety category for a breastfeeding infant.

    Args:
        medication: Generic medication name (e.g., 'sertraline').

    Returns the Hale category (L1–L5) with rationale and source ID, or a
    'not_found' status when the medication is outside the curated subset.
    """
    logger.info("tool_lookup_lactation_safety med=%s", medication)
    if not medication:
        return {"status": "error", "error_message": "medication is required"}
    entry = lactation_safety_lookup(medication)
    if entry is None:
        return {
            "status":     "not_found",
            "medication": medication,
            "message":    (
                f"'{medication}' is not in the curated LactMed subset. "
                "Default to L3 (probably compatible) but recommend the prescriber "
                "verify on https://www.ncbi.nlm.nih.gov/books/NBK501922/ before use."
            ),
        }
    return {"status": "found", **entry}


def check_feeding_milestones(
    feeding_method: str,
    age_days: int,
    weight_loss_pct: float,
    feeding_concerns: list[str],
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Apply AAP / ABM feeding milestones to the dyad."""
    logger.info(
        "tool_check_feeding_milestones method=%s age_d=%s wl=%s n_concerns=%d",
        feeding_method, age_days, weight_loss_pct, len(feeding_concerns or []),
    )
    return feeding_milestone_check(
        feeding_method=feeding_method,
        age_days=int(age_days),
        weight_loss_pct=float(weight_loss_pct) if weight_loss_pct else None,
        feeding_concerns=feeding_concerns,
    )


def interpret_epds(
    epds_total: int,
    self_harm_item_present: bool,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Interpret an EPDS score with awareness of Item 10 (self-harm)."""
    logger.info(
        "tool_interpret_epds total=%s self_harm=%s",
        epds_total, self_harm_item_present,
    )
    return edinburgh_score_interpretation(
        epds_total=int(epds_total),
        self_harm_item_present=bool(self_harm_item_present),
    )


def interpret_phq9(
    phq9_total: int,
    self_harm_item_present: bool,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Interpret a PHQ-9 score with awareness of Item 9 (self-harm)."""
    logger.info(
        "tool_interpret_phq9 total=%s self_harm=%s",
        phq9_total, self_harm_item_present,
    )
    return phq9_score_interpretation(
        phq9_total=int(phq9_total),
        self_harm_item_present=bool(self_harm_item_present),
    )


def summarize_sdoh(concerns: list[str], tool_context: ToolContext) -> dict[str, Any]:
    """Convert free-text SDOH concerns into structured interventions with audit IDs."""
    logger.info("tool_summarize_sdoh n_concerns=%d", len(concerns or []))
    return sdoh_screen_summary(concerns=concerns or [])
