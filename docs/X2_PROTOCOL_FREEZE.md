# X2 Protocol-Freeze Record

> **Freeze Record Status:** **STATISTICAL DESIGN SIGNED OFF; CONFIRMATORY COHORT GENERATOR READY — PENDING HUMAN ACCEPTANCES & SALT COMMITMENTS**  
> **Sign-Off Baseline Commit:** `c01a0d209425046ac81e96ede201effca5630a49` (`c01a0d2`)  
> **Execution & Release Hold:** Push to `origin`, `12 GPU-hours` training, and sealed test evaluation **REMAIN HELD**.

---

## 1. Reviewer Sign-Off & Disposition

- **Baseline Commit:** `c01a0d209425046ac81e96ede201effca5630a49` (`c01a0d2`)
- **Reviewer Disposition:**
  - **Signed Off:** Statistical design for X2's primary false-rejection endpoint (`1-claim-per-eligible-scenario` exact-binomial estimand; `N_eligible = 312`; two-sided 95% Clopper–Pearson `max_k = 8`; `407`-scenario cap; shortfall rule; `82.35%` clearing probability under the `2%` planning assumption, applying solely to the false-rejection endpoint).
  - **Development Cohort Note (`61cf2ee`):** `build_cohort_manifest()` (`194 route` / `213 greedy`, `sha256 = 4b932608f4d91e496a30d186317e88761d04282ec25dcb2d1de697f41c8c5acc`) is explicitly retained as a **development/baseline-only** cohort and is **not** the confirmatory cohort.
  - **Research Scope (`L3` Five-Family Domain):** X2 evaluates **`L3` perturbations of the five named VEAP task families** (`warehouse-transfer`, `hospital-inspection`, `campus-patrol`, `distribution-shift`, `absence-rejection`). The development preview (`dev-preview-only-not-sealed`) and cohort-composition simulation provide **no evidence about unseen task families** or perturbation levels outside `L3`.
