"""
FHIR context helper for the Clinical Knowledge MCP server.

Prompt Opinion sends three headers on every tool call when FHIR context is
authorized for this server:

  X-FHIR-Server-URL     - Base URL of the patient's FHIR R4 server.
  X-FHIR-Access-Token   - SMART access token (Bearer scheme).
  X-Patient-ID          - Active patient context ID.

This module reads those headers from the in-flight ASGI request via a
ContextVar that's populated by `FhirHeaderMiddleware`. Tools that want to
talk to the patient's FHIR server import `get_fhir_context()`.

Stateless tools (Beers lookup etc.) don't use FHIR context at all and
will work whether the user authorizes FHIR or not.
"""

from __future__ import annotations

import logging
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Any

import httpx
from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FhirContext:
    server_url: str
    access_token: str
    patient_id: str


_current_fhir_context: ContextVar[FhirContext | None] = ContextVar(
    "current_fhir_context",
    default=None,
)


def get_fhir_context() -> FhirContext | None:
    """Return the FHIR context for the in-flight request, or None if absent."""
    return _current_fhir_context.get()


class FhirHeaderMiddleware:
    """Read PromptOpinion's FHIR headers from each request and stash them in
    a ContextVar so tools can pick them up.

    The headers are *only* present when:
      1. The MCP server declared the `ai.promptopinion/fhir-context` extension
         in its initialize response, AND
      2. The user authorized FHIR context for this server in PO settings.

    When absent, tools that need FHIR will return a clear error instead of
    crashing.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        headers = {k.decode("latin-1").lower(): v.decode("latin-1") for k, v in scope.get("headers", [])}
        server_url = headers.get("x-fhir-server-url")
        access_token = headers.get("x-fhir-access-token")
        patient_id = headers.get("x-patient-id")

        token = None
        if server_url and access_token and patient_id:
            ctx = FhirContext(
                server_url=server_url.rstrip("/"),
                access_token=access_token,
                patient_id=patient_id,
            )
            token = _current_fhir_context.set(ctx)
            logger.info(
                "fhir_context_received patient_id=%s server=%s",
                patient_id,
                server_url[:60],
            )

        try:
            await self.app(scope, receive, send)
        finally:
            if token is not None:
                _current_fhir_context.reset(token)


# ── Helpers that talk to the FHIR server using the active context ──────────────


def fhir_get(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """GET a FHIR resource using the in-flight FHIR context.

    `path` may be absolute (`https://...`) or relative to the FHIR base URL.
    Raises if no FHIR context is active or the request fails.
    """
    ctx = get_fhir_context()
    if ctx is None:
        raise RuntimeError(
            "No FHIR context available. The MCP host must authorize FHIR access "
            "for this server before patient-aware tools can be used."
        )

    url = path if path.startswith("http") else f"{ctx.server_url}/{path.lstrip('/')}"
    headers = {
        "Authorization": f"Bearer {ctx.access_token}",
        "Accept": "application/fhir+json",
    }
    response = httpx.get(url, params=params, headers=headers, timeout=15.0)
    response.raise_for_status()
    return response.json()


def list_active_medications() -> list[str]:
    """Return generic medication names from the patient's active MedicationRequests."""
    ctx = get_fhir_context()
    if ctx is None:
        return []
    bundle = fhir_get(
        "MedicationRequest",
        params={"patient": ctx.patient_id, "status": "active", "_count": 100},
    )
    names: list[str] = []
    for entry in bundle.get("entry", []) or []:
        rsrc = entry.get("resource") or {}
        if rsrc.get("resourceType") != "MedicationRequest":
            continue
        med = rsrc.get("medicationCodeableConcept") or {}
        text = med.get("text")
        if not text:
            for c in (med.get("coding") or []):
                text = c.get("display") or c.get("code")
                if text:
                    break
        if text:
            names.append(text)
    return names


def latest_egfr() -> float | None:
    """Return the most recent eGFR (mL/min/1.73m^2) for the patient, or None."""
    ctx = get_fhir_context()
    if ctx is None:
        return None
    egfr_loincs = "62238-1,69405-9,77147-7,33914-3,48642-3,48643-1"
    try:
        bundle = fhir_get(
            "Observation",
            params={
                "patient": ctx.patient_id,
                "code": egfr_loincs,
                "_sort": "-date",
                "_count": 1,
            },
        )
    except Exception as e:
        logger.warning("fhir_egfr_lookup_failed err=%s", e)
        return None

    for entry in bundle.get("entry", []) or []:
        rsrc = entry.get("resource") or {}
        if rsrc.get("resourceType") != "Observation":
            continue
        v = rsrc.get("valueQuantity") or {}
        val = v.get("value")
        if val is not None:
            try:
                return float(val)
            except (TypeError, ValueError):
                continue
    return None


def patient_age_years() -> int | None:
    """Return the patient's age in years, or None if birthDate isn't available."""
    ctx = get_fhir_context()
    if ctx is None:
        return None
    try:
        patient = fhir_get(f"Patient/{ctx.patient_id}")
    except Exception as e:
        logger.warning("fhir_patient_lookup_failed err=%s", e)
        return None
    birth = patient.get("birthDate")
    if not birth:
        return None
    try:
        from datetime import date

        bd = date.fromisoformat(birth[:10])
        today = date.today()
        return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
    except Exception:
        return None
