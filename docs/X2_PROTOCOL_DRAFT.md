# X2 Research Protocol Draft (Trajectory vs Endpoint Verification)

> **Status:** DRAFT — Pre-Freeze Specification (Development-Only Calibration)  
> **Companion Artifacts:** `x2/detection_attribution.py`, `x2/precision_analysis.py`, `x2/precision_report.json`

## 1. Objective & Scope

X2 evaluates whether trajectory-level verification improves detection of reference-false (`DONE == False`) claims relative to endpoint-only verification without exceeding a 5% false-rejection ceiling on reference-true (`DONE == True`) claims. All parameter selection, threshold calibration, and precision analysis are performed strictly on the development split prior to unsealing the test split.

---

## 2. Diagnostic Threshold Specification

The trajectory diagnostic monitor evaluates per-step clearance margin against declared obstacles and forbidden-zone boundaries, as well as step-level kinematic consistency. The frozen diagnostic threshold is specified as follows:

| Parameter | Specification |
| --- | --- |
| **Metric** | Minimum signed obstacle/forbidden-zone clearance margin $\Delta_{\min}$ across the trajectory |
| **Numerical Value** | `0.05` |
| **Units** | `meters` (`m`) |
| **Comparison Operator** | Strict inequality `<` for diagnostic trigger; `>= 0.05 m` is **diagnostic flag clear** (`>` vs `>=`: **diagnostic flag clear** iff $\Delta_{\min} \ge 0.05\text{ m}$; diagnostic triggers iff $\Delta_{\min} < 0.05\text{ m}$) |
| **Boundary Treatment** | Exact equality $\Delta_{\min} == 0.05\text{ m}$ is **diagnostic flag clear** (boundary-inclusive non-triggering). Floating-point values are evaluated in IEEE-754 `float64` without rounding or epsilon tolerance. |
| **Mode (Flag-Only vs Verdict-Changing)** | **Flag-only** (`diagnostic_flag = True`). The diagnostic threshold emits a structured warning flag in the audit log for post-hoc attribution and hardening review, and **does not** override or mutate the checker's primary verdict (`compliant`, `violating`, or `inconclusive`). Any transition from flag-only to verdict-changing requires a separate pre-registered protocol amendment before test unsealing. |

---

## 3. Detection Attribution Rules

All detection attribution is computed by `x2/detection_attribution.py` (`attribute_detection`) over paired `(adjudicator_done, trajectory_verdict, endpoint_verdict)` tuples, where verdicts are strictly in `{"compliant", "violating", "inconclusive"}`.

### 3.1 Separating `compliant` and `inconclusive` Endpoint Outcomes

On reference-false claims (`DONE == False`), trajectory-vs-endpoint attribution **must** report `compliant` and `inconclusive` outcomes separately rather than collapsing them:

- `trajectory_only_compliant`: `DONE == False`, trajectory = `violating`, endpoint = `compliant`
- `trajectory_only_inconclusive`: `DONE == False`, trajectory = `violating`, endpoint = `inconclusive`
- `endpoint_only_compliant`: `DONE == False`, endpoint = `violating`, trajectory = `compliant`
- `endpoint_only_inconclusive`: `DONE == False`, endpoint = `violating`, trajectory = `inconclusive`
- `both_violating`: `DONE == False`, trajectory = `violating`, endpoint = `violating`
- `neither_violating`: `DONE == False`, neither checker returns `violating`

### 3.2 Paired Recall Improvement (`gains - losses`)

Over all reference-false (`DONE == False`) claims:

$$\text{gains} = \text{trajectory\_only\_compliant} + \text{trajectory\_only\_inconclusive}$$

$$\text{losses} = \text{endpoint\_only\_compliant} + \text{endpoint\_only\_inconclusive}$$

$$\text{paired\_recall\_improvement (count)} = \text{gains} - \text{losses}$$

Rate differences are reported under both denominators:

1. **Primary (All-Claims Denominator):**
   $$\Delta_{\text{all}} = \frac{\text{gains} - \text{losses}}{N_{\text{ref\_false}}}$$
   where `inconclusive` is counted in the denominator as a non-detection (not `violating`).
2. **Secondary / Sensitivity (Definitive-Only Denominators):**
   - Paired both-definitive rate difference: $(\text{trajectory\_only\_compliant} - \text{endpoint\_only\_compliant}) / N_{\text{both\_definitive}}$.
   - Unpaired definitive-only rate difference: $\text{recall}_{\text{traj,def}} - \text{recall}_{\text{endp,def}}$.
   - Per-checker `inconclusive` counts and rates on both `DONE == False` and `DONE == True` claims must be reported alongside all rates.

---

## 4. Freeze Decision Table

