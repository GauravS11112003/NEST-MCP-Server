"""
NEST — A2A application entry point.

Start the server with:
    uvicorn nest_agent.app:a2a_app --host 0.0.0.0 --port 8005

The agent card is served publicly at:
    GET http://localhost:8005/.well-known/agent-card.json

For Prompt Opinion registration, set:
    NEST_AGENT_URL=https://<your-public-url>
    PO_PLATFORM_BASE_URL=https://<your-prompt-opinion-workspace>
"""

from __future__ import annotations

import os

from a2a.types import AgentSkill
from shared.app_factory import create_a2a_app

from .agent import root_agent

a2a_app = create_a2a_app(
    agent=root_agent,
    name="nest_agent",
    description=(
        "NEST — Newborn & Maternal Safe Transition. A multi-specialist agent that "
        "converts postpartum discharge into a structured, evidence-backed transition "
        "plan for the mother-infant dyad. Convenes Maternal-OB, Pediatrics, Lactation, "
        "Mental Health, and Social Work as in-process sub-agents and synthesizes a "
        "unified report with transition score, dyad recovery timeline, medication "
        "card, dual red-flag cards, care-team task board, caregiver summary, and an "
        "evidence-backed audit log linking every recommendation to its source rule."
    ),
    url=os.getenv(
        "NEST_AGENT_URL",
        os.getenv("BASE_URL", "http://localhost:8005"),
    ),
    port=8005,
    fhir_extension_uri=(
        f"{os.getenv('PO_PLATFORM_BASE_URL', 'http://localhost:5139')}"
        "/schemas/a2a/v1/fhir-context"
    ),
    fhir_scopes=[
        {"name": "patient/Patient.rs",           "required": True},   # mother + infant demographics
        {"name": "patient/Condition.rs",         "required": True},   # delivery, comorbidities, complications
        {"name": "patient/MedicationRequest.rs", "required": True},   # discharge medications
        {"name": "patient/Observation.rs",       "required": True},   # BP, EPDS, weight, bilirubin
        {"name": "patient/Encounter.rs",         "required": False},  # delivery + nursery encounter
        {"name": "patient/CarePlan.rs",          "required": False},  # existing care plan if any
        {"name": "patient/Appointment.rs",       "required": False},  # scheduled follow-ups
        {"name": "patient/DocumentReference.rs", "required": False},  # discharge summary
        {"name": "patient/ServiceRequest.rs",    "required": False},  # orders / referrals
    ],
    skills=[
        AgentSkill(
            id="postpartum-transition-plan",
            name="postpartum-transition-plan",
            description=(
                "Comprehensive postpartum discharge transition plan for the "
                "mother-infant dyad. Returns transition score, recovery timeline, "
                "medication card, dual red-flag cards, care-team task board, "
                "caregiver summary, and an evidence-backed audit log."
            ),
            tags=["postpartum", "newborn", "maternal-health", "fhir", "discharge", "acog", "aap"],
        ),
        AgentSkill(
            id="acog-postpartum-visit-plan",
            name="acog-postpartum-visit-plan",
            description=(
                "Generate the ACOG-compliant postpartum visit schedule (initial "
                "contact within 1 week, comprehensive visit by 12 weeks, with risk-"
                "tailored early visits for hypertension or hemorrhage)."
            ),
            tags=["acog", "postpartum", "scheduling"],
        ),
        AgentSkill(
            id="aap-newborn-visit-plan",
            name="aap-newborn-visit-plan",
            description=(
                "Generate the AAP Bright Futures newborn well-child visit schedule "
                "(48–72h post-discharge, 1 month, 2 months) with vaccine timing."
            ),
            tags=["aap", "newborn", "scheduling", "vaccines"],
        ),
        AgentSkill(
            id="lactation-medication-safety",
            name="lactation-medication-safety",
            description=(
                "Review every maternal medication for breastfeeding safety per NIH "
                "LactMed and Hale categories L1–L5."
            ),
            tags=["lactation", "breastfeeding", "lactmed", "medication-safety"],
        ),
        AgentSkill(
            id="postpartum-mental-health-screen",
            name="postpartum-mental-health-screen",
            description=(
                "Interpret EPDS / PHQ-9 with explicit attention to suicide-risk "
                "items (EPDS Item 10, PHQ-9 Item 9), per ACOG and USPSTF."
            ),
            tags=["mental-health", "epds", "phq-9", "postpartum-depression"],
        ),
        AgentSkill(
            id="postpartum-sdoh-screen",
            name="postpartum-sdoh-screen",
            description=(
                "Translate free-text SDOH concerns into structured interventions "
                "with assigned owners using the CMS AHC HRSN taxonomy."
            ),
            tags=["sdoh", "social-work", "equity", "care-coordination"],
        ),
        AgentSkill(
            id="newborn-jaundice-classifier",
            name="newborn-jaundice-classifier",
            description=(
                "Classify a newborn TSB measurement against AAP 2022 phototherapy "
                "thresholds by infant age and risk band."
            ),
            tags=["newborn", "jaundice", "bilirubin", "aap-2022"],
        ),
    ],
)
