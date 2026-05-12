"""
American Academy of Pediatrics (AAP) newborn care knowledge base.

Sources:
  • AAP Bright Futures: Guidelines for Health Supervision (4th ed, 2017,
    reaffirmed 2024). Schedule of well-child visits.
  • AAP Clinical Report — Hospital Stay for Healthy Term Newborn Infants
    (2015, reaffirmed 2022). https://doi.org/10.1542/peds.2015-0699
  • AAP Hyperbilirubinemia in the Newborn (2022 update).
    https://doi.org/10.1542/peds.2022-058859
  • AAP Breastfeeding and the Use of Human Milk (2022).
  • CDC Recommended Immunization Schedule (2025).

Curated subset for hackathon demonstration.
"""

from __future__ import annotations

from typing import Any


# ── AAP / Bright Futures well-child visit schedule (newborn period) ─────────

NEWBORN_VISIT_SCHEDULE = [
    # (age_min_days, age_max_days, label, purpose, source_id)
    (1, 5,   "First newborn visit (3–5 days of life)",  "Weight check, jaundice screen, feeding assessment, parent counseling. AAP requires within 48–72 hours after hospital discharge.", "AAP-BF-V1"),
    (10, 21, "1-month visit (catch-up window)",         "Weight, length, head circumference, feeding, sleep, depression screen for parent.",                                              "AAP-BF-V2"),
    (28, 42, "1-month well-child visit",                "Hep B #2 (if not given), comprehensive exam, anticipatory guidance.",                                                            "AAP-BF-V3"),
    (56, 70, "2-month well-child visit",                "DTaP, IPV, Hib, PCV15, RV, Hep B (if not given). Schedule next visit.",                                                          "AAP-BF-V4"),
]

# Newborn nursery medications / prophylaxis (universal in US)
NEWBORN_NURSERY_MEDICATIONS = [
    {"medication": "Vitamin K 1 mg IM × 1",                "indication": "Prophylaxis of vitamin K deficiency bleeding (HDN)", "source_id": "AAP-VitK-2003"},
    {"medication": "Erythromycin ophthalmic 0.5% × 1",     "indication": "Gonococcal ophthalmia neonatorum prophylaxis",      "source_id": "AAP-EryOpht-2018"},
    {"medication": "Hepatitis B vaccine #1, IM × 1",       "indication": "Universal birth-dose Hep B per ACIP",                "source_id": "ACIP-HepB-2018"},
]


# ── Newborn red flags (AAP / Bright Futures + CDC Sick Baby panel) ──────────

NEWBORN_RED_FLAGS = [
    {"id": "NB-RF-01", "name": "Rectal temperature ≥ 38.0 °C (100.4 °F) in first 28 days", "severity": "EMERGENCY", "interpretation": "Neonatal fever — sepsis workup required regardless of appearance.",     "source_id": "AAP-NeonatalFever-2021"},
    {"id": "NB-RF-02", "name": "Persistent rectal temperature < 36.0 °C (96.8 °F)",        "severity": "EMERGENCY", "interpretation": "Hypothermia — possible sepsis or hypoglycemia.",                          "source_id": "AAP-BF-NB"},
    {"id": "NB-RF-03", "name": "Jaundice visible in first 24 hours of life",               "severity": "EMERGENCY", "interpretation": "Pathologic jaundice — assess for hemolysis (ABO/Rh, G6PD).",              "source_id": "AAP-Hyperbili-2022"},
    {"id": "NB-RF-04", "name": "Yellow color extending below the umbilicus",               "severity": "URGENT",   "interpretation": "Likely TSB > phototherapy threshold — measure now.",                      "source_id": "AAP-Hyperbili-2022"},
    {"id": "NB-RF-05", "name": "Respiratory rate > 60 / min sustained, retractions, or grunting", "severity": "EMERGENCY", "interpretation": "Possible sepsis, RDS, congenital heart disease.",                "source_id": "AAP-BF-NB"},
    {"id": "NB-RF-06", "name": "Cyanosis around mouth, nailbeds, or trunk",                "severity": "EMERGENCY", "interpretation": "Possible CCHD, hypoxemia, sepsis.",                                       "source_id": "AAP-CCHD-2011"},
    {"id": "NB-RF-07", "name": "Feeding fewer than 8 times in 24 hours after day 3",       "severity": "URGENT",   "interpretation": "Risk of dehydration, hypoglycemia, hyperbilirubinemia.",                  "source_id": "AAP-BF-NB"},
    {"id": "NB-RF-08", "name": "Fewer than 6 wet diapers / day after day 5",               "severity": "URGENT",   "interpretation": "Possible dehydration / inadequate intake.",                               "source_id": "AAP-BF-NB"},
    {"id": "NB-RF-09", "name": "Weight loss > 10% from birth weight",                      "severity": "URGENT",   "interpretation": "Inadequate intake; reassess feeding plan immediately.",                   "source_id": "AAP-BFM-2022"},
    {"id": "NB-RF-10", "name": "No regain of birth weight by 14 days",                     "severity": "URGENT",   "interpretation": "Failure to thrive workup.",                                               "source_id": "AAP-BFM-2022"},
    {"id": "NB-RF-11", "name": "Inconsolable crying > 2 hours, decreased activity, lethargy", "severity": "URGENT", "interpretation": "Possible sepsis, intussusception, child abuse, NAS.",                    "source_id": "AAP-BF-NB"},
    {"id": "NB-RF-12", "name": "Vomiting (esp. bilious / projectile)",                     "severity": "EMERGENCY", "interpretation": "Possible bowel obstruction, pyloric stenosis (~3 wk onset).",             "source_id": "AAP-BF-NB"},
    {"id": "NB-RF-13", "name": "Seizure-like activity",                                    "severity": "EMERGENCY", "interpretation": "Possible HIE, infection, metabolic, intracranial bleed.",                 "source_id": "AAP-NeoSeizure-2021"},
    {"id": "NB-RF-14", "name": "Umbilical erythema, drainage, or odor",                    "severity": "URGENT",   "interpretation": "Possible omphalitis — high mortality if untreated.",                      "source_id": "AAP-BF-NB"},
]


