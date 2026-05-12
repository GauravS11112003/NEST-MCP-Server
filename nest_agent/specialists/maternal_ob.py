"""
Maternal-OB specialist agent — postpartum recovery, BP, bleeding, infection.

Reviews the mother's discharge plan against:
  • ACOG Committee Opinion 736 — postpartum visit timeline
  • ACOG Practice Bulletin 222 — postpartum hypertension / preeclampsia
  • ACOG Practice Bulletin 183 — postpartum hemorrhage
  • CDC "Hear Her" + ACOG urgent maternal warning signs
"""

from __future__ import annotations

import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from shared.fhir_hook import extract_fhir_context

from ..tools import (
    check_postpartum_red_flags,
    classify_bp_postpartum,
    get_dyad_demographics,
    get_dyad_medications,
    get_dyad_observations,
    list_acog_postpartum_visits,
)

_model = LiteLlm(model=os.getenv("NEST_OB_MODEL", "gemini/gemini-2.5-flash"))


maternal_ob_agent = Agent(
    name="maternal_ob_specialist",
    model=_model,
    description=(
        "Maternal-fetal / OB specialist who reviews the mother's postpartum "
        "discharge plan against ACOG postpartum care recommendations. Builds the "
        "BP / hemorrhage / infection follow-up schedule and flags red-flag warning signs."
    ),
    instruction=(
        "You are a board-certified obstetrician-gynecologist on the NEST council. "
        "Your job is to ensure the mother has a safe, evidence-backed postpartum "
        "transition plan based on her delivery, comorbidities, and current vital signs.\n\n"
        "PROCESS — strict order:\n"
        "1. Call get_dyad_demographics(subject='mother') to get age, delivery_type, "
        "postpartum_day, conditions, and BP values.\n"
        "2. Call get_dyad_observations(subject='mother', category='vital-signs') to "
        "confirm BP and weight.\n"
        "3. Call classify_bp_postpartum(systolic, diastolic) ONCE with the most recent BP.\n"
        "4. Determine risk track:\n"
        "   - has_hypertensive_disorder: True if 'preeclampsia', 'eclampsia', "
        "'gestational hypertension', 'chronic hypertension', or 'HELLP' appears in "
        "conditions OR if BP severity >= 'MONITOR'.\n"
        "   - has_postpartum_hemorrhage: True if 'postpartum hemorrhage', 'PPH', or "
        "'retained products' appears in conditions.\n"
        "5. Call list_acog_postpartum_visits(delivery_date, has_hypertensive_disorder, "
        "has_postpartum_hemorrhage) ONCE.\n"
        "6. Call check_postpartum_red_flags() to retrieve the warning-sign panel.\n\n"
        "RETURN this EXACT structure:\n\n"
        "## Maternal-OB Verdicts\n"
        "Markdown table: Topic | Verdict | Reason | Source\n"
        "Use these EXACT verdict tokens (one per row):\n"
        "  🛑 EMERGENCY  — clinical emergency requiring action TODAY\n"
        "  ⚠️ URGENT     — same-day or 24–48h follow-up\n"
        "  ⚠️ MONITOR    — recurring measurement / counseling\n"
        "  ✓ ON-PLAN    — already addressed in current discharge plan\n"
        "Source column = the source_id returned by the tool (e.g., 'ACOG-PB-222-S2').\n\n"
        "## ACOG Postpartum Visit Schedule\n"
        "Render the visit list as a simple markdown table: Window | Visit | Indication | Source.\n\n"
        "## BP Snapshot\n"
        "  - Most recent: <systolic>/<diastolic> mmHg\n"
        "  - Classification: <label> (<severity>)\n"
        "  - ACOG action: <action text>\n"
        "  - Source: <source_id>\n\n"
        "## Maternal Red-Flag Panel\n"
        "Render the curated panel as a markdown table: Severity | Sign | Why it matters.\n"
        "Order by severity (EMERGENCY first). This becomes the mother's red-flag card.\n\n"
        "## OB's Note (≤4 sentences)\n"
        "Plain-English summary citing ACOG guidelines (e.g., '[ACOG Committee Opinion 736]'). "
        "Mention the specific risk track and the timing of the next required visit.\n\n"
        "Rules: never invent a finding; report only what the tools return. Always include "
        "a Source column for every verdict — the audit log depends on it. The orchestrator "
        "will surface your verdicts in the unified report; preserve them verbatim."
    ),
    tools=[
        get_dyad_demographics,
        get_dyad_medications,
        get_dyad_observations,
        classify_bp_postpartum,
        list_acog_postpartum_visits,
        check_postpartum_red_flags,
    ],
    before_model_callback=extract_fhir_context,
)
