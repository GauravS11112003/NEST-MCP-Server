"""
Anticholinergic Cognitive Burden (ACB) Scale.

Source: Boustani M, Campbell N, Munger S, et al. Impact of anticholinergics
on the aging brain: a review and practical application. Aging Health. 2008.
DOI: 10.2217/1745509X.4.3.311

Score interpretation (per medication):
  0 = no known anticholinergic effect
  1 = possibly anticholinergic (mild)
  2 = definitely anticholinergic (moderate)
  3 = definitely anticholinergic with strong CNS effects

Total ACB score interpretation (sum across all patient meds):
  0     = no clinically relevant burden
  1-2   = increased risk of cognitive impairment
  ≥3    = clinically significant — each 1-point increase associated with
          increased risk of cognitive impairment, falls, and mortality
"""

from typing import Any

# Curated subset of the ACB scale — most commonly prescribed medications.
ACB_SCORE: dict[str, int] = {
    # ── Score 3 (highest burden) ───────────────────────────────────────────
    "amitriptyline": 3,
    "atropine": 3,
    "benztropine": 3,
    "carbinoxamine": 3,
    "chlorpheniramine": 3,
    "chlorpromazine": 3,
    "clemastine": 3,
    "clomipramine": 3,
    "clozapine": 3,
    "darifenacin": 3,
    "desipramine": 3,
    "dicyclomine": 3,
    "diphenhydramine": 3,
    "doxepin": 3,
    "fesoterodine": 3,
    "flavoxate": 3,
    "hydroxyzine": 3,
    "hyoscyamine": 3,
    "imipramine": 3,
    "meclizine": 3,
    "methocarbamol": 3,
    "nortriptyline": 3,
    "olanzapine": 3,
    "orphenadrine": 3,
    "oxybutynin": 3,
    "paroxetine": 3,
    "perphenazine": 3,
    "promethazine": 3,
    "propantheline": 3,
    "quetiapine": 3,
    "scopolamine": 3,
    "solifenacin": 3,
    "thioridazine": 3,
    "tolterodine": 3,
    "trifluoperazine": 3,
    "trihexyphenidyl": 3,
    "trospium": 3,
    # ── Score 2 (moderate burden) ──────────────────────────────────────────
    "amantadine": 2,
    "belladonna": 2,
    "carbamazepine": 2,
    "cyclobenzaprine": 2,
    "cyproheptadine": 2,
    "loxapine": 2,
    "meperidine": 2,
    "molindone": 2,
    "oxcarbazepine": 2,
    "pimozide": 2,
    # ── Score 1 (mild burden) ──────────────────────────────────────────────
    "alprazolam": 1,
    "aripiprazole": 1,
    "asenapine": 1,
    "atenolol": 1,
    "bupropion": 1,
    "captopril": 1,
    "chlorthalidone": 1,
    "cimetidine": 1,
    "clorazepate": 1,
    "codeine": 1,
    "colchicine": 1,
    "diazepam": 1,
    "digoxin": 1,
    "dipyridamole": 1,
    "disopyramide": 1,
    "fentanyl": 1,
    "furosemide": 1,
    "fluvoxamine": 1,
    "haloperidol": 1,
    "hydralazine": 1,
    "hydrocortisone": 1,
    "iloperidone": 1,
    "isosorbide": 1,
    "levocetirizine": 1,
    "loperamide": 1,
    "loratadine": 1,
    "metoprolol": 1,
    "morphine": 1,
    "nifedipine": 1,
    "oxcodone": 1,
    "oxycodone": 1,
    "prednisone": 1,
    "quinidine": 1,
    "ranitidine": 1,
    "risperidone": 1,
    "theophylline": 1,
    "tramadol": 1,
    "trazodone": 1,
    "triamterene": 1,
    "venlafaxine": 1,
    "warfarin": 1,
    "ziprasidone": 1,
}


def acb_score_for(medication: str) -> int:
    """Return ACB score for a single medication. 0 if unknown / no burden."""
    if not medication:
        return 0
    key = medication.strip().lower()
    for suffix in (" er", " xr", " sr", " la", " hcl", " hydrochloride", " sulfate", " tartrate"):
        if key.endswith(suffix):
            key = key[: -len(suffix)].strip()
    if key in ACB_SCORE:
        return ACB_SCORE[key]
    for k, v in ACB_SCORE.items():
        if k in key or key in k:
            return v
    return 0


def calculate_total_acb(medications: list[str]) -> dict[str, Any]:
    """Calculate the cumulative ACB score across a medication list.

    Returns:
        {
          "total_score": int,
          "risk_level": "none" | "increased" | "significant",
          "contributors": [{"medication": str, "score": int}, ...],
          "interpretation": str,
        }
    """
    contributors: list[dict[str, Any]] = []
    total = 0
    for med in medications or []:
        score = acb_score_for(med)
        if score > 0:
            contributors.append({"medication": med, "score": score})
            total += score

    if total == 0:
        risk = "none"
        interp = "No clinically significant anticholinergic burden."
    elif total < 3:
        risk = "increased"
        interp = (
            "Mild-to-moderate anticholinergic burden. "
            "Some increase in cognitive impairment / fall risk; consider deprescribing where possible."
        )
    else:
        risk = "significant"
        interp = (
            f"Clinically significant anticholinergic burden (ACB score {total}). "
            "Each 1-point increase associated with increased cognitive impairment, falls, and mortality. "
            "Strongly consider deprescribing or substituting non-anticholinergic alternatives."
        )

    contributors.sort(key=lambda x: x["score"], reverse=True)
    return {
        "total_score": total,
        "risk_level": risk,
        "contributors": contributors,
        "interpretation": interp,
    }
