# X2 Protocol-Freeze Record

> **Freeze Record Status:** **STATISTICAL DESIGN SIGNED OFF; COHORT MANIFEST CLOSED — PENDING HUMAN ASSIGNMENTS & SALT COMMITMENTS**  
> **Sign-Off Baseline Commit:** `c01a0d209425046ac81e96ede201effca5630a49` (`c01a0d2`)  
> **Execution & Release Hold:** Push to `origin`, `12 GPU-hours` training, and sealed test evaluation **REMAIN HELD**.

---

## 1. Reviewer Sign-Off & Disposition

- **Baseline Commit:** `c01a0d209425046ac81e96ede201effca5630a49` (`c01a0d2`)
- **Reviewer Disposition:**
  - **Signed Off:** Statistical design for X2's primary false-rejection endpoint (`1-claim-per-eligible-scenario` exact-binomial estimand; `N_eligible = 312`; two-sided 95% Clopper–Pearson `max_k = 8`; `407`-scenario cap; shortfall rule; `82.35%` clearing probability under the `2%` planning assumption, applying solely to the false-rejection endpoint).
  - **Held:** `git push`, `12 GPU-hours` development training, and sealed test evaluation remain held until the named adjudication acceptance and salt commitments in Section 3 are filled in and signed off against the resulting freeze commit.

---

## 2. Verification of Required Full-Freeze Elements

Direct cross-reference against [docs/X2_PROTOCOL_DRAFT.md](X2_PROTOCOL_DRAFT.md) and [x2/cohort_manifest.py](../x2/cohort_manifest.py):

| Required Element | Freeze Status | Specification / Recorded Values |
| --- | --- | --- |
| **Paired-recall decision rule** | **CLOSED** | [docs/X2_PROTOCOL_DRAFT.md](X2_PROTOCOL_DRAFT.md) §3.1, §3.2, §4 (`gains - losses` over all `DONE == False` claims; `>= 0.10` minimum meaningful improvement via 95% scenario-clustered Student-$t$ CI; `supported` iff `CI_low >= 0.10`, `contradicted` iff `CI_high < 0.10`, `inconclusive` otherwise; all-claims primary denominator, `compliant` vs `inconclusive` reported separately). |
| **Verdict-blind claim-selection procedure** | **CLOSED** | [docs/X2_PROTOCOL_DRAFT.md](X2_PROTOCOL_DRAFT.md) §4 & [x2/cohort_manifest.py](../x2/cohort_manifest.py) (`select_blind_genuine_claim` via `sha256(selection_salt \| scenario_id)` on canonically ordered genuine claims, blind to `trajectory_verdict` and `endpoint_verdict`). |
| **Scenario order, policy mix & canonical claim ordering** | **CLOSED** | Implemented in [x2/cohort_manifest.py](../x2/cohort_manifest.py). **Total cap:** `407` scenarios (`1..407`, round-robin across `warehouse-transfer`, `hospital-inspection`, `campus-patrol`, `distribution-shift`, `absence-rejection`). **Policy weights:** `{"route": 0.50, "greedy": 0.50}`, assigned deterministically via `sha256("x2-policy-v1|{index}|{scenario_id}")` (`route = 194`, `greedy = 213`). **Private manifest retained locally** (`x2/.private_cohort_manifest.json`, gitignored) with **SHA-256:** `4b932608f4d91e496a30d186317e88761d04282ec25dcb2d1de697f41c8c5acc`. **Canonical genuine-claim ordering before salted selection:** lexicographical sort by `(scenario_id, episode_id, claim_id, claim_seq)` so replay selects the identical claim regardless of file or database iteration order. |
| **Adjudication** | **PROCEDURE CLOSED / NAMES PENDING ACCEPTANCE** | **Inspection scope:** Adjudicator and tie-breaker inspect only the task contract, reference-state specification, and raw trajectory/environment observations (checker implementations, checker identity, checker verdicts, and `diagnostic_flag` are stripped). **Finality rule:** Reference labels (`DONE == True/False` or no-claim/timeout) and the eligible genuine-claim list become final and immutable **before** either checker's verdict is revealed. **Assignments:** Adjudicator: `[PENDING ACCEPTANCE]`; Ambiguous-label tie-breaker: `[PENDING ACCEPTANCE]`. |
| **Salt custody** | **PROCEDURE CLOSED / CUSTODIAN & COMMITMENTS PENDING** | **Recommended custodian:** **Frank** `[PENDING USER CONFIRMATION]`. Separate `test_salt` and `selection_salt` are generated on the custodian's device and retained privately. **Commitments:** `sha256(test_salt): [PENDING CUSTODIAN COMMITMENT]`; `sha256(selection_salt): [PENDING CUSTODIAN COMMITMENT]`. |

---

## 3. Remaining Entries to Finalize Full X2 Freeze

1. **Adjudicator Acceptance:** Record the accepting **Adjudicator** and **Ambiguous-label tie-breaker** names above.
2. **Salt Custodian Confirmation & Commitments:** Confirm **Frank** as salt custodian and record the two on-device generated `SHA-256` commitments (`sha256(test_salt)` and `sha256(selection_salt)`).
3. **Final Freeze Tag / SHA:** Once those entries are populated, commit, tag the exact commit SHA, and obtain reviewer sign-off against that SHA before unsealing or running GPU jobs.
