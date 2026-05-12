"""
FHIR tools — query a FHIR R4 server on behalf of the patient in context.

These tools are registered with the agent in agent.py.  At call time, each
tool reads the FHIR credentials (fhir_url, fhir_token, patient_id) from
tool_context.state — values that were injected by fhir_hook.extract_fhir_context
before the LLM was called.  The credentials never appear in the prompt.

─────────────────────────────────────────────────────────────────────────────
Adding your own FHIR tools
─────────────────────────────────────────────────────────────────────────────
1. Write a new function in this file (or create a new file in shared/tools/).
2. Add tool_context: ToolContext as the LAST parameter.
3. Start with  ctx = _get_fhir_context(tool_context); if isinstance(ctx, dict): return ctx
4. Export it from shared/tools/__init__.py.
5. Add it to the tools=[...] list in whichever agent(s) need it.

All FHIR REST calls go through _fhir_get(), which attaches the Bearer token
and sets the Accept header.  httpx is used (already a transitive dependency of
google-adk / a2a-sdk — no extra install required).
"""
import logging

import httpx
from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)

_FHIR_TIMEOUT = 15  # seconds


# ── Private helpers ────────────────────────────────────────────────────────────

def _get_fhir_context(tool_context: ToolContext):
    """
    Read FHIR credentials injected by fhir_hook into the session state.

    Returns (fhir_url, fhir_token, patient_id) on success.
    Returns an error dict if any credential is missing so the caller can
    return it directly as the tool result. The error message advises the
    caller to either supply FHIR metadata or call set_inline_patient_context.
    """
    fhir_url   = tool_context.state.get("fhir_url",   "").rstrip("/")
    fhir_token = tool_context.state.get("fhir_token", "")
    patient_id = tool_context.state.get("patient_id", "")

    missing = [
        name for name, val in [
            ("fhir_url",   fhir_url),
            ("fhir_token", fhir_token),
            ("patient_id", patient_id),
        ]
        if not val
    ]
    if missing:
        return {
            "status": "error",
            "error_message": (
                f"No patient context available — missing FHIR credentials: {', '.join(missing)}. "
                "Either include 'fhir-context' in the A2A message metadata, or call "
                "set_inline_patient_context with the patient data from the user's prompt."
            ),
        }
    return fhir_url, fhir_token, patient_id


def _fhir_get(fhir_url: str, token: str, path: str, params: dict | None = None) -> dict:
    """Perform an authenticated FHIR GET and return the parsed JSON response."""
    response = httpx.get(
        f"{fhir_url}/{path}",
        params=params,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept":        "application/fhir+json",
        },
        timeout=_FHIR_TIMEOUT,
    )
    response.raise_for_status()
    return response.json()


def _http_error_result(exc: httpx.HTTPStatusError) -> dict:
    return {
        "status":        "error",
        "http_status":   exc.response.status_code,
        "error_message": f"FHIR server returned HTTP {exc.response.status_code}: {exc.response.text[:200]}",
    }


def _connection_error_result(exc: Exception) -> dict:
    return {
        "status":        "error",
        "error_message": f"Could not reach FHIR server: {exc}",
    }


def _coding_display(codings: list) -> str:
    """Return the first human-readable display text from a list of FHIR codings."""
    for c in codings:
        if c.get("display"):
            return c["display"]
    return "Unknown"


# ── Tool: patient demographics ─────────────────────────────────────────────────

def get_patient_demographics(tool_context: ToolContext) -> dict:
    """
    Fetches the demographic information for the current patient.

    If inline patient context has been bound via set_inline_patient_context,
    returns the inline data. Otherwise queries the FHIR server.

    Returns name, date of birth, gender, and primary contact details.
    No arguments required — the patient identity comes from the session context.
    """
    inline = tool_context.state.get("inline_patient")
    if inline:
        logger.info("tool_get_patient_demographics source=inline name=%s", inline.get("name"))
        return {
            "status":         "success",
            "source":         "inline",
            "patient_id":     "inline",
            "name":           inline.get("name"),
            "age":            inline.get("age"),
            "gender":         inline.get("sex"),
            "weight_kg":      inline.get("weight_kg"),
            "serum_creatinine_mg_dl": inline.get("serum_creatinine_mg_dl"),
            "birth_date":     None,
            "active":         True,
            "contacts":       [],
            "address":        None,
            "marital_status": None,
        }

    ctx = _get_fhir_context(tool_context)
    if isinstance(ctx, dict):
        return ctx
    fhir_url, fhir_token, patient_id = ctx

    logger.info("tool_get_patient_demographics patient_id=%s", patient_id)
    try:
        patient = _fhir_get(fhir_url, fhir_token, f"Patient/{patient_id}")
    except httpx.HTTPStatusError as e:
        return _http_error_result(e)
    except Exception as e:
        return _connection_error_result(e)

    names    = patient.get("name", [])
    official = next((n for n in names if n.get("use") == "official"), names[0] if names else {})
    given    = " ".join(official.get("given", []))
    family   = official.get("family", "")
    full_name = f"{given} {family}".strip() or "Unknown"

    contacts = [
        {"system": t.get("system"), "value": t.get("value"), "use": t.get("use")}
        for t in patient.get("telecom", [])
    ]

    addrs   = patient.get("address", [])
    address = None
    if addrs:
        a = addrs[0]
        address = ", ".join(filter(None, [
            " ".join(a.get("line", [])),
            a.get("city"), a.get("state"), a.get("postalCode"), a.get("country"),
        ]))

    return {
        "status":         "success",
        "patient_id":     patient_id,
        "name":           full_name,
        "birth_date":     patient.get("birthDate"),
        "gender":         patient.get("gender"),
        "active":         patient.get("active"),
        "contacts":       contacts,
        "address":        address,
        "marital_status": (patient.get("maritalStatus") or {}).get("text"),
    }


