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
| **Primary False-Rejection Design & Scenario Count** | **1-claim-per-eligible-scenario exact-binomial design (`N_eligible = 312` proposed planning point; total scenario cap `407`)** | **Primary estimand:** probability that a randomly selected genuine (`DONE == True`) claim from an independently sampled eligible scenario receives `"violating"` from the trajectory checker (with `"inconclusive"` and `"compliant"` fractions reported separately). Under two-sided 95% exact Clopper-Pearson, `N_eligible = 312` (`max_k = 8` rejections) achieves **`82.35%`** clearing probability at `2%` true FPR (note: `82.35%` applies **only** to the false-rejection endpoint). Exact milestones (`x2/feasibility_report.json`): `1%` FPR / `80%` -> `142` (`max_k=2`, `82.94%`); `1%` / `90%` -> `173` (`max_k=3`, `90.33%`); `2%` / `80%` -> `312` (`max_k=8`, `82.35%`); `2%` / `90%` -> `390` (`max_k=11`, `90.41%`). All issued claims are retained for paired recall analysis, all no-claim/timeout episodes in all-episode accounting, and clustered methods (`student_t`, `cluster_score`, `scenario_bootstrap`) as secondary diagnostics only. |
| **Prespecified Cohort & Shortfall Rule** | **First `312` eligible scenarios in prespecified order; `407`-scenario cap (`95.77%` at `80%` eligibility)** | Scenarios are evaluated in a prespecified, pre-registered order under a fixed policy mix. **Eligibility:** scenario has $\ge 1$ genuine (`DONE == True`) claim. **Blind uniform claim selection:** within each eligible scenario, 1 genuine claim is selected uniformly at random via a pre-committed deterministic seed (`sha256(selection_salt \| scenario_id)`), strictly blind to checker verdicts. **Cap & shortfall rule:** evaluate up to `407` total scenarios (`P(Binomial(407, 0.80) >= 312) = 95.77%`), taking the first `312` eligible scenarios in order; if `< 312` eligible scenarios are obtained within the `407`-scenario cap, evaluate all available eligible scenarios and report the exact shortfall transparently without post-hoc extension. |
| **Acceptance Thresholds: Minimum Meaningful Recall Improvement** | **`>= 0.10`** (10 percentage points) | `supported` iff $\text{CI}_{\text{low}} \ge 0.10$; `contradicted` iff $\text{CI}_{\text{high}} < 0.10$; `inconclusive` otherwise. |
| **Acceptance Thresholds: False-Rejection Ceiling** | **`<= 0.05`** (5% ceiling) via **95% exact Clopper-Pearson CI** on 1-claim-per-eligible-scenario | **Primary rejection definition:** trajectory checker returning `"violating"` on the 1 blindly selected genuine (`DONE == True`) claim per eligible scenario; `"inconclusive"` and `"compliant"` fractions on genuine claims must be reported separately alongside the rejection rate. `supported` iff Clopper-Pearson $\text{CI}_{\text{high}} \le 0.05$; `contradicted` iff $\text{CI}_{\text{low}} > 0.05$; `inconclusive` otherwise. |
| **Acceptance Thresholds: CI Rule** | Primary: 95% exact Clopper-Pearson (FPR) & 95% scenario-clustered Student-$t$ (recall); Secondary: clustered FPR diagnostics | Primary FPR inference uses two-sided 95% exact Clopper-Pearson on `N_eligible` independent eligible-scenario draws (`N_eligible = 312`, `max_k = 8`). Clustered FPR methods (`student_t`, `cluster_score`, `scenario_bootstrap`) are retained **only as secondary diagnostics** (calibration comparison in `x2/interval_calibration_report.json` showed none met worst-case `min_cov >= 0.92` and `max_umiss <= 0.05` at `rho = 0.50`, and `N = 60` exhibited `0 -> 1` non-monotonicity). |
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

---

## 6. Fixed-Cluster Monotonicity & Exact-Binomial Reference Feasibility

### 6.1 Fixed-Cluster Monotonicity Check (`x2/feasibility_and_monotonicity.py`)

Holding `N = 60` fixed (`unequal_1_to_7` and `equal_4` clusters) and flipping genuine claims one at a time from `0` to `10` false rejections reveals **non-monotonicity** in all three clustered intervals (`student_t`: 42 anomaly steps, `cluster_score`: 32, `scenario_bootstrap`: 43 across 6 runs):
- At `0` rejections, the `N = 60` Wilson floor yields `ci_high = 0.0602` (`inconclusive`).
- Flipping `1` rejection causes `ci_high` to **drop below `0.05`** (e.g., to `0.0071` for `student_t`/`scenario_bootstrap` and `0.0202` for `cluster_score` in `unequal_1_to_7 | distinct_scenarios_largest_first`; `0.0125` / `0.0233` in `equal_4`), flipping the decision from `inconclusive` to `supported` as rejections *increase*.

### 6.2 Exact-Binomial Reference Arm Feasibility (`x2/feasibility_report.json`)

For a reference arm sampling **1 randomly selected genuine claim per independently sampled eligible scenario** (blind to checker verdict) with a two-sided 95% exact Clopper-Pearson interval (`N = 72` is a **mathematical minimum at 0 rejections**, *not* a recommended sample size; all claims remain preserved for paired recall analysis and secondary clustered comparison):

| `N_eligible` | `zero_ub` | `max_k` (`<= 5%`) | `P(clear)` @ `1%` FPR | `P(clear)` @ `2%` FPR | `P(clear)` @ `3%` FPR | Expected `N_total` (`100%` / `90%` / `80%` elig.) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 60 | 0.05963 | None | 0.0000 | 0.0000 | 0.0000 | 60.0 / 66.7 / 75.0 |
| 71 | 0.05063 | None | 0.0000 | 0.0000 | 0.0000 | 71.0 / 78.9 / 88.8 |
| 72 | 0.04994 | 0 | 0.4850 | 0.2335 | 0.1116 | 72.0 / 80.0 / 90.0 |
| 80 | 0.04506 | 0 | 0.4475 | 0.1986 | 0.0874 | 80.0 / 88.9 / 100.0 |
| 90 | 0.04016 | 0 | 0.4047 | 0.1623 | 0.0645 | 90.0 / 100.0 / 112.5 |
| 100 | 0.03622 | 0 | 0.3660 | 0.1326 | 0.0476 | 100.0 / 111.1 / 125.0 |
| 120 | 0.03027 | 1 | 0.6623 | 0.3054 | 0.1218 | 120.0 / 133.3 / 150.0 |
| 150 | 0.02429 | 2 | 0.8095 | 0.4209 | 0.1693 | 150.0 / 166.7 / 187.5 |
| 200 | 0.01828 | 3 | 0.8580 | 0.4315 | 0.1472 | 200.0 / 222.2 / 250.0 |
| 250 | 0.01465 | 5 | 0.9588 | 0.6160 | 0.2373 | 250.0 / 277.8 / 312.5 |
| 300 | 0.01222 | 7 | 0.9885 | 0.7454 | 0.3203 | 300.0 / 333.3 / 375.0 |
