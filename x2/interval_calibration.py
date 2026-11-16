"""Interval calibration for X2 equal-weighted scenario-averaged false-rejection rate.

Estimand:
    Equal-weighted scenario-averaged false-rejection rate across N = 60 scenarios
    (scenarios with zero genuine claims are excluded from the equal-weighted mean
    and guarded against in scenario design). Rejection is defined as the trajectory
    checker returning ``"violating"`` on a genuine (``DONE == True``) claim
    (``"inconclusive"`` tracked separately).

Methods Compared:
    1. ``student_t``: Scenario-clustered Student-t CI (df = N - 1, N-scenario Wilson floor at 0).
    2. ``cluster_score``: Cluster-adjusted Wilson/score interval using effective sample size
       ``n_eff = min(M, max(1, p_hat * (1 - p_hat) / Var_cluster(p_hat)))`` (or ``N`` at 0).
    3. ``scenario_bootstrap``: Whole-scenario percentile bootstrap (B resamples, N-scenario
       Wilson fallback at 0).
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

DEV_SEED = 20261116
CONFIRM_SEED = 20262201
Z_95 = 1.959963984540054

CALIBRATION_TOLERANCE = {
    "min_coverage_95": 0.92,
    "max_upper_tail_miss": 0.05,
}


def wilson_ci_from_p(p_hat: float, n_eff: float, z: float = Z_95) -> tuple[float, float]:
    """Compute two-sided 95% Wilson score interval at ``(p_hat, n_eff)``."""
    if n_eff <= 0.0:
        return (0.0, 1.0)
    z2 = z * z
    denom = 1.0 + z2 / n_eff
    center = (p_hat + z2 / (2.0 * n_eff)) / denom
    half = z * math.sqrt((p_hat * (1.0 - p_hat) / n_eff) + (z2 / (4.0 * n_eff * n_eff))) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def _draw_scenario_fpr_counts(
    rng: random.Random,
    cluster_sizes: tuple[int, ...],
    true_fpr: float,
    rho: float,
) -> tuple[list[float], int, int]:
    """Draw correlated per-scenario genuine-claim rejections using Beta-Binomial.

    Scenarios with ``m_i == 0`` genuine claims are excluded from the equal-weighted mean.
    """
    valid_sizes = tuple(m for m in cluster_sizes if m > 0)
    if len(valid_sizes) < 2:
        raise ValueError("Need at least 2 scenarios with >0 genuine claims")

    scenario_fprs: list[float] = []
    total_rejections = 0
    total_claims = 0

    if rho > 0.0 and 0.0 < true_fpr < 1.0:
        concentration = (1.0 - rho) / rho
        alpha = true_fpr * concentration
        beta = (1.0 - true_fpr) * concentration
    else:
        alpha = beta = 0.0

    for m_i in valid_sizes:
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
    """Method 1 (``student_t``): 95% scenario-clustered Student-t CI with Wilson floor at 0."""
    n_scenarios = len(scenario_fprs)
    mean_fpr = sum(scenario_fprs) / n_scenarios
    var_fpr = sum((f - mean_fpr) ** 2 for f in scenario_fprs) / (n_scenarios - 1)
    if total_rejections == 0 or (var_fpr == 0.0 and mean_fpr == 0.0):
        return (0.0, wilson_ci(0, zero_event_denominator)[1])
    t_crit = t_critical_95(n_scenarios - 1)
    se_fpr = math.sqrt(var_fpr / n_scenarios)
    return (max(0.0, mean_fpr - t_crit * se_fpr), min(1.0, mean_fpr + t_crit * se_fpr))


def cluster_score_fpr_ci(
    scenario_fprs: list[float],
    total_rejections: int,
    total_claims: int,
) -> tuple[float, float]:
    """Method 2 (``cluster_score``): Cluster-adjusted Wilson/score interval using n_eff."""
    n_scenarios = len(scenario_fprs)
    if total_rejections == 0:
        return wilson_ci_from_p(0.0, float(n_scenarios))
    p_hat = sum(scenario_fprs) / n_scenarios
    var_s = sum((f - p_hat) ** 2 for f in scenario_fprs) / (n_scenarios - 1)
    var_cluster = var_s / n_scenarios
    if var_cluster <= 0.0 or p_hat <= 0.0 or p_hat >= 1.0:
        n_eff = float(n_scenarios)
    else:
        n_eff = min(float(total_claims), max(1.0, (p_hat * (1.0 - p_hat)) / var_cluster))
    return wilson_ci_from_p(p_hat, n_eff)


def scenario_bootstrap_fpr_ci(
    scenario_fprs: list[float],
    total_rejections: int,
    boot_rng: random.Random,
    n_boot: int = 250,
) -> tuple[float, float]:
    """Method 3 (``scenario_bootstrap``): Whole-scenario percentile bootstrap."""
    n_scenarios = len(scenario_fprs)
    if total_rejections == 0:
        return (0.0, wilson_ci(0, n_scenarios)[1])
    draws: list[float] = []
    randrange = boot_rng.randrange
    for _ in range(n_boot):
        s = 0.0
        for _ in range(n_scenarios):
            s += scenario_fprs[randrange(n_scenarios)]
        draws.append(s / n_scenarios)
    draws.sort()
    lo_idx = int(math.floor(0.025 * n_boot))
    hi_idx = min(n_boot - 1, int(math.ceil(0.975 * n_boot)) - 1)
    return (draws[lo_idx], draws[hi_idx])


def _binom_mcse(p: float, n: int) -> float:
    return math.sqrt(max(0.0, p * (1.0 - p)) / n)


def evaluate_methods_for_cell(
    *,
    rho: float,
    true_fpr: float,
    cluster_sizes: tuple[int, ...] = UNEQUAL_CLUSTER_SIZES_60,
    ceiling: float = 0.05,
    n_replicates: int = 1000,
    n_boot: int = 250,
    seed: int = CONFIRM_SEED,
) -> dict[str, dict[str, Any]]:
    """Evaluate all 3 CI methods on the same simulated replicates for one ``(rho, true_fpr)`` cell."""
    data_rng = random.Random(seed)
    boot_rng = random.Random(seed + 500_000)
    n_scenarios = len([m for m in cluster_sizes if m > 0])

    methods = ("student_t", "cluster_score", "scenario_bootstrap")
    acc: dict[str, dict[str, Any]] = {
        m: {"cov": 0, "upper_miss": 0, "support": 0, "widths": []} for m in methods
    }

    for _ in range(n_replicates):
        scenario_fprs, total_rej, m_total = _draw_scenario_fpr_counts(
            data_rng, cluster_sizes, true_fpr, rho
        )
        intervals = {
            "student_t": scenario_clustered_fpr_ci(scenario_fprs, total_rej, n_scenarios),
            "cluster_score": cluster_score_fpr_ci(scenario_fprs, total_rej, m_total),
            "scenario_bootstrap": scenario_bootstrap_fpr_ci(
                scenario_fprs, total_rej, boot_rng, n_boot=n_boot
            ),
        }
        for m, (lo, hi) in intervals.items():
            if lo <= true_fpr <= hi:
                acc[m]["cov"] += 1
            if hi < true_fpr:
                acc[m]["upper_miss"] += 1
            if hi <= ceiling:
                acc[m]["support"] += 1
            acc[m]["widths"].append(hi - lo)

    if true_fpr < ceiling:
        regime_tag = "below_ceiling"
    elif true_fpr == ceiling:
        regime_tag = "boundary"
    else:
        regime_tag = "above_ceiling"

    out: dict[str, dict[str, Any]] = {}
    for m in methods:
        cov = acc[m]["cov"] / n_replicates
        umiss = acc[m]["upper_miss"] / n_replicates
        sup = acc[m]["support"] / n_replicates
        widths = acc[m]["widths"]
        mean_w = sum(widths) / n_replicates
        var_w = sum((w - mean_w) ** 2 for w in widths) / max(1, n_replicates - 1)
        w_mcse = math.sqrt(var_w / n_replicates)

        out[m] = {
            "method": m,
            "rho": rho,
            "true_fpr": true_fpr,
            "regime_tag": regime_tag,
            "coverage_95": cov,
            "coverage_95_mcse": _binom_mcse(cov, n_replicates),
            "upper_tail_miss": umiss,
            "upper_tail_miss_mcse": _binom_mcse(umiss, n_replicates),
            "mean_width": mean_w,
            "mean_width_mcse": w_mcse,
            "support_prob": sup,
            "support_prob_mcse": _binom_mcse(sup, n_replicates),
        }
    return out


def run_interval_calibration(
    *,
    rhos: tuple[float, ...] = (0.0, 0.25, 0.50),
    true_fprs: tuple[float, ...] = (0.0, 0.049, 0.050, 0.051, 0.060, 0.070),
    n_replicates: int = 1000,
    n_boot: int = 250,
    dev_seed: int = DEV_SEED,
    confirm_seed: int = CONFIRM_SEED,
) -> dict[str, Any]:
    """Run dev sanity check on ``dev_seed`` and locked confirmation grid on ``confirm_seed``."""
    # Lightweight dev-seed sanity check (locked before confirmation run)
    dev_sanity = evaluate_methods_for_cell(
        rho=0.25, true_fpr=0.050, n_replicates=200, n_boot=n_boot, seed=dev_seed
    )

    # Fresh confirmation evaluation across full (rho, true_fpr) grid
    rows_by_method: dict[str, list[dict[str, Any]]] = {
        "student_t": [],
        "cluster_score": [],
        "scenario_bootstrap": [],
    }
    for r_idx, rho in enumerate(rhos):
        for f_idx, true_fpr in enumerate(true_fprs):
            cell_seed = confirm_seed + r_idx * 100 + f_idx
            res = evaluate_methods_for_cell(
                rho=rho,
                true_fpr=true_fpr,
                n_replicates=n_replicates,
                n_boot=n_boot,
                seed=cell_seed,
            )
            for m, row in res.items():
                rows_by_method[m].append(row)

    worst_case_summary: dict[str, dict[str, Any]] = {}
    for m, rows in rows_by_method.items():
        pos_rows = [r for r in rows if r["true_fpr"] > 0.0]
        above_rows = [r for r in rows if r["true_fpr"] > 0.05]
        min_cov_row = min(pos_rows, key=lambda r: r["coverage_95"])
        max_umiss_row = max(pos_rows, key=lambda r: r["upper_tail_miss"])
        max_incorr_row = max(above_rows, key=lambda r: r["support_prob"])
        meets_tol = (
            min_cov_row["coverage_95"] >= CALIBRATION_TOLERANCE["min_coverage_95"]
            and max_umiss_row["upper_tail_miss"] <= CALIBRATION_TOLERANCE["max_upper_tail_miss"]
        )
        worst_case_summary[m] = {
            "min_coverage_95": min_cov_row["coverage_95"],
            "min_coverage_at": {"rho": min_cov_row["rho"], "true_fpr": min_cov_row["true_fpr"]},
            "max_upper_tail_miss": max_umiss_row["upper_tail_miss"],
            "max_upper_tail_miss_at": {
                "rho": max_umiss_row["rho"],
                "true_fpr": max_umiss_row["true_fpr"],
            },
            "max_incorrect_support_rate": max_incorr_row["support_prob"],
            "max_incorrect_support_at": {
                "rho": max_incorr_row["rho"],
                "true_fpr": max_incorr_row["true_fpr"],
            },
            "meets_calibration_tolerance": meets_tol,
        }

    calibrated_candidates = [
        m for m, summary in worst_case_summary.items() if summary["meets_calibration_tolerance"]
    ]

    return {
        "schema": "veap-x2-interval-calibration/2",
        "estimand": (
            "Equal-weighted scenario-averaged false-rejection rate across N = 60 scenarios "
            "(scenarios with zero genuine claims excluded from mean and guarded against in design)"
        ),
        "rejection_definition": (
            "Trajectory checker returning 'violating' on a genuine (DONE = True) claim; "
            "'inconclusive' tracked separately"
        ),
        "seeds": {"dev_seed": dev_seed, "confirm_seed": confirm_seed},
        "n_replicates_confirm": n_replicates,
        "n_boot": n_boot,
        "calibration_tolerance": CALIBRATION_TOLERANCE,
        "cluster_sizes": {
            "n_scenarios": len(UNEQUAL_CLUSTER_SIZES_60),
            "min_claims": min(UNEQUAL_CLUSTER_SIZES_60),
            "max_claims": max(UNEQUAL_CLUSTER_SIZES_60),
            "mean_claims": sum(UNEQUAL_CLUSTER_SIZES_60) / len(UNEQUAL_CLUSTER_SIZES_60),
            "total_genuine_claims": sum(UNEQUAL_CLUSTER_SIZES_60),
        },
        "dev_sanity_check": dev_sanity,
        "results_by_method": rows_by_method,
        "worst_case_summary": worst_case_summary,
        "calibrated_candidates": calibrated_candidates,
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
        f"(calibrated_candidates={rep['calibrated_candidates']})"
    )
    for m, s in rep["worst_case_summary"].items():
        print(
            f"  {m}: min_cov={s['min_coverage_95']:.4f} at {s['min_coverage_at']}, "
            f"max_umiss={s['max_upper_tail_miss']:.4f} at {s['max_upper_tail_miss_at']}, "
            f"max_incorr_sup={s['max_incorrect_support_rate']:.4f}, "
            f"meets_tol={s['meets_calibration_tolerance']}"
        )