# ── Tool: active medications ───────────────────────────────────────────────────

def _bundle_to_meds(bundle: dict) -> list[dict]:
    """Extract medication summaries from a MedicationRequest search Bundle."""
    out: list[dict] = []
    for entry in bundle.get("entry", []) or []:
        res = entry.get("resource", {})
        if res.get("resourceType") != "MedicationRequest":
            continue
        med_concept = res.get("medicationCodeableConcept", {}) or {}
        med_name = (
            med_concept.get("text")
            or _coding_display(med_concept.get("coding", []))
            or (res.get("medicationReference") or {}).get("display")
            or "Unknown"
        )
        dosage_list = [d.get("text", "No dosage text") for d in res.get("dosageInstruction", []) or []]
        out.append({
            "medication":  med_name,
            "status":      res.get("status"),
            "intent":      res.get("intent"),
            "dosage":      dosage_list[0] if dosage_list else "Not specified",
            "authored_on": res.get("authoredOn"),
            "requester":   (res.get("requester") or {}).get("display"),
        })
    return out


def get_active_medications(tool_context: ToolContext) -> dict:
    """
    Retrieves the patient's current medication list from the FHIR server.

    Search strategy (in order):
      1. MedicationRequest?status=active            → preferred, real active meds
      2. MedicationRequest?status=active,on-hold,draft   → permissive
      3. MedicationRequest?_sort=-authoredon&_count=20    → fallback for demo /
         Synthea / completed-only patients so the council can still review the
         most recent prescriptions

    The response includes a `source` field so the council can warn the user
    when the fallback was used. No arguments required.

    If inline patient context has been bound via set_inline_patient_context,
    returns the inline medication list with source='inline'.
    """
    inline_meds = tool_context.state.get("inline_medications")
    if inline_meds is not None:
        logger.info("tool_get_active_medications source=inline count=%d", len(inline_meds))
        return {
            "status":      "success",
            "patient_id":  "inline",
            "source":      "inline",
            "source_note": None,
            "count":       len(inline_meds),
            "medications": inline_meds,
        }

    ctx = _get_fhir_context(tool_context)
    if isinstance(ctx, dict):
        return ctx
    fhir_url, fhir_token, patient_id = ctx

    logger.info("tool_get_active_medications patient_id=%s", patient_id)

    def _query(params: dict) -> dict:
        return _fhir_get(fhir_url, fhir_token, "MedicationRequest", params=params)

    medications: list[dict] = []
    source = "active"
    try:
        bundle = _query({"patient": patient_id, "status": "active", "_count": "50"})
        medications = _bundle_to_meds(bundle)

        if not medications:
            source = "active_or_pending"
            bundle = _query({
                "patient": patient_id,
                "status": "active,on-hold,draft",
                "_count": "50",
            })
            medications = _bundle_to_meds(bundle)

        if not medications:
            source = "most_recent_any_status"
            bundle = _query({
                "patient": patient_id,
                "_sort": "-authoredon",
                "_count": "20",
            })
            medications = _bundle_to_meds(bundle)
    except httpx.HTTPStatusError as e:
        return _http_error_result(e)
    except Exception as e:
        return _connection_error_result(e)

    return {
        "status":      "success",
        "patient_id":  patient_id,
        "source":      source,
        "source_note": (
            "Patient has no FHIR-active prescriptions; falling back to the "
            "20 most recent MedicationRequests regardless of status. The council "
            "is reviewing these as if they were the patient's current regimen — "
            "verify with the patient before acting on recommendations."
            if source == "most_recent_any_status"
            else None
        ),
        "count":       len(medications),
        "medications": medications,
    }


# ── Tool: active conditions (problem list) ─────────────────────────────────────

