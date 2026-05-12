# NEST Hackathon Demo Script

**Goal:** Show how NEST transforms a messy, multi-patient (dyad) postpartum handoff into a structured, evidence-backed transition plan using Prompt Opinion's A2A protocol and FHIR context.

**Time:** ~3-4 minutes

---

## 🎬 Setup (Before Recording)

1. **Prompt Opinion:**
   - Have your BYO Coordinator Agent open in the Prompt Opinion UI.
   - Ensure the agent has the **NEST A2A Transition Plan** skill attached.
   - Ensure the agent is connected to the Sarah Chen FHIR patient (`32b7b48e-...`).
2. **Local Environment:**
   - NEST server running (`uvicorn nest_agent.app:a2a_app --port 8005`)
   - Ngrok tunnel active and URL updated in PO agent card settings.
3. **Screen Layout:**
   - Left side: Prompt Opinion chat interface.
   - Right side (optional): Terminal showing NEST logs, or just full screen PO.

---

## 📹 Scene 1: The Problem (0:00 - 0:45)

**Narrator/You:**
"The postpartum period is the most dangerous time for mothers and newborns, but discharge planning is often fragmented. The mother's chart and the baby's chart are separate, and guidelines from ACOG, AAP, and LactMed are hard to synthesize at the bedside."

**Action:**
Show the Prompt Opinion UI. Select the Sarah Chen patient context.

**Narrator/You:**
"Here we have Sarah Chen, Postpartum Day 2, and her infant, Baby Boy Chen. I'm using Prompt Opinion as my clinical coordinator. Instead of manually reviewing both charts and looking up guidelines, I'm going to ask my coordinator to consult NEST—our specialized Newborn & Maternal Safe Transition agent."

---

## 📹 Scene 2: The Handoff (0:45 - 1:30)

**Action:**
Type in the PO chat:
> *"Is this patient ready for discharge?"*

**Narrator/You:**
"I just ask a simple question: 'Is this patient ready for discharge?' Because we have FHIR context enabled, the Prompt Opinion coordinator knows who Sarah is. It automatically reaches out to NEST via the A2A protocol, passing along the FHIR credentials."

**Action:**
While waiting for the response, explain what NEST is doing under the hood.

**Narrator/You:**
"Behind the scenes, NEST isn't just one LLM. It's an orchestrator convening five specialists in parallel: an OB, a Pediatrician, a Lactation consultant, a Mental Health specialist, and a Social Worker. NEST pulls the maternal FHIR chart, extracts both mother and baby data, and runs it through clinical knowledge bases."

---

## 📹 Scene 3: The Reveal (1:30 - 2:45)

**Action:**
The response from NEST appears in the PO chat. Scroll through the artifact slowly.

**Narrator/You:**
"And here is the result. NEST returns a structured, visual 'Control Panel' artifact."

**Action:**
Highlight specific sections as you talk:

1. **The Disposition:** "Right at the top, we get a clear signal: Critical Hold. Not ready for routine discharge. The transition score is 0/100."
2. **The Hold Reasons:** "Why? NEST identified severe-range blood pressure for the mother (162/108), nearly 10% weight loss and jaundice for the baby, and food insecurity at home."
3. **The Task Board:** "It doesn't just flag problems; it creates an actionable 'Today Board' assigning specific tasks to OB, Pediatrics, Lactation, and Social Work."
4. **The Caregiver Summary:** "It also drafts a plain-language summary we can actually hand to Sarah."

---

## 📹 Scene 4: The Evidence Trail (2:45 - 3:15)

**Action:**
Scroll down to the 'Evidence Anchors' or 'Audit Log' section.

**Narrator/You:**
"But the most important part for clinical trust is the evidence trail. LLMs hallucinate, so NEST is designed to link every single recommendation back to a source rule."

**Action:**
Point to specific citations.

**Narrator/You:**
"You can see exactly why it flagged the blood pressure—ACOG Practice Bulletin 222. You can see the jaundice rules map to the AAP 2022 guidelines. Every decision is grounded in curated clinical knowledge."

---

## 📹 Scene 5: Conclusion (3:15 - 3:30)

**Narrator/You:**
"By combining Prompt Opinion's FHIR context and A2A routing with NEST's multi-agent clinical reasoning, we transformed a fragmented, risky discharge into a safe, auditable, and actionable care plan for the entire dyad. Thank you."

---

## 💡 Pro-Tips for Recording

- **Pacing:** The A2A call to NEST might take a few seconds. Use that time to explain the architecture (the 5 specialists). Don't just sit in silence.
- **Visuals:** The orange TUI-style markdown (`# 🟧 NEST`) looks great on screen. Make sure your PO chat window is wide enough so the ASCII boxes (`┌─ NEST CONTROL PANEL ─┐`) don't wrap awkwardly.
- **Fallback:** If the live FHIR fetch is slow during recording, NEST has a built-in demo fallback for Sarah Chen that will instantly return the correct clinical picture based on her ID.
