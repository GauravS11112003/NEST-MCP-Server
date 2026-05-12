"""
Inline patient context — bypass FHIR for synthetic / demo / sandbox patients.

When the user describes a patient inline in their prompt (e.g., a synthetic
demo patient that does not exist in any FHIR server), the orchestrator agent
calls `set_inline_patient_context` once. The standard FHIR tools then read
this inline data from session state instead of issuing FHIR queries:

  • get_patient_demographics  → returns the inline patient
  • get_active_medications    → returns the inline medication list
  • get_recent_observations   → returns inline eGFR / SCr as observations

This preserves the real FHIR pipeline 100% — only when no FHIR patient is
bound and inline data is provided does the inline path activate.

State keys written:
  inline_patient        dict  patient demographics + body data
  inline_medications    list  list of medication dicts (FHIR-shaped)
  inline_observations   dict  category → list of observation dicts
"""

from __future__ import annotations

import logging
import re
from typing import Any

from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)


_GENERIC_RE = re.compile(r"^[A-Za-z][A-Za-z\-]+")


def _extract_generic_name(med_text: str) -> str:
    """Pull the lowercase generic drug name out of a free-text dose string.

    Examples:
      'Diphenhydramine 50 mg PO QHS'   → 'diphenhydramine'
      'oxybutynin (IR) 5 mg PO TID'    → 'oxybutynin'
      'apixaban 5mg BID'               → 'apixaban'
      'trimethoprim-sulfamethoxazole'  → 'trimethoprim-sulfamethoxazole'
    """
    s = (med_text or "").strip()
    m = _GENERIC_RE.match(s)
    return m.group(0).lower() if m else s.split(" ")[0].lower()


def set_inline_patient_context(
    name: str,
    age: int,
    sex: str,
    medications: list[str],
    egfr: float,
    weight_kg: float,
    serum_creatinine_mg_dl: float,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Bind inline patient data to the council session, bypassing FHIR.

    Use this when the patient is described in the user's prompt and not
    available in the FHIR server (e.g., synthetic demo patients, paper
    records, or any case where FHIR queries return no MedicationRequests).

    After this call, the council's standard FHIR tools — get_patient_demographics,
    get_active_medications, and get_recent_observations — will return this
    inline data instead of querying FHIR.

    Args:
        name: Patient's full name, e.g. "John Hall".
        age: Age in years (integer).
        sex: 'male' / 'female' / 'other'.
        medications: List of medication strings WITH dose/route/frequency,
            e.g. ["diphenhydramine 50 mg PO QHS", "amitriptyline 50 mg PO QHS"].
            Pass an empty list ([]) only if intentionally testing an empty regimen.
        egfr: Most recent eGFR in mL/min/1.73m^2. Use 0 if unknown.
        weight_kg: Body weight in kg. Use 0 if unknown.
        serum_creatinine_mg_dl: Serum creatinine in mg/dL. Use 0 if unknown.

    Returns:
        Confirmation dict with `status='success'`, the bound patient summary,
        and `inline_mode=True`.
    """
    if not name:
        return {"status": "error", "error_message": "name is required"}
    if age is None or age < 0:
        return {"status": "error", "error_message": "age (>=0) is required"}

    inline_meds: list[dict[str, Any]] = []
    for med in medications or []:
        med_text = str(med).strip()
        if not med_text:
            continue
        generic = _extract_generic_name(med_text)
        inline_meds.append({
            "medication":   med_text,
            "generic_name": generic,
            "status":       "active",
            "intent":       "order",
            "dosage":       med_text,
            "authored_on":  None,
            "requester":    "Inline patient summary",
        })

    inline_observations: dict[str, list[dict[str, Any]]] = {"laboratory": [], "vital-signs": []}
    if egfr and egfr > 0:
        inline_observations["laboratory"].append({
            "observation":    "eGFR (CKD-EPI 2021)",
            "value":          float(egfr),
            "unit":           "mL/min/1.73m^2",
            "components":     None,
            "effective_date": None,
            "status":         "final",
            "interpretation": None,
        })
    if serum_creatinine_mg_dl and serum_creatinine_mg_dl > 0:
        inline_observations["laboratory"].append({
            "observation":    "Creatinine [Mass/volume] in Serum or Plasma",
            "value":          float(serum_creatinine_mg_dl),
            "unit":           "mg/dL",
            "components":     None,
            "effective_date": None,
            "status":         "final",
            "interpretation": None,
        })
    if weight_kg and weight_kg > 0:
        inline_observations["vital-signs"].append({
            "observation":    "Body weight",
            "value":          float(weight_kg),
            "unit":           "kg",
            "components":     None,
            "effective_date": None,
            "status":         "final",
            "interpretation": None,
        })

    tool_context.state["inline_patient"] = {
        "name":                   name,
        "age":                    int(age),
        "sex":                    (sex or "").lower(),
        "weight_kg":              float(weight_kg) if weight_kg else None,
        "serum_creatinine_mg_dl": float(serum_creatinine_mg_dl) if serum_creatinine_mg_dl else None,
    }
    tool_context.state["inline_medications"] = inline_meds
    tool_context.state["inline_observations"] = inline_observations
    tool_context.state["inline_egfr"] = float(egfr) if egfr else None

    logger.info(
        "tool_set_inline_patient_context name=%s age=%s sex=%s n_meds=%d egfr=%s weight=%s scr=%s",
        name, age, sex, len(inline_meds), egfr, weight_kg, serum_creatinine_mg_dl,
    )

    return {
        "status":      "success",
        "inline_mode": True,
        "summary":     (
            f"Inline patient context bound: {name}, {age}{(sex or '?')[:1].upper()}, "
            f"{len(inline_meds)} medications, eGFR {egfr if egfr else 'unknown'}."
        ),
        "patient":     tool_context.state["inline_patient"],
        "medication_count": len(inline_meds),
    }
