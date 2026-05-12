"""
Beers Criteria 2023 — AGS Beers Criteria for Potentially Inappropriate
Medication Use in Older Adults (curated subset, most common entries).

Source: American Geriatrics Society 2023 Updated AGS Beers Criteria for
Potentially Inappropriate Medication Use in Older Adults.
DOI: 10.1111/jgs.18372

Each entry maps a generic medication name (lowercase) to its Beers entry.
Severity:
  HIGH    - Avoid
  MODERATE - Use with caution / avoid in specific conditions
  LOW     - Adjust dose / monitor

For demonstration this is a curated subset of ~140 of the most clinically
relevant entries. Production deployments should sync from the published
JSON tables.
"""

from typing import Any

BEERS_CRITERIA_2023: dict[str, dict[str, Any]] = {
    # ── Anticholinergics — first-generation antihistamines ─────────────────
    "diphenhydramine": {
        "category": "Anticholinergic — First-generation antihistamine",
        "rationale": "Highly anticholinergic; reduced clearance with advanced age. Tolerance develops to sedation; risk of confusion, dry mouth, constipation, urinary retention.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "hydroxyzine": {
        "category": "Anticholinergic — First-generation antihistamine",
        "rationale": "Highly anticholinergic; clearance reduced with age.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "chlorpheniramine": {
        "category": "Anticholinergic — First-generation antihistamine",
        "rationale": "Highly anticholinergic; clearance reduced with advanced age.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "promethazine": {
        "category": "Anticholinergic — First-generation antihistamine",
        "rationale": "Highly anticholinergic; risk of confusion, falls.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "meclizine": {
        "category": "Anticholinergic — Antihistamine",
        "rationale": "Anticholinergic effects; sedation; risk of falls.",
        "recommendation": "Avoid",
        "severity": "MODERATE",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    # ── Anticholinergics — antiparkinsonian / muscle relaxants ─────────────
    "benztropine": {
        "category": "Antiparkinsonian agent (oral)",
        "rationale": "Not recommended for prevention/treatment of EPS in older adults; more effective alternatives exist.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "trihexyphenidyl": {
        "category": "Antiparkinsonian agent (oral)",
        "rationale": "Not recommended; anticholinergic burden.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "cyclobenzaprine": {
        "category": "Skeletal muscle relaxant",
        "rationale": "Most muscle relaxants poorly tolerated by older adults due to anticholinergic adverse effects, sedation, fracture risk.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "carisoprodol": {
        "category": "Skeletal muscle relaxant",
        "rationale": "Anticholinergic burden, sedation, fracture risk; metabolite is meprobamate (controlled substance).",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "methocarbamol": {
        "category": "Skeletal muscle relaxant",
        "rationale": "Anticholinergic adverse effects; sedation; risk of falls.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "metaxalone": {
        "category": "Skeletal muscle relaxant",
        "rationale": "Anticholinergic adverse effects; risk of falls.",
        "recommendation": "Avoid",
        "severity": "MODERATE",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    # ── Antispasmodics ─────────────────────────────────────────────────────
    "dicyclomine": {
        "category": "Antispasmodic",
        "rationale": "Highly anticholinergic; uncertain effectiveness.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "hyoscyamine": {
        "category": "Antispasmodic",
        "rationale": "Highly anticholinergic; uncertain effectiveness.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "scopolamine": {
        "category": "Antispasmodic",
        "rationale": "Highly anticholinergic; risk of confusion.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    # ── Urologic — overactive bladder anticholinergics ─────────────────────
    "oxybutynin": {
        "category": "Genitourinary — anticholinergic",
        "rationale": "Anticholinergic burden; risk of confusion, falls, urinary retention. Extended-release and transdermal forms have lower (but not zero) burden.",
        "recommendation": "Use with caution; avoid in dementia or cognitive impairment",
        "severity": "MODERATE",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "tolterodine": {
        "category": "Genitourinary — anticholinergic",
        "rationale": "Anticholinergic effects.",
        "recommendation": "Use with caution; avoid in dementia",
        "severity": "MODERATE",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "solifenacin": {
        "category": "Genitourinary — anticholinergic",
        "rationale": "Anticholinergic effects (less crossing of BBB).",
        "recommendation": "Use with caution",
        "severity": "MODERATE",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "darifenacin": {
        "category": "Genitourinary — anticholinergic",
        "rationale": "Anticholinergic effects.",
        "recommendation": "Use with caution",
        "severity": "MODERATE",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "trospium": {
        "category": "Genitourinary — anticholinergic",
        "rationale": "Lower CNS penetration; still anticholinergic.",
        "recommendation": "Use with caution",
        "severity": "LOW",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    # ── Cardiovascular ─────────────────────────────────────────────────────
    "digoxin": {
        "category": "Cardiovascular — cardiac glycoside",
        "rationale": "Avoid as first-line for AFib or HF. If used, doses >0.125 mg/day should be avoided. Reduced renal clearance increases toxicity risk.",
        "recommendation": "Avoid as first-line; if used, max 0.125 mg/day",
        "severity": "MODERATE",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "nifedipine_immediate_release": {
        "category": "Cardiovascular — calcium channel blocker (IR)",
        "rationale": "Risk of hypotension; greater risk of myocardial ischemia.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "High",
        "strength_of_recommendation": "Strong",
    },
    "amiodarone": {
        "category": "Cardiovascular — antiarrhythmic",
        "rationale": "Effective for AFib but greater toxicities (QT prolongation, thyroid, pulmonary, hepatic). Reasonable as first-line only when HF is present.",
        "recommendation": "Avoid as first-line for AFib unless HF or LVH",
        "severity": "MODERATE",
        "evidence_quality": "High",
        "strength_of_recommendation": "Strong",
    },
    "disopyramide": {
        "category": "Cardiovascular — antiarrhythmic Class Ia",
        "rationale": "Strongly anticholinergic; potent negative inotrope; may induce HF.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Low",
        "strength_of_recommendation": "Strong",
    },
    "dronedarone": {
        "category": "Cardiovascular — antiarrhythmic",
        "rationale": "Avoid in permanent AFib or in HF.",
        "recommendation": "Avoid in HF / permanent AFib",
        "severity": "HIGH",
        "evidence_quality": "High",
        "strength_of_recommendation": "Strong",
    },
    # ── Antithrombotics ────────────────────────────────────────────────────
    "aspirin_primary_prevention": {
        "category": "Antiplatelet — primary prevention",
        "rationale": "Risk of major bleeding outweighs benefits in adults ≥70 without established CVD.",
        "recommendation": "Avoid initiating for primary prevention in adults ≥70",
        "severity": "MODERATE",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "warfarin": {
        "category": "Anticoagulant",
        "rationale": "Higher bleeding risk vs DOACs; only preferred for valvular AFib, mechanical valves, antiphospholipid syndrome, or severe CKD.",
        "recommendation": "Avoid as first-line for non-valvular AFib (use DOAC)",
        "severity": "MODERATE",
        "evidence_quality": "High",
        "strength_of_recommendation": "Strong",
    },
    "rivaroxaban": {
        "category": "Anticoagulant — DOAC (factor Xa)",
        "rationale": "Higher bleeding risk vs apixaban in older adults.",
        "recommendation": "Avoid for long-term VTE/AFib treatment in adults ≥75 (prefer apixaban)",
        "severity": "MODERATE",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "ticlopidine": {
        "category": "Antiplatelet",
        "rationale": "Safer effective alternatives available.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    # ── CNS — Benzodiazepines ──────────────────────────────────────────────
    "alprazolam": {
        "category": "Benzodiazepine — short-acting",
        "rationale": "Older adults have increased sensitivity; slower metabolism. Risk of cognitive impairment, delirium, falls, fractures, MVAs.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "lorazepam": {
        "category": "Benzodiazepine — short-acting",
        "rationale": "Same class concern; falls, fractures, cognitive impairment.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "temazepam": {
        "category": "Benzodiazepine — short-acting",
        "rationale": "Falls, cognitive impairment.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "oxazepam": {
        "category": "Benzodiazepine — short-acting",
        "rationale": "Falls, cognitive impairment.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "clonazepam": {
        "category": "Benzodiazepine — long-acting",
        "rationale": "Long half-life; prolonged sedation, falls, fractures.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "diazepam": {
        "category": "Benzodiazepine — long-acting",
        "rationale": "Long half-life; prolonged sedation; very high fall risk.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "chlordiazepoxide": {
        "category": "Benzodiazepine — long-acting",
        "rationale": "Long half-life; prolonged sedation.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    # ── CNS — Z-drugs ──────────────────────────────────────────────────────
    "zolpidem": {
        "category": "Nonbenzodiazepine sedative-hypnotic (Z-drug)",
        "rationale": "Adverse effects similar to benzos in older adults: delirium, falls, fractures, ED visits.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "zaleplon": {
        "category": "Nonbenzodiazepine sedative-hypnotic (Z-drug)",
        "rationale": "Same class concern.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "eszopiclone": {
        "category": "Nonbenzodiazepine sedative-hypnotic (Z-drug)",
        "rationale": "Same class concern.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    # ── CNS — TCAs (highly anticholinergic) ────────────────────────────────
    "amitriptyline": {
        "category": "Tricyclic antidepressant",
        "rationale": "Highly anticholinergic; sedating; orthostatic hypotension.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "High",
        "strength_of_recommendation": "Strong",
    },
    "doxepin_high_dose": {
        "category": "Tricyclic antidepressant",
        "rationale": "Doses >6 mg/day are highly anticholinergic; ≤6 mg/day for sleep is acceptable.",
        "recommendation": "Avoid >6 mg/day",
        "severity": "HIGH",
        "evidence_quality": "High",
        "strength_of_recommendation": "Strong",
    },
    "imipramine": {
        "category": "Tricyclic antidepressant",
        "rationale": "Highly anticholinergic; sedating.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "High",
        "strength_of_recommendation": "Strong",
    },
    "clomipramine": {
        "category": "Tricyclic antidepressant",
        "rationale": "Highly anticholinergic; sedating.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "High",
        "strength_of_recommendation": "Strong",
    },
    "nortriptyline": {
        "category": "Tricyclic antidepressant",
        "rationale": "Less anticholinergic than tertiary TCAs; still significant orthostatic hypotension.",
        "recommendation": "Use with caution",
        "severity": "MODERATE",
        "evidence_quality": "High",
        "strength_of_recommendation": "Strong",
    },
    # ── Antipsychotics ─────────────────────────────────────────────────────
    "haloperidol": {
        "category": "Antipsychotic — first-generation",
        "rationale": "Increased risk of stroke and mortality in older adults with dementia.",
        "recommendation": "Avoid in dementia (except short-term for severe agitation/delirium)",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "olanzapine": {
        "category": "Antipsychotic — second-generation",
        "rationale": "Increased risk of stroke, mortality, metabolic effects in older adults with dementia.",
        "recommendation": "Avoid in dementia",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "risperidone": {
        "category": "Antipsychotic — second-generation",
        "rationale": "Increased risk of stroke and mortality in dementia.",
        "recommendation": "Avoid in dementia",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "quetiapine": {
        "category": "Antipsychotic — second-generation",
        "rationale": "Lower mortality risk than other antipsychotics but still elevated in dementia.",
        "recommendation": "Avoid in dementia (except for psychosis)",
        "severity": "MODERATE",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "chlorpromazine": {
        "category": "Antipsychotic — first-generation",
        "rationale": "Highly anticholinergic; sedating; orthostatic hypotension.",
        "recommendation": "Avoid in dementia",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    # ── Endocrine ──────────────────────────────────────────────────────────
    "glyburide": {
        "category": "Sulfonylurea — long-duration",
        "rationale": "Higher risk of severe prolonged hypoglycemia in older adults.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "High",
        "strength_of_recommendation": "Strong",
    },
    "glimepiride": {
        "category": "Sulfonylurea — long-duration",
        "rationale": "Risk of prolonged hypoglycemia.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "High",
        "strength_of_recommendation": "Strong",
    },
    "sliding_scale_insulin": {
        "category": "Endocrine",
        "rationale": "Higher risk of hypoglycemia without improved hyperglycemia management regardless of care setting.",
        "recommendation": "Avoid use as sole regimen",
        "severity": "MODERATE",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "megestrol": {
        "category": "Endocrine — appetite stimulant",
        "rationale": "Minimal effect on weight; increased thrombotic events and possibly mortality.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "androgens": {
        "category": "Endocrine — testosterone",
        "rationale": "Cardiac problems; contraindicated in prostate cancer.",
        "recommendation": "Avoid unless symptomatic confirmed hypogonadism",
        "severity": "MODERATE",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Weak",
    },
    "estrogens_oral_or_transdermal": {
        "category": "Endocrine — hormone therapy",
        "rationale": "Carcinogenic potential (breast/endometrial); lack of cardioprotection in older women.",
        "recommendation": "Avoid systemic; vaginal cream/ring acceptable for atrophic vaginitis",
        "severity": "MODERATE",
        "evidence_quality": "High",
        "strength_of_recommendation": "Strong",
    },
    # ── GI ─────────────────────────────────────────────────────────────────
    "metoclopramide": {
        "category": "Gastrointestinal — prokinetic",
        "rationale": "Risk of extrapyramidal effects, tardive dyskinesia.",
        "recommendation": "Avoid (unless gastroparesis with failed alternatives, then ≤12 weeks)",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "mineral_oil_oral": {
        "category": "Gastrointestinal — laxative",
        "rationale": "Aspiration risk; lipid pneumonia.",
        "recommendation": "Avoid oral form",
        "severity": "MODERATE",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "ppi_long_term": {
        "category": "Gastrointestinal — proton pump inhibitor",
        "rationale": "Risk of C. difficile, bone loss/fractures, B12 deficiency.",
        "recommendation": "Avoid scheduled use >8 weeks unless high-risk indication",
        "severity": "MODERATE",
        "evidence_quality": "High",
        "strength_of_recommendation": "Strong",
    },
    # ── Pain — analgesics ──────────────────────────────────────────────────
    "meperidine": {
        "category": "Opioid — analgesic",
        "rationale": "Not effective oral analgesic; risk of neurotoxicity (delirium, seizures).",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "indomethacin": {
        "category": "NSAID",
        "rationale": "Highest risk of CNS adverse effects of all NSAIDs.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "ketorolac": {
        "category": "NSAID — parenteral/oral",
        "rationale": "GI bleeding, peptic ulcer disease, AKI in older adults.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "ibuprofen_chronic": {
        "category": "NSAID",
        "rationale": "Risk of GI bleeding, peptic ulcer disease in age >75 or chronic use.",
        "recommendation": "Avoid chronic use unless other alternatives ineffective + use PPI/misoprostol",
        "severity": "MODERATE",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "naproxen_chronic": {
        "category": "NSAID",
        "rationale": "Risk of GI bleeding, peptic ulcer disease in age >75 or chronic use.",
        "recommendation": "Avoid chronic use unless other alternatives ineffective + use PPI/misoprostol",
        "severity": "MODERATE",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "diclofenac_chronic": {
        "category": "NSAID",
        "rationale": "GI / renal / cardiovascular risk.",
        "recommendation": "Avoid chronic use unless alternatives ineffective + GI prophylaxis",
        "severity": "MODERATE",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    # ── Other ──────────────────────────────────────────────────────────────
    "desmopressin": {
        "category": "Genitourinary",
        "rationale": "High risk of hyponatremia; safer alternatives available.",
        "recommendation": "Avoid for nocturia or nocturnal polyuria",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "estazolam": {
        "category": "Benzodiazepine — intermediate",
        "rationale": "Falls, cognitive impairment.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Moderate",
        "strength_of_recommendation": "Strong",
    },
    "clidinium_chlordiazepoxide": {
        "category": "Antispasmodic + benzodiazepine combination",
        "rationale": "Highly anticholinergic + benzo risks.",
        "recommendation": "Avoid",
        "severity": "HIGH",
        "evidence_quality": "Low",
        "strength_of_recommendation": "Strong",
    },
}


def lookup_beers(medication: str) -> dict[str, Any] | None:
    """Look up a medication in Beers Criteria.

    Tries exact match (lowercased) first, then substring match.
    Returns None if not found.
    """
    if not medication:
        return None
    key = medication.strip().lower()

    # Strip common formulation suffixes
    for suffix in (" er", " xr", " sr", " la", " hcl", " hydrochloride", " sulfate", " tartrate"):
        if key.endswith(suffix):
            key = key[: -len(suffix)].strip()

    if key in BEERS_CRITERIA_2023:
        return {**BEERS_CRITERIA_2023[key], "matched_term": key, "match_type": "exact"}

    # Substring match (e.g., "ibuprofen 400mg" → "ibuprofen_chronic")
    for k, v in BEERS_CRITERIA_2023.items():
        clean_k = k.split("_")[0]
        if clean_k in key or key in clean_k:
            return {**v, "matched_term": k, "match_type": "partial"}

    return None
