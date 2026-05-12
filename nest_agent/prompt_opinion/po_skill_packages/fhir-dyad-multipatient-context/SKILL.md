---
id: fhir-dyad-multipatient-context
name: fhir-dyad-multipatient-context
description: >-
  Declares multipatient readiness under Prompt Opinion FHIR context: mother and
  infant Patient scope, chart-first facts (Condition, MedicationRequest,
  Observation), explicit requests for missing subject IDs or auth, and dyad-safe
  relay to peers—without fabricating undocumented vitals, scores, or orders.
tags:
  - fhir
  - interoperability
  - dyad
  - patient-context
---

# FHIR dyad multipatient context

## When another agent should call this skill

The **parent workflow** already has or expects **FHIR-backed** sessions (Prompt Opinion FHIR extension), and the callee must **honor two subjects** (birthing parent + newborn) or clearly state what is missing.

## Contract (what you do)

1. Assume **two `Patient` contexts** may be required. If only one is bound, **name the gap** and ask for the second ID, a linked encounter, or a pasted dyad summary—do not silently merge identities.
2. Pull **Conditions, MedicationRequest, Observation** (BP, mood screens, weights, bilirubin) before narrative inference.
3. If FHIR is **required** by configuration and absent, **halt** with a precise checklist (server URL, token if applicable, patient id(s)) instead of guessing labs or meds.
4. When forwarding to **NEST** or another agent, **carry infant-shaped fields** explicitly (DOL, feeds, outputs, TSB, GA, birth weight, current weight).

## Privacy

Do not echo raw bearer tokens or full resource bundles into generic logs; summarize at chat-appropriate granularity.
