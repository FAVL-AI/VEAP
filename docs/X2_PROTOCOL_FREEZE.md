# X2 Protocol-Freeze Record

> **Freeze Record Status:** **STATISTICAL DESIGN SIGNED OFF (PARTIAL FREEZE)** — Operational manifests & custody assignments listed in Section 3 remain **OPEN** prior to unsealing.  
> **Sign-Off Baseline Commit:** `c01a0d209425046ac81e96ede201effca5630a49` (`c01a0d2`)  
> **Execution & Release Hold:** Push to `origin`, `12 GPU-hours` training, and sealed test evaluation **REMAIN HELD**.

---

## 1. Reviewer Sign-Off & Disposition

- **Baseline Commit:** `c01a0d209425046ac81e96ede201effca5630a49` (`c01a0d2`)
- **Reviewer Disposition:**
  - **Signed Off:** Statistical design for X2's primary false-rejection endpoint:
    - **Estimand:** Probability that VEAP's trajectory checker returns `"violating"` on one genuine (`DONE == True`) completion claim selected uniformly (blind to both checker verdicts) from an independently sampled eligible scenario (`>= 1` genuine `DONE == True` claim), with `"inconclusive"` and `"compliant"` fractions reported separately.
    - **Sample-Size & Decision Rule:** `N_eligible = 312` eligible scenarios under a two-sided 95% exact Clopper–Pearson interval against the `<= 0.05` ceiling (`max_k = 8` rejections allowed; `82.35%` clearing probability under the `2%` planning assumption, applying solely to the false-rejection endpoint).
    - **Cohort Cap & Shortfall Rule:** Total cap of `407` scenarios in prespecified order (`95.77%` probability of obtaining `>= 312` eligible scenarios at `80%` independent eligibility), using the first `312` eligible scenarios in order and reporting any shortfall transparently if `< 312`.
    - **Preserved Analyses:** All issued claims preserved for paired recall analysis; all no-claim/timeout episodes preserved in all-episode accounting; clustered FPR intervals retained as secondary diagnostics only.
  - **Scope Note:** Sign-off covers the **statistical design** only (based on local test/claims reports for `c01a0d2`).
  - **Held:** `git push`, `12 GPU-hours` development training, and sealed test evaluation remain held until the open full-freeze items in Section 3 are completed.

---

## 2. Verification of Required Full-Freeze Elements

Direct cross-reference against [docs/X2_PROTOCOL_DRAFT.md](X2_PROTOCOL_DRAFT.md):

| Required Element | Freeze Status | Reference / Current State |
| --- | --- | --- |
| **Paired-recall decision rule** | **DEFINED** | [docs/X2_PROTOCOL_DRAFT.md](X2_PROTOCOL_DRAFT.md) §3.1, §3.2, §4 (`gains - losses` over all `DONE == False` claims; `>= 0.10` minimum meaningful improvement via 95% scenario-clustered Student-$t$ CI; `supported` iff `CI_low >= 0.10`, `contradicted` iff `CI_high < 0.10`, `inconclusive` otherwise; all-claims primary denominator, `compliant` vs `inconclusive` reported separately). |
| **Verdict-blind claim-selection procedure** | **DEFINED** | [docs/X2_PROTOCOL_DRAFT.md](X2_PROTOCOL_DRAFT.md) §4 (`sha256(selection_salt \| scenario_id)` uniform selection among `DONE == True` claims in each eligible scenario, blind to `trajectory_verdict` and `endpoint_verdict`). |
| **Scenario order and policy mix** | **OPEN (Manifest Pending)** | Procedure defined in [docs/X2_PROTOCOL_DRAFT.md](X2_PROTOCOL_DRAFT.md) §4, **but the concrete ordered 407-scenario manifest and explicit policy-mix proportions/weights are not yet frozen**. |
| **Adjudicator** | **OPEN (Assignment Pending)** | Double-blinded adjudication schema defined in [docs/X2_PROTOCOL_DRAFT.md](X2_PROTOCOL_DRAFT.md) §4 (stripping checker identity, verdicts, and `diagnostic_flag`), **but the named adjudicator (and ambiguous-label tie-breaker) is not yet assigned**. |
| **Salt custodian** | **OPEN (Custodian & Commitment Pending)** | `SHA-256(S)` commitment and deterministic split procedure defined in [docs/X2_PROTOCOL_DRAFT.md](X2_PROTOCOL_DRAFT.md) §4, **but the named salt custodian and published `SHA-256(test_salt)` / `SHA-256(selection_salt)` commitment digests are not yet recorded**. |

---

## 3. Open Items Required Before Full X2 Freeze & Unsealing

1. **Concrete Scenario Order & Policy Mix Manifest:** Commit the exact prespecified 407-scenario ordered list, eligibility rule implementation reference, and fixed policy-mix weights.
2. **Named Adjudicator:** Record the named author/adjudicator (working from task contracts and reference-state specs without reading VEAP's verifier implementation or outputs) and ambiguous-label resolution owner.
3. **Named Salt Custodian & Published Commitments:** Record the named custodian holding `test_salt` and `selection_salt` on-device, and publish `SHA-256(test_salt)` and `SHA-256(selection_salt)` in this freeze record before test unsealing.
4. **Hardening & SHA-256 Code Manifest:** Record `SHA-256` digests of the frozen checker entry points (`x2/leakage_controls.py`), attribution/scoring scripts (`x2/detection_attribution.py`), and verifier (`veap/verifier.py`) per [docs/X2_PROTOCOL_DRAFT.md](X2_PROTOCOL_DRAFT.md) §5.
