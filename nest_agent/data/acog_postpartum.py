"""
ACOG postpartum care knowledge base.

Sources:
  • ACOG Committee Opinion 736 — Optimizing Postpartum Care (2018, reaffirmed 2021).
    https://www.acog.org/clinical/clinical-guidance/committee-opinion/articles/2018/05/optimizing-postpartum-care
  • ACOG Practice Bulletin 222 — Gestational Hypertension and Preeclampsia (2020).
  • ACOG Postpartum Hemorrhage Practice Bulletin 183 (2017, reaffirmed 2024).
  • Hypertensive Disorders of Pregnancy management guidance.
  • CDC "Hear Her" maternal warning signs.

This is a curated subset for hackathon demonstration. Production deployments
should replace these with the full ACOG / CDC / ACNM datasets and keep them
versioned.
"""

from __future__ import annotations

from typing import Any


# ── ACOG postpartum visit schedule ──────────────────────────────────────────
# Each entry: (window_start_day, window_end_day, label, indication, source_id)

POSTPARTUM_VISIT_SCHEDULE_STANDARD = [
    (3,  7,  "Initial postpartum contact",      "All postpartum patients — phone, in-person, or virtual within 1 week",                "ACOG-CO-736-A"),
    (14, 21, "Initial follow-up visit",         "All postpartum patients — first comprehensive check by 3 weeks",                       "ACOG-CO-736-B"),
    (40, 84, "Comprehensive postpartum visit",  "All postpartum patients — final visit by 12 weeks",                                    "ACOG-CO-736-C"),
]

POSTPARTUM_VISIT_SCHEDULE_HYPERTENSIVE = [
    (3,  10, "Early BP check",                  "Hypertensive disorders — BP measurement within 7–10 days; sooner if symptomatic",     "ACOG-PB-222-A"),
    (14, 21, "Initial follow-up visit",         "Comprehensive maternal review by 3 weeks",                                             "ACOG-CO-736-B"),
    (40, 84, "Comprehensive postpartum visit",  "Final 12-week visit",                                                                  "ACOG-CO-736-C"),
]

POSTPARTUM_VISIT_SCHEDULE_HEMORRHAGE = [
    (1,  7,  "Bleeding & anemia check",         "Postpartum hemorrhage — assess H&H, fundal tone, lochia within 1 week",                "ACOG-PB-183-A"),
    (14, 21, "Initial follow-up visit",         "Comprehensive maternal review by 3 weeks",                                             "ACOG-CO-736-B"),
    (40, 84, "Comprehensive postpartum visit",  "Final 12-week visit",                                                                  "ACOG-CO-736-C"),
]


# ── Postpartum BP thresholds (preeclampsia / postpartum hypertension) ───────
# Per ACOG PB 222 + AHA / NHBPEP definitions.

BP_BANDS_POSTPARTUM = [
    # (sys_low, sys_high, dia_low, dia_high, label, severity, action, source_id)
    (None, 120, None, 80,  "Normal",                          "OK",       "Routine follow-up.",                                                      "ACOG-PB-222-N"),
    (120,  140, 80,   90,  "Elevated / Stage 1",              "MONITOR",  "Recheck in 24h. Counsel on warning signs. Schedule 7–10 day BP visit.",   "ACOG-PB-222-S1"),
    (140,  160, 90,   110, "Stage 2 / Postpartum hypertension", "URGENT", "Recheck within 1 hour. Notify clinician. Consider antihypertensive.",     "ACOG-PB-222-S2"),
    (160,  None, 110, None, "Severe range — preeclampsia/HELLP risk", "EMERGENCY", "EMERGENCY. Send to L&D / ED for IV antihypertensive within 60 minutes per ACOG. Do not wait for symptoms.", "ACOG-PB-222-SEV"),
]


# ── Postpartum red flags (CDC Hear Her + ACOG urgent maternal warning signs) ──

