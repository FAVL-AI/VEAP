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
| **Candidate Scenario Count (`N`)** | **Candidate design: `N = 60` scenarios** (not a final freeze; ~3 `DONE == False` and 4 genuine `DONE == True` claims per scenario; 180 ref-false, 240 genuine ref-true claims) | From cluster-aware `x2/precision_report.json` (`x2/precision_analysis.py`, using scenario-clustered Student-$t$ CIs for both endpoints), every simulated study is classified into mutually exclusive `supported`, `contradicted`, or `inconclusive` states. At `N = 60`, nominal `joint` outcomes are `90.05%` `supported` (`1801/2000`), `0.00%` `contradicted`, `9.95%` `inconclusive` (`recall`: `98.70%` supported / `1.30%` inconclusive; `false_rejection`: `91.30%` supported / `8.70%` inconclusive). Pessimistic `joint` outcomes are `54.30%` `supported` (`1086/2000`), `0.00%` `contradicted`, `45.70%` `inconclusive` (`recall`: `78.25%` supported / `21.75%` inconclusive; `false_rejection`: `68.45%` supported / `31.55%` inconclusive). Final freeze requires confirming whether `N = 60` or a larger `N` is adopted. |
| **Acceptance Thresholds: Minimum Meaningful Recall Improvement** | **`>= 0.10`** (10 percentage points) | `supported` iff $\text{CI}_{\text{low}} \ge 0.10$; `contradicted` iff $\text{CI}_{\text{high}} < 0.10$; `inconclusive` otherwise. |
| **Acceptance Thresholds: False-Rejection Ceiling** | **`<= 0.05`** (5% ceiling) on **equal-weighted scenario-averaged FPR** | **Estimand:** equal-weighted scenario-averaged false-rejection rate across `N = 60` scenarios ($\frac{1}{N}\sum_{i=1}^{N} k_i/m_i$; scenarios with zero genuine claims $m_i = 0$ are excluded from the equal-weighted mean and guarded against in scenario design). **Rejection definition:** trajectory checker returning `"violating"` on a genuine (`DONE == True`) claim (`"inconclusive"` tracked separately). **Boundary terminology:** `support_prob_at_boundary` (`true_fpr == 0.050`, upper-tail miss diagnostic) is tracked separately from `incorrect_support_rate` (`true_fpr > 0.050`: `0.051`, `0.060`, `0.070`). `supported` iff $\text{CI}_{\text{high}} \le 0.05$; `contradicted` iff $\text{CI}_{\text{low}} > 0.05$; `inconclusive` otherwise. |
| **Acceptance Thresholds: CI Rule** | Two-sided 95% CI (`alpha = 0.05`); calibration comparison in `x2/interval_calibration_report.json` | Three prespecified FPR intervals were compared on fresh confirmation seeds (`confirm_seed = 20262201`, separate from `dev_seed = 20261116`) across `rho in [0.0, 0.25, 0.50]` and `true_fpr in [0.0, 0.049, 0.050, 0.051, 0.060, 0.070]` with unequal cluster sizes `1..7`: `student_t` (worst-case `min_cov = 0.8820`, `max_umiss = 0.1150`, `max_incorr_sup = 0.1100`), `cluster_score` (`min_cov = 0.8970`, `max_umiss = 0.0660`, `max_incorr_sup = 0.0440`), and `scenario_bootstrap` (`min_cov = 0.8820`, `max_umiss = 0.1050`, `max_incorr_sup = 0.1020`). **Calibration outcome:** none of the three methods met the prespecified worst-case tolerance (`min_cov >= 0.92` and `max_umiss <= 0.05` at `rho = 0.50`), so `precision_analysis.py` is held on `student_t` without switching to an uncalibrated replacement. |
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
