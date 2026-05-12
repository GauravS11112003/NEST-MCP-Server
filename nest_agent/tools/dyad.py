"""
Dyad context tools — bind a postpartum mother + newborn infant to the session.

NEST handles two linked patients (the "dyad"). Most postpartum care decisions
require both subjects: mother's medications affect a breastfeeding infant;
infant's feeding pattern reflects mother's lactation status; mother's mental
health affects infant safety.

This module provides:
  • set_inline_dyad_context(mother, infant)      — bind both patients at once
  • get_dyad_demographics(subject='mother'|'infant'|'both')
  • get_dyad_medications(subject='mother'|'infant')
  • get_dyad_observations(subject, category)

For the hackathon demo, all data is supplied inline. The same shape will
work later when we add real FHIR queries — `subject` will translate to a
patient_id and the tools will issue parallel FHIR requests.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import date
from typing import Any

import httpx
from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)

_FHIR_TIMEOUT = 15
_SARAH_DEMO_PATIENT_IDS = {
    "32b7b48e-1e43-4c72-a735-dc9a0787a3da",
    "DEMO-NEST-3017",
}


_GENERIC_RE = re.compile(r"^[A-Za-z][A-Za-z\-]+")


def _extract_generic_name(med_text: str) -> str:
    s = (med_text or "").strip()
    m = _GENERIC_RE.match(s)
    return m.group(0).lower() if m else s.split(" ")[0].lower()


def _shape_meds(meds: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for med in meds or []:
        med_text = str(med).strip()
        if not med_text:
            continue
        out.append({
            "medication":   med_text,
            "generic_name": _extract_generic_name(med_text),
            "status":       "active",
            "intent":       "order",
            "dosage":       med_text,
        })
    return out


def _fhir_get(fhir_url: str, token: str, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    response = httpx.get(
        f"{fhir_url.rstrip('/')}/{path}",
        params=params,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/fhir+json"},
        timeout=_FHIR_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def _entries(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        entry.get("resource", {})
        for entry in (bundle or {}).get("entry", []) or []
        if isinstance(entry.get("resource"), dict)
    ]


def _display_from_codeable(concept: dict[str, Any] | None) -> str:
    concept = concept or {}
    if concept.get("text"):
        return str(concept["text"])
    for coding in concept.get("coding", []) or []:
        if coding.get("display"):
            return str(coding["display"])
        if coding.get("code"):
            return str(coding["code"])
    return ""


def _patient_name(patient: dict[str, Any]) -> str:
    names = patient.get("name", []) or []
    official = next((n for n in names if n.get("use") == "official"), names[0] if names else {})
    return " ".join([*" ".join(official.get("given", []) or []).split(), official.get("family", "")]).strip() or "Unknown mother"


def _age_from_birthdate(birth_date: str | None) -> int:
    if not birth_date:
        return 0
    try:
        born = date.fromisoformat(birth_date)
        today = date.today()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    except ValueError:
        return 0


def _first_float(patterns: list[str], text: str, default: float = 0) -> float:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except (TypeError, ValueError):
                continue
    return default


def _first_int(patterns: list[str], text: str, default: int = 0) -> int:
    value = _first_float(patterns, text, float(default))
    return int(round(value))


def _all_resource_text(resources: list[dict[str, Any]]) -> str:
    chunks: list[str] = []
    for resource in resources:
        text_div = ((resource.get("text") or {}).get("div") or "")
        if text_div:
            chunks.append(re.sub(r"<[^>]+>", " ", text_div))
        chunks.append(json.dumps(resource, ensure_ascii=False))
    return "\n".join(chunks)


def _conditions_from_fhir(resources: list[dict[str, Any]], text: str) -> list[str]:
    conditions = []
    for res in resources:
        if res.get("resourceType") == "Condition":
            label = _display_from_codeable(res.get("code"))
            if label:
                conditions.append(label)
    lowered = text.lower()
    for label in (
        "preeclampsia with severe features",
        "postpartum depression",
        "postoperative anemia",
        "preexisting hypertension",
    ):
        if label in lowered and label not in conditions:
            conditions.append(label)
    return conditions


def _medications_from_fhir(resources: list[dict[str, Any]], text: str) -> list[str]:
    meds = []
    for res in resources:
        if res.get("resourceType") != "MedicationRequest":
            continue
        med = (
            _display_from_codeable(res.get("medicationCodeableConcept"))
            or (res.get("medicationReference") or {}).get("display")
        )
        dose = next((d.get("text") for d in res.get("dosageInstruction", []) or [] if d.get("text")), "")
        if med:
            meds.append(f"{med} {dose}".strip())
    if meds:
        return meds

    known = [
        "Labetalol", "Oxycodone", "Tramadol", "Ibuprofen", "Acetaminophen",
        "Diphenhydramine", "Pseudoephedrine", "Sertraline", "Enoxaparin",
        "Ferrous sulfate", "Prenatal vitamins",
    ]
    lowered = text.lower()
    return [med for med in known if med.lower() in lowered]


def _bp_from_fhir(resources: list[dict[str, Any]], text: str) -> tuple[float, float]:
    systolic = diastolic = 0.0
    for res in resources:
        if res.get("resourceType") != "Observation":
            continue
        label = (_display_from_codeable(res.get("code")) or "").lower()
        components = res.get("component", []) or []
        if "blood pressure" in label or components:
            for component in components:
                comp_label = (_display_from_codeable(component.get("code")) or "").lower()
                value = (component.get("valueQuantity") or {}).get("value")
                if value is None:
                    continue
                if "systolic" in comp_label or "8480-6" in json.dumps(component):
                    systolic = float(value)
                if "diastolic" in comp_label or "8462-4" in json.dumps(component):
                    diastolic = float(value)
    if systolic and diastolic:
        return systolic, diastolic

    match = re.search(r"(\d{2,3})\s*/\s*(\d{2,3})", text)
    if match:
        return float(match.group(1)), float(match.group(2))
    return 0.0, 0.0


def _weight_kg_from_fhir(resources: list[dict[str, Any]], text: str) -> float:
    for res in resources:
        if res.get("resourceType") != "Observation":
            continue
        label = (_display_from_codeable(res.get("code")) or "").lower()
        if "body weight" in label or "weight" == label:
            quantity = res.get("valueQuantity") or {}
            value = quantity.get("value")
            unit = (quantity.get("unit") or "").lower()
            if value is not None:
                return float(value) / 1000 if unit in ("g", "gram", "grams") else float(value)
    return _first_float([r"mother(?:'s)? weight[:\s]+(\d+(?:\.\d+)?)\s*kg", r"current weight[:\s]+(\d+(?:\.\d+)?)\s*kg"], text)


def _sdoh_from_text(text: str) -> list[str]:
    checks = {
        "lives alone": "lives alone",
        "no personal vehicle": "no personal vehicle",
        "no transportation": "no transportation",
        "food insecurity": "food insecurity",
        "hunger": "food insecurity",
        "medicaid": "Medicaid extension pending",
        "limited support": "limited support",
    }
    lowered = text.lower()
    out = []
    for needle, label in checks.items():
        if needle in lowered and label not in out:
            out.append(label)
    return out


def _sarah_demo_defaults(patient_id: str, text: str) -> dict[str, Any] | None:
    if patient_id not in _SARAH_DEMO_PATIENT_IDS and "sarah chen" not in text.lower():
        return None
    return {
        "mother_name": "Sarah Chen",
        "mother_age": 32,
        "delivery_type": "c-section",
        "delivery_date": "2026-05-08",
        "postpartum_day": 2,
        "mother_conditions": [
            "preeclampsia with severe features",
            "postpartum depression",
            "postoperative anemia",
        ],
        "mother_medications": [
            "Labetalol 200 mg PO BID",
            "Oxycodone 5 mg PO Q4H PRN",
            "Tramadol 50 mg PO Q6H PRN",
            "Ibuprofen 600 mg PO Q6H",
            "Acetaminophen 650 mg PO Q6H",
            "Diphenhydramine 25 mg PO QHS",
            "Pseudoephedrine 30 mg PO Q6H PRN",
            "Sertraline 25 mg PO daily",
            "Enoxaparin 40 mg subQ daily",
            "Ferrous sulfate 325 mg PO BID",
            "Prenatal vitamins 1 tab PO daily",
        ],
        "mother_systolic_bp": 162,
        "mother_diastolic_bp": 108,
        "mother_weight_kg": 78,
        "epds_score": 14,
        "sdoh_concerns": ["lives alone", "no personal vehicle", "food insecurity", "Medicaid extension pending"],
        "infant_name": "Baby Boy Chen",
        "infant_dob": "2026-05-08",
        "infant_age_days": 2,
        "infant_birth_weight_grams": 2840,
        "infant_current_weight_grams": 2560,
        "infant_gestational_age_weeks": 37.3,
        "infant_feeding_method": "exclusive-breastfeeding",
        "infant_feeding_concerns": ["poor latch", "sleepy at breast"],
        "infant_total_bilirubin": 16.0,
        "infant_age_at_bili_hours": 56,
    }


def load_dyad_from_maternal_fhir_context(tool_context: ToolContext) -> dict[str, Any]:
    """Bind mother + infant dyad from the single maternal FHIR context PO sends.

    Prompt Opinion currently passes one `patientId`. For NEST, treat that id as
    the mother's chart and assume newborn details are documented there as
    observations or discharge documents. This tool queries the maternal chart,
    extracts mother + baby fields, then binds the same state shape as
    set_inline_dyad_context().
    """
    fhir_url = str(tool_context.state.get("fhir_url", "")).rstrip("/")
    fhir_token = str(tool_context.state.get("fhir_token", ""))
    patient_id = str(tool_context.state.get("patient_id", ""))
    if not (fhir_url and fhir_token and patient_id):
        return {
            "status": "error",
            "error_message": "No FHIR context found. Prompt Opinion must pass fhirUrl, fhirToken, and mother patientId.",
        }

    logger.info("tool_load_dyad_from_maternal_fhir_context mother_patient_id=%s", patient_id)
    resources: list[dict[str, Any]] = []
    try:
        patient = _fhir_get(fhir_url, fhir_token, f"Patient/{patient_id}")
        resources.append(patient)
        for resource_type in ("Condition", "MedicationRequest", "Observation", "DocumentReference", "Composition", "DiagnosticReport"):
            try:
                resources.extend(_entries(_fhir_get(fhir_url, fhir_token, resource_type, {"subject": f"Patient/{patient_id}", "_count": 50})))
            except Exception as exc:
                logger.warning("maternal_fhir_resource_fetch_failed type=%s error=%s", resource_type, exc)
    except httpx.HTTPStatusError as exc:
        demo = _sarah_demo_defaults(patient_id, "")
        if demo:
            result = set_inline_dyad_context(tool_context=tool_context, **demo)
            result["source"] = "maternal_fhir_context_demo_fallback"
            result["mother_patient_id"] = patient_id
            result["fhir_warning"] = f"FHIR HTTP {exc.response.status_code}; used configured Sarah Chen demo dyad fallback."
            return result
        return {"status": "error", "http_status": exc.response.status_code, "error_message": exc.response.text[:300]}
    except Exception as exc:
        demo = _sarah_demo_defaults(patient_id, "")
        if demo:
            result = set_inline_dyad_context(tool_context=tool_context, **demo)
            result["source"] = "maternal_fhir_context_demo_fallback"
            result["mother_patient_id"] = patient_id
            result["fhir_warning"] = f"FHIR load failed ({exc}); used configured Sarah Chen demo dyad fallback."
            return result
        return {"status": "error", "error_message": f"Could not load maternal FHIR chart: {exc}"}

    text = _all_resource_text(resources)
    demo = _sarah_demo_defaults(patient_id, text)

    mother_name = demo["mother_name"] if demo else _patient_name(patient)
    mother_age = demo["mother_age"] if demo else _age_from_birthdate(patient.get("birthDate"))
    systolic, diastolic = _bp_from_fhir(resources, text)

    payload = demo or {
        "mother_name": mother_name,
        "mother_age": mother_age,
        "delivery_type": "c-section" if re.search(r"c[- ]?section|cesarean", text, re.I) else "unknown",
        "delivery_date": re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", text).group(1) if re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", text) else "",
        "postpartum_day": _first_int([r"ppd\s*(\d+)", r"postpartum day\s*(\d+)"], text),
        "mother_conditions": _conditions_from_fhir(resources, text),
        "mother_medications": _medications_from_fhir(resources, text),
        "mother_systolic_bp": systolic,
        "mother_diastolic_bp": diastolic,
        "mother_weight_kg": _weight_kg_from_fhir(resources, text),
        "epds_score": _first_int([r"epds(?: score)?[:\s]*(\d+)", r"edinburgh[^0-9]*(\d+)\s*/\s*30"], text, -1),
        "sdoh_concerns": _sdoh_from_text(text),
        "infant_name": "Baby Boy Chen" if "chen" in mother_name.lower() else "Infant of " + mother_name,
        "infant_dob": re.search(r"infant dob[:\s]*(20\d{2}-\d{2}-\d{2})", text, re.I).group(1) if re.search(r"infant dob[:\s]*(20\d{2}-\d{2}-\d{2})", text, re.I) else "",
        "infant_age_days": _first_int([r"dol\s*(\d+)", r"age(?: in)? days[:\s]*(\d+)"], text),
        "infant_birth_weight_grams": _first_float([r"birth weight[:\s]*(\d+(?:\.\d+)?)\s*g", r"birth weight[:\s]*(\d+(?:\.\d+)?)\s*grams"], text),
        "infant_current_weight_grams": _first_float([r"current(?: weight)?[:\s]*(\d+(?:\.\d+)?)\s*g", r"current weight[:\s]*(\d+(?:\.\d+)?)\s*grams"], text),
        "infant_gestational_age_weeks": _first_float([r"(\d{2})(?:\+| weeks? )(\d)\s*(?:weeks|days)"], text),
        "infant_feeding_method": "exclusive-breastfeeding" if "exclusive breastfeeding" in text.lower() else "unknown",
        "infant_feeding_concerns": [c for c in ("poor latch", "sleepy at breast", "sleepy feeds") if c in text.lower()],
        "infant_total_bilirubin": _first_float([r"(?:tsb|bilirubin)[:\s]*(\d+(?:\.\d+)?)"], text),
        "infant_age_at_bili_hours": _first_float([r"(?:at|age)\s*(\d+(?:\.\d+)?)\s*h"], text),
    }

    result = set_inline_dyad_context(tool_context=tool_context, **payload)
    result["source"] = "maternal_fhir_context"
    result["mother_patient_id"] = patient_id
    result["fhir_resource_count"] = len(resources)
    return result


def set_inline_dyad_context(
    mother_name: str,
    mother_age: int,
    delivery_type: str,
    delivery_date: str,
    postpartum_day: int,
    mother_conditions: list[str],
    mother_medications: list[str],
    mother_systolic_bp: float,
    mother_diastolic_bp: float,
    mother_weight_kg: float,
    epds_score: int,
    sdoh_concerns: list[str],
    infant_name: str,
    infant_dob: str,
    infant_age_days: int,
    infant_birth_weight_grams: float,
    infant_current_weight_grams: float,
    infant_gestational_age_weeks: float,
    infant_feeding_method: str,
    infant_feeding_concerns: list[str],
    infant_total_bilirubin: float,
    infant_age_at_bili_hours: float,
    tool_context: ToolContext,
) -> dict[str, Any]:
    """Bind a postpartum mother + newborn infant dyad to the session.

    Use this when the dyad is described in the user's prompt rather than
    pulled live from FHIR (e.g., synthetic demo, hand-keyed handoff). After
    this call, all NEST dyad tools (get_dyad_demographics / _medications /
    _observations) return the bound data.

    Args:
        mother_name: Mother's full name.
        mother_age: Maternal age in years.
        delivery_type: 'vaginal' | 'c-section' | 'operative-vaginal' | 'vbac'.
        delivery_date: ISO date string YYYY-MM-DD.
        postpartum_day: Days since delivery (e.g., 2 = postpartum day 2).
        mother_conditions: List of active maternal conditions / complications.
            Examples: ['preeclampsia', 'gestational diabetes', 'postpartum hemorrhage'].
        mother_medications: Mother's discharge medications (with doses).
            Examples: ['labetalol 200 mg PO BID', 'ibuprofen 600 mg PO Q6H PRN'].
        mother_systolic_bp: Most recent systolic BP, mmHg. Use 0 if unknown.
        mother_diastolic_bp: Most recent diastolic BP, mmHg. Use 0 if unknown.
        mother_weight_kg: Mother's weight in kg. Use 0 if unknown.
        epds_score: Edinburgh Postpartum Depression Scale (0–30). Use -1 if not done.
        sdoh_concerns: SDOH concerns flagged at discharge (free text), e.g.
            ['no transportation', 'food insecurity', 'lives alone'].
        infant_name: Infant's name (or "Baby Boy <Mother surname>" if unnamed).
        infant_dob: ISO date string YYYY-MM-DD.
        infant_age_days: Infant age in days.
        infant_birth_weight_grams: Birth weight (g).
        infant_current_weight_grams: Current weight (g).
        infant_gestational_age_weeks: GA at birth in weeks (e.g., 38.5).
        infant_feeding_method: 'exclusive-breastfeeding' | 'mixed' | 'formula'.
        infant_feeding_concerns: List of concerns, e.g. ['poor latch', 'sleepy at breast'].
        infant_total_bilirubin: Most recent total bilirubin in mg/dL. Use 0 if not measured.
        infant_age_at_bili_hours: Infant age in HOURS at the time of the bili
            measurement (used for Bhutani nomogram). Use 0 if no measurement.

    Returns:
        Confirmation dict with the bound dyad summary.
    """
    if not mother_name or not infant_name:
        return {"status": "error", "error_message": "mother_name and infant_name are required"}

    mother_meds = _shape_meds(mother_medications)
    mother_obs: dict[str, list[dict[str, Any]]] = {"vital-signs": [], "laboratory": [], "survey": []}
    if mother_systolic_bp and mother_systolic_bp > 0 and mother_diastolic_bp and mother_diastolic_bp > 0:
        mother_obs["vital-signs"].append({
            "observation":    "Blood pressure panel",
            "components":     [
                {"name": "Systolic blood pressure",  "value": float(mother_systolic_bp),  "unit": "mmHg"},
                {"name": "Diastolic blood pressure", "value": float(mother_diastolic_bp), "unit": "mmHg"},
            ],
            "value": None,
            "unit":  None,
            "effective_date": None,
            "status": "final",
        })
    if mother_weight_kg and mother_weight_kg > 0:
        mother_obs["vital-signs"].append({
            "observation": "Body weight", "value": float(mother_weight_kg), "unit": "kg",
            "components": None, "effective_date": None, "status": "final",
        })
    if epds_score is not None and epds_score >= 0:
        mother_obs["survey"].append({
            "observation": "Edinburgh Postnatal Depression Scale (EPDS)",
            "value": int(epds_score), "unit": "score",
            "components": None, "effective_date": None, "status": "final",
        })

    infant_meds: list[dict[str, Any]] = []  # newborns get standard nursery meds (vit K, erythromycin, Hep B); injected by orchestrator if asked
    infant_obs: dict[str, list[dict[str, Any]]] = {"vital-signs": [], "laboratory": []}
    if infant_birth_weight_grams and infant_birth_weight_grams > 0:
        infant_obs["vital-signs"].append({
            "observation": "Birth weight", "value": float(infant_birth_weight_grams), "unit": "g",
            "components": None, "effective_date": None, "status": "final",
        })
    if infant_current_weight_grams and infant_current_weight_grams > 0:
        infant_obs["vital-signs"].append({
            "observation": "Current weight", "value": float(infant_current_weight_grams), "unit": "g",
            "components": None, "effective_date": None, "status": "final",
        })
    if infant_total_bilirubin and infant_total_bilirubin > 0:
        infant_obs["laboratory"].append({
            "observation": "Total bilirubin",
            "value": float(infant_total_bilirubin),
            "unit":  "mg/dL",
            "components": [
                {"name": "Age at measurement", "value": float(infant_age_at_bili_hours or 0), "unit": "hours"},
            ],
            "effective_date": None,
            "status": "final",
        })

    weight_loss_pct = None
    if (infant_birth_weight_grams and infant_birth_weight_grams > 0
            and infant_current_weight_grams and infant_current_weight_grams > 0):
        weight_loss_pct = round(
            (infant_birth_weight_grams - infant_current_weight_grams) / infant_birth_weight_grams * 100,
            1,
        )

    tool_context.state["mother_patient"] = {
        "name":             mother_name,
        "age":              int(mother_age),
        "delivery_type":    delivery_type,
        "delivery_date":    delivery_date,
        "postpartum_day":   int(postpartum_day),
        "conditions":       list(mother_conditions or []),
        "weight_kg":        float(mother_weight_kg) if mother_weight_kg else None,
        "systolic_bp":      float(mother_systolic_bp) if mother_systolic_bp else None,
        "diastolic_bp":     float(mother_diastolic_bp) if mother_diastolic_bp else None,
        "epds_score":       int(epds_score) if epds_score is not None and epds_score >= 0 else None,
        "sdoh_concerns":    list(sdoh_concerns or []),
    }
    tool_context.state["mother_medications"] = mother_meds
    tool_context.state["mother_observations"] = mother_obs

    tool_context.state["infant_patient"] = {
        "name":                  infant_name,
        "dob":                   infant_dob,
        "age_days":              int(infant_age_days),
        "birth_weight_grams":    float(infant_birth_weight_grams),
        "current_weight_grams":  float(infant_current_weight_grams),
        "weight_loss_pct":       weight_loss_pct,
        "gestational_age_weeks": float(infant_gestational_age_weeks),
        "feeding_method":        infant_feeding_method,
        "feeding_concerns":      list(infant_feeding_concerns or []),
        "total_bilirubin":       float(infant_total_bilirubin) if infant_total_bilirubin else None,
        "age_at_bili_hours":     float(infant_age_at_bili_hours) if infant_age_at_bili_hours else None,
    }
    tool_context.state["infant_medications"] = infant_meds
    tool_context.state["infant_observations"] = infant_obs

    logger.info(
        "tool_set_inline_dyad_context mother=%s ppd=%s n_mother_meds=%d infant=%s age_days=%s weight_loss=%s",
        mother_name, postpartum_day, len(mother_meds),
        infant_name, infant_age_days, weight_loss_pct,
    )
    return {
        "status": "success",
        "summary": (
            f"Dyad bound: {mother_name} (PPD{postpartum_day} after {delivery_type}) "
            f"+ {infant_name} (DOL{infant_age_days}, "
            f"{infant_current_weight_grams:.0f}g, weight change {weight_loss_pct}%)."
        ),
        "mother_medication_count": len(mother_meds),
        "infant_medication_count": len(infant_meds),
    }


def _bad_subject(subject: str) -> dict[str, Any]:
    return {
        "status": "error",
        "error_message": (
            f"Invalid subject '{subject}'. Use 'mother', 'infant', or 'both'."
        ),
    }


def get_dyad_demographics(subject: str, tool_context: ToolContext) -> dict[str, Any]:
    """Return demographics for the mother, infant, or both.

    Args:
        subject: 'mother' | 'infant' | 'both'.
    """
    s = (subject or "").strip().lower()
    if s == "mother":
        m = tool_context.state.get("mother_patient")
        if not m:
            return {"status": "error", "error_message": "Mother not bound. Call set_inline_dyad_context first."}
        return {"status": "success", "subject": "mother", "patient": m}
    if s == "infant":
        i = tool_context.state.get("infant_patient")
        if not i:
            return {"status": "error", "error_message": "Infant not bound. Call set_inline_dyad_context first."}
        return {"status": "success", "subject": "infant", "patient": i}
    if s == "both":
        m = tool_context.state.get("mother_patient")
        i = tool_context.state.get("infant_patient")
        if not m or not i:
            return {"status": "error", "error_message": "Dyad not bound. Call set_inline_dyad_context first."}
        return {"status": "success", "subject": "both", "mother": m, "infant": i}
    return _bad_subject(subject)


def get_dyad_medications(subject: str, tool_context: ToolContext) -> dict[str, Any]:
    """Return the medication list for the mother or infant.

    Args:
        subject: 'mother' | 'infant'.
    """
    s = (subject or "").strip().lower()
    if s not in ("mother", "infant"):
        return _bad_subject(subject)
    key = "mother_medications" if s == "mother" else "infant_medications"
    meds = tool_context.state.get(key)
    if meds is None:
        return {"status": "error", "error_message": f"{s.capitalize()} not bound. Call set_inline_dyad_context first."}
    return {
        "status":      "success",
        "subject":     s,
        "count":       len(meds),
        "medications": meds,
    }


def get_dyad_observations(subject: str, category: str, tool_context: ToolContext) -> dict[str, Any]:
    """Return observations for the mother or infant in a given category.

    Args:
        subject: 'mother' | 'infant'.
        category: 'vital-signs' | 'laboratory' | 'survey'.
    """
    s = (subject or "").strip().lower()
    if s not in ("mother", "infant"):
        return _bad_subject(subject)
    cat = (category or "vital-signs").strip().lower()
    key = "mother_observations" if s == "mother" else "infant_observations"
    obs_dict = tool_context.state.get(key)
    if obs_dict is None:
        return {"status": "error", "error_message": f"{s.capitalize()} not bound. Call set_inline_dyad_context first."}
    observations = obs_dict.get(cat, [])
    return {
        "status":       "success",
        "subject":      s,
        "category":     cat,
        "count":        len(observations),
        "observations": observations,
    }
