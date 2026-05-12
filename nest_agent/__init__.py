"""
NEST — Newborn & Maternal Safe Transition Agent.

NEST orchestrates a multi-specialist council that turns postpartum discharge
into a structured, evidence-backed transition plan for the mother-infant
dyad.

Specialists (in-process A2A sub-agents):
  • Maternal-OB       — ACOG postpartum timeline, BP / preeclampsia / hemorrhage
  • Pediatric         — AAP newborn schedule, jaundice, feeding milestones
  • Lactation         — Breastfeeding plan, LactMed medication safety
  • Mental Health     — EPDS / PHQ-9 postpartum depression screen
  • Social Worker     — SDOH screen, support, transportation, follow-up access

Outputs:
  • Transition Score (0–100)
  • 7-day mom-and-baby recovery timeline
  • Medication card (start / stop / continue)
  • Red-flag symptom cards for mom and baby
  • Care-team task board with assignees
  • Caregiver-friendly summary
  • Evidence-backed audit log linking each recommendation to its source rule

Each recommendation carries an audit `source` linking back to the FHIR
resource or guideline rule that produced it.
"""

from shared.logging_utils import configure_logging

configure_logging("nest_agent")
