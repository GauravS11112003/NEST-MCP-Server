"""
Social Determinants of Health (SDOH) screening summary.

Sources:
  • CMS / AHC HRSN Screening Tool (Accountable Health Communities Health-
    Related Social Needs Tool, 2017). https://innovation.cms.gov/files/worksheets/ahcm-screeningtool.pdf
  • Hunger Vital Sign — Hager ER et al. Pediatrics. 2010;126:e26-e32.
  • AAP Bright Futures social-needs screening recommendations.

We treat each SDOH concern as a structured signal that drives a specific
follow-up task with a clear owner. The Social Worker specialist is the
default owner; specific tasks may be reassigned (e.g., transportation
assistance to care management).
"""

from __future__ import annotations

from typing import Any


# Each entry maps a free-text concern keyword set to a structured intervention.
_SDOH_LIBRARY: list[dict[str, Any]] = [
    {
        "id":       "SDOH-FOOD",
        "keywords": ["food", "hunger", "wic", "snap", "meals"],
        "domain":   "Food security",
        "severity": "URGENT",
        "intervention": "Refer to WIC; place same-day SNAP application support; provide local food bank list; lactation needs ↑ caloric requirement.",
        "source_id": "CMS-AHC-HRSN",
    },
    {
        "id":       "SDOH-HOUSING",
        "keywords": ["housing", "homeless", "shelter", "eviction", "unsafe"],
        "domain":   "Housing instability",
        "severity": "URGENT",
        "intervention": "Care-management referral. Identify safe place for postpartum recovery before discharge. Connect to local homelessness coalition.",
        "source_id": "CMS-AHC-HRSN",
    },
    {
        "id":       "SDOH-TRANSPORT",
        "keywords": ["transportation", "car", "rides", "no car"],
        "domain":   "Transportation barrier",
        "severity": "URGENT",
        "intervention": "Arrange Medicaid NEMT / rideshare voucher for follow-up appointments. Schedule home visits where possible.",
        "source_id": "CMS-AHC-HRSN",
    },
    {
        "id":       "SDOH-SUPPORT",
        "keywords": ["alone", "lives alone", "isolated", "no support", "single mom"],
        "domain":   "Social support",
        "severity": "MONITOR",
        "intervention": "Mobilize community doula, lactation peer counselor, family/visitor schedule. Postpartum peer-support group referral.",
        "source_id": "ACOG-CO-757",
    },
    {
        "id":       "SDOH-IPV",
        "keywords": ["abuse", "domestic violence", "ipv", "unsafe partner"],
        "domain":   "Intimate partner violence",
        "severity": "EMERGENCY",
        "intervention": "Immediate social-work consultation. Provide safety plan. Connect to local DV agency / hotline (1-800-799-7233). Confidential follow-up plan.",
        "source_id": "USPSTF-IPV-2018",
    },
    {
        "id":       "SDOH-CHILDCARE",
        "keywords": ["childcare", "older children", "daycare"],
        "domain":   "Childcare for older children",
        "severity": "MONITOR",
        "intervention": "Connect to childcare resource & referral agency; assess emergency family support during recovery.",
        "source_id": "AAP-BF-Family",
    },
    {
        "id":       "SDOH-INSURANCE",
        "keywords": [
            "insurance", "uninsured", "no coverage",
            "medicaid", "coverage gap", "extension pending", "coverage pending",
        ],
        "domain":   "Insurance / coverage gap",
        "severity": "URGENT",
        "intervention": "Enroll in postpartum Medicaid extension (now 12 months in most states). Verify infant Medicaid enrollment.",
        "source_id": "CMS-PostpartumCoverage-2022",
    },
    {
        "id":       "SDOH-LANGUAGE",
        "keywords": ["language", "limited english", "interpreter"],
        "domain":   "Language barrier",
        "severity": "MONITOR",
        "intervention": "Arrange certified medical interpreter for all follow-ups. Translate discharge instructions; do NOT rely on family for medical translation.",
        "source_id": "JointCommission-LEP",
    },
    {
        "id":       "SDOH-MENTALHEALTH-ACCESS",
        "keywords": ["no therapist", "rural", "mental health", "psychiatrist"],
        "domain":   "Mental-health access gap",
        "severity": "URGENT",
        "intervention": "Telepsychiatry referral; warm-handoff to perinatal mental health collaborative care; provide PSI helpline (1-800-944-4773).",
        "source_id": "ACOG-CO-757",
    },
]


def sdoh_screen_summary(concerns: list[str]) -> dict[str, Any]:
    """Map free-text SDOH concerns to structured interventions with audit IDs.

    Each concern string is matched against the curated keyword library. A
    concern that matches no library entry still produces a generic finding
    so it can be flagged for the social worker to investigate manually.
    """
    findings: list[dict[str, Any]] = []
    seen_ids: set[str] = set()

    for raw in concerns or []:
        concern = (raw or "").strip().lower()
        if not concern:
            continue
        matched = False
        for entry in _SDOH_LIBRARY:
            if any(kw in concern for kw in entry["keywords"]):
                if entry["id"] in seen_ids:
                    matched = True
                    break
                seen_ids.add(entry["id"])
                findings.append({
                    "id":            entry["id"],
                    "domain":        entry["domain"],
                    "severity":      entry["severity"],
                    "raw_concern":   raw,
                    "intervention":  entry["intervention"],
                    "source_id":     entry["source_id"],
                })
                matched = True
                break
        if not matched:
            findings.append({
                "id":            "SDOH-OTHER",
                "domain":        "Other social need",
                "severity":      "MONITOR",
                "raw_concern":   raw,
                "intervention":  "Social-work consultation; complete CMS AHC HRSN tool to characterize.",
                "source_id":     "CMS-AHC-HRSN",
            })

    severity_rank = {"OK": 0, "MONITOR": 1, "URGENT": 2, "EMERGENCY": 3}
    overall = "OK"
    for f in findings:
        if severity_rank.get(f["severity"], 0) > severity_rank.get(overall, 0):
            overall = f["severity"]

    return {
        "concern_count":  len(findings),
        "overall_severity": overall,
        "findings":       findings,
    }
