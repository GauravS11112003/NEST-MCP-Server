# NEST — Newborn & Maternal Safe Transition

> A multi-specialist agent that converts postpartum discharge into a
> structured, evidence-backed transition plan for the **mother-infant
> dyad**, with every recommendation linked to its source rule.

---

## Why NEST

The United States has the worst maternal mortality among developed
nations — about 700 maternal deaths each year, 80 % preventable. The
single most dangerous window is the postpartum period: most ED visits
and deaths happen *after* discharge.

NEST attacks the gap directly. It convenes five specialists in
parallel — exactly the team that would be needed in person — and
returns a single discharge handoff that:

- scores **how complete** the transition plan is (Transition Score)
- lays out the next **7 days** for both mom and baby on a single timeline
- flags every medication for **breastfeeding safety** (LactMed L1–L5)
- prints the **mother's** and **baby's** red-flag cards
- generates a **care-team task board** with assignees and due dates
- writes a **caregiver summary** in plain language
- links every recommendation to a **source rule** (ACOG / AAP / LactMed /
  CMS) for an auditable evidence trail

---

## The Council

| Specialist | What they do | Knowledge bases |
|-----------|--------------|-----------------|
| 🩺 **Maternal-OB** | ACOG postpartum visit schedule, BP / preeclampsia / hemorrhage workup, maternal red flags | ACOG CO 736, ACOG PB 222 / 183, CDC "Hear Her" |
| 👶 **Pediatric** | AAP newborn well-baby schedule, hyperbilirubinemia, feeding milestones, vaccines, newborn red flags | AAP Bright Futures (2017, reaff. 2024), AAP Hyperbilirubinemia 2022, ACIP |
| 🤱 **Lactation** | LactMed safety category for every maternal med, feeding plan support | NIH LactMed, ABM clinical protocols, FDA codeine/tramadol warning |
| 🧠 **Mental Health** | EPDS / PHQ-9 interpretation with explicit suicide-risk handling | ACOG CO 757, USPSTF 2023 Perinatal Depression |
| 🏠 **Social Worker** | SDOH screen → structured interventions with owners and timing | CMS AHC HRSN tool, CMS postpartum coverage extension, USPSTF IPV |

Each specialist returns a verdict table where **every row carries a
`Source` column**. The orchestrator joins them into the unified report.

---

## Quick start

### 1. Run the smoke test (no server needed)

```bash
python scripts/test_nest_local.py
```

Exercises every NEST tool against the synthetic Chen dyad and prints the
findings — useful for verifying findings before recording the demo.

### 2. Start the NEST A2A server

```bash
honcho start nest          # via Procfile
# or directly:
uvicorn nest_agent.app:a2a_app --host 0.0.0.0 --port 8005
```

The agent card is served at `GET http://localhost:8005/.well-known/agent-card.json`.

### 3. Register with Prompt Opinion

Set in `.env`:

```bash
NEST_AGENT_URL=https://<your-public-url>          # e.g. ngrok URL
PO_PLATFORM_BASE_URL=https://<your-po-workspace>
```

Then add the agent card URL in the Prompt Opinion external-agents UI.

### 4. Run the demo

Open the chat with `nest_agent` selected and paste the **Demo Prompt**
from `nest_agent/DEMO_DYAD_SARAH_CHEN.md`. The orchestrator will:

1. Detect the inline dyad block, call `set_inline_dyad_context` to bind
   both patients
2. Convene the 5 specialists in parallel
3. Compute the Transition Score
4. Render the unified report with source-linked audit log

---

## Demo recording script (3 minutes)

| Time | Beat | What to say |
|------|------|-------------|
| 0:00 – 0:20 | Hook | "The US has the worst maternal mortality among developed nations. 80 % is preventable, and most of it happens after discharge — yet a typical postpartum patient gets one 6-week visit." |
| 0:20 – 0:40 | Show patient | Open `DEMO_DYAD_SARAH_CHEN.md`. "This is Sarah Chen — 32 years old, Cesarean 2 days ago for severe preeclampsia. Her BP this morning is 162 over 108. Her baby weighed 6 lb 4 at birth and is now down nearly 10 %, with a bilirubin above the AAP threshold. She lives alone, no transportation, food insecure. Her current discharge plan? *Follow up in 6 weeks.*" |
| 0:40 – 1:00 | Show the council | Run the demo prompt. Highlight the parallel specialist calls in Prompt Opinion's tool view. |
| 1:00 – 1:50 | Walk the report | "Transition score: 5 out of 100 — critical. Here's the council vote — all five specialists in one matrix. Severe-range BP fires the EMERGENCY box at the top with a 60-minute action window. Lactation flagged tramadol — FDA boxed warning, infant deaths reported. Mental health: EPDS 14, urgent referral within 7 days. Social work: transport, food, and Medicaid coverage all need to be solved before she walks out." |
| 1:50 – 2:20 | Show the audit log | Scroll to the audit log. "Every line traces to ACOG, AAP, LactMed, the CMS HRSN tool, or the FDA. This is what makes it usable in the real world — clinicians can't act on findings they can't trace." |
| 2:20 – 2:50 | Closing | "NEST scales the multi-specialist postpartum council to every dyad, in 90 seconds, with full evidence trails. It works equally well for the next patient and the next thousand." |
| 2:50 – 3:00 | Logo / link | End. |

