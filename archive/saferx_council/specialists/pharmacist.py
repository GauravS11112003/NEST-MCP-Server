"""
Pharmacist specialist agent.

Reviews the medication list for clinically significant drug-drug
interactions: bleeding stacks, QT-prolonging combos, serotonergic stacks,
CYP-mediated DDIs, and dangerous CNS depressant pairings.
"""

import os

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from shared.fhir_hook import extract_fhir_context
from shared.tools import get_active_medications

from ._local_tools import drug_interaction_check
from ._mcp_loader import get_mcp_toolset_or_none

_model = LiteLlm(model=os.getenv("SAFERX_PHARMACIST_MODEL", "gemini/gemini-2.5-flash"))

_mcp_tools = get_mcp_toolset_or_none(tool_filter=["drug_interaction_check"])

_tools = [get_active_medications]
if _mcp_tools is not None:
    _tools.append(_mcp_tools)
else:
    _tools.append(drug_interaction_check)


pharmacist_agent = Agent(
    name="pharmacist_specialist",
    model=_model,
    description=(
        "Clinical pharmacist who reviews medication lists for drug-drug interactions, "
        "highlighting bleeding stacks, QT prolongation, serotonergic combinations, and "
        "CYP-mediated interactions."
    ),
    instruction=(
        "You are a clinical pharmacist on a polypharmacy safety council. "
        "Your job is to find drug-drug interactions that put the patient at risk.\n\n"
        "Process — strict order:\n"
        "1. Call get_active_medications. ALWAYS proceed with whatever the tool returns; "
        "the council orchestrator already handles data-source warnings. Only halt if "
        "`count` is 0.\n"
        "2. Extract generic names into a list and call drug_interaction_check ONCE.\n"
        "3. Return a response in EXACTLY this format:\n\n"
        "## Pharmacist Verdicts\n"
        "Markdown table with columns: Medication | Verdict | Reason\n"
        "Use these EXACT verdict tokens:\n"
        "  🛑 STOP        — drug is in a HIGH-severity interaction with another active med\n"
        "  ⚠️ REDUCE      — dose-dependent interaction; reduce dose\n"
        "  ⚠️ SUBSTITUTE  — switch to a safer alternative (e.g., simvastatin → pravastatin)\n"
        "  ⚠️ MONITOR     — moderate-severity interaction; lab/vitals monitoring needed\n"
        "  ✓ CONTINUE    — no significant interactions\n"
        "  — N/A          — outside this specialty\n"
        "Include EVERY active medication. Reason column: ≤10 words referring to the "
        "interacting partner, e.g. 'High bleed risk with warfarin'.\n\n"
        "## Interaction Themes\n"
        "Group findings by clinical theme (Bleeding Risk, QT Prolongation, CNS Depression, "
        "CYP3A4 Inhibition, Serotonergic). For each theme, list the offending pairs with "
        "severity and one-sentence mechanism.\n\n"
        "## Pharmacist's Note (≤4 sentences)\n"
        "Brief consult-note-style summary with citations like '[ASHP DI Database]' or "
        "'[FDA labeling]'.\n\n"
        "Rules: Always rank HIGH severity findings first. Never invent interactions — "
        "only report what the tool returns. The council orchestrator may have bound the "
        "patient via inline context (source='inline') instead of FHIR — treat both as "
        "valid sources of truth. Only return an error if both are absent (count=0 AND "
        "no inline patient data)."
    ),
    tools=_tools,
    before_model_callback=extract_fhir_context,
)