# ── Bhutani nomogram (simplified) — phototherapy threshold by age ───────────
# Not a replacement for the full nomogram; calibrated for the curated demo.
# In production, use the full table from AAP 2022 (Pediatrics. 2022;150:e2022058859).

# Each entry: (age_hours_max, low_risk_threshold_mg_dL, medium_risk_threshold, high_risk_threshold)
# Risk band depends on GA + isoimmunization / G6PD risk factors.
_BHUTANI_THRESHOLDS = [
    # age_h, low,  med,  high   (mg/dL — phototherapy threshold)
    (24,    8.0,   6.0,  4.0),
    (36,   10.0,   8.0,  6.0),
    (48,   12.0,  10.0,  8.0),
    (72,   15.0,  13.0, 10.0),
    (96,   18.0,  15.0, 13.0),
    (120,  20.0,  17.0, 14.0),
    (144,  21.0,  18.0, 15.0),
    (168,  21.0,  18.0, 15.0),  # ≥ 7 days
]


def bhutani_phototherapy_threshold(
    age_hours: float,
    total_bilirubin_mg_dl: float,
    risk_band: str = "low",
) -> dict[str, Any]:
    """Compare a TSB measurement to the Bhutani phototherapy threshold.

    Args:
        age_hours: Infant age in HOURS at the time of measurement.
        total_bilirubin_mg_dl: Total serum bilirubin in mg/dL.
        risk_band: 'low' (≥38 wk, no risk factors), 'medium' (35–37 6/7 wk
                    or risk factors), 'high' (35–37 6/7 wk + risk factors).

    Returns:
        Decision dict including threshold, severity, action, and source.
    """
    if not age_hours or age_hours <= 0 or not total_bilirubin_mg_dl or total_bilirubin_mg_dl <= 0:
        return {
            "label":     "No bilirubin measurement",
            "severity":  "UNKNOWN",
            "action":    "Obtain transcutaneous or serum bilirubin. AAP recommends universal screening before discharge.",
            "source_id": "AAP-Hyperbili-2022",
        }

    band = (risk_band or "low").strip().lower()
    threshold = None
    for age_h_max, low_t, med_t, high_t in _BHUTANI_THRESHOLDS:
        if age_hours <= age_h_max:
            threshold = {"low": low_t, "medium": med_t, "high": high_t}.get(band, low_t)
            break
    if threshold is None:
        threshold = {"low": 21.0, "medium": 18.0, "high": 15.0}.get(band, 21.0)

    delta = round(total_bilirubin_mg_dl - threshold, 1)

    if total_bilirubin_mg_dl >= threshold:
        severity = "URGENT"
        if total_bilirubin_mg_dl >= threshold + 5:
            severity = "EMERGENCY"
        action = (
            f"TSB {total_bilirubin_mg_dl} ≥ phototherapy threshold {threshold} mg/dL "
            f"(over by {delta}). Initiate phototherapy now; if exchange transfusion threshold "
            "approached, urgent NICU consult."
        )
    elif total_bilirubin_mg_dl >= threshold - 2:
        severity = "MONITOR"
        action = (
            f"TSB {total_bilirubin_mg_dl} is within 2 mg/dL of threshold {threshold}. "
            "Recheck in 4–6 hours; consider lactation support and feeding optimization."
        )
    else:
        severity = "OK"
        action = (
            f"TSB {total_bilirubin_mg_dl} below phototherapy threshold {threshold}. "
            "Continue routine monitoring; recheck per AAP nomogram."
        )

    return {
        "age_hours":             float(age_hours),
        "total_bilirubin_mg_dl": float(total_bilirubin_mg_dl),
        "risk_band":             band,
        "threshold_mg_dl":       threshold,
        "delta_mg_dl":           delta,
        "severity":              severity,
        "action":                action,
        "source_id":             "AAP-Hyperbili-2022",
    }


