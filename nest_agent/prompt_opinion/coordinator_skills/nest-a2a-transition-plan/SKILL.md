---
id: nest-a2a-transition-plan
name: nest-a2a-transition-plan
description: >-
  Orchestrate a consult to the external NEST agent to produce a full postpartum
  transition artifact: transition score, 7-day dual timeline, three-lane
  medication card, separate maternal and newborn red-flag cards, care-team task
  board, caregiver-friendly summary, and a source-linked audit trail when the
  caller needs an evidence-structured handoff rather than conversational advice
  alone.
tags:
  - a2a
  - nest
  - postpartum
  - care-coordination
  - discharge
---

# NEST A2A transition plan

## When this skill applies

Use when the user or care team needs a **discharge-transition–style artifact** that is **explicitly evidence-traced**, not a conversational summary only.

## Behavior

- **Consult** the registered external agent **NEST** (see your deployment’s agent card URL) with a message that includes either **complete FHIR-backed context** for mother and infant or a **single inline dyad block** (vitals, meds, screens, feeding, bili, SDOH, timing).
- Ask NEST to return its **full structured report** (score, timeline, medication card, dual red-flag cards, task board, caregiver summary, audit log).
- Your role is **orchestration and synthesis for the user**: present NEST’s output faithfully; only compress or clarify wording if the product UI requires a short wrapper.

## Consult prompt alignment

If a custom **Consult Prompt** is configured, follow it for how to frame urgency (e.g., severe BP, hemorrhage, self-harm, high-risk bilirubin) in the **first sentence** of the consult message.

## Limits

Do not claim NEST ran if consultation did not complete; do not invent **source IDs** or guideline citations that NEST did not provide.