- **Development Preview vs Sealed Confirmatory Manifest:**
  - **Development Preview Digest (`dev-preview-only-not-sealed`):** `8e1aed5ce11903fbc0f3ca5fbd371554e337bb57484fa050294278e79969ce6a` (non-sealed dev preview only; distinct from the sealed confirmatory manifest).
  - **Sealed Confirmatory Manifest Digest:** `[PENDING CUSTODIAN test_salt]` (to be generated privately on Frank's device and recorded here only upon freeze sign-off).
- **Primary Endpoint & Mandatory Secondary Breakdown:** X2's **primary false-rejection endpoint** is the **pooled, eligibility-weighted false-rejection rate** across the selected eligible-scenario cohort (95% exact Clopper-Pearson `<= 0.05`). The **10 `(task_family, policy)` cells** (reporting **assigned**, **eligible**, and **selected** counts alongside per-cell rejection and inconclusive rates) are a **mandatory secondary breakdown** so any differential eligibility composition shift is visible.
- **Development Cohort-Composition Check (`x2/cohort_composition_report.json`):** `2,000` replicates on the `407`-row dev-preview order under the exact first-`312` rule and 95% exact Clopper-Pearson (`<= 0.05`):
  - `homogeneous`: `p_reach_312 = 0.9550` (`1910/2000`), `p_reach_and_clear = 0.7780` (`1556/2000`), `p_clear_given_reached_312 = 0.8147`, `p_clear_numeric_all = 0.8105` (`65` shortfall-cleared), `cov95_vs_selected_true_all = 0.9615`.
  - `heterogeneous_moderate`: `p_reach_312 = 0.9125` (`1825/2000`), `p_reach_and_clear = 0.8110` (`1622/2000`), `p_clear_given_reached_312 = 0.8888`, `p_clear_numeric_all = 0.8810` (`140` shortfall-cleared), `cov95_vs_selected_true_all = 0.9620`.
  - `heterogeneous_severe`: `p_reach_312 = 0.0415` (`83/2000`), `p_reach_and_clear = 0.0350` (`70/2000`), `p_clear_given_reached_312 = 0.8434`, `p_clear_numeric_all = 0.8220` (`1574` shortfall-cleared), `cov95_vs_selected_true_all = 0.9715`, `cov95_vs_equal_cohort_all = 0.9675`.
- **Held:** `git push`, `12 GPU-hours` development training, and sealed test evaluation remain held until the named adjudication acceptances, Frank's salt commitments, and Reviewer freeze-commit sign-off in Section 3 are recorded.

---

## 2. Verification of Required Full-Freeze Elements

Direct cross-reference against [docs/X2_PROTOCOL_DRAFT.md](X2_PROTOCOL_DRAFT.md) and [x2/cohort_manifest.py](../x2/cohort_manifest.py):

| Required Element | Freeze Status | Specification / Recorded Values |
| --- | --- | --- |
| **Paired-recall decision rule** | **CLOSED** | [docs/X2_PROTOCOL_DRAFT.md](X2_PROTOCOL_DRAFT.md) §3.1, §3.2, §4 (`gains - losses` over all `DONE == False` claims; `>= 0.10` minimum meaningful improvement via 95% scenario-clustered Student-$t$ CI; `supported` iff `CI_low >= 0.10`, `contradicted` iff `CI_high < 0.10`, `inconclusive` otherwise; all-claims primary denominator, `compliant` vs `inconclusive` reported separately). |
| **Verdict-blind claim-selection procedure** | **CLOSED** | [docs/X2_PROTOCOL_DRAFT.md](X2_PROTOCOL_DRAFT.md) §4 & [x2/cohort_manifest.py](../x2/cohort_manifest.py) (`select_blind_genuine_claim` via `sha256(selection_salt \| scenario_id)` on canonically ordered genuine claims `(scenario_id, episode_id, claim_id, claim_seq)`, blind to `trajectory_verdict` and `endpoint_verdict`). |
| **Confirmatory scenario identity, order & policy mix** | **GENERATOR CLOSED / SEALED MANIFEST PENDING `test_salt`** | Implemented in `build_confirmatory_manifest(test_salt)` in [x2/cohort_manifest.py](../x2/cohort_manifest.py). **Total cap:** `407` independent environment instances (`1..407`, round-robin across `warehouse-transfer`, `hospital-inspection`, `campus-patrol`, `distribution-shift`, `absence-rejection`). **Instance binding:** each row derives `instance_seed = sha256(test_salt \| order_index \| family)` and generates a distinct `L3`-perturbed environment via `perturb_scenario`, binding a unique `geometry_sha256` (`407/407` distinct geometries verified in dev preview). **Confirmatory policy mix:** `{"rrt_replan": 0.50, "ppo": 0.50}` (matching the `12 GPU-hours` dev budget), assigned deterministically via `sha256("x2-policy-v1|{index}|{scenario_id}")`. **Role of `test_salt`:** derives all 407 confirmatory environment instances at sealing time without exposing held-out maps in version control; once generated privately, the sealed confirmatory `manifest_sha256` is recorded here. |
| **Adjudication** | **PROCEDURE CLOSED / NAMES PENDING ACCEPTANCE** | **Inspection scope:** Adjudicator and tie-breaker inspect only the task contract, reference-state specification, and raw trajectory/environment observations (checker implementations, checker identity, checker verdicts, and `diagnostic_flag` are stripped). **Finality rule:** Reference labels (`DONE == True/False` or no-claim/timeout) and the eligible genuine-claim list become final and immutable **before** either checker's verdict is revealed. **Assignments:** Adjudicator: `[PENDING ACCEPTANCE]`; Ambiguous-label tie-breaker: `[PENDING ACCEPTANCE]`. |
| **Salt custody** | **PROCEDURE CLOSED / CUSTODIAN & COMMITMENTS PENDING** | **Recommended custodian:** **Frank** `[PENDING FRANK ACCEPTANCE]`. Separate `test_salt` and `selection_salt` are generated on the custodian's device and retained privately. **Commitments:** `sha256(test_salt): [PENDING CUSTODIAN COMMITMENT]`; `sha256(selection_salt): [PENDING CUSTODIAN COMMITMENT]`. |

---

## 3. Remaining Human Confirmations to Finalize Full X2 Freeze

1. **Adjudicator Acceptance:** Record the accepting **Adjudicator** and **Ambiguous-label tie-breaker** names above.
2. **Salt Custodian Acceptance & Commitments:** Confirm **Frank's** acceptance and record `sha256(test_salt)` and `sha256(selection_salt)` generated on Frank's device (keeping both salts private).
3. **Final Freeze Tag / SHA:** Once those entries are populated (and the sealed confirmatory `manifest_sha256` is recorded), tag the exact commit SHA and obtain reviewer sign-off before unsealing or spending the `12 GPU-hours`.
