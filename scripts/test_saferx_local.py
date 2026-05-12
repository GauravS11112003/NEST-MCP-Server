"""
Local end-to-end test of the SafeRx Council without a real FHIR server.

Mocks `httpx.get` so the FHIR tools return realistic synthetic data for
an 82-year-old polypharmacy patient with CKD3b. Then invokes the council
through the ADK Runner and prints the synthesized council report.

Run with:
    SAFERX_SKIP_MCP=true python scripts/test_saferx_local.py
"""

from __future__ import annotations

import asyncio
import os
import sys
import warnings
from pathlib import Path
from unittest.mock import MagicMock, patch

# Make sure the project root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Suppress experimental warnings for a cleaner demo output
warnings.filterwarnings("ignore", category=UserWarning)
os.environ.setdefault("ADK_SUPPRESS_GEMINI_LITELLM_WARNINGS", "true")
os.environ.setdefault("SAFERX_SKIP_MCP", "true")

from dotenv import load_dotenv

load_dotenv()


# ── Synthetic FHIR data ───────────────────────────────────────────────────────

PATIENT_82F = {
    "resourceType": "Patient",
    "id": "demo-82f-polypharmacy",
    "active": True,
    "name": [{"use": "official", "given": ["Eleanor"], "family": "Whitaker"}],
    "birthDate": "1944-04-15",  # makes her 82 in 2026
    "gender": "female",
    "telecom": [{"system": "phone", "value": "+1-555-0142", "use": "home"}],
    "address": [
        {
            "line": ["821 Maplewood Ln"],
            "city": "Cleveland",
            "state": "OH",
            "postalCode": "44106",
            "country": "USA",
        }
    ],
    "maritalStatus": {"text": "Widowed"},
}

MEDS_BUNDLE = {
    "resourceType": "Bundle",
    "type": "searchset",
    "entry": [
        {
            "resource": {
                "resourceType": "MedicationRequest",
                "status": "active",
                "medicationCodeableConcept": {"text": med},
                "dosageInstruction": [{"text": dose}],
                "authoredOn": "2025-12-01",
                "requester": {"display": "Dr. Internal Medicine"},
            }
        }
        for med, dose in [
            ("apixaban",        "5 mg PO BID"),
            ("warfarin",        "2 mg PO daily"),    # intentional duplicate anticoagulation for demo
            ("aspirin",         "81 mg PO daily"),
            ("ibuprofen",       "600 mg PO TID PRN"),
            ("simvastatin",     "40 mg PO QHS"),
            ("amiodarone",      "200 mg PO daily"),
            ("citalopram",      "20 mg PO daily"),
            ("ondansetron",     "4 mg PO Q8H PRN"),
            ("diphenhydramine", "50 mg PO QHS PRN"),
            ("oxybutynin",      "5 mg PO BID"),
            ("amitriptyline",   "25 mg PO QHS"),
            ("metformin",       "500 mg PO BID"),
            ("digoxin",         "0.25 mg PO daily"),
            ("lisinopril",      "20 mg PO daily"),
        ]
    ],
}

OBSERVATIONS_BUNDLE = {
    "resourceType": "Bundle",
    "type": "searchset",
    "entry": [
        {
            "resource": {
                "resourceType": "Observation",
                "status": "final",
                "code": {"text": "Estimated GFR (CKD-EPI 2021)"},
                "valueQuantity": {"value": 38.0, "unit": "mL/min/1.73m2"},
                "effectiveDateTime": "2026-04-22",
            }
        },
        {
            "resource": {
                "resourceType": "Observation",
                "status": "final",
                "code": {"text": "Creatinine, Serum"},
                "valueQuantity": {"value": 1.6, "unit": "mg/dL"},
                "effectiveDateTime": "2026-04-22",
            }
        },
        {
            "resource": {
                "resourceType": "Observation",
                "status": "final",
                "code": {"text": "Potassium, Serum"},
                "valueQuantity": {"value": 4.7, "unit": "mmol/L"},
                "effectiveDateTime": "2026-04-22",
            }
        },
    ],
}


def _fake_fhir_get(url: str, *args, **kwargs):
    """Stand-in for httpx.get used by FHIR tools."""
    response = MagicMock()
    response.raise_for_status = MagicMock()
    if "Patient/" in url:
        response.json = MagicMock(return_value=PATIENT_82F)
    elif "MedicationRequest" in url:
        response.json = MagicMock(return_value=MEDS_BUNDLE)
    elif "Observation" in url:
        response.json = MagicMock(return_value=OBSERVATIONS_BUNDLE)
    else:
        response.json = MagicMock(return_value={})
    return response


# ── Drive the council via the ADK Runner ──────────────────────────────────────

async def run_council_demo() -> None:
    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService
    from google.genai.types import Content, Part

    from saferx_council.agent import root_agent

    session_service = InMemorySessionService()
    runner = Runner(
        agent=root_agent,
        app_name="saferx_demo",
        session_service=session_service,
    )

    session = await session_service.create_session(
        app_name="saferx_demo",
        user_id="demo-clinician",
        # Pre-populate the FHIR credentials that extract_fhir_context normally injects.
        state={
            "fhir_url":   "https://demo.fhir.local/r4",
            "fhir_token": "demo-token",
            "patient_id": PATIENT_82F["id"],
        },
    )

    user_msg = Content(
        role="user",
        parts=[
            Part(
                text=(
                    "Convene the SafeRx Council on this patient. Run a comprehensive "
                    "polypharmacy safety review and return the unified Council Report."
                )
            )
        ],
    )

    print("\n" + "=" * 78)
    print(" SafeRx Council Demo — Eleanor Whitaker, 82F, eGFR 38, on 14 medications")
    print("=" * 78 + "\n")

    final_text = ""
    with patch("shared.tools.fhir.httpx.get", side_effect=_fake_fhir_get):
        async for event in runner.run_async(
            user_id="demo-clinician",
            session_id=session.id,
            new_message=user_msg,
        ):
            if event.is_final_response() and event.content and event.content.parts:
                for p in event.content.parts:
                    if getattr(p, "text", None):
                        final_text = p.text
            elif event.content and event.content.parts:
                for p in event.content.parts:
                    fc = getattr(p, "function_call", None)
                    if fc:
                        print(f"[tool-call] {fc.name}({list((fc.args or {}).keys())})")

    print("\n" + "─" * 78)
    print(" COUNCIL REPORT")
    print("─" * 78 + "\n")
    print(final_text or "(no final text emitted)")
    print()


if __name__ == "__main__":
    asyncio.run(run_council_demo())
