"""
SafeRx Council — multi-agent polypharmacy safety review for older adults.

The Council convenes specialists who collaboratively review a patient's
medication list against guidelines:

  • Geriatrician  → Beers Criteria 2023, anticholinergic burden
  • Pharmacist     → Drug-drug interactions, QT, bleeding stacks
  • Renal          → Dose adjustments based on eGFR

Each specialist runs in-process as an ADK Agent, called via AgentTool by
the orchestrator. FHIR credentials flow through shared session state.
The clinical knowledge tools come from the Clinical Knowledge MCP server.
"""

from shared.logging_utils import configure_logging

configure_logging("saferx_council")
