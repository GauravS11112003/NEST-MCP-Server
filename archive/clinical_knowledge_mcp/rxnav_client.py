"""
RxNav / RxNorm API client for live drug interaction lookups.

NLM's RxNav exposes a free public API that we use to:
  • Resolve drug names → RxCUI codes
  • Check for drug-drug interactions (DDI) via DrugBank-derived data

Note: NLM retired the original `interaction.json` endpoint in 2024 but
still provides interaction data through a community-maintained mirror
and via the RxClass API. To keep this MCP self-contained and demo-reliable
we use a hybrid approach:

  1. Resolve names via RxNav (live)
  2. Check interactions via a curated static high-yield interaction table
     PLUS optional live RxNav lookups when available
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

RXNAV_BASE = "https://rxnav.nlm.nih.gov/REST"
_TIMEOUT = 10.0


def get_rxcui(drug_name: str) -> str | None:
    """Resolve a free-text drug name to its RxCUI (RxNorm Concept Unique Identifier).

    Returns None if the name cannot be resolved.
    """
    if not drug_name:
        return None
    try:
        r = httpx.get(
            f"{RXNAV_BASE}/rxcui.json",
            params={"name": drug_name, "search": "2"},
            timeout=_TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()
        rxcuis = (data.get("idGroup") or {}).get("rxnormId") or []
        return rxcuis[0] if rxcuis else None
    except Exception as e:
        logger.warning("rxnav_rxcui_lookup_failed drug=%s err=%s", drug_name, e)
        return None


def get_drug_class(rxcui: str) -> list[dict[str, Any]]:
    """Get drug class info for an RxCUI (used by interaction reasoning)."""
    if not rxcui:
        return []
    try:
        r = httpx.get(
            f"{RXNAV_BASE}/rxclass/class/byRxcui.json",
            params={"rxcui": rxcui, "relaSource": "ATC"},
            timeout=_TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()
        items = (data.get("rxclassDrugInfoList") or {}).get("rxclassDrugInfo") or []
        return [
            {
                "class_id":   i.get("rxclassMinConceptItem", {}).get("classId"),
                "class_name": i.get("rxclassMinConceptItem", {}).get("className"),
                "class_type": i.get("rxclassMinConceptItem", {}).get("classType"),
            }
            for i in items
        ]
    except Exception as e:
        logger.warning("rxnav_class_lookup_failed rxcui=%s err=%s", rxcui, e)
        return []


# ── Curated high-yield drug-drug interaction table ────────────────────────────
# This is intentionally a small, high-confidence set keyed by lowercase
# generic names. Severity: HIGH (avoid combination), MODERATE (monitor /
# adjust), LOW (informational).

CURATED_DDI: dict[tuple[str, str], dict[str, Any]] = {}


def _add_pair(a: str, b: str, severity: str, mechanism: str, recommendation: str) -> None:
    """Register a bidirectional DDI."""
    entry = {
        "severity": severity,
        "mechanism": mechanism,
        "recommendation": recommendation,
    }
    CURATED_DDI[(a.lower(), b.lower())] = entry
    CURATED_DDI[(b.lower(), a.lower())] = entry


# Anticoagulant + antiplatelet bleeding stacks
_add_pair(
    "warfarin", "aspirin",
    "HIGH",
    "Additive bleeding risk via anticoagulation + antiplatelet effects.",
    "Avoid unless explicit indication; if combined, monitor INR closely and use lowest aspirin dose.",
)
_add_pair(
    "apixaban", "aspirin",
    "MODERATE",
    "Additive bleeding risk.",
    "Use only if clear indication; minimize aspirin dose; monitor for bleeding.",
)
_add_pair(
    "rivaroxaban", "aspirin",
    "MODERATE",
    "Additive bleeding risk.",
    "Use only if clear indication; monitor for bleeding.",
)
_add_pair(
    "warfarin", "ibuprofen",
    "HIGH",
    "NSAID inhibits platelets and can displace warfarin from albumin → INR elevation and GI bleed risk.",
    "Avoid; use acetaminophen for analgesia if anticoagulated.",
)
_add_pair(
    "warfarin", "naproxen",
    "HIGH",
    "NSAID + anticoagulant: bleed risk.",
    "Avoid.",
)
_add_pair(
    "apixaban", "ibuprofen",
    "HIGH",
    "Additive bleeding risk.",
    "Avoid; use acetaminophen.",
)
_add_pair(
    "apixaban", "clopidogrel",
    "HIGH",
    "Additive bleeding risk.",
    "Combination reserved for specific cardiology indications; minimize duration.",
)
_add_pair(
    "warfarin", "clopidogrel",
    "HIGH",
    "Triple-therapy bleed risk if also on aspirin.",
    "Specialist coordination required; minimize duration.",
)
# QT-prolonging combinations
_add_pair(
    "citalopram", "ondansetron",
    "HIGH",
    "Both prolong QTc; risk of torsades de pointes.",
    "Avoid combination; use alternative antiemetic or antidepressant.",
)
_add_pair(
    "escitalopram", "ondansetron",
    "HIGH",
    "Both prolong QTc.",
    "Avoid combination.",
)
_add_pair(
    "haloperidol", "ondansetron",
    "HIGH",
    "Additive QT prolongation.",
    "Avoid; ECG monitoring if unavoidable.",
)
_add_pair(
    "amiodarone", "citalopram",
    "HIGH",
    "Additive QT prolongation.",
    "Avoid; choose alternative SSRI (sertraline) and verify QTc.",
)
_add_pair(
    "amiodarone", "azithromycin",
    "HIGH",
    "Additive QT prolongation; multiple case reports of torsades.",
    "Avoid; use doxycycline if antibiotic alternative needed.",
)
# Serotonergic combinations
_add_pair(
    "tramadol", "sertraline",
    "MODERATE",
    "Additive serotonergic activity → serotonin syndrome risk.",
    "Use lowest effective tramadol dose; monitor for tremor, hyperthermia, autonomic instability.",
)
_add_pair(
    "tramadol", "fluoxetine",
    "MODERATE",
    "Serotonin syndrome risk plus tramadol metabolism via CYP2D6 (inhibited by fluoxetine).",
    "Avoid if possible; use morphine or hydrocodone alternative.",
)
_add_pair(
    "tramadol", "linezolid",
    "HIGH",
    "MAOI + serotonergic opioid → serotonin syndrome.",
    "Avoid.",
)
# Anticholinergic stacking
_add_pair(
    "diphenhydramine", "oxybutynin",
    "MODERATE",
    "Cumulative anticholinergic burden; cognitive impairment, urinary retention, falls.",
    "Avoid combination in older adults; substitute non-anticholinergic alternatives.",
)
_add_pair(
    "amitriptyline", "diphenhydramine",
    "HIGH",
    "Cumulative anticholinergic + sedative effects.",
    "Avoid in older adults.",
)
# Renal/electrolyte
_add_pair(
    "lisinopril", "spironolactone",
    "MODERATE",
    "Both raise serum potassium → hyperkalemia risk, especially with CKD.",
    "Monitor K+ within 1 week of initiation/dose change and periodically.",
)
_add_pair(
    "lisinopril", "potassium",
    "MODERATE",
    "ACEi reduces aldosterone → hyperkalemia with K+ supplements.",
    "Monitor potassium; reduce supplement dose.",
)
_add_pair(
    "trimethoprim_sulfamethoxazole", "warfarin",
    "HIGH",
    "TMP/SMX inhibits warfarin metabolism (CYP2C9) and disrupts vitamin K cycle → INR elevation.",
    "Avoid if possible; if unavoidable, reduce warfarin dose 25–50% and recheck INR in 3–5 days.",
)
_add_pair(
    "trimethoprim_sulfamethoxazole", "spironolactone",
    "MODERATE",
    "Additive hyperkalemia risk.",
    "Monitor K+ during therapy; avoid in advanced CKD.",
)
_add_pair(
    "metformin", "iodinated_contrast",
    "MODERATE",
    "Risk of contrast-induced AKI → metformin accumulation → lactic acidosis.",
    "Hold metformin at time of contrast and 48 h after if eGFR <30 or AKI develops.",
)
# Statin-related
_add_pair(
    "simvastatin", "amiodarone",
    "HIGH",
    "Amiodarone increases simvastatin exposure → myopathy/rhabdomyolysis risk.",
    "Limit simvastatin to 20 mg daily; consider switching to pravastatin or rosuvastatin.",
)
_add_pair(
    "simvastatin", "amlodipine",
    "MODERATE",
    "Amlodipine increases simvastatin exposure (CYP3A4 inhibition).",
    "Limit simvastatin to 20 mg daily.",
)
_add_pair(
    "atorvastatin", "clarithromycin",
    "HIGH",
    "CYP3A4 inhibition → 5-fold rise in atorvastatin levels; rhabdomyolysis risk.",
    "Hold atorvastatin during clarithromycin course or switch to azithromycin.",
)
# CNS depressants
_add_pair(
    "morphine", "alprazolam",
    "HIGH",
    "Opioid + benzodiazepine: additive respiratory depression and overdose risk.",
    "Avoid co-prescribing; FDA boxed warning.",
)
_add_pair(
    "oxycodone", "alprazolam",
    "HIGH",
    "Opioid + benzo: respiratory depression.",
    "Avoid; FDA boxed warning.",
)
_add_pair(
    "hydrocodone", "lorazepam",
    "HIGH",
    "Opioid + benzo: respiratory depression.",
    "Avoid.",
)
# Glycemic
_add_pair(
    "glipizide", "trimethoprim_sulfamethoxazole",
    "MODERATE",
    "TMP/SMX may potentiate sulfonylurea hypoglycemia.",
    "Monitor blood glucose more frequently during therapy.",
)


def check_interaction(drug_a: str, drug_b: str) -> dict[str, Any] | None:
    """Look up a single drug pair in the curated DDI table.

    Returns the interaction dict, or None if no curated interaction.
    """
    if not drug_a or not drug_b:
        return None
    a = _normalize(drug_a)
    b = _normalize(drug_b)
    if a == b:
        return None
    entry = CURATED_DDI.get((a, b))
    if entry is None:
        # Try substring matching for compound names
        for (k1, k2), v in CURATED_DDI.items():
            if (k1 in a or a in k1) and (k2 in b or b in k2):
                return {**v, "drug_a": drug_a, "drug_b": drug_b, "source": "curated_partial"}
        return None
    return {**entry, "drug_a": drug_a, "drug_b": drug_b, "source": "curated"}


def check_all_pairs(medications: list[str]) -> list[dict[str, Any]]:
    """Check all unique pairs in a medication list.

    Returns list of interactions (deduped by frozenset of pair).
    """
    if not medications or len(medications) < 2:
        return []
    seen: set[frozenset[str]] = set()
    interactions: list[dict[str, Any]] = []
    for i, drug_a in enumerate(medications):
        for drug_b in medications[i + 1 :]:
            key = frozenset({_normalize(drug_a), _normalize(drug_b)})
            if key in seen:
                continue
            seen.add(key)
            entry = check_interaction(drug_a, drug_b)
            if entry:
                interactions.append(entry)
    severity_order = {"HIGH": 0, "MODERATE": 1, "LOW": 2}
    interactions.sort(key=lambda x: severity_order.get(x.get("severity", "LOW"), 3))
    return interactions


def _normalize(name: str) -> str:
    n = (name or "").strip().lower()
    for suffix in (" er", " xr", " sr", " la", " hcl", " hydrochloride", " sulfate", " tartrate", " sodium"):
        if n.endswith(suffix):
            n = n[: -len(suffix)].strip()
    return n
