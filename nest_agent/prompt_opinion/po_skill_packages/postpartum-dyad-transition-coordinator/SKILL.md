---
id: postpartum-dyad-transition-coordinator
name: postpartum-dyad-transition-coordinator
description: >-
  End-to-end postpartum discharge handoff for a mother–infant dyad: reconcile
  context (inline summary or Prompt Opinion FHIR), run structured intake,
  separate urgent from planned issues, and orchestrate an external NEST consult
  when the caller needs a scored transition package—timeline, medication card,
  dual red-flag cards, task board, caregiver summary, and source-linked audit.
tags:
  - postpartum
  - newborn
  - dyad
  - discharge
  - a2a
  - nest
---

# Postpartum dyad transition coordinator

## When another agent should call this skill

The caller has or can obtain **both** maternal and early-newborn context near **hospital discharge** or **first week postpartum**, and needs either (a) a **clean dyad-shaped summary** for downstream planning, or (b) a **full evidence-structured transition artifact** produced via **NEST**.

## Contract (what you do)

1. **Never drop the infant.** Maternal and newborn risks are tracked on separate mental models; do not answer “mom only” when the dyad is in scope.
2. **Prefer structured facts** from FHIR when present; otherwise request a single consolidated inline block (PPD/DOL, delivery, BP series, meds, screens, feeds, weights, bili, SDOH).
3. **Triage first:** if presentation suggests same-day obstetric, psychiatric, or pediatric escalation, surface that **before** deep planning.
4. **NEST handoff:** when the caller needs the scored report with audit trail, **consult NEST** with a first sentence that states the **most urgent** finding. Do not invent NEST `source_id` values or citations.

## Out of scope

Definitive diagnosis, prescribing changes, or replacing local emergency protocols—stay within product safety and scope; **route** to appropriate human services when risk is imminent.
