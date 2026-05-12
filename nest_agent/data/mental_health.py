"""
Postpartum mental health screening interpretation.

Sources:
  • Edinburgh Postnatal Depression Scale (EPDS) — Cox JL, Holden JM, Sagovsky R.
    Br J Psychiatry. 1987;150:782-786.
  • PHQ-9 — Kroenke K, Spitzer RL, Williams JB. J Gen Intern Med. 2001;16:606-613.
  • ACOG Committee Opinion 757 — Screening for Perinatal Depression (2018,
    reaffirmed 2024).
  • USPSTF 2023 — Screening for Perinatal Depression.
  • Item 10 of EPDS specifically asks about self-harm — any non-zero answer
    is treated as a clinical emergency.
"""

from __future__ import annotations

from typing import Any


def edinburgh_score_interpretation(
    epds_total: int,
    self_harm_item_present: bool = False,
) -> dict[str, Any]:
    """Interpret an EPDS total score and any positive self-harm item.

    Args:
        epds_total: Total EPDS score (0–30). Pass -1 if not done.
        self_harm_item_present: True if Item 10 (self-harm) was scored > 0.

    Returns:
        {severity, label, interpretation, action, source_id}
    """
    if epds_total is None or epds_total < 0:
        return {
            "severity":       "UNKNOWN",
            "label":          "Not screened",
            "interpretation": "EPDS not completed at discharge.",
            "action":         "Administer EPDS or PHQ-9 before discharge per ACOG Committee Opinion 757.",
            "source_id":      "ACOG-CO-757",
        }

    if self_harm_item_present:
        return {
            "severity":       "EMERGENCY",
            "label":          "Positive self-harm item",
            "interpretation": (
                "Any positive answer on EPDS Item 10 is a clinical emergency — "
                "regardless of total score."
            ),
            "action":         "Immediate mental-health evaluation BEFORE discharge. Do NOT discharge until safety plan in place. Consider voluntary inpatient admission.",
            "source_id":      "ACOG-CO-757",
        }

    if epds_total >= 13:
        severity = "URGENT"
        label    = "Probable major postpartum depression"
        action   = (
            "Schedule mental-health follow-up within 7 days. Initiate sertraline 25 mg or "
            "discuss therapy options. Diagnostic interview required to confirm."
        )
    elif epds_total >= 10:
        severity = "MONITOR"
        label    = "Possible postpartum depression"
        action   = (
            "Schedule mental-health follow-up within 14 days. Provide patient education on PPD."
        )
    elif epds_total >= 7:
        severity = "MONITOR"
        label    = "Mild distress"
        action   = (
            "Repeat EPDS at 2 and 6 weeks; provide self-care resources and family support."
        )
    else:
        severity = "OK"
        label    = "No significant depressive symptoms"
        action   = (
            "Routine screening at all postpartum visits per ACOG Committee Opinion 757."
        )

    return {
        "severity":       severity,
        "score":          int(epds_total),
        "label":          label,
        "interpretation": f"EPDS = {epds_total}/30",
        "action":         action,
        "source_id":      "ACOG-CO-757",
    }


def phq9_score_interpretation(phq9_total: int, self_harm_item_present: bool = False) -> dict[str, Any]:
    """Interpret a PHQ-9 total score (0–27) and any positive Item 9 (self-harm).

    Args:
        phq9_total: Total PHQ-9 score (0–27). Pass -1 if not done.
        self_harm_item_present: True if Item 9 was scored > 0.
    """
    if phq9_total is None or phq9_total < 0:
        return {
            "severity":       "UNKNOWN",
            "label":          "Not screened",
            "interpretation": "PHQ-9 not completed.",
            "action":         "Administer PHQ-9 or EPDS at the first postpartum visit per ACOG.",
            "source_id":      "USPSTF-2023-Perinatal",
        }

    if self_harm_item_present:
        return {
            "severity":       "EMERGENCY",
            "label":          "Positive self-harm item (Item 9)",
            "interpretation": "Any positive answer on PHQ-9 Item 9 requires immediate evaluation.",
            "action":         "Immediate mental-health evaluation. Do NOT discharge until safety plan in place.",
            "source_id":      "USPSTF-2023-Perinatal",
        }

    if phq9_total >= 20:
        severity, label = "URGENT",   "Severe depression"
        action = "Mental-health referral within 48h; medication usually indicated."
    elif phq9_total >= 15:
        severity, label = "URGENT",   "Moderately severe depression"
        action = "Initiate treatment (medication + therapy); follow-up in 1 week."
    elif phq9_total >= 10:
        severity, label = "MONITOR",  "Moderate depression"
        action = "Treatment plan with clinician; reassess in 2 weeks."
    elif phq9_total >= 5:
        severity, label = "MONITOR",  "Mild depression"
        action = "Watchful waiting; recheck in 2–4 weeks."
    else:
        severity, label = "OK",       "Minimal symptoms"
        action = "Routine follow-up."

    return {
        "severity":       severity,
        "score":          int(phq9_total),
        "label":          label,
        "interpretation": f"PHQ-9 = {phq9_total}/27",
        "action":         action,
        "source_id":      "USPSTF-2023-Perinatal",
    }
