"""Local end-to-end smoke test for NEST.

Exercises every NEST tool against the synthetic Chen dyad and prints the
results so you can verify findings before recording the demo.

Run:
    python scripts/test_nest_local.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from nest_agent.tools import (  # noqa: E402
    check_feeding_milestones,
    check_newborn_red_flags,
    check_postpartum_red_flags,
    classify_bp_postpartum,
    classify_jaundice_risk,
    get_dyad_demographics,
    get_dyad_medications,
    get_dyad_observations,
    interpret_epds,
    list_aap_newborn_visits,
    list_acog_postpartum_visits,
    lookup_lactation_safety,
    set_inline_dyad_context,
    summarize_sdoh,
)


def header(title: str) -> None:
    print()
    print("=" * 70)
    print(f" {title}")
    print("=" * 70)


def jdump(obj) -> None:
    print(json.dumps(obj, indent=2, default=str))


def main() -> None:
    ctx = MagicMock()
    ctx.state = {}

    header("1. Bind Sarah Chen + Baby Boy Chen dyad")
    bind = set_inline_dyad_context(
        mother_name="Sarah Chen",
        mother_age=32,
        delivery_type="c-section",
        delivery_date="2026-05-08",
        postpartum_day=2,
        mother_conditions=["preeclampsia with severe features", "postoperative anemia", "postpartum depression"],
        mother_medications=[
            "labetalol 200 mg PO BID",
            "oxycodone 5 mg PO Q4H PRN",
            "tramadol 50 mg PO Q6H PRN",
            "ibuprofen 600 mg PO Q6H",
            "acetaminophen 650 mg PO Q6H",
            "diphenhydramine 25 mg PO QHS",
            "pseudoephedrine 30 mg PO Q6H PRN",
            "sertraline 25 mg PO daily",
            "enoxaparin 40 mg subQ daily",
            "ferrous sulfate 325 mg PO BID",
            "prenatal vitamins 1 tab PO daily",
        ],
        mother_systolic_bp=162,
        mother_diastolic_bp=108,
        mother_weight_kg=78,
        epds_score=14,
        sdoh_concerns=[
            "lives alone",
            "no transportation to follow-ups",
            "Medicaid postpartum extension pending",
            "food insecurity",
        ],
        infant_name="Baby Boy Chen",
        infant_dob="2026-05-08",
        infant_age_days=2,
        infant_birth_weight_grams=2840,
        infant_current_weight_grams=2560,
        infant_gestational_age_weeks=37.3,
        infant_feeding_method="exclusive-breastfeeding",
        infant_feeding_concerns=["poor latch", "sleepy at breast"],
        infant_total_bilirubin=16.0,
        infant_age_at_bili_hours=56,
        tool_context=ctx,
    )
    jdump(bind)

    header("2. get_dyad_demographics(both)")
    jdump(get_dyad_demographics("both", ctx))

    header("3. get_dyad_medications(mother) — counts only")
    meds = get_dyad_medications("mother", ctx)
    print(f"count: {meds['count']}")
    for m in meds["medications"]:
        print(f"  - {m['medication']} (generic={m['generic_name']})")

    header("4. classify_bp_postpartum(162, 108)")
    jdump(classify_bp_postpartum(162, 108, ctx))

    header("5. list_acog_postpartum_visits — hypertensive track")
    jdump(list_acog_postpartum_visits(
        delivery_date="2026-05-08",
        has_hypertensive_disorder=True,
        has_postpartum_hemorrhage=False,
        tool_context=ctx,
    ))

    header("6. check_postpartum_red_flags — count + severities")
    pp = check_postpartum_red_flags(ctx)
    print(f"count: {len(pp['red_flags'])}")
    severities: dict[str, int] = {}
    for r in pp["red_flags"]:
        severities[r["severity"]] = severities.get(r["severity"], 0) + 1
    jdump(severities)

    header("7. classify_jaundice_risk(56, 16.0, low)")
    jdump(classify_jaundice_risk(56, 16.0, "low", ctx))

    header("8. check_feeding_milestones")
    jdump(check_feeding_milestones(
        feeding_method="exclusive-breastfeeding",
        age_days=2,
        weight_loss_pct=9.86,
        feeding_concerns=["poor latch", "sleepy at breast"],
        tool_context=ctx,
    ))

    header("9. list_aap_newborn_visits")
    jdump(list_aap_newborn_visits(infant_age_days=2, hospital_discharge_day=2, tool_context=ctx))

    header("10. check_newborn_red_flags — count + severities")
    nb = check_newborn_red_flags(ctx)
    print(f"count: {len(nb['red_flags'])}")
    severities = {}
    for r in nb["red_flags"]:
        severities[r["severity"]] = severities.get(r["severity"], 0) + 1
    jdump(severities)

    header("11. lookup_lactation_safety — every maternal medication")
    for med_dict in meds["medications"]:
        med = med_dict["generic_name"]
        result = lookup_lactation_safety(med, ctx)
        if result.get("status") == "found":
            print(f"  {med:25s} → {result['category']}  {result['rationale'][:70]}")
        else:
            print(f"  {med:25s} → not_found")

    header("12. interpret_epds(14, self_harm=False)")
    jdump(interpret_epds(14, False, ctx))

    header("13. summarize_sdoh — all 4 concerns")
    sdoh = summarize_sdoh(
        ["lives alone", "no transportation to follow-ups",
         "Medicaid postpartum extension pending", "food insecurity"],
        ctx,
    )
    jdump(sdoh)

    header("Summary expected")
    print("""
Expected high-impact findings (sanity check against the demo doc):

  - BP 162/108 → severe range, EMERGENCY (ACOG-PB-222-SEV).
  - Hypertensive postpartum track — 7-10 day visit required.
  - TSB 16.0 mg/dL @ 56h, low band threshold 15.0 → URGENT phototherapy.
  - Weight loss 9.86% → MONITOR (approaching 10%) — lactation consult today.
  - First AAP visit window 1-5 days → not scheduled in current plan.
  - Lactation: pseudoephedrine L4 (-24% supply), tramadol L4 (FDA warning),
    diphenhydramine L3, oxycodone L3, sertraline L1, labetalol L2,
    ferrous sulfate L1, prenatal L1.
  - EPDS 14 → URGENT mental-health follow-up within 7 days.
  - SDOH: 4 findings — food URGENT, transport URGENT, insurance URGENT,
    lives-alone MONITOR.
""")


if __name__ == "__main__":
    main()
