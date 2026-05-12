"""
LactMed — simplified medication safety in lactation reference.

Source: NIH National Library of Medicine LactMed (Drugs and Lactation Database).
https://www.ncbi.nlm.nih.gov/books/NBK501922/

Each medication is mapped to a Hale category equivalent:

  L1  Compatible            Extensively studied; no observed adverse effects.
  L2  Probably compatible   Limited studies; minor adverse effects unlikely.
  L3  Probably compatible*  No controlled studies; risk assumed low. Default for
                            new drugs without lactation data.
  L4  Possibly hazardous    Evidence of risk; use only when benefit > risk.
  L5  Hazardous             Documented harm; contraindicated in lactation.

Curated subset of ~80 of the most commonly prescribed postpartum medications.
Production deployments should sync from LactMed nightly.
"""

from __future__ import annotations

from typing import Any


# Hale lactation categories
_LACT_CATEGORY_INTERP = {
    "L1": ("Compatible",            "Compatible with breastfeeding; extensively studied; no observed adverse effects."),
    "L2": ("Probably compatible",   "Limited studies; minor adverse effects unlikely."),
    "L3": ("Probably compatible*",  "Limited / no controlled data; risk assumed low. Monitor infant."),
    "L4": ("Possibly hazardous",    "Documented risk; use only when benefit > risk; consider alternative; monitor infant closely."),
    "L5": ("Hazardous",             "Documented harm; contraindicated in lactation. Use alternative."),
}


