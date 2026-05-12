"""
Geriatrician specialist agent.

Reviews a patient's medication list against:
  • AGS Beers Criteria 2023 (potentially inappropriate meds in older adults)
  • Anticholinergic Cognitive Burden (ACB) scale

Uses FHIR demographics to confirm the patient is ≥65 (otherwise Beers may
not apply) and reads the active medication list from FHIR.
"""

import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from shared.fhir_hook import extract_fhir_context
from shared.tools import (
    get_active_medications,
    get_patient_demographics,
)

from ._local_tools import anticholinergic_burden, beers_criteria_lookup
from ._mcp_loader import get_mcp_toolset_or_none

_model = LiteLlm(model=os.getenv("SAFERX_GERIATRICIAN_MODEL", "gemini/gemini-2.5-flash"))

_mcp_tools = get_mcp_toolset_or_none(
    tool_filter=["beers_criteria_lookup", "anticholinergic_burden"]
)

_tools = [
    get_patient_demographics,
    get_active_medications,
]
if _mcp_tools is not None:
    _tools.append(_mcp_tools)
else:
    _tools.extend([beers_criteria_lookup, anticholinergic_burden])


geriatrician_agent = Agent(
    name="geriatrician_specialist",
    model=_model,
    description=(
        "Geriatric medicine specialist who reviews medication lists for older adults "
        "against the AGS Beers Criteria 2023 and the Anticholinergic Cognitive Burden scale."
    ),
    instruction=(
        "You are a board-certified geriatrician on a polypharmacy safety council. "
        "Your job is to review the patient's medication list and identify safety concerns "
        "specific to older adults.\n\n"
        "Process — strict order:\n"
        "1. Call get_patient_demographics to confirm the patient's age. "
        "Beers Criteria are written for adults ≥65; if the patient is younger, still "
        "produce a verdict table but note in the Note that Beers may not apply.\n"
        "2. Call get_active_medications. ALWAYS proceed with whatever the tool returns. "
        "If the response's `source` is 'most_recent_any_status', mention that briefly "
        "in your Note — but still review the meds. Only halt if `count` is 0.\n"
        "3. For each medication, call beers_criteria_lookup. Collect any matches.\n"
        "4. Call anticholinergic_burden ONCE with the full list of generic names.\n"
        "5. Return a response in EXACTLY this format:\n\n"
        "## Geriatrician Verdicts\n"
        "Markdown table with columns: Medication | Verdict | Reason\n"
        "Use these EXACT verdict tokens:\n"
        "  🛑 STOP        — high-severity Beers / strong Avoid recommendation\n"
        "  ⚠️ REDUCE      — Beers caution / dose reduction advised\n"
        "  ⚠️ SUBSTITUTE  — flagged for class-switch (e.g., anticholinergic alternative)\n"
        "  ✓ CONTINUE    — no Beers/ACB concern\n"
        "  — N/A          — outside this specialty\n"
        "Include EVERY active medication, even ones without concerns (mark CONTINUE).\n"
        "Reason column: ≤10 words, e.g. 'Beers HIGH: anticholinergic, fall risk'.\n\n"
        "## Anticholinergic Cognitive Burden\n"
        "  - Total ACB score: <number>\n"
        "  - Risk level: <none/increased/significant>\n"
        "  - Top contributors: <medication (score), ...>\n\n"
        "## Geriatrician's Note (≤4 sentences)\n"
        "Brief clinical reasoning with citations like '[AGS Beers 2023]' or '[ACB Scale, Boustani 2008]'.\n\n"
        "Rules: Cite guidelines by name. Never invent medications or guideline entries — "
        "only report what the tools return. The council orchestrator may have bound the "
        "patient via inline context (source='inline') instead of FHIR — treat both as "
        "valid sources of truth. Only return an error if both are absent (count=0 AND "
        "no inline patient data)."
    ),
    tools=_tools,
    before_model_callback=extract_fhir_context,
)
