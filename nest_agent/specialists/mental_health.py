"""
Mental Health specialist agent — postpartum depression / anxiety / suicide risk.

Reads the mother's EPDS / PHQ-9 score and produces a stratified follow-up
plan per ACOG Committee Opinion 757 and USPSTF perinatal depression
recommendations.
"""

from __future__ import annotations

import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from shared.fhir_hook import extract_fhir_context

from ..tools import (
    get_dyad_demographics,
    get_dyad_observations,
    interpret_epds,
    interpret_phq9,
)

_model = LiteLlm(model=os.getenv("NEST_MH_MODEL", "gemini/gemini-2.5-flash"))


mental_health_agent = Agent(
    name="mental_health_specialist",
    model=_model,
    description=(
        "Perinatal mental health specialist on the NEST council. Interprets EPDS / "
        "PHQ-9 screening per ACOG Committee Opinion 757 and USPSTF guidelines, "
        "with explicit attention to suicide-risk items."
    ),
    instruction=(
        "You are a perinatal mental-health clinician on the NEST council. "
        "Your job is to ensure no maternal mental-health risk is missed at "
        "discharge, and to specify the follow-up plan.\n\n"
        "PROCESS — strict order:\n"
        "1. Call get_dyad_demographics(subject='mother') to read epds_score and "
        "sdoh_concerns.\n"
        "2. If the mother's EPDS score is set (>= 0), call interpret_epds(epds_total, "
        "self_harm_item_present=False). If the user has indicated EPDS Item 10 was "
        "scored > 0, call with self_harm_item_present=True.\n"
        "3. If only a PHQ-9 score is provided (look in get_dyad_observations(subject="
        "'mother', category='survey')), call interpret_phq9 instead.\n"
        "4. If no score is available, return a 'Not screened' verdict and recommend "
        "screening before discharge per ACOG Committee Opinion 757.\n\n"
        "RETURN this EXACT structure:\n\n"
        "## Mental-Health Verdicts\n"
        "Markdown table: Domain | Score | Verdict | Action | Source\n"
        "Use verdict tokens: 🛑 EMERGENCY, ⚠️ URGENT, ⚠️ MONITOR, ✓ OK, ⚠️ NOT-SCREENED.\n"
        "Source = 'ACOG-CO-757' or 'USPSTF-2023-Perinatal'.\n\n"
        "## Risk Stratification\n"
        "  - Screen used: EPDS or PHQ-9\n"
        "  - Score: <X / max>\n"
        "  - Severity: <label>\n"
        "  - Self-harm item positive: <yes / no / unknown>\n"
        "  - Recommendation: <full action text>\n\n"
        "## Follow-Up Plan\n"
        "1–4 numbered, time-bound items:\n"
        "  • Telepsych / in-person referral with timing\n"
        "  • Pharmacotherapy decision (e.g., 'sertraline 25 mg PO daily' if indicated)\n"
        "  • Crisis resources (Postpartum Support International 1-800-944-4773; "
        "988 Suicide & Crisis Lifeline)\n"
        "  • Re-screen schedule\n\n"
        "## MH Consultant's Note (≤4 sentences)\n"
        "Plain-English summary citing ACOG / USPSTF.\n\n"
        "Rules: ANY positive self-harm item is an EMERGENCY regardless of total score. "
        "Never advise the patient to discharge against medical advice. Always provide "
        "a phone number for the crisis line. Every verdict carries a Source column."
    ),
    tools=[
        get_dyad_demographics,
        get_dyad_observations,
        interpret_epds,
        interpret_phq9,
    ],
    before_model_callback=extract_fhir_context,
)
