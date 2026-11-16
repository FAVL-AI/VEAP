"""Fixed-cluster monotonicity check and exact-binomial reference design feasibility.

1. Evaluates monotonicity of ``student_t``, ``cluster_score``, and ``scenario_bootstrap``
   as genuine-claim false rejections increase one flip at a time (0..10) at fixed N = 60.
2. Computes a two-sided 95% exact Clopper-Pearson binomial feasibility table for the
   1-claim-per-eligible-scenario reference arm across N_eligible in
   [60, 71, 72, 80, 90, 100, 120, 150, 200, 250, 300].
"""

from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = str(Path(__file__).resolve().parent.parent)
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from x2.interval_calibration import (
    UNEQUAL_CLUSTER_SIZES_60,
    cluster_score_fpr_ci,
    scenario_bootstrap_fpr_ci,
    scenario_clustered_fpr_ci,
)

DEFAULT_REPORT_PATH = Path(__file__).resolve().parent / "feasibility_report.json"

EQUAL_CLUSTER_SIZES_60 = (4,) * 60
N_ELIGIBLE_GRID = (60, 71, 72, 80, 90, 100, 120, 150, 200, 250, 300)


def _flip_order(cluster_sizes: tuple[int, ...], pattern: str) -> list[int]:
    """Return scenario index sequence for 10 single-claim flips under ``pattern``."""
    n = len(cluster_sizes)
    indices = list(range(n))
    if pattern == "distinct_scenarios_largest_first":
        return sorted(indices, key=lambda i: (-cluster_sizes[i], i))[:10]
    if pattern == "distinct_scenarios_smallest_first":
        return sorted(indices, key=lambda i: (cluster_sizes[i], i))[:10]
    if pattern == "single_cluster":
        ordered = sorted(indices, key=lambda i: (-cluster_sizes[i], i))
        seq: list[int] = []
        for idx in ordered:
            seq.extend([idx] * cluster_sizes[idx])
            if len(seq) >= 10:
                break
        return seq[:10]
    raise ValueError(f"Unknown flip pattern: {pattern!r}")


def run_monotonicity_check(n_boot: int = 500, seed: int = 20261116) -> dict[str, Any]:
    """Check whether CI upper bounds and decisions behave monotonically as rejections rise."""
    cluster_configs = {
        "unequal_1_to_7": UNEQUAL_CLUSTER_SIZES_60,
        "equal_4": EQUAL_CLUSTER_SIZES_60,
    }
    patterns = (
        "distinct_scenarios_largest_first",
        "distinct_scenarios_smallest_first",
        "single_cluster",
    )
    methods = ("student_t", "cluster_score", "scenario_bootstrap")

    runs: list[dict[str, Any]] = []
    anomalies_summary: dict[str, int] = {m: 0 for m in methods}

    for cfg_name, sizes in cluster_configs.items():
        n_scenarios = len(sizes)
        total_claims = sum(sizes)
        for pattern in patterns:
            order = _flip_order(sizes, pattern)
            counts = [0] * n_scenarios
            steps: list[dict[str, Any]] = []
            prev_hi: dict[str, float | None] = {m: None for m in methods}
            zero_hi: dict[str, float | None] = {m: None for m in methods}
            prev_dec: dict[str, str | None] = {m: None for m in methods}
            pattern_anomalies: list[dict[str, Any]] = []

            for flip_k in range(11):
                if flip_k > 0:
                    counts[order[flip_k - 1]] += 1
                scenario_fprs = [c / m for c, m in zip(counts, sizes)]
                total_rej = sum(counts)

                lo_t, hi_t = scenario_clustered_fpr_ci(scenario_fprs, total_rej, n_scenarios)
                lo_cs, hi_cs = cluster_score_fpr_ci(scenario_fprs, total_rej, total_claims)
                lo_sb, hi_sb = scenario_bootstrap_fpr_ci(
                    scenario_fprs,
                    total_rej,
                    random.Random(seed + flip_k),
                    n_boot=n_boot,
                )

                step_res = {
                    "student_t": (lo_t, hi_t),
                    "cluster_score": (lo_cs, hi_cs),
                    "scenario_bootstrap": (lo_sb, hi_sb),
                }
                step_entry: dict[str, Any] = {
                    "total_flips": flip_k,
                    "mean_scenario_fpr": sum(scenario_fprs) / n_scenarios,
                    "methods": {},
                }

                for m, (lo, hi) in step_res.items():
                    decision = "supported" if hi <= 0.05 else ("contradicted" if lo > 0.05 else "inconclusive")
                    if flip_k == 0:
                        zero_hi[m] = hi

                    drop_vs_prev = prev_hi[m] is not None and hi < prev_hi[m] - 1e-12
                    drop_vs_zero = zero_hi[m] is not None and hi < zero_hi[m] - 1e-12
                    decision_flip = prev_dec[m] == "inconclusive" and decision == "supported"

                    if drop_vs_prev or drop_vs_zero or decision_flip:
                        anomalies_summary[m] += 1
                        pattern_anomalies.append(
                            {
                                "method": m,
                                "total_flips": flip_k,
                                "ci_high": hi,
                                "prev_ci_high": prev_hi[m],
                                "zero_ci_high": zero_hi[m],
                                "drop_vs_prev": drop_vs_prev,
                                "drop_vs_zero": drop_vs_zero,
                                "decision_flip_inconclusive_to_supported": decision_flip,
                                "prev_decision": prev_dec[m],
                                "new_decision": decision,
                            }
                        )

                    step_entry["methods"][m] = {
                        "ci_low": lo,
                        "ci_high": hi,
                        "decision": decision,
                    }
                    prev_hi[m] = hi
                    prev_dec[m] = decision

                steps.append(step_entry)

            runs.append(
                {
                    "cluster_config": cfg_name,
                    "flip_pattern": pattern,
                    "n_scenarios": n_scenarios,
                    "total_claims": total_claims,
                    "anomalies": pattern_anomalies,
                    "steps": steps,
                }
            )

    return {
        "n_runs": len(runs),
        "anomaly_step_counts_by_method": anomalies_summary,
        "runs": runs,
    }


