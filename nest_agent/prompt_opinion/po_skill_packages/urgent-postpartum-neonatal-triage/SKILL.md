---
id: urgent-postpartum-neonatal-triage
name: urgent-postpartum-neonatal-triage
description: >-
  Same-day safety triage for postpartum and early-newborn time windows:
  severe-range BP or neuro symptoms, hemorrhage or sepsis concern, suicidal
  ideation, newborn respiratory distress, fever, refusal to feed, or marked
  lethargy—returns escalate-now vs scheduled-follow-up signals for the parent agent.
tags:
  - triage
  - emergency
  - postpartum
  - newborn
  - safety
---

# Urgent postpartum and neonatal triage

## When another agent should call this skill

Any agent holding **partial dyad context** needs a **fast risk sort** before scheduling, billing, education, or care-management steps—or before spending tokens on a long plan.

## Contract (what you do)

1. Output a **short ladder**: **Escalate now** (with reason), **Measure / observe next** (specific vitals or checks), **Safe for scheduled pathway** (with timeframe caveats).
2. Use **only documented** symptoms and vitals from the caller’s payload; mark unknowns explicitly.
3. Align language with **local protocol** placeholders (e.g., “emergency services / labor deck / pediatric acute”) without asserting jurisdiction-specific legal duties.
4. If stable after triage, **offer** chaining to `postpartum-dyad-transition-coordinator` for a full NEST-backed transition package—do not duplicate that artifact here.

## Limits

Not a substitute for **911**, **labor triage**, or **pediatric emergency** services when the narrative supports imminent harm; the parent agent must surface crisis numbers when indicated by policy.