**Money line for the closing slide:**
> *"Severe BP, a baby above the phototherapy threshold, two
> breastfeeding-incompatible medications, no transportation home — and
> the current plan would have caught none of it. NEST surfaces all of it
> in 90 seconds, every recommendation linked to a guideline."*

---

## File map

```
nest_agent/
├── README.md                     this file
├── DEMO_DYAD_SARAH_CHEN.md       synthetic dyad + demo prompt
├── __init__.py
├── agent.py                      orchestrator (NEST council)
├── app.py                        A2A entry point (uvicorn)
├── data/                         curated knowledge bases
│   ├── acog_postpartum.py        ACOG visit schedule + BP bands + red flags
│   ├── aap_newborn.py            AAP visits + Bhutani thresholds + red flags
│   ├── lactmed.py                LactMed safety (Hale categories L1–L5)
│   ├── mental_health.py          EPDS + PHQ-9 interpretation
│   └── sdoh.py                   CMS HRSN SDOH library
├── specialists/
│   ├── maternal_ob.py
│   ├── pediatric.py
│   ├── lactation.py
│   ├── mental_health.py
│   └── social_worker.py
└── tools/
    ├── dyad.py                   set_inline_dyad_context, get_dyad_*
    └── knowledge.py              ADK adapters around data/

scripts/
└── test_nest_local.py            offline smoke test (no server / FHIR needed)
```

---

## Architecture notes

### Dual-patient context

NEST extends the inline-context pattern to two linked patients (mother +
infant). The orchestrator calls `set_inline_dyad_context` once with the
full dyad payload; specialists then call `get_dyad_*(subject='mother')`
or `get_dyad_*(subject='infant')` to read each side. The same shape will
work later when we add real FHIR queries — `subject` translates to a
patient ID and the tools fan out parallel reads.

### Audit log as a first-class output

Every specialist returns its verdicts as a Markdown table where the last
column is `Source` — the rule ID that produced the verdict
(e.g., `ACOG-PB-222-SEV` or `LactMed-pseudoephedrine`). The orchestrator
joins all those source IDs into the final audit log table and maps them
to full citations. **No recommendation appears in the report without a
source.**

### Knowledge bases

The hackathon build ships curated subsets of the major guidelines. They
are intentionally small enough to be entirely client-side (no API
calls), large enough to drive a realistic demo:

- ACOG Committee Opinion 736, Practice Bulletins 222 / 183, Committee
  Opinion 757
- AAP Bright Futures, AAP Hyperbilirubinemia 2022, AAP BFM 2022
- NIH LactMed (~80 most-prescribed postpartum medications, Hale L1–L5)
- CMS Accountable Health Communities Health-Related Social Needs Tool
- CDC "Hear Her" Maternal Warning Signs panel
- USPSTF Perinatal Depression 2023, USPSTF IPV 2018

For production, replace each module with a synced live source.

---

## Prompt Opinion `SendA2AMessage` and `taskId`

The A2A stack treats each **`taskId`** as a single conversation run. After
that task reaches **`completed`** (or failed / canceled), **another**
`SendA2AMessage` must **not** reuse the same `taskId` — the server returns
`Task … is in terminal state: completed`.

For **each new** consult to NEST (or any follow-up after a finished report),
omit `taskId` from the tool arguments, or let the client allocate a **new**
id. Only reuse `taskId` when continuing the **same** in-flight task (e.g.
multi-step `input_required`). If Prompt Opinion always forwards the previous
task id, start a **new** external consult / session or ask their support to
clear task context on new sends.

---

## What's next (post-hackathon)

- Replace `inline` mode with live FHIR queries scoped per subject
  (`mother_patient_id`, `infant_patient_id`) — 1 day
- Add **Task** write-back to the FHIR server so the care-team task board
  becomes real assignments — 2 days
- Add SMS / patient-portal delivery of the caregiver summary and red-flag
  cards — 2 days
- Sync knowledge bases nightly from authoritative sources — 1 week
- Extend to **other dyad workflows**: pediatric-asthma child + caregiver,
  oncology patient + family caregiver, transplant donor + recipient — the
  dual-subject scaffolding generalizes directly.
