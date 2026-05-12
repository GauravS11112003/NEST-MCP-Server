---
id: urgent-maternal-newborn-escalation
name: urgent-maternal-newborn-escalation
description: >-
  First-pass safety triage for time-sensitive postpartum and neonatal
  presentations; separates immediate escalation from scheduled pathways and
  returns structured cues for the calling agent or NEST handoff.
tags:
  - triage
  - emergency
  - postpartum
  - newborn
  - safety
---

# Urgent maternal–newborn escalation

## When this skill applies

Another agent or workflow routes a case that may require **same-day** obstetric, psychiatric, or pediatric escalation.

## Behavior

- Screen for **high-acuity** maternal patterns (e.g., severe-range BP with neuro symptoms, uncontrolled bleeding, sepsis concern) and **neonatal** patterns (e.g., respiratory distress, fever, poor feeding, marked lethargy, jaundice with red flags per protocol context).
- Output a short **action ladder**: what must happen **now** (per local protocol wording), what to **measure** next, and what can wait for **scheduled** follow-up—without exceeding the product’s medical scope.
- When stable enough for planning, offer to **chain** into `nest-a2a-transition-plan` for a documented transition package.
