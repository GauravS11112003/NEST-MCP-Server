"""
Local tool wrappers around Clinical Knowledge MCP datasets.

These are used as fallback when the MCP server isn't reachable, and also
by `adk web` (which doesn't drive an MCP server). They're thin adapters
that call the same underlying functions from `clinical_knowledge_mcp.data`
and `clinical_knowledge_mcp.rxnav_client`.
"""

from __future__ import annotations

import logging
from typing import Any

from google.adk.tools import ToolContext

from clinical_knowledge_mcp.data import (
    calculate_total_acb,
    get_renal_recommendation,
    lookup_beers,
)
from clinical_knowledge_mcp.rxnav_client import check_all_pairs

logger = logging.getLogger(__name__)

SEDATIVE_MEDS = {
    "alprazolam",
    "amitriptyline",
    "clonazepam",
    "diazepam",
    "diphenhydramine",
    "doxepin",
    "hydroxyzine",
    "lorazepam",
    "olanzapine",
    "oxycodone",
    "quetiapine",
    "tramadol",
    "zolpidem",
}
BETA_BLOCKER_MEDS = {"atenolol", "carvedilol", "metoprolol", "propranolol"}
DIURETIC_MEDS = {"furosemide", "hydrochlorothiazide", "torsemide", "bumetanide", "chlorthalidone"}
STIMULANT_MEDS = {"amphetamine", "methylphenidate", "lisdexamfetamine", "pseudoephedrine"}
STEROID_MEDS = {"prednisone", "methylprednisolone", "dexamethasone"}
OPIOID_BENZO_MEDS = {
    "alprazolam",
    "clonazepam",
    "diazepam",
    "hydrocodone",
    "lorazepam",
    "morphine",
    "oxycodone",
    "tramadol",
}


def _numbers(value: Any) -> list[float]:
    """Normalize scalar/list metric values into floats for trend analysis."""
    if value is None:
        return []
    if isinstance(value, (int, float)):
        return [float(value)]
    if not isinstance(value, list):
        return []
    numbers = []
    for item in value:
        try:
            numbers.append(float(item))
        except (TypeError, ValueError):
            continue
    return numbers


