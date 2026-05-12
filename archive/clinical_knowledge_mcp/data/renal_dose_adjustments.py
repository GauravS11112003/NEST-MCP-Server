"""
Renal dose adjustment recommendations for commonly prescribed drugs.

eGFR thresholds use the CKD-EPI 2021 equation (ml/min/1.73m^2).
Recommendations are simplified summaries from package inserts and
KDIGO guidelines. Always confirm with current prescribing information.
"""

from typing import Any

# Each entry: list of (egfr_min, egfr_max, recommendation)
RENAL_ADJUSTMENTS: dict[str, list[tuple[int | None, int | None, str]]] = {
    # ── Direct Oral Anticoagulants ─────────────────────────────────────────
    "apixaban": [
        (60, None, "Standard dose (5 mg BID for AFib)."),
        (30, 59, "Standard dose; reduce to 2.5 mg BID if 2 of 3: age ≥80, weight ≤60 kg, SCr ≥1.5."),
        (15, 29, "2.5 mg BID for AFib."),
        (None, 14, "Use with caution; limited data. Avoid in dialysis without specialty input."),
    ],
    "rivaroxaban": [
        (50, None, "Standard dose (20 mg daily for AFib)."),
        (15, 49, "15 mg daily for AFib."),
        (None, 14, "Avoid."),
    ],
    "dabigatran": [
        (50, None, "Standard dose (150 mg BID)."),
        (30, 49, "Consider dose reduction (110 mg BID — outside US labeling)."),
        (15, 29, "75 mg BID."),
        (None, 14, "Avoid."),
    ],
    "edoxaban": [
        (50, 95, "60 mg daily."),
        (15, 49, "30 mg daily."),
        (None, 14, "Avoid."),
        (95, None, "Avoid (reduced efficacy)."),
    ],
    "enoxaparin": [
        (30, None, "Standard dose."),
        (None, 29, "Reduce dose by 50% (1 mg/kg daily for treatment, 30 mg daily for prophylaxis)."),
    ],
    # ── Antibiotics ────────────────────────────────────────────────────────
    "ciprofloxacin": [
        (50, None, "Standard dose."),
        (30, 49, "250–500 mg every 12h."),
        (None, 29, "250–500 mg every 18h."),
    ],
    "levofloxacin": [
        (50, None, "Standard dose (500 mg daily)."),
        (20, 49, "500 mg loading then 250 mg every 24h."),
        (10, 19, "500 mg loading then 250 mg every 48h."),
    ],
    "vancomycin": [
        (None, None, "Dose by trough levels and weight; consult pharmacy. Reduce frequency in CKD."),
    ],
    "trimethoprim_sulfamethoxazole": [
        (30, None, "Standard dose."),
        (15, 29, "Reduce dose by 50%."),
        (None, 14, "Avoid (or use 50% dose with close monitoring)."),
    ],
    "nitrofurantoin": [
        (60, None, "Standard dose (100 mg BID)."),
        (None, 59, "Avoid — reduced efficacy and increased toxicity."),
    ],
    "amoxicillin": [
        (30, None, "Standard dose."),
        (10, 29, "Reduce dose or extend interval."),
        (None, 9, "500 mg every 24h."),
    ],
    # ── Diabetes ───────────────────────────────────────────────────────────
    "metformin": [
        (45, None, "Standard dose."),
        (30, 44, "Use with caution; do not initiate. Max 1 g/day."),
        (None, 29, "Contraindicated."),
    ],
    "sitagliptin": [
        (45, None, "100 mg daily."),
        (30, 44, "50 mg daily."),
        (None, 29, "25 mg daily."),
    ],
    "saxagliptin": [
        (45, None, "5 mg daily."),
        (None, 44, "2.5 mg daily."),
    ],
    "empagliflozin": [
        (30, None, "Standard dose."),
        (20, 29, "10 mg daily; not recommended for glycemic control but cardio/renal benefit retained."),
        (None, 19, "Avoid for new initiation."),
    ],
    "dapagliflozin": [
        (45, None, "Standard dose."),
        (25, 44, "Continue if already on therapy."),
        (None, 24, "Avoid initiation."),
    ],
    # ── Cardiovascular ─────────────────────────────────────────────────────
    "digoxin": [
        (50, None, "0.125–0.25 mg daily."),
        (10, 49, "0.0625–0.125 mg daily; check level."),
        (None, 9, "0.0625 mg every 48h or less; monitor closely."),
    ],
    "spironolactone": [
        (60, None, "Standard dose."),
        (30, 59, "Reduce dose; monitor K closely."),
        (None, 29, "Avoid."),
    ],
    "eplerenone": [
        (50, None, "Standard dose."),
        (30, 49, "25 mg daily; monitor K."),
        (None, 29, "Avoid."),
    ],
    # ── Pain ──────────────────────────────────────────────────────────────
    "gabapentin": [
        (60, None, "Standard dose (up to 3600 mg/day in 3 divided doses)."),
        (30, 59, "Max 1400 mg/day."),
        (15, 29, "Max 700 mg/day."),
        (None, 14, "Max 300 mg/day."),
    ],
    "pregabalin": [
        (60, None, "Standard dose."),
        (30, 59, "Reduce dose by 50%."),
        (15, 29, "Reduce dose by 75%."),
        (None, 14, "Reduce dose by 87%; daily single dose."),
    ],
    "morphine": [
        (60, None, "Standard dose."),
        (30, 59, "Use with caution; reduce dose."),
        (None, 29, "Avoid; active metabolites accumulate. Use hydromorphone or fentanyl."),
    ],
    "tramadol": [
        (30, None, "Standard dose."),
        (None, 29, "Max 200 mg/day; extend interval to every 12h."),
    ],
    # ── Other ─────────────────────────────────────────────────────────────
    "allopurinol": [
        (60, None, "Standard dose (300 mg daily)."),
        (30, 59, "Max 200 mg/day."),
        (15, 29, "Max 100 mg/day."),
        (None, 14, "Max 100 mg every other day."),
    ],
    "famotidine": [
        (50, None, "Standard dose."),
        (None, 49, "Reduce dose by 50%."),
    ],
    "ranitidine": [
        (50, None, "Standard dose (off-market in US)."),
        (None, 49, "Reduce dose by 50%."),
    ],
    "lithium": [
        (None, None, "Narrow therapeutic index; reduce dose with any CKD; monitor levels closely."),
    ],
    "atenolol": [
        (35, None, "Standard dose."),
        (15, 34, "Reduce dose by 50%."),
        (None, 14, "Reduce dose by 75%."),
    ],
}