_LACT_DATA: dict[str, dict[str, Any]] = {
    # ── Pain / NSAID ────────────────────────────────────────────────────────
    "acetaminophen":  {"category": "L1", "rationale": "Drug of choice for analgesia in lactation. Minimal infant exposure.",                                          "source_id": "LactMed-acetaminophen"},
    "ibuprofen":      {"category": "L1", "rationale": "NSAID of choice in lactation. <1% relative infant dose.",                                                       "source_id": "LactMed-ibuprofen"},
    "naproxen":       {"category": "L3", "rationale": "Long half-life; prefer ibuprofen; case report of infant bleeding.",                                             "source_id": "LactMed-naproxen"},
    "ketorolac":      {"category": "L2", "rationale": "Short courses acceptable. Minimal milk transfer.",                                                              "source_id": "LactMed-ketorolac"},
    "celecoxib":      {"category": "L2", "rationale": "Limited data; minimal milk transfer.",                                                                          "source_id": "LactMed-celecoxib"},
    # ── Opioids ─────────────────────────────────────────────────────────────
    "oxycodone":      {"category": "L3", "rationale": "Use lowest effective dose for shortest duration. Watch infant for sedation, poor feeding.",                     "source_id": "LactMed-oxycodone"},
    "hydrocodone":    {"category": "L3", "rationale": "Limit duration ≤4 days; monitor infant for sedation and apnea.",                                                "source_id": "LactMed-hydrocodone"},
    "morphine":       {"category": "L3", "rationale": "Preferred opioid post-Cesarean. Monitor infant for sedation.",                                                  "source_id": "LactMed-morphine"},
    "codeine":        {"category": "L4", "rationale": "AVOID — CYP2D6 ultra-rapid metabolizers can produce toxic morphine; infant deaths reported.",                   "source_id": "FDA-2017-Codeine"},
    "tramadol":       {"category": "L4", "rationale": "AVOID — same FDA warning as codeine.",                                                                          "source_id": "FDA-2017-Tramadol"},
    "fentanyl":       {"category": "L2", "rationale": "Very short half-life via milk; acceptable for procedural / labor analgesia.",                                   "source_id": "LactMed-fentanyl"},
    # ── Antibiotics ─────────────────────────────────────────────────────────
    "amoxicillin":          {"category": "L1", "rationale": "Compatible. Watch for diarrhea / thrush in infant.",                                                       "source_id": "LactMed-amoxicillin"},
    "cephalexin":           {"category": "L1", "rationale": "Compatible.",                                                                                              "source_id": "LactMed-cephalexin"},
    "azithromycin":         {"category": "L2", "rationale": "Compatible; preferred macrolide.",                                                                         "source_id": "LactMed-azithromycin"},
    "clindamycin":          {"category": "L2", "rationale": "Compatible. Watch infant for diarrhea (rare C. diff).",                                                    "source_id": "LactMed-clindamycin"},
    "metronidazole":        {"category": "L3", "rationale": "Single dose preferred; for longer courses, hold breastfeeding 12–24h after dose.",                         "source_id": "LactMed-metronidazole"},
    "doxycycline":          {"category": "L3", "rationale": "Short courses acceptable; long-term may stain infant teeth — caution > 21 days.",                          "source_id": "LactMed-doxycycline"},
    "trimethoprim_sulfamethoxazole": {"category": "L3", "rationale": "Avoid in newborn < 2 months due to bilirubin displacement.",                                      "source_id": "LactMed-tmpsmx"},
    "nitrofurantoin":       {"category": "L3", "rationale": "Avoid if infant G6PD deficient or < 1 month old.",                                                         "source_id": "LactMed-nitrofurantoin"},
    "ciprofloxacin":        {"category": "L3", "rationale": "Limited data; alternative preferred when possible.",                                                       "source_id": "LactMed-ciprofloxacin"},
    # ── BP / Antihypertensives ──────────────────────────────────────────────
    "labetalol":            {"category": "L2", "rationale": "Preferred postpartum antihypertensive in lactation.",                                                      "source_id": "LactMed-labetalol"},
    "nifedipine":           {"category": "L2", "rationale": "Preferred CCB; minimal milk transfer.",                                                                    "source_id": "LactMed-nifedipine"},
    "enalapril":            {"category": "L2", "rationale": "Compatible after initial postpartum period.",                                                              "source_id": "LactMed-enalapril"},
    "lisinopril":           {"category": "L3", "rationale": "Limited data; enalapril preferred.",                                                                       "source_id": "LactMed-lisinopril"},
    "hydrochlorothiazide":  {"category": "L3", "rationale": "Suppresses lactation at high doses; limit to ≤25 mg/day.",                                                 "source_id": "LactMed-hctz"},
    "atenolol":             {"category": "L4", "rationale": "AVOID — case reports of bradycardia, cyanosis in infants.",                                                "source_id": "LactMed-atenolol"},
    "methyldopa":           {"category": "L2", "rationale": "Compatible.",                                                                                              "source_id": "LactMed-methyldopa"},
    "hydralazine":          {"category": "L2", "rationale": "Compatible.",                                                                                              "source_id": "LactMed-hydralazine"},
    # ── Anticoagulants ──────────────────────────────────────────────────────
    "warfarin":             {"category": "L1", "rationale": "Compatible; does not transfer to milk meaningfully.",                                                      "source_id": "LactMed-warfarin"},
    "heparin":              {"category": "L1", "rationale": "Compatible — does not pass into milk.",                                                                    "source_id": "LactMed-heparin"},
    "enoxaparin":           {"category": "L2", "rationale": "Not absorbed orally by infant.",                                                                           "source_id": "LactMed-enoxaparin"},
    "apixaban":             {"category": "L4", "rationale": "Limited data; alternative anticoagulant preferred.",                                                       "source_id": "LactMed-apixaban"},
    "rivaroxaban":          {"category": "L4", "rationale": "Limited data; warfarin / heparin preferred.",                                                              "source_id": "LactMed-rivaroxaban"},
    # ── Mental health ───────────────────────────────────────────────────────
    "sertraline":           {"category": "L1", "rationale": "Preferred SSRI in lactation.",                                                                             "source_id": "LactMed-sertraline"},
    "paroxetine":           {"category": "L2", "rationale": "Compatible; less preferred than sertraline due to neonatal withdrawal in late pregnancy.",                 "source_id": "LactMed-paroxetine"},
    "fluoxetine":           {"category": "L3", "rationale": "Long half-life; observe infant for fussiness / sleep changes.",                                            "source_id": "LactMed-fluoxetine"},
    "escitalopram":         {"category": "L2", "rationale": "Compatible.",                                                                                              "source_id": "LactMed-escitalopram"},
    "venlafaxine":          {"category": "L3", "rationale": "Compatible; monitor infant for somnolence.",                                                               "source_id": "LactMed-venlafaxine"},
    "bupropion":            {"category": "L3", "rationale": "Compatible; rare seizure cases reported.",                                                                 "source_id": "LactMed-bupropion"},
    "lithium":              {"category": "L4", "rationale": "Documented infant toxicity; check infant levels if used.",                                                 "source_id": "LactMed-lithium"},
    "lamotrigine":          {"category": "L3", "rationale": "Monitor infant for rash and sedation; check infant level if symptomatic.",                                 "source_id": "LactMed-lamotrigine"},
    "alprazolam":           {"category": "L3", "rationale": "Short-term use only; monitor infant for sedation, poor feeding.",                                          "source_id": "LactMed-alprazolam"},
    "lorazepam":            {"category": "L3", "rationale": "Compatible for occasional use; chronic use → sedation risk.",                                              "source_id": "LactMed-lorazepam"},
    "diazepam":             {"category": "L4", "rationale": "Long half-life; accumulation in infant; alternative preferred.",                                           "source_id": "LactMed-diazepam"},
    # ── Diabetes ────────────────────────────────────────────────────────────
    "insulin":              {"category": "L1", "rationale": "Compatible — no oral absorption by infant.",                                                               "source_id": "LactMed-insulin"},
    "metformin":            {"category": "L1", "rationale": "Compatible.",                                                                                              "source_id": "LactMed-metformin"},
    "glyburide":            {"category": "L2", "rationale": "Compatible; monitor infant glucose.",                                                                      "source_id": "LactMed-glyburide"},
    # ── Contraception ───────────────────────────────────────────────────────
    "norethindrone":        {"category": "L1", "rationale": "Progestin-only — preferred postpartum contraception in lactation.",                                        "source_id": "LactMed-norethindrone"},
    "levonorgestrel":       {"category": "L1", "rationale": "Progestin-only; compatible.",                                                                              "source_id": "LactMed-levonorgestrel"},
    "ethinyl_estradiol":    {"category": "L4", "rationale": "Combined oral contraceptives may suppress lactation in first 6 weeks; avoid until milk supply established.", "source_id": "LactMed-ee"},
    # ── GI ──────────────────────────────────────────────────────────────────
    "omeprazole":           {"category": "L2", "rationale": "Compatible.",                                                                                              "source_id": "LactMed-omeprazole"},
    "pantoprazole":         {"category": "L2", "rationale": "Compatible.",                                                                                              "source_id": "LactMed-pantoprazole"},
    "ondansetron":          {"category": "L2", "rationale": "Compatible.",                                                                                              "source_id": "LactMed-ondansetron"},
    "famotidine":           {"category": "L2", "rationale": "Compatible.",                                                                                              "source_id": "LactMed-famotidine"},
    # ── Allergy / cold ──────────────────────────────────────────────────────
    "loratadine":           {"category": "L2", "rationale": "Preferred antihistamine in lactation.",                                                                    "source_id": "LactMed-loratadine"},
    "cetirizine":           {"category": "L2", "rationale": "Compatible.",                                                                                              "source_id": "LactMed-cetirizine"},
    "diphenhydramine":      {"category": "L3", "rationale": "Sedates infant; may decrease milk supply with chronic use; prefer non-sedating antihistamines.",           "source_id": "LactMed-diphenhydramine"},
    "pseudoephedrine":      {"category": "L4", "rationale": "Reduces milk supply by up to 24%. Avoid.",                                                                 "source_id": "LactMed-pseudoephedrine"},
    # ── Misc ────────────────────────────────────────────────────────────────
    "prenatal_vitamins":    {"category": "L1", "rationale": "Continue throughout breastfeeding.",                                                                       "source_id": "ACOG-postpartum-supps"},
    "iron":                 {"category": "L1", "rationale": "Compatible.",                                                                                              "source_id": "LactMed-iron"},
    "ferrous":              {"category": "L1", "rationale": "Compatible (ferrous sulfate / gluconate / fumarate).",                                                     "source_id": "LactMed-ferrous"},
    "ferrous_sulfate":      {"category": "L1", "rationale": "Compatible. Standard postpartum iron supplementation.",                                                    "source_id": "LactMed-ferrous"},
    "fluoxetine_high_dose": {"category": "L4", "rationale": "Doses > 40 mg/day: case reports of infant fussiness, poor feeding, weight loss.",                          "source_id": "LactMed-fluoxetine-hd"},
}