| Dimension | Frozen Decision | Basis / Operational Rule |
| --- | --- | --- |
| **Candidate Scenario Count (`N`)** | **Candidate design: `N = 60` scenarios** (not a final freeze; ~3 `DONE == False` and 4 genuine `DONE == True` claims per scenario; 180 ref-false, 240 genuine ref-true claims) | From cluster-aware `x2/precision_report.json` (`x2/precision_analysis.py`, using scenario-clustered Student-$t$ CIs for both endpoints), `N = 60` is the smallest candidate design achieving $\ge 80\%$ joint resolution in nominal (`90.05%`) and $\ge 50\%$ in pessimistic (`54.30%`). **Pessimistic inconclusive risk:** even at `N = 60`, there remains a **`45.70%` pessimistic risk** (`1 - 0.5430`) that the study is inconclusive on at least one gate (FPR ceiling `68.45%`, recall `78.25%`). Final freeze requires confirming whether `N = 60` or a larger `N` is adopted. |
| **Acceptance Thresholds: Minimum Meaningful Recall Improvement** | **`>= 0.10`** (10 percentage points) | Lower bound of the two-sided 95% scenario-clustered Student-$t$ CI for paired recall improvement ($\Delta_{\text{all}}$) must satisfy $\text{CI}_{\text{low}} \ge 0.10$. |
| **Acceptance Thresholds: False-Rejection Ceiling** | **`<= 0.05`** (5% ceiling) | Upper bound of the two-sided 95% Wilson score CI on the trajectory checker's false-rejection (`violating` on `DONE == True`) rate must satisfy $\text{CI}_{\text{high}} \le 0.05$. |
| **Acceptance Thresholds: CI Rule** | Two-sided 95% scenario-clustered Student-$t$ CIs (`alpha = 0.05`) | Both paired recall improvement and false-rejection rate use scenario-clustered Student-$t$ intervals ($df = N - 1$); when zero false rejections are observed across all scenarios, a pooled 95% Wilson score upper bound ($z = 1.95996$) serves as the floor. |
| **Acceptance Thresholds: Inconclusive Denominator Rule** | **All-claims denominator is primary**; definitive-only is secondary | `inconclusive` verdicts remain in the denominator for primary recall and false-rejection acceptance gates so abstention cannot artificially inflate performance. |
| **Adjudicator Blinding** | **Double-blinded to checker identity & verdicts** | Adjudicators assigning `DONE` (`True`/`False`) receive only raw trajectory/environment observations and claim definitions. Checker names (`trajectory` vs `endpoint`), checker verdicts, and `diagnostic_flag` outputs are stripped prior to adjudication. |
| **Test Salt Commitment & Split-Generation Procedure** | **Pre-committed SHA-256 salt + deterministic hash split** | Before unsealing test scenarios, generate a 256-bit random test salt $S$, publish $\text{SHA-256}(S)$ in the freeze manifest, and assign each scenario ID deterministically via `int(sha256(f"{S}|{scenario_id}").hexdigest()[:8], 16) % 100`. Split boundaries are frozen prior to salt reveal; test split is executed **once** after reviewer sign-off. |
| **GPU Budget & Stopping Rule** | **12 GPU-hours dev cap** + early stopping + **sealed single-pass eval** | Development tuning, ablation, and diagnostic calibration are capped at **12 GPU-hours**. Stop dev runs early if either (a) 12 GPU-hours are exhausted or (b) dev precision/gate metrics stabilize across two consecutive checkpoints with no code changes. Sealed test evaluation runs in a separate, single-pass job using frozen weights/parameters and is excluded from the 12 GPU-hour dev budget. |

---

## 5. Hardening-Change Audit Checklist

Before transitioning from `DRAFT` to `FROZEN` and unsealing the test split, a reviewer must verify every item below:

- [ ] **Code & Parameter Freeze:** `SHA-256` digests of `x2/detection_attribution.py`, `x2/precision_analysis.py`, verifier modules, and diagnostic threshold (`0.05 m`, `<`, flag-only) are recorded in the freeze manifest.
- [ ] **No Post-Freeze Tuning:** Zero hyperparameter, threshold, or prompt/policy edits are permitted after test salt reveal. Any bugfix requires re-freezing and documenting in an erratum before re-running.
- [ ] **Precision Report Verified:** `x2/precision_report.json` is regenerated from clean `x2/precision_analysis.py` on dev assumptions only (`recommended_n = 60`).
- [ ] **Adjudicator Blinding Audit:** Adjudication export schema verified to exclude `trajectory_verdict`, `endpoint_verdict`, and `diagnostic_flag`.
- [ ] **Test Salt Commitment Verified:** `SHA-256(test_salt)` committed in version control before test split generation; no test scenarios inspected during dev.
- [ ] **GPU Budget Log Complete:** Total dev GPU-hours logged and verified `<= 12.0` GPU-hours prior to sealed evaluation.
- [ ] **Inconclusive Reporting Intact:** Attribution output includes separate `trajectory_only_compliant`, `trajectory_only_inconclusive`, `endpoint_only_compliant`, `endpoint_only_inconclusive`, and both denominators.
