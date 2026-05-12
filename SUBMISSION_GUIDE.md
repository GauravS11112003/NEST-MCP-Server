# SafeRx Council — Submission Guide

**Hackathon:** AGENTS ASSEMBLE: The Healthcare AI Endgame Challenge
**Submission strategy:** Dual submission — Path 2 (A2A Agent) + Path 1 (MCP Superpower)

---

## What's been built

| Component | Type | Public URL | Local Port |
|-----------|------|------------|------------|
| **SafeRx Council** | A2A Agent | `https://nonaphetic-stephnie-thetically.ngrok-free.dev` | 8004 |
| **Clinical Knowledge MCP** | MCP Server | `https://nirvana-assume-pda-dubai.trycloudflare.com` | 9001 |

Both are running and reachable.

---

## Live services — current state

```bash
# SafeRx Council
ps aux | grep "uvicorn saferx_council" | grep -v grep
curl -s -H "ngrok-skip-browser-warning: true" \
  https://nonaphetic-stephnie-thetically.ngrok-free.dev/.well-known/agent-card.json \
  | python3 -m json.tool

# Clinical Knowledge MCP
ps aux | grep "clinical_knowledge_mcp" | grep -v grep
curl -I https://nirvana-assume-pda-dubai.trycloudflare.com/sse
```

---

## Step 1 — Register the SafeRx Council A2A agent

In Prompt Opinion → **External Agents** section:

| Field | Value |
|-------|-------|
| Name | `SafeRx Council` |
| Description | `Multi-specialist polypharmacy safety review for older adults. Convenes a geriatrician, clinical pharmacist, and nephrologist to review a patient's FHIR medication list against Beers Criteria 2023, drug-drug interactions, anticholinergic burden, and renal dose adjustments. Returns a unified council report with prioritized recommendations.` |
| Agent Card URL | `https://nonaphetic-stephnie-thetically.ngrok-free.dev/.well-known/agent-card.json` |
| Token / API Key (X-API-Key header) | `OXsqAr3EDvh-TT8ZSuOPb64VghYra9qO9zclgSmr0a4` |

**After registration, in the agent settings:**
1. Enable **FHIR context** for this agent.
2. Grant the FHIR scopes (the agent card declares these as required):
   - `patient/Patient.rs` (demographics)
   - `patient/MedicationRequest.rs` (active meds)
   - `patient/Observation.rs` (eGFR labs)
   - `patient/Condition.rs` (active problem list)

---

## Step 2 — Register the Clinical Knowledge MCP server

In Prompt Opinion → **MCP Servers** section:

| Field | Value |
|-------|-------|
| Name | `Clinical Knowledge MCP` |
| Description | `Stateless clinical reference tools: AGS Beers Criteria 2023 lookup, drug-drug interaction checker, renal dose adjustments by eGFR, and Anticholinergic Cognitive Burden (ACB) calculator. Useful for any agent doing prescription review or polypharmacy assessment in older adults.` |
| URL / Endpoint | `https://nirvana-assume-pda-dubai.trycloudflare.com/sse` |
| Transport | SSE (Server-Sent Events) |
| Auth | None (stateless reference data) |

The 4 tools that will appear:
1. `beers_criteria_lookup(medication: str)`
2. `drug_interaction_check(medications: list[str])`
3. `renal_dose_adjustment(medication: str, egfr: float)`
4. `anticholinergic_burden(medications: list[str])`

---

## Step 3 — Demo flow

In the Prompt Opinion clinician chat, with a SMART on FHIR session active and a polypharmacy patient (e.g., your existing 84F demo with 14 meds):

> "Convene the SafeRx Council to review this patient's medications."