def get_renal_recommendation(medication: str, egfr: float) -> dict[str, Any]:
    """Return renal dose adjustment recommendation for medication at given eGFR.

    Args:
        medication: Generic name (case-insensitive).
        egfr:       eGFR in ml/min/1.73m^2.

    Returns:
        {
          "medication": str,
          "egfr": float,
          "found": bool,
          "recommendation": str,
          "ckd_stage": str,
        }
    """
    if not medication:
        return {"found": False, "error": "No medication provided"}

    key = medication.strip().lower()
    for suffix in (" er", " xr", " sr", " la", " hcl"):
        if key.endswith(suffix):
            key = key[: -len(suffix)].strip()

    matched_key = None
    if key in RENAL_ADJUSTMENTS:
        matched_key = key
    else:
        for k in RENAL_ADJUSTMENTS:
            if k in key or key in k:
                matched_key = k
                break

    ckd_stage = _ckd_stage(egfr)
    if not matched_key:
        return {
            "medication": medication,
            "egfr": egfr,
            "ckd_stage": ckd_stage,
            "found": False,
            "recommendation": (
                f"No renal adjustment data on file for '{medication}'. "
                "Refer to current prescribing information for guidance."
            ),
        }

    bands = RENAL_ADJUSTMENTS[matched_key]
    for low, high, rec in bands:
        if (low is None or egfr >= low) and (high is None or egfr <= high):
            return {
                "medication": medication,
                "matched_drug": matched_key,
                "egfr": egfr,
                "ckd_stage": ckd_stage,
                "found": True,
                "recommendation": rec,
            }

    return {
        "medication": medication,
        "matched_drug": matched_key,
        "egfr": egfr,
        "ckd_stage": ckd_stage,
        "found": True,
        "recommendation": (bands[-1][2] if bands else "No band matched."),
    }


def _ckd_stage(egfr: float) -> str:
    if egfr >= 90:
        return "G1 (normal/high)"
    if egfr >= 60:
        return "G2 (mildly decreased)"
    if egfr >= 45:
        return "G3a (mild-moderate)"
    if egfr >= 30:
        return "G3b (moderate-severe)"
    if egfr >= 15:
        return "G4 (severe)"
    return "G5 (kidney failure)"