def feeding_milestone_check(
    feeding_method: str,
    age_days: int,
    weight_loss_pct: float | None,
    feeding_concerns: list[str] | None = None,
) -> dict[str, Any]:
    """Apply AAP feeding milestones to the dyad's current pattern.

    Returns severity + action + source for tracking against AAP Bright Futures
    and ABM (Academy of Breastfeeding Medicine) Protocol #3.
    """
    findings: list[dict[str, Any]] = []
    method = (feeding_method or "").lower()

    if weight_loss_pct is not None and weight_loss_pct > 10:
        findings.append({
            "id":             "FEED-01",
            "severity":       "URGENT",
            "finding":        f"Weight loss {weight_loss_pct}% exceeds 10% of birth weight.",
            "action":         "Lactation consult today. Consider supplementation if < 24h old or evidence of dehydration. Reassess in 24h.",
            "source_id":      "AAP-BFM-2022",
        })
    elif weight_loss_pct is not None and weight_loss_pct > 7:
        findings.append({
            "id":             "FEED-02",
            "severity":       "MONITOR",
            "finding":        f"Weight loss {weight_loss_pct}% — approaching the 10% threshold.",
            "action":         "Closer feeding observation; lactation referral; daily weights until trend reverses.",
            "source_id":      "AAP-BFM-2022",
        })

    if "exclusive-breastfeeding" in method or "breast" in method:
        if age_days >= 5 and (weight_loss_pct is None or weight_loss_pct > 10):
            findings.append({
                "id":        "FEED-03",
                "severity":  "MONITOR",
                "finding":   "Insufficient feeding volume signal in exclusively-breastfed infant.",
                "action":    "Verify ≥8 feeds / 24h, ≥6 wet diapers / day, ≥3 stools / day. Lactation evaluation if any are below.",
                "source_id": "AAP-BFM-2022",
            })

    for concern in feeding_concerns or []:
        findings.append({
            "id":        "FEED-99",
            "severity":  "MONITOR",
            "finding":   f"Caregiver-reported concern: {concern}.",
            "action":    "Lactation / feeding evaluation; address concern before discharge.",
            "source_id": "ABM-Protocol-3",
        })

    if not findings:
        findings.append({
            "id":        "FEED-00",
            "severity":  "OK",
            "finding":   "Feeding pattern within AAP expected range for current day of life.",
            "action":    "Continue current feeding plan; reassess at well-child visit.",
            "source_id": "AAP-BF-NB",
        })

    return {
        "feeding_method":  feeding_method,
        "age_days":        age_days,
        "weight_loss_pct": weight_loss_pct,
        "findings":        findings,
    }


def aap_newborn_visits(infant_age_days: int, hospital_discharge_day: int) -> dict[str, Any]:
    """Return the AAP / Bright Futures newborn visit schedule indexed to discharge."""
    return {
        "infant_age_days":         infant_age_days,
        "hospital_discharge_day":  hospital_discharge_day,
        "visits": [
            {
                "age_min_days":  age_min,
                "age_max_days":  age_max,
                "label":         label,
                "purpose":       purpose,
                "source_id":     src,
            }
            for age_min, age_max, label, purpose, src in NEWBORN_VISIT_SCHEDULE
        ],
        "note": (
            "AAP requires the first newborn visit 48–72 hours after hospital "
            "discharge for breastfeeding term infants. [AAP Bright Futures, 2024]"
        ),
    }


def newborn_red_flag_panel() -> list[dict[str, Any]]:
    """Return the full curated newborn red-flag panel."""
    return list(NEWBORN_RED_FLAGS)
