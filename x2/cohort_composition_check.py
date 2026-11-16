"""Development-only cohort composition and coverage simulation for X2.

Loads the 407-row order from ``build_confirmatory_manifest("dev-preview-only-not-sealed")``
and simulates 2,000 Monte Carlo replicates across 3 regimes (``homogeneous``,
``heterogeneous_moderate``, ``heterogeneous_severe``) under the exact first-312
rule and two-sided 95% exact Clopper-Pearson interval against <= 0.05.
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

from x2.cohort_manifest import build_confirmatory_manifest
from x2.feasibility_and_monotonicity import _binom_cdf, clopper_pearson_upper

DEFAULT_REPORT_PATH = Path(__file__).resolve().parent / "cohort_composition_report.json"

TARGET_ELIGIBLE = 312
CEILING = 0.05

REGIMES: dict[str, dict[tuple[str, str], tuple[float, float]]] = {
    "homogeneous": {
        (fam, pol): (0.80, 0.020)
        for fam in (
            "warehouse-transfer",
            "hospital-inspection",
            "campus-patrol",
            "distribution-shift",
            "absence-rejection",
        )
        for pol in ("ppo", "rrt_replan")
    },
    "heterogeneous_moderate": {
        ("absence-rejection", "ppo"): (0.45, 0.035),
        ("absence-rejection", "rrt_replan"): (0.70, 0.025),
        ("distribution-shift", "ppo"): (0.75, 0.030),
        ("distribution-shift", "rrt_replan"): (0.82, 0.020),
        ("warehouse-transfer", "ppo"): (0.85, 0.015),
        ("warehouse-transfer", "rrt_replan"): (0.88, 0.012),
        ("hospital-inspection", "ppo"): (0.82, 0.018),
        ("hospital-inspection", "rrt_replan"): (0.86, 0.014),
        ("campus-patrol", "ppo"): (0.88, 0.012),
        ("campus-patrol", "rrt_replan"): (0.90, 0.010),
    },
    "heterogeneous_severe": {
        ("absence-rejection", "ppo"): (0.25, 0.055),
        ("absence-rejection", "rrt_replan"): (0.55, 0.040),
        ("distribution-shift", "ppo"): (0.55, 0.045),
        ("distribution-shift", "rrt_replan"): (0.75, 0.030),
        ("warehouse-transfer", "ppo"): (0.85, 0.012),
        ("warehouse-transfer", "rrt_replan"): (0.90, 0.008),
        ("hospital-inspection", "ppo"): (0.80, 0.015),
        ("hospital-inspection", "rrt_replan"): (0.88, 0.010),
        ("campus-patrol", "ppo"): (0.88, 0.008),
        ("campus-patrol", "rrt_replan"): (0.92, 0.005),
    },
}


def clopper_pearson_lower(k: int, n: int, alpha: float = 0.05) -> float:
    """Exact two-sided (1 - alpha) Clopper-Pearson lower confidence limit."""
    if n <= 0 or k <= 0:
        return 0.0
    target = alpha / 2.0
    if k >= n:
        return target ** (1.0 / n)
    lo, hi = 0.0, k / n
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        upper_tail = 1.0 - _binom_cdf(k - 1, n, mid)
        if upper_tail < target:
            lo = mid
        else:
            hi = mid
    return lo


def simulate_cohort_composition(
    *,
    n_replicates: int = 2000,
    seed: int = 20261116,
) -> dict[str, Any]:
    """Run cohort-composition simulation on the 407-row dev-preview manifest."""
    preview = build_confirmatory_manifest("dev-preview-only-not-sealed")
    scenarios = preview["manifest"]["scenarios"]
    n_cap = len(scenarios)
    row_keys = [(r["task_family"], r["policy"]) for r in scenarios]

    all_cells = sorted(set(row_keys))
    manifest_counts = {cell: row_keys.count(cell) for cell in all_cells}

    cp_cache: dict[tuple[int, int], tuple[float, float]] = {}

    def _get_cp(k: int, n: int) -> tuple[float, float]:
        key = (k, n)
        if key not in cp_cache:
            cp_cache[key] = (clopper_pearson_lower(k, n), clopper_pearson_upper(k, n))
        return cp_cache[key]

    regime_results: dict[str, Any] = {}

    for r_idx, (regime_name, cell_params) in enumerate(REGIMES.items()):
        rng = random.Random(seed + r_idx * 1000)

        equal_cohort_fpr = sum(cell_params[k][1] for k in row_keys) / n_cap
        elig_weights = [cell_params[k][0] for k in row_keys]
        selected_true_fpr = sum(
            cell_params[k][0] * cell_params[k][1] for k in row_keys
        ) / sum(elig_weights)

        reach_312_count = 0
        reached_and_cleared_count = 0
        shortfall_cleared_count = 0
        selected_n_sum = 0
        cov_selected_true_all = 0
        cov_selected_true_reached = 0
        cov_equal_cohort_all = 0
        cov_equal_cohort_reached = 0
        cell_eligible_sums = {cell: 0 for cell in all_cells}
        cell_selected_sums = {cell: 0 for cell in all_cells}

        for _ in range(n_replicates):
            n_sel = 0
            k_rej = 0
            for cell in row_keys:
                p_elig, p_fpr = cell_params[cell]
                is_elig = rng.random() < p_elig
                if is_elig:
                    cell_eligible_sums[cell] += 1
                    if n_sel < TARGET_ELIGIBLE:
                        n_sel += 1
                        cell_selected_sums[cell] += 1
                        if rng.random() < p_fpr:
                            k_rej += 1

            reached = n_sel >= TARGET_ELIGIBLE
            if reached:
                reach_312_count += 1
            selected_n_sum += n_sel

            lo, hi = _get_cp(k_rej, n_sel)
            cleared = hi <= CEILING
            if reached and cleared:
                reached_and_cleared_count += 1
            elif (not reached) and cleared:
                shortfall_cleared_count += 1

            if lo <= selected_true_fpr <= hi:
                cov_selected_true_all += 1
                if reached:
                    cov_selected_true_reached += 1
            if lo <= equal_cohort_fpr <= hi:
                cov_equal_cohort_all += 1
                if reached:
                    cov_equal_cohort_reached += 1

        n_cleared_numeric_all = reached_and_cleared_count + shortfall_cleared_count
        mean_selected_n = selected_n_sum / n_replicates
        composition: list[dict[str, Any]] = []
        for fam, pol in all_cells:
            m_cnt = manifest_counts[(fam, pol)]
            m_share = m_cnt / n_cap
            mean_elig_cnt = cell_eligible_sums[(fam, pol)] / n_replicates
            mean_sel_cnt = cell_selected_sums[(fam, pol)] / n_replicates
            mean_sel_share = mean_sel_cnt / mean_selected_n if mean_selected_n > 0 else 0.0
            p_elig, p_fpr = cell_params[(fam, pol)]
            composition.append(
                {
                    "task_family": fam,
                    "policy": pol,
                    "p_elig": p_elig,
                    "p_fpr": p_fpr,
                    "assigned_count": m_cnt,
                    "manifest_count": m_cnt,
                    "manifest_share": m_share,
                    "mean_eligible_count": mean_elig_cnt,
                    "mean_selected_count": mean_sel_cnt,
                    "mean_selected_share": mean_sel_share,
                    "share_shift": mean_sel_share - m_share,
                }
            )

        regime_results[regime_name] = {
            "n_replicates": n_replicates,
            "n_reached_312": reach_312_count,
            "n_reached_312_and_cleared_5pct": reached_and_cleared_count,
            "n_shortfall_but_cleared_5pct_numerically": shortfall_cleared_count,
            "n_cleared_numeric_all": n_cleared_numeric_all,
            "p_reach_312": reach_312_count / n_replicates,
            "p_reach_and_clear": reached_and_cleared_count / n_replicates,
            "p_clear_given_reached_312": (
                reached_and_cleared_count / reach_312_count if reach_312_count > 0 else None
            ),
            "p_clear_numeric_all": n_cleared_numeric_all / n_replicates,
            "p_clear_5pct": n_cleared_numeric_all / n_replicates,
            "mean_selected_n": mean_selected_n,
            "selected_true_fpr": selected_true_fpr,
            "equal_cohort_fpr": equal_cohort_fpr,
            "cov95_vs_selected_true_all": cov_selected_true_all / n_replicates,
            "cov95_vs_selected_true_given_reached_312": (
                cov_selected_true_reached / reach_312_count if reach_312_count > 0 else None
            ),
            "cov95_vs_equal_cohort_all": cov_equal_cohort_all / n_replicates,
            "cov95_vs_equal_cohort_given_reached_312": (
                cov_equal_cohort_reached / reach_312_count if reach_312_count > 0 else None
            ),
            "coverage_95_vs_selected_true": cov_selected_true_all / n_replicates,
            "coverage_95_vs_equal_cohort": cov_equal_cohort_all / n_replicates,
            "composition": composition,
        }

    return {
        "schema": "veap-x2-cohort-composition-check/1",
        "scope": "development-only",
        "dev_preview_manifest_sha256": preview["manifest_sha256"],
        "n_cap": n_cap,
        "target_eligible": TARGET_ELIGIBLE,
        "n_replicates": n_replicates,
        "seed": seed,
        "regimes": regime_results,
    }


def main(output_path: Path = DEFAULT_REPORT_PATH) -> dict[str, Any]:
    report = simulate_cohort_composition()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    rep = main()
    print(f"Wrote {DEFAULT_REPORT_PATH} (preview_sha256={rep['dev_preview_manifest_sha256'][:12]}...)")
    for name, res in rep["regimes"].items():
        print(
            f"  {name}: p_reach_312={res['p_reach_312']:.4f}, "
            f"mean_n={res['mean_selected_n']:.2f}, "
            f"sel_fpr={res['selected_true_fpr']:.4f}, eq_fpr={res['equal_cohort_fpr']:.4f}, "
            f"cov_sel={res['coverage_95_vs_selected_true']:.4f}, cov_eq={res['coverage_95_vs_equal_cohort']:.4f}, "
            f"p_clear={res['p_clear_5pct']:.4f}"
        )