def _binom_pmf(k: int, n: int, p: float) -> float:
    if p <= 0.0:
        return 1.0 if k == 0 else 0.0
    if p >= 1.0:
        return 1.0 if k == n else 0.0
    log_c = math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)
    return math.exp(log_c + k * math.log(p) + (n - k) * math.log(1.0 - p))


def _binom_cdf(k: int, n: int, p: float) -> float:
    return sum(_binom_pmf(j, n, p) for j in range(k + 1))


def clopper_pearson_upper(k: int, n: int, alpha: float = 0.05) -> float:
    """Exact two-sided (1 - alpha) Clopper-Pearson upper confidence limit."""
    if n <= 0:
        return 1.0
    if k >= n:
        return 1.0
    target = alpha / 2.0
    if k == 0:
        return 1.0 - (target ** (1.0 / n))
    lo, hi = k / n, 1.0
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if _binom_cdf(k, n, mid) > target:
            lo = mid
        else:
            hi = mid
    return hi


def run_exact_binomial_feasibility(
    n_grid: tuple[int, ...] = N_ELIGIBLE_GRID,
    ceiling: float = 0.05,
    alpha: float = 0.05,
    p_eligible_values: tuple[float, ...] = (1.00, 0.90, 0.80),
) -> list[dict[str, Any]]:
    """Compute exact Clopper-Pearson feasibility table for 1-claim-per-eligible-scenario arm."""
    rows: list[dict[str, Any]] = []
    for n_elig in n_grid:
        zero_ub = clopper_pearson_upper(0, n_elig, alpha=alpha)
        max_k: int | None = None
        for k in range(n_elig + 1):
            if clopper_pearson_upper(k, n_elig, alpha=alpha) <= ceiling:
                max_k = k
            else:
                break

        clear_probs = {}
        for p_true in (0.01, 0.02, 0.03):
            key = f"p_clear_at_{int(round(p_true * 100))}pct"
            clear_probs[key] = 0.0 if max_k is None else _binom_cdf(max_k, n_elig, p_true)

        expected_total_scenarios = {
            f"p_elig_{int(round(pe * 100))}pct": n_elig / pe for pe in p_eligible_values
        }

        rows.append(
            {
                "n_eligible": n_elig,
                "zero_rejection_upper_limit": zero_ub,
                "max_k_clearing_5pct": max_k,
                **clear_probs,
                "expected_total_scenarios": expected_total_scenarios,
            }
        )
    return rows


def find_first_n_eligible(
    true_fpr: float,
    target_power: float,
    *,
    ceiling: float = 0.05,
    alpha: float = 0.05,
    max_n: int = 1000,
) -> dict[str, Any]:
    """Find the exact first ``N_eligible`` reaching ``target_power`` under 95% Clopper-Pearson."""
    for n_elig in range(1, max_n + 1):
        max_k: int | None = None
        for k in range(n_elig + 1):
            if clopper_pearson_upper(k, n_elig, alpha=alpha) <= ceiling:
                max_k = k
            else:
                break
        if max_k is None:
            continue
        p_clear = _binom_cdf(max_k, n_elig, true_fpr)
        if p_clear >= target_power:
            return {
                "true_fpr": true_fpr,
                "target_power": target_power,
                "n_eligible": n_elig,
                "max_k_clearing_5pct": max_k,
                "p_clear": p_clear,
            }
    raise RuntimeError(f"No N_eligible <= {max_n} reached target_power={target_power}")


def compute_planning_milestones() -> list[dict[str, Any]]:
    """Verify the four exact integer sample-size milestones."""
    specs = (
        (0.01, 0.80),
        (0.01, 0.90),
        (0.02, 0.80),
        (0.02, 0.90),
    )
    return [find_first_n_eligible(fpr, target) for fpr, target in specs]


def eligibility_cap_probability(
    cap: int = 407,
    target_eligible: int = 312,
    p_eligible: float = 0.80,
) -> float:
    """Compute ``P(Binomial(cap, p_eligible) >= target_eligible)``."""
    if target_eligible <= 0:
        return 1.0
    if target_eligible > cap:
        return 0.0
    return 1.0 - _binom_cdf(target_eligible - 1, cap, p_eligible)


def main(output_path: Path = DEFAULT_REPORT_PATH) -> dict[str, Any]:
    monotonicity = run_monotonicity_check()
    feasibility = run_exact_binomial_feasibility()
    milestones = compute_planning_milestones()
    cap_prob = eligibility_cap_probability(cap=407, target_eligible=312, p_eligible=0.80)
    report = {
        "schema": "veap-x2-feasibility-and-monotonicity/1",
        "scope": "development-only",
        "monotonicity_check": monotonicity,
        "exact_binomial_feasibility": feasibility,
        "planning_milestones": milestones,
        "eligibility_cap_check": {
            "cap": 407,
            "target_eligible": 312,
            "p_eligible": 0.80,
            "p_reach_target": cap_prob,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    rep = main()
    print(
        f"Wrote {DEFAULT_REPORT_PATH} "
        f"(anomalies={rep['monotonicity_check']['anomaly_step_counts_by_method']}, "
        f"n_grid={len(rep['exact_binomial_feasibility'])}, "
        f"cap_prob={rep['eligibility_cap_check']['p_reach_target']:.4f})"
    )