def _normalize(name: str) -> str:
    n = (name or "").strip().lower()
    for suffix in (" er", " xr", " sr", " la", " hcl", " hydrochloride", " sulfate", " tartrate", " sodium"):
        if n.endswith(suffix):
            n = n[: -len(suffix)].strip()
    return n


def lactation_safety_lookup(medication: str) -> dict[str, Any] | None:
    """Look up a medication's LactMed safety category.

    Returns dict with category (L1–L5), label, rationale, recommendation, and
    source_id for audit trail. Returns None when the medication is not in the
    curated subset.
    """
    if not medication:
        return None
    key = _normalize(medication)

    entry = _LACT_DATA.get(key)
    if entry is None:
        for k, v in _LACT_DATA.items():
            clean_k = k.split("_")[0]
            if clean_k in key or key in clean_k:
                entry = {**v, "matched_term": k, "match_type": "partial"}
                break

    if entry is None:
        return None

    cat = entry.get("category", "L3")
    label, default_interp = _LACT_CATEGORY_INTERP.get(cat, ("Unknown", "Insufficient data."))
    return {
        "medication":     medication,
        "category":       cat,
        "label":          label,
        "interpretation": default_interp,
        "rationale":      entry.get("rationale", ""),
        "source_id":      entry.get("source_id", "LactMed"),
        "matched_term":   entry.get("matched_term", key),
        "match_type":     entry.get("match_type", "exact"),
    }
