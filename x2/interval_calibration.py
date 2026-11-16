"""Interval calibration for X2 equal-weighted scenario-averaged false-rejection rate.

Estimand:
    Equal-weighted scenario-averaged false-rejection rate across N = 60 scenarios,
    where rejection is defined as the trajectory checker returning ``"violating"``
    on a genuine (``DONE == True``) claim (``"inconclusive"`` tracked separately).

Interval Convention:
    Two-sided 95% scenario-clustered Student-t CI (df = N - 1) when scenario-level
    variance is non-zero, with an explicit comparison of the zero-event Wilson
    upper-bound floor under the N = 60 scenario-level denominator (~6.02%) vs the
    240 pooled-claim denominator (~1.58%).
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

from x2.precision_analysis import t_critical_95, wilson_ci

DEFAULT_REPORT_PATH = Path(__file__).resolve().parent / "interval_calibration_report.json"

# 60 scenarios with unequal genuine-claim counts in 1..7, mean = 4.0, total = 240
UNEQUAL_CLUSTER_SIZES_60 = tuple([1, 2, 3, 4, 5, 6, 7, 4, 4, 4] * 6)


def _draw_scenario_fpr_counts(
    rng: random.Random,
    cluster_sizes: tuple[int, ...],
    true_fpr: float,
    rho: float,
) -> tuple[list[float], int, int]:
    """Draw correlated per-scenario genuine-claim rejections using Beta-Binomial."""
    scenario_fprs: list[float] = []
    total_rejections = 0
    total_claims = 0

    if rho > 0.0 and 0.0 < true_fpr < 1.0:
        concentration = (1.0 - rho) / rho
        alpha = true_fpr * concentration
        beta = (1.0 - true_fpr) * concentration
    else:
        alpha = beta = 0.0

    for m_i in cluster_sizes:
        if rho > 0.0 and 0.0 < true_fpr < 1.0:
            p_i = rng.betavariate(alpha, beta)
        else:
            p_i = true_fpr
        k_i = sum(1 for _ in range(m_i) if rng.random() < p_i)
        scenario_fprs.append(k_i / m_i)
        total_rejections += k_i
        total_claims += m_i

    return scenario_fprs, total_rejections, total_claims


def scenario_clustered_fpr_ci(
    scenario_fprs: list[float],
    total_rejections: int,
    zero_event_denominator: int,
) -> tuple[float, float]:
    """Compute 95% scenario-clustered Student-t CI with specified zero-event Wilson floor."""
    n_scenarios = len(scenario_fprs)
    mean_fpr = sum(scenario_fprs) / n_scenarios
    var_fpr = sum((f - mean_fpr) ** 2 for f in scenario_fprs) / (n_scenarios - 1)
    if var_fpr == 0.0 and mean_fpr == 0.0:
        return (0.0, wilson_ci(0, zero_event_denominator)[1])
    t_crit = t_critical_95(n_scenarios - 1)
    se_fpr = math.sqrt(var_fpr / n_scenarios)
    ci_low = max(0.0, mean_fpr - t_crit * se_fpr)
    ci_high = min(1.0, mean_fpr + t_crit * se_fpr)
    return (ci_low, ci_high)


def calibrate_fpr_cell(
    *,
    rho: float,
    true_fpr: float,
    cluster_sizes: tuple[int, ...] = UNEQUAL_CLUSTER_SIZES_60,
    ceiling: float = 0.05,
    n_replicates: int = 2000,
    seed: int = 20261116,
) -> dict[str, Any]:
    """Calibrate coverage, Type-I error, and zero-event floor behavior for one ``(rho, true_fpr)`` cell."""
    rng = random.Random(seed)
    n_scenarios = len(cluster_sizes)
    total_claims = sum(cluster_sizes)

    covered_pooled_floor = 0
    covered_scenario_floor = 0
    zero_events = 0

    states_pooled_floor = {"supported": 0, "contradicted": 0, "inconclusive": 0}
    states_scenario_floor = {"supported": 0, "contradicted": 0, "inconclusive": 0}

    for _ in range(n_replicates):
        scenario_fprs, total_rej, m_total = _draw_scenario_fpr_counts(
            rng, cluster_sizes, true_fpr, rho
        )
        if total_rej == 0:
            zero_events += 1

        lo_p, hi_p = scenario_clustered_fpr_ci(scenario_fprs, total_rej, m_total)
        lo_s, hi_s = scenario_clustered_fpr_ci(scenario_fprs, total_rej, n_scenarios)

        if lo_p <= true_fpr <= hi_p:
            covered_pooled_floor += 1
        if lo_s <= true_fpr <= hi_s:
            covered_scenario_floor += 1

        for lo, hi, bucket in (
            (lo_p, hi_p, states_pooled_floor),
            (lo_s, hi_s, states_scenario_floor),
        ):
            if hi <= ceiling:
                bucket["supported"] += 1
            elif lo > ceiling:
                bucket["contradicted"] += 1
            else:
                bucket["inconclusive"] += 1

    return {
        "rho": rho,
        "true_fpr": true_fpr,
        "n_scenarios": n_scenarios,
        "total_genuine_claims": total_claims,
        "zero_event_rate": zero_events / n_replicates,
        "coverage_95": covered_pooled_floor / n_replicates,
        "incorrect_support_rate": states_pooled_floor["supported"] / n_replicates,
        "supported_rate": states_pooled_floor["supported"] / n_replicates,
        "contradicted_rate": states_pooled_floor["contradicted"] / n_replicates,
        "inconclusive_rate": states_pooled_floor["inconclusive"] / n_replicates,
        "scenario_floor_comparison": {
            "zero_event_floor_n60": wilson_ci(0, n_scenarios)[1],
            "zero_event_floor_240": wilson_ci(0, total_claims)[1],
            "coverage_95_scenario_floor": covered_scenario_floor / n_replicates,
            "supported_rate_scenario_floor": states_scenario_floor["supported"] / n_replicates,
            "inconclusive_rate_scenario_floor": states_scenario_floor["inconclusive"] / n_replicates,
        },
    }


def calibrate_subtarget_regime(
    *,
    true_recall_gain: float = 0.03,
    true_fpr: float = 0.08,
    rho_fpr: float = 0.25,
    cluster_sizes: tuple[int, ...] = UNEQUAL_CLUSTER_SIZES_60,
    claims_false_per_scenario: int = 3,
    scenario_sd_recall: float = 0.08,
    min_meaningful_improvement: float = 0.10,
    max_false_rejection_rate: float = 0.05,
    n_replicates: int = 2000,
    seed: int = 20261199,
) -> dict[str, Any]:
    """Exercise the ``contradicted`` branch with sub-target recall gain (0.03) and high FPR (0.08)."""
    rng = random.Random(seed)
    n_scenarios = len(cluster_sizes)
    t_crit = t_critical_95(n_scenarios - 1)
    p_loss = 0.03
    p_gain = true_recall_gain + p_loss

    recall_counts = {"supported": 0, "contradicted": 0, "inconclusive": 0}
    fpr_counts = {"supported": 0, "contradicted": 0, "inconclusive": 0}
    joint_counts = {"supported": 0, "contradicted": 0, "inconclusive": 0}

    for _ in range(n_replicates):
        scenario_diffs: list[float] = []
        for _ in range(n_scenarios):
            p_gain_i = max(0.0, min(1.0 - p_loss, p_gain + rng.gauss(0.0, scenario_sd_recall)))
            diff_sum = 0
            for _ in range(claims_false_per_scenario):
                u = rng.random()
                if u < p_gain_i:
                    diff_sum += 1
                elif u < p_gain_i + p_loss:
                    diff_sum -= 1
            scenario_diffs.append(diff_sum / claims_false_per_scenario)

        mean_d = sum(scenario_diffs) / n_scenarios
        var_d = sum((d - mean_d) ** 2 for d in scenario_diffs) / (n_scenarios - 1)
        se_d = math.sqrt(var_d / n_scenarios)
        ci_low_r = mean_d - t_crit * se_d
        ci_high_r = mean_d + t_crit * se_d

        scenario_fprs, total_rej, m_total = _draw_scenario_fpr_counts(
            rng, cluster_sizes, true_fpr, rho_fpr
        )
        ci_low_f, ci_high_f = scenario_clustered_fpr_ci(scenario_fprs, total_rej, m_total)

        if ci_low_r >= min_meaningful_improvement:
            r_state = "supported"
        elif ci_high_r < min_meaningful_improvement:
            r_state = "contradicted"
        else:
            r_state = "inconclusive"

        if ci_high_f <= max_false_rejection_rate:
            f_state = "supported"
        elif ci_low_f > max_false_rejection_rate:
            f_state = "contradicted"
        else:
            f_state = "inconclusive"

        if r_state == "supported" and f_state == "supported":
            j_state = "supported"
        elif r_state == "contradicted" or f_state == "contradicted":
            j_state = "contradicted"
        else:
            j_state = "inconclusive"

        recall_counts[r_state] += 1
        fpr_counts[f_state] += 1
        joint_counts[j_state] += 1

    return {
        "description": "Sub-target calibration regime exercising contradicted branch",
        "true_recall_gain": true_recall_gain,
        "true_fpr": true_fpr,
        "rho_fpr": rho_fpr,
        "n_scenarios": n_scenarios,
        "n_replicates": n_replicates,
        "outcomes": {
            "recall": {k: v / n_replicates for k, v in recall_counts.items()},
            "false_rejection": {k: v / n_replicates for k, v in fpr_counts.items()},
            "joint": {k: v / n_replicates for k, v in joint_counts.items()},
        },
    }


def run_interval_calibration(
    *,
    rhos: tuple[float, ...] = (0.0, 0.25, 0.50),
    true_fprs: tuple[float, ...] = (0.015, 0.030, 0.050, 0.070, 0.100),
    n_replicates: int = 2000,
    seed: int = 20261116,
) -> dict[str, Any]:
    """Run full FPR interval calibration grid and sub-target contradicted check."""
    grid: list[dict[str, Any]] = []
    for r_idx, rho in enumerate(rhos):
        for f_idx, true_fpr in enumerate(true_fprs):
            cell_seed = seed + r_idx * 100 + f_idx
            grid.append(
                calibrate_fpr_cell(
                    rho=rho,
                    true_fpr=true_fpr,
                    n_replicates=n_replicates,
                    seed=cell_seed,
                )
            )

    subtarget = calibrate_subtarget_regime(n_replicates=n_replicates, seed=seed + 9999)

    return {
        "schema": "veap-x2-interval-calibration/1",
        "estimand": "Equal-weighted scenario-averaged false-rejection rate across N = 60 scenarios",
        "rejection_definition": "Trajectory checker returning 'violating' on a genuine (DONE = True) claim; 'inconclusive' tracked separately",
        "interval_convention": {
            "nonzero_variance": "Two-sided 95% scenario-clustered Student-t CI (df = N - 1)",
            "zero_event_floor_n60": wilson_ci(0, len(UNEQUAL_CLUSTER_SIZES_60))[1],
            "zero_event_floor_240": wilson_ci(0, sum(UNEQUAL_CLUSTER_SIZES_60))[1],
        },
        "cluster_sizes": {
            "n_scenarios": len(UNEQUAL_CLUSTER_SIZES_60),
            "min_claims": min(UNEQUAL_CLUSTER_SIZES_60),
            "max_claims": max(UNEQUAL_CLUSTER_SIZES_60),
            "mean_claims": sum(UNEQUAL_CLUSTER_SIZES_60) / len(UNEQUAL_CLUSTER_SIZES_60),
            "total_genuine_claims": sum(UNEQUAL_CLUSTER_SIZES_60),
        },
        "n_replicates": n_replicates,
        "fpr_calibration_grid": grid,
        "subtarget_contradicted_check": subtarget,
    }


def main(output_path: Path = DEFAULT_REPORT_PATH) -> dict[str, Any]:
    report = run_interval_calibration()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    rep = main()
    print(
        f"Wrote {DEFAULT_REPORT_PATH} "
        f"(cells={len(rep['fpr_calibration_grid'])}, "
        f"floor_n60={rep['interval_convention']['zero_event_floor_n60']:.4f}, "
        f"floor_240={rep['interval_convention']['zero_event_floor_240']:.4f}, "
        f"subtarget_joint_contradicted={rep['subtarget_contradicted_check']['outcomes']['joint']['contradicted']:.4f})"
    )