POSTPARTUM_RED_FLAGS = [
    {"id": "PP-RF-01",  "name": "Severe headache not relieved by acetaminophen", "severity": "EMERGENCY", "interpretation": "Possible preeclampsia / cerebral venous thrombosis.",                  "source_id": "CDC-HearHer-1"},
    {"id": "PP-RF-02",  "name": "Vision changes (blurring, scotomata, photophobia)", "severity": "EMERGENCY", "interpretation": "Possible preeclampsia.",                                              "source_id": "CDC-HearHer-2"},
    {"id": "PP-RF-03",  "name": "BP ≥ 160/110 mmHg", "severity": "EMERGENCY", "interpretation": "Severe-range hypertension; preeclampsia treatment required within 60 min.",                            "source_id": "ACOG-PB-222-SEV"},
    {"id": "PP-RF-04",  "name": "Heavy vaginal bleeding (>1 pad/hour, or passing clots > golf ball)", "severity": "EMERGENCY", "interpretation": "Possible postpartum hemorrhage / retained tissue.",   "source_id": "ACOG-PB-183-RF"},
    {"id": "PP-RF-05",  "name": "Chest pain, severe shortness of breath, palpitations", "severity": "EMERGENCY", "interpretation": "Possible cardiomyopathy / PE / MI.",                                "source_id": "CDC-HearHer-5"},
    {"id": "PP-RF-06",  "name": "Calf pain, swelling, redness — especially unilateral", "severity": "URGENT", "interpretation": "Possible DVT.",                                                        "source_id": "CDC-HearHer-6"},
    {"id": "PP-RF-07",  "name": "Fever ≥ 38.0 °C (100.4 °F)", "severity": "URGENT", "interpretation": "Possible endometritis, mastitis, wound infection, septic thrombophlebitis.",                    "source_id": "CDC-HearHer-7"},
    {"id": "PP-RF-08",  "name": "Severe abdominal or perineal pain", "severity": "URGENT", "interpretation": "Possible wound dehiscence, hematoma, retained products.",                                "source_id": "CDC-HearHer-8"},
    {"id": "PP-RF-09",  "name": "Foul-smelling lochia", "severity": "URGENT", "interpretation": "Possible endometritis.",                                                                              "source_id": "CDC-HearHer-9"},
    {"id": "PP-RF-10",  "name": "Thoughts of harming self or baby; suicidal ideation", "severity": "EMERGENCY", "interpretation": "Postpartum mental health emergency. Do NOT delay.",                  "source_id": "CDC-HearHer-10"},
    {"id": "PP-RF-11",  "name": "Persistent sadness or hopelessness lasting > 2 weeks", "severity": "URGENT", "interpretation": "Possible postpartum depression — escalate to mental health.",         "source_id": "ACOG-CO-757"},
    {"id": "PP-RF-12",  "name": "Painful, swollen, red breasts with fever", "severity": "URGENT", "interpretation": "Possible mastitis / abscess.",                                                     "source_id": "ABM-Mastitis-2022"},
    {"id": "PP-RF-13",  "name": "Inability to keep down food / severe dehydration", "severity": "URGENT", "interpretation": "Possible HELLP, infection, postpartum hyperemesis.",                       "source_id": "CDC-HearHer-13"},
    {"id": "PP-RF-14",  "name": "Confusion, difficulty waking, severe lethargy", "severity": "EMERGENCY", "interpretation": "Possible eclampsia, postpartum stroke, sepsis, severe anemia.",            "source_id": "CDC-HearHer-14"},
]


def acog_postpartum_visits(
    delivery_date: str,
    has_hypertensive_disorder: bool,
    has_postpartum_hemorrhage: bool,
) -> dict[str, Any]:
    """Return the ACOG-recommended postpartum visit schedule for this patient.

    Picks the schedule based on documented risk factors:
      • hypertensive disorder (preeclampsia, gestational HTN, chronic HTN)
        → adds an early BP check at 7–10 days
      • postpartum hemorrhage
        → adds a 7-day bleeding & anemia check
      • otherwise → standard schedule (initial contact within 1 week,
        comprehensive visit by 3 weeks, final visit by 12 weeks)
    """
    if has_hypertensive_disorder:
        schedule = POSTPARTUM_VISIT_SCHEDULE_HYPERTENSIVE
        track = "hypertensive"
    elif has_postpartum_hemorrhage:
        schedule = POSTPARTUM_VISIT_SCHEDULE_HEMORRHAGE
        track = "hemorrhage"
    else:
        schedule = POSTPARTUM_VISIT_SCHEDULE_STANDARD
        track = "standard"

    return {
        "track":          track,
        "delivery_date":  delivery_date,
        "visits": [
            {
                "window_start_day": s,
                "window_end_day":   e,
                "label":            label,
                "indication":       reason,
                "source_id":        src,
            }
            for s, e, label, reason, src in schedule
        ],
        "note": (
            "ACOG advises a continuum of postpartum care, not a single 6-week visit. "
            "The first contact should occur within 3 weeks (within 7–10 days for hypertensive "
            "patients), with a comprehensive visit by 12 weeks. [ACOG Committee Opinion 736]"
        ),
    }


def bp_postpartum_assessment(systolic: float, diastolic: float) -> dict[str, Any]:
    """Classify a postpartum BP reading and return action guidance.

    Uses the worse of systolic / diastolic to determine the band (one or the
    other crossing a threshold escalates the entire reading).
    """
    if not systolic or systolic <= 0 or not diastolic or diastolic <= 0:
        return {
            "label":        "No reading available",
            "severity":     "UNKNOWN",
            "action":       "Obtain a postpartum BP reading; required by ACOG within 7–10 days for hypertensive patients.",
            "source_id":    "ACOG-PB-222-A",
        }

    chosen = None
    for sys_low, sys_high, dia_low, dia_high, label, severity, action, source_id in BP_BANDS_POSTPARTUM:
        sys_match = (sys_low is None or systolic >= sys_low) and (sys_high is None or systolic < sys_high)
        dia_match = (dia_low is None or diastolic >= dia_low) and (dia_high is None or diastolic < dia_high)
        if sys_match or dia_match:
            chosen = (label, severity, action, source_id)

    label, severity, action, source_id = chosen if chosen else ("Out of curated bands", "UNKNOWN", "Reassess.", "ACOG-PB-222-N")
    return {
        "systolic":  float(systolic),
        "diastolic": float(diastolic),
        "label":     label,
        "severity":  severity,
        "action":    action,
        "source_id": source_id,
    }


def postpartum_red_flag_panel() -> list[dict[str, Any]]:
    """Return the full curated postpartum red-flag panel."""
    return list(POSTPARTUM_RED_FLAGS)