def _trend_delta(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    return values[-1] - values[0]


def _percent_change(values: list[float]) -> float:
    if len(values) < 2 or values[0] == 0:
        return 0.0
    return ((values[-1] - values[0]) / values[0]) * 100


def _med_name(medication: Any) -> str:
    if isinstance(medication, str):
        return medication.strip().lower()
    if isinstance(medication, dict):
        for key in ("generic_name", "medication", "name", "display"):
            value = medication.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip().lower()
    return ""


def beers_criteria_lookup(medication: str, tool_context: ToolContext) -> dict[str, Any]:
    """Check whether a single medication is on the AGS Beers Criteria 2023.

    Args:
        medication: Generic medication name (e.g., 'diphenhydramine').

    Returns the Beers entry with rationale, severity, and recommendation,
    or a not_found status.
    """
    logger.info("tool_beers_criteria_lookup medication=%s", medication)
    if not medication:
        return {"status": "error", "error_message": "medication is required"}
    entry = lookup_beers(medication)
    if entry is None:
        return {
            "status": "not_found",
            "medication": medication,
            "message": f"'{medication}' not on curated Beers Criteria 2023 subset.",
        }
    return {"status": "found", "medication": medication, **entry}


def drug_interaction_check(medications: list[str], tool_context: ToolContext) -> dict[str, Any]:
    """Check a list of medications for known drug-drug interactions.

    Args:
        medications: List of generic medication names.

    Returns interactions sorted by severity (HIGH > MODERATE > LOW), with
    mechanism and clinical recommendation for each.
    """
    logger.info("tool_drug_interaction_check meds=%d", len(medications or []))
    if not medications:
        return {"status": "error", "error_message": "medications list is required"}
    if len(medications) < 2:
        return {
            "status": "success",
            "medication_count": len(medications),
            "interactions": [],
            "summary": "Only one medication provided.",
        }
    interactions = check_all_pairs(medications)
    high = sum(1 for i in interactions if i.get("severity") == "HIGH")
    mod = sum(1 for i in interactions if i.get("severity") == "MODERATE")
    return {
        "status": "success",
        "medication_count": len(medications),
        "interactions_found": len(interactions),
        "high_severity_count": high,
        "moderate_severity_count": mod,
        "summary": f"Found {len(interactions)} interactions ({high} HIGH, {mod} MODERATE)",
        "interactions": interactions,
    }


def renal_dose_adjustment(medication: str, egfr: float, tool_context: ToolContext) -> dict[str, Any]:
    """Recommend a dose adjustment for a medication at a given eGFR.

    Args:
        medication: Generic medication name.
        egfr:       eGFR in ml/min/1.73m^2.

    Returns CKD stage and the medication-specific dose recommendation.
    """
    logger.info("tool_renal_dose_adjustment medication=%s egfr=%s", medication, egfr)
    if not medication:
        return {"status": "error", "error_message": "medication is required"}
    if not egfr or egfr <= 0:
        return {"status": "error", "error_message": "valid eGFR (>0) is required"}
    rec = get_renal_recommendation(medication, float(egfr))
    return {"status": "success", **rec}


def anticholinergic_burden(medications: list[str], tool_context: ToolContext) -> dict[str, Any]:
    """Calculate the cumulative Anticholinergic Cognitive Burden (ACB) score.

    Args:
        medications: List of generic medication names.

    Returns total ACB score, risk level, contributing meds, and interpretation.
    """
    logger.info("tool_anticholinergic_burden meds=%d", len(medications or []))
    if not medications:
        return {"status": "error", "error_message": "medications list is required"}
    return {
        "status": "success",
        "medication_count": len(medications),
        **calculate_total_acb(medications),
    }


def analyze_wearable_trends(payload: dict[str, Any], tool_context: ToolContext) -> dict[str, Any]:
    """Detect clinically relevant trend signals from smartwatch-style data.

    Args:
        payload: Dictionary containing wearable metrics. Supported keys include
            resting_hr, steps, sleep_hours, spo2_min, hrv_ms, falls, dizziness,
            and med_changes. Values may be scalars or day-ordered arrays.

    Returns deterministic signal flags with severity, rationale, and triage notes.
    """
    logger.info("tool_analyze_wearable_trends keys=%s", sorted((payload or {}).keys()))
    if not payload:
        return {
            "status": "missing",
            "message": "No wearable payload supplied. Ask the caller for smartwatch trend JSON.",
            "signals": [],
            "overall_severity": "NONE",
        }

    resting_hr = _numbers(payload.get("resting_hr") or payload.get("resting_heart_rate"))
    steps = _numbers(payload.get("steps") or payload.get("daily_steps"))
    sleep_hours = _numbers(payload.get("sleep_hours") or payload.get("sleep_duration_hours"))
    spo2_min = _numbers(payload.get("spo2_min") or payload.get("night_spo2_min"))
    hrv_ms = _numbers(payload.get("hrv_ms") or payload.get("hrv"))
    falls = int(payload.get("falls") or payload.get("fall_events") or 0)
    dizziness = bool(payload.get("dizziness") or payload.get("near_syncope"))

    signals: list[dict[str, Any]] = []

    hr_delta = _trend_delta(resting_hr)
    if hr_delta >= 10 or (resting_hr and resting_hr[-1] >= 100):
        signals.append({
            "id": "rising_resting_hr",
            "severity": "MODERATE",
            "finding": f"Resting heart rate increased by {hr_delta:.0f} bpm.",
            "interpretation": "May reflect dehydration, infection, pain, stimulant effect, steroid effect, or withdrawal.",
        })
    if resting_hr and resting_hr[-1] < 50:
        signals.append({
            "id": "bradycardia",
            "severity": "HIGH" if dizziness or falls else "MODERATE",
            "finding": f"Latest resting heart rate is {resting_hr[-1]:.0f} bpm.",
            "interpretation": "Can be medication-related, especially with beta blockers or rate-control drugs.",
        })

    step_change = _percent_change(steps)
    if len(steps) >= 2 and step_change <= -35:
        signals.append({
            "id": "activity_collapse",
            "severity": "MODERATE",
            "finding": f"Daily steps changed {step_change:.0f}% from baseline.",
            "interpretation": "Functional decline signal; check sedation, dizziness, dyspnea, pain, or acute illness.",
        })

    sleep_delta = _trend_delta(sleep_hours)
    if len(sleep_hours) >= 2 and (sleep_delta <= -1.5 or sleep_hours[-1] < 5):
        signals.append({
            "id": "sleep_disruption",
            "severity": "MODERATE",
            "finding": f"Sleep decreased by {abs(sleep_delta):.1f} hours from baseline.",
            "interpretation": "May be worsened by stimulants, steroids, nocturia from diuretics, pain, or OTC sleep aids.",
        })

    if spo2_min and min(spo2_min[-3:] or spo2_min) < 90:
        signals.append({
            "id": "low_night_spo2",
            "severity": "HIGH",
            "finding": f"Nighttime SpO2 minimum reached {min(spo2_min):.0f}%.",
            "interpretation": "Potential respiratory safety signal; review sedatives, opioids, benzodiazepines, and cardiopulmonary symptoms.",
        })
    elif spo2_min and min(spo2_min[-3:] or spo2_min) <= 92:
        signals.append({
            "id": "borderline_night_spo2",
            "severity": "MODERATE",
            "finding": f"Nighttime SpO2 minimum reached {min(spo2_min):.0f}%.",
            "interpretation": "Consider sleep-disordered breathing, respiratory illness, heart failure, or sedating medications.",
        })

    hrv_change = _percent_change(hrv_ms)
    if len(hrv_ms) >= 2 and hrv_change <= -25:
        signals.append({
            "id": "hrv_drop",
            "severity": "LOW",
            "finding": f"HRV changed {hrv_change:.0f}% from baseline.",
            "interpretation": "Nonspecific strain signal; interpret with symptoms and medication changes.",
        })

    if falls > 0:
        signals.append({
            "id": "fall_event",
            "severity": "HIGH",
            "finding": f"Wearable reported {falls} fall event(s).",
            "interpretation": "Review sedatives, anticholinergics, antihypertensives, hypoglycemics, and orthostasis risk.",
        })
    if dizziness:
        signals.append({
            "id": "dizziness",
            "severity": "MODERATE",
            "finding": "Dizziness or near-syncope was reported with wearable review.",
            "interpretation": "Check blood pressure, hydration, heart rate, glucose risk, and recent medication changes.",
        })

    severity_rank = {"NONE": 0, "LOW": 1, "MODERATE": 2, "HIGH": 3}
    overall = "NONE"
    for signal in signals:
        if severity_rank[signal["severity"]] > severity_rank[overall]:
            overall = signal["severity"]

    return {
        "status": "success",
        "overall_severity": overall,
        "signals_found": len(signals),
        "signals": signals,
        "med_changes": payload.get("med_changes") or payload.get("medication_changes") or [],
        "safety_note": (
            "Wearable data is a physiologic signal, not proof of medication causation. "
            "Correlate with symptoms, vitals, and clinician review."
        ),
    }


def map_wearable_medication_risks(
    medications: list[Any],
    wearable_findings: dict[str, Any],
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Map wearable signals to medication classes that can plausibly contribute."""
    logger.info("tool_map_wearable_medication_risks meds=%d", len(medications or []))
    if not medications:
        return {"status": "error", "error_message": "medications list is required"}
    if not wearable_findings or wearable_findings.get("status") == "missing":
        return {
            "status": "missing_wearable_findings",
            "message": "Run analyze_wearable_trends before mapping medication risks.",
            "medication_risks": [],
        }

    signal_ids = {signal.get("id") for signal in wearable_findings.get("signals", [])}
    med_names = [_med_name(med) for med in medications]
    med_names = [name for name in med_names if name]
    risks: list[dict[str, Any]] = []

    def add_if_present(med_set: set[str], verdict: str, reason: str, linked_signals: set[str]) -> None:
        matched_signals = sorted(signal_ids.intersection(linked_signals))
        if not matched_signals:
            return
        for med in med_names:
            if any(term in med for term in med_set):
                risks.append({
                    "medication": med,
                    "verdict": verdict,
                    "reason": reason,
                    "linked_signals": matched_signals,
                })

    add_if_present(
        SEDATIVE_MEDS,
        "⚠️ SUBSTITUTE",
        "Sedation/fall/sleep signal",
        {"activity_collapse", "sleep_disruption", "fall_event", "low_night_spo2", "borderline_night_spo2"},
    )
    add_if_present(
        OPIOID_BENZO_MEDS,
        "🛑 STOP",
        "Respiratory/fall risk signal",
        {"low_night_spo2", "fall_event"},
    )
    add_if_present(
        BETA_BLOCKER_MEDS,
        "⚠️ MONITOR",
        "Bradycardia/dizziness signal",
        {"bradycardia", "dizziness", "fall_event"},
    )
    add_if_present(
        DIURETIC_MEDS,
        "⚠️ MONITOR",
        "Tachycardia/dehydration signal",
        {"rising_resting_hr", "dizziness", "activity_collapse"},
    )
    add_if_present(
        STIMULANT_MEDS,
        "⚠️ MONITOR",
        "HR/sleep disruption signal",
        {"rising_resting_hr", "sleep_disruption"},
    )
    add_if_present(
        STEROID_MEDS,
        "⚠️ MONITOR",
        "HR/sleep disruption signal",
        {"rising_resting_hr", "sleep_disruption"},
    )

    seen: set[tuple[str, str, str]] = set()
    unique_risks = []
    for risk in risks:
        key = (risk["medication"], risk["verdict"], risk["reason"])
        if key not in seen:
            seen.add(key)
            unique_risks.append(risk)

    return {
        "status": "success",
        "medication_count": len(med_names),
        "signals_considered": sorted(signal_ids),
        "risks_found": len(unique_risks),
        "medication_risks": unique_risks,
        "triage_triggers": [
            "Chest pain, severe shortness of breath, confusion, syncope, or SpO2 persistently <90% warrants urgent evaluation.",
            "New fall, severe dizziness, or very low heart rate should prompt same-day clinician review.",
        ],
    }