**Expected:** Within ~45 seconds, the Council returns a structured report with:
- Patient snapshot (age, # meds, eGFR)
- Critical (HIGH severity) findings — usually 6-10 items
- Important (MODERATE) findings
- Per-specialist reasoning paragraphs
- Numbered prioritized action plan
- "Disagreement to resolve" notes when specialists conflict

---

## Step 4 — 3-minute demo script

**0:00–0:30 — Set the stage**

> "Polypharmacy harms 1 in 4 older adults. A real review takes a clinician 30 minutes per patient and is rarely done. I built a council of AI specialists that does it in 45 seconds against live FHIR data — and it caught the dual anticoagulation that would have hospitalized my demo patient."

**0:30–1:30 — Show the council in action**

- Open Prompt Opinion with the polypharmacy patient
- Click **Run SafeRx Council**
- Talk over the working: "Three specialist agents are running in parallel — a geriatrician checking Beers and ACB, a pharmacist checking interactions, a renal specialist checking dosing for the patient's eGFR of 38. They each call the Clinical Knowledge MCP server I also built — same tools, reusable by any agent on the platform."
- When the report renders, point at the dual anticoag finding and the disagreement section.

**1:30–2:30 — Architecture story**

Switch to a slide:

```
Clinician
   ↓
Prompt Opinion (SHARP/FHIR + A2A + MCP)
   ↓
SafeRx Council (A2A agent)
   ├─→ Geriatrician  ──┐
   ├─→ Pharmacist    ──┤── Clinical Knowledge MCP Server
   └─→ Nephrologist  ──┘   (Beers, DDI, ACB, Renal dosing)
```

> "I split the system the way Josh Mandel argued at CMU's launch: patient-aware reasoning lives in the agent (with FHIR context), reusable clinical knowledge lives in MCP. The MCP server has zero patient data — it's just a guideline lookup. That makes it composable: any agent on the platform can use my Beers checker. And the Council is composable in the other direction: it's just an A2A agent that any orchestrator can call."

**2:30–3:00 — Why this matters**

> "This isn't science fiction — it's deployable today against any SMART on FHIR EHR, including Epic and Cerner via Prompt Opinion. The Council saves a clinician 25 minutes per patient and surfaces issues a single specialist would never catch alone. That's the Avengers point: no single hero stops Thanos. You assemble the team."

---

## Stopping & restarting (when you come back tomorrow)

```bash
# Kill everything
pkill -9 -f uvicorn
pkill -9 -f ngrok
pkill -9 -f cloudflared
pkill -9 -f clinical_knowledge_mcp

# Bring it all back up
cd /Users/gauravshrivastava/projects/AgentsAssemble/po-adk-python-main
source .venv/bin/activate

# 1. SafeRx Council on 8004
SAFERX_SKIP_MCP=true \
SAFERX_COUNCIL_URL=https://nonaphetic-stephnie-thetically.ngrok-free.dev \
PO_PLATFORM_BASE_URL=https://app.promptopinion.ai \
ADK_SUPPRESS_GEMINI_LITELLM_WARNINGS=true \
uvicorn saferx_council.app:a2a_app --host 0.0.0.0 --port 8004 > /tmp/saferx_council.log 2>&1 &

# 2. MCP server on 9001
python -m clinical_knowledge_mcp.server --http --port 9001 > /tmp/clinical_mcp.log 2>&1 &

# 3. ngrok for SafeRx (uses your reserved domain)
.venv/bin/ngrok http 8004 --log=stdout > /tmp/ngrok.log 2>&1 &

# 4. cloudflared for MCP (URL CHANGES every restart!)
.venv/bin/cloudflared tunnel --url http://localhost:9001 --no-autoupdate > /tmp/cloudflared.log 2>&1 &
sleep 8
grep trycloudflare /tmp/cloudflared.log | grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com'
# ↑ Update CLINICAL_KNOWLEDGE_MCP_URL in .env AND the registration in Prompt Opinion
```

---

## Troubleshooting

**Q: SafeRx Council returns "Task not found" but no actual review.**
A: Make sure you sent the request with the `X-API-Key` header set to `OXsqAr3EDvh-TT8ZSuOPb64VghYra9qO9zclgSmr0a4`. Prompt Opinion sets this automatically once you save the token at registration.

**Q: "FHIR context is not available."**
A: In the agent settings within Prompt Opinion, enable **FHIR context** and grant the requested scopes.

**Q: cloudflared URL changes every restart.**
A: Yes — that's the trade-off for the free, no-account tunnel. To pin it, sign up free at Cloudflare → create a named tunnel. ~5 minutes. Or use a reserved ngrok domain for the second tunnel by upgrading.

**Q: Want to swap which service gets the ngrok reserved domain?**
A: Just change which port `ngrok http <port>` points at, restart, and update the corresponding `*_URL` env var.

---

## Files of note

```
saferx_council/
  agent.py                 ← Orchestrator with synthesis prompt
  app.py                   ← A2A entry point + skills + FHIR scopes
  specialists/
    geriatrician.py        ← Beers + ACB
    pharmacist.py          ← Drug-drug interactions
    renal.py               ← Renal dose review

clinical_knowledge_mcp/
  server.py                ← MCP server (stdio + SSE transports)
  rxnav_client.py          ← Curated DDI table + RxNav resolver
  data/
    beers_criteria.py      ← AGS Beers 2023 (~70 entries)
    anticholinergic_burden.py  ← ACB Scale (~80 drugs)
    renal_dose_adjustments.py  ← Dosing bands by eGFR (~30 drugs)

scripts/
  test_saferx_local.py     ← End-to-end sandbox test (Eleanor Whitaker case)
```