def get_active_conditions(tool_context: ToolContext) -> dict:
    """
    Retrieves the patient's active conditions and diagnoses from the FHIR server.

    Queries Condition resources with clinical-status=active and returns the
    problem list with condition names, severity, and onset dates.
    No arguments required.
    """
    ctx = _get_fhir_context(tool_context)
    if isinstance(ctx, dict):
        return ctx
    fhir_url, fhir_token, patient_id = ctx

    logger.info("tool_get_active_conditions patient_id=%s", patient_id)
    try:
        bundle = _fhir_get(
            fhir_url, fhir_token, "Condition",
            params={"patient": patient_id, "clinical-status": "active", "_count": "50"},
        )
    except httpx.HTTPStatusError as e:
        return _http_error_result(e)
    except Exception as e:
        return _connection_error_result(e)

    conditions = []
    for entry in bundle.get("entry", []):
        res   = entry.get("resource", {})
        code  = res.get("code", {})
        onset = res.get("onsetDateTime") or (res.get("onsetPeriod") or {}).get("start")
        conditions.append({
            "condition":       code.get("text") or _coding_display(code.get("coding", [])),
            "clinical_status": (
                (res.get("clinicalStatus") or {}).get("coding", [{}])[0].get("code")
            ),
            "severity":        (res.get("severity") or {}).get("text"),
            "onset":           onset,
            "recorded_date":   res.get("recordedDate"),
        })

    return {
        "status":     "success",
        "patient_id": patient_id,
        "count":      len(conditions),
        "conditions": conditions,
    }


# ── Tool: recent observations (vitals / labs) ──────────────────────────────────

def get_recent_observations(category: str, tool_context: ToolContext) -> dict:
    """
    Retrieves recent clinical observations for the patient from the FHIR server.

    Args:
        category: FHIR observation category. Common values:
                    'vital-signs'    — blood pressure, heart rate, temperature, SpO2
                    'laboratory'     — lab results (CBC, HbA1c, metabolic panel, etc.)
                    'social-history' — smoking status, alcohol use, etc.
                  Defaults to 'vital-signs' if not specified.

    Returns the 20 most recent observations in the category, newest first.

    If inline patient context has been bound via set_inline_patient_context,
    returns inline observations (eGFR, SCr, weight) for the requested category.
    """
    category = (category or "vital-signs").strip().lower()

    inline_obs = tool_context.state.get("inline_observations")
    if inline_obs is not None:
        observations = inline_obs.get(category, [])
        logger.info(
            "tool_get_recent_observations source=inline category=%s count=%d",
            category, len(observations),
        )
        return {
            "status":       "success",
            "source":       "inline",
            "patient_id":   "inline",
            "category":     category,
            "count":        len(observations),
            "observations": observations,
        }

    ctx = _get_fhir_context(tool_context)
    if isinstance(ctx, dict):
        return ctx
    fhir_url, fhir_token, patient_id = ctx
    logger.info("tool_get_recent_observations patient_id=%s category=%s", patient_id, category)
    try:
        bundle = _fhir_get(
            fhir_url, fhir_token, "Observation",
            params={"patient": patient_id, "category": category, "_sort": "-date", "_count": "20"},
        )
    except httpx.HTTPStatusError as e:
        return _http_error_result(e)
    except Exception as e:
        return _connection_error_result(e)

    observations = []
    for entry in bundle.get("entry", []):
        res  = entry.get("resource", {})
        code = res.get("code", {})
        obs_name = code.get("text") or _coding_display(code.get("coding", []))

        value, unit = None, None
        if "valueQuantity" in res:
            vq    = res["valueQuantity"]
            value = vq.get("value")
            unit  = vq.get("unit") or vq.get("code")
        elif "valueCodeableConcept" in res:
            value = (res["valueCodeableConcept"].get("text")
                     or _coding_display(res["valueCodeableConcept"].get("coding", [])))
        elif "valueString" in res:
            value = res["valueString"]

        components = []
        for comp in res.get("component", []):
            comp_code = (comp.get("code") or {})
            comp_name = comp_code.get("text") or _coding_display(comp_code.get("coding", []))
            comp_vq   = comp.get("valueQuantity", {})
            components.append({
                "name":  comp_name,
                "value": comp_vq.get("value"),
                "unit":  comp_vq.get("unit") or comp_vq.get("code"),
            })

        observations.append({
            "observation":    obs_name,
            "value":          value,
            "unit":           unit,
            "components":     components or None,
            "effective_date": res.get("effectiveDateTime") or (res.get("effectivePeriod") or {}).get("start"),
            "status":         res.get("status"),
            "interpretation": (
                (res.get("interpretation") or [{}])[0].get("text")
                or _coding_display((res.get("interpretation") or [{}])[0].get("coding", []))
            ),
        })

    return {
        "status":       "success",
        "patient_id":   patient_id,
        "category":     category,
        "count":        len(observations),
        "observations": observations,
    }
