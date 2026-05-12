"""
SafeRx Council — A2A application entry point.

Start the server with:
    uvicorn saferx_council.app:a2a_app --host 0.0.0.0 --port 8004

The agent card is served publicly at:
    GET http://localhost:8004/.well-known/agent-card.json

All other endpoints require an X-API-Key header (see shared/middleware.py).

For Prompt Opinion registration, set:
    SAFERX_COUNCIL_URL=https://<your-public-url>
    PO_PLATFORM_BASE_URL=https://<your-prompt-opinion-workspace>
"""

import os

from a2a.types import AgentSkill
from shared.app_factory import create_a2a_app

from .agent import root_agent

a2a_app = create_a2a_app(
    agent=root_agent,
    name="saferx_council",
    description=(
        "SafeRx Council — a multi-specialist agent that reviews an older adult's "
        "medication list for Beers Criteria violations, drug-drug interactions, "
        "anticholinergic burden, renal dose adjustments, and smartwatch trend signals. "
        "Convenes a geriatrician, pharmacist, nephrologist, and wearable sentinel as "
        "in-process A2A sub-agents and synthesizes a unified council report."
    ),
    url=os.getenv(
        "SAFERX_COUNCIL_URL",
        os.getenv("BASE_URL", "http://localhost:8004"),
    ),
    port=8004,
    fhir_extension_uri=(
        f"{os.getenv('PO_PLATFORM_BASE_URL', 'http://localhost:5139')}"
        "/schemas/a2a/v1/fhir-context"
    ),
    fhir_scopes=[
        {"name": "patient/Patient.rs",           "required": True},   # demographics & age
        {"name": "patient/MedicationRequest.rs", "required": True},   # active medication list
        {"name": "patient/Condition.rs",         "required": False},  # context for specialist reasoning
        {"name": "patient/Observation.rs",       "required": True},   # eGFR for renal specialist
    ],
    skills=[
        AgentSkill(
            id="polypharmacy-review",
            name="polypharmacy-review",
            description=(
                "Comprehensive medication safety review for older adults. "
                "Returns prioritized action plan covering Beers Criteria, drug interactions, "
                "anticholinergic burden, and renal dosing."
            ),
            tags=["polypharmacy", "geriatrics", "deprescribing", "fhir", "beers"],
        ),
        AgentSkill(
            id="beers-criteria-screen",
            name="beers-criteria-screen",
            description="Screen a medication list against AGS Beers Criteria 2023.",
            tags=["beers", "geriatrics", "deprescribing"],
        ),
        AgentSkill(
            id="drug-interaction-screen",
            name="drug-interaction-screen",
            description="Identify clinically significant drug-drug interactions in a med list.",
            tags=["pharmacology", "interactions", "safety"],
        ),
        AgentSkill(
            id="anticholinergic-burden-score",
            name="anticholinergic-burden-score",
            description="Calculate cumulative ACB score for cognitive risk assessment.",
            tags=["geriatrics", "cognition", "falls"],
        ),
        AgentSkill(
            id="renal-dose-review",
            name="renal-dose-review",
            description="Review every medication for required renal dose adjustments based on eGFR.",
            tags=["nephrology", "dosing", "ckd"],
        ),
        AgentSkill(
            id="wearable-medication-safety-review",
            name="wearable-medication-safety-review",
            description=(
                "Correlate smartwatch trend signals with medication safety risks, "
                "including falls, low SpO2, bradycardia, tachycardia, sedation, and sleep disruption."
            ),
            tags=["wearables", "remote-monitoring", "polypharmacy", "fhir", "safepulse"],
        ),
    ],
)
