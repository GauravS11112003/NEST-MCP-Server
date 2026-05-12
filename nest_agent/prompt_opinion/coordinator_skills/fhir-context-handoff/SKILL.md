---
id: fhir-context-handoff
name: fhir-context-handoff
description: >-
  Operate with Prompt Opinion FHIR context when enabled: honor mother and infant
  patient scope, prefer chart-derived conditions, medications, and observations
  over inference, request missing subject IDs or authorization clearly, and relay
  a dyad-shaped summary to the next step without fabricating undocumented vitals,
  scores, or orders.
tags:
  - fhir
  - interoperability
  - patient-context
  - dyad
---

# FHIR context handoff

## When this skill applies

Use when the workspace or session provides **FHIR server URL**, **authorization**, and **patient identifier(s)** per Prompt Opinion’s FHIR context extension, or when the user indicates data should come from **the connected chart** rather than free text.

## Behavior

- Assume chart data may be **split across two subjects** (mother `Patient` and infant `Patient`). If only one patient is in context, **name the gap** and ask whether both charts can be linked or whether the user will paste a consolidated dyad summary.
- Prefer **structured facts from FHIR** (conditions, medication requests, observations for BP, mood scores, bilirubin, weights) over guesses from narrative.
- If **FHIR context is required** for this agent configuration and is missing, **stop and tell the user** what must be supplied (server, token if applicable, patient id(s)) instead of fabricating vitals or meds.
- When consulting another agent, **carry forward** enough structured detail that the delegate can run without silent omissions—especially **infant-specific** data.

## Privacy

Do not echo raw tokens or full PHI bundles into general logs; summarize at an appropriate level for the chat transcript.
