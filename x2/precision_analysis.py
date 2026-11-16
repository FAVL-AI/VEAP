"""Development-only precision analysis for X2 scenario count selection.

Uses plain Python (``math``, ``random``, ``json``) to estimate the joint
probability across candidate scenario counts ``N`` that a study resolves BOTH:
1. Paired recall improvement >= ``min_meaningful_improvement`` (95% scenario-clustered Student-t CI lower bound), and
2. False-rejection rate <= ``max_false_rejection_rate`` (5% ceiling via 95% scenario-clustered Student-t CI upper bound, with pooled Wilson floor when zero false rejections are observed),
across nominal and pessimistic development regimes.
"""

from __future__ import annotations

import json
import math
import random
from pathlib import Path
from typing import Any

DEFAULT_CANDIDATE_N = (10, 15, 20, 30, 40, 60)
DEFAULT_OUTPUT_PATH = Path(__file__).resolve().parent / "precision_report.json"

# Two-sided 95% Student-t critical values for common df; falls back to 1.95996 for large df.
_T_CRIT_95 = {
    9: 2.262157,
    14: 2.144787,
    19: 2.093024,
    29: 2.045230,
    39: 2.022691,
    59: 2.000995,
}


def t_critical_95(df: int) -> float:
    """Return two-sided 95% Student-t critical value for ``df`` degrees of freedom."""
    if df <= 0:
        raise ValueError("df must be positive")
    if df in _T_CRIT_95:
        return _T_CRIT_95[df]
    # Cornish-Fisher approximation for arbitrary df >= 1
    z = 1.959963984540054
    return z + (z**3 + z) / (4 * df) + (5 * z**5 + 16 * z**3 + 3 * z) / (96 * df * df)


def wilson_ci(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    """Return 95% Wilson score confidence interval ``(low, high)``."""
    if n <= 0:
        return (0.0, 1.0)
    p = k / n
    z2 = z * z
    denom = 1.0 + z2 / n
    center = (p + z2 / (2.0 * n)) / denom
    half = z * math.sqrt((p * (1.0 - p) / n) + (z2 / (4.0 * n * n))) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def fpr_ci(
    scenario_fprs: list[float],
    false_rejections_total: int,
    m_true_total: int,
) -> tuple[float, float]:
    """Return 95% scenario-clustered Student-t CI for FPR with zero-variance Wilson guard.

    When all scenario FPRs are ``0.0`` (``std == 0``), an ordinary Student-t interval
    collapses to ``[0, 0]``. This function enforces the 95% Wilson upper-bound floor
    so the interval is never degenerate at zero false rejections.
    """
    n_scenarios = len(scenario_fprs)
    if n_scenarios < 2:
        raise ValueError("n_scenarios must be >= 2")
    w_low, w_high = wilson_ci(false_rejections_total, m_true_total)
    mean_fpr = sum(scenario_fprs) / n_scenarios
    var_fpr = sum((f - mean_fpr) ** 2 for f in scenario_fprs) / (n_scenarios - 1)
    if var_fpr == 0.0 and mean_fpr == 0.0:
        return (0.0, w_high)
    t_crit = t_critical_95(n_scenarios - 1)
    se_fpr = math.sqrt(var_fpr / n_scenarios)
    t_low = max(0.0, mean_fpr - t_crit * se_fpr)
    t_high = min(1.0, mean_fpr + t_crit * se_fpr)
    return (min(t_low, w_low), max(t_high, w_high))


def _state_summary(counts: dict[str, int], n_replicates: int) -> dict[str, Any]:
    return {
        "counts": dict(counts),
        "rates": {k: v / n_replicates for k, v in counts.items()},
    }


def simulate_regime_for_n(
    n_scenarios: int,
    *,
    p_gain: float,
    p_loss: float,
    fpr_true: float,
    scenario_sd_recall: float,
    scenario_sd_fpr: float,
    claims_false_per_scenario: int,
    claims_true_per_scenario: int,
    min_meaningful_improvement: float,
    max_false_rejection_rate: float,
    n_replicates: int,
    seed: int,
) -> dict[str, Any]:
    """Simulate ``n_replicates`` studies for a single ``(regime, n_scenarios)`` cell."""
    if n_scenarios < 2:
        raise ValueError("n_scenarios must be >= 2")
    rng = random.Random(seed)
    t_crit = t_critical_95(n_scenarios - 1)

    recall_counts = {"supported": 0, "contradicted": 0, "inconclusive": 0}
    fpr_counts = {"supported": 0, "contradicted": 0, "inconclusive": 0}
    joint_counts = {"supported": 0, "contradicted": 0, "inconclusive": 0}
    mean_recall_est_sum = 0.0
    mean_fpr_est_sum = 0.0

    m_true_total = n_scenarios * claims_true_per_scenario

    for _ in range(n_replicates):
        scenario_diffs: list[float] = []
        scenario_fprs: list[float] = []
        false_rejections_total = 0

        for _ in range(n_scenarios):
            # Recall paired outcomes on reference-false claims
            p_loss_i = p_loss
            p_gain_i = _clamp(
                p_gain + (rng.gauss(0.0, scenario_sd_recall) if scenario_sd_recall > 0 else 0.0),
                0.0,
                max(0.0, 1.0 - p_loss_i),
            )
            diff_sum = 0
            for _ in range(claims_false_per_scenario):
                u = rng.random()
                if u < p_gain_i:
                    diff_sum += 1
                elif u < p_gain_i + p_loss_i:
                    diff_sum -= 1
            scenario_diffs.append(diff_sum / claims_false_per_scenario)

            # False-rejection outcomes on reference-true (genuine) claims
            fpr_i = _clamp(
                fpr_true + (rng.gauss(0.0, scenario_sd_fpr) if scenario_sd_fpr > 0 else 0.0),
                0.0,
                1.0,
            )
            false_rej_i = 0
            for _ in range(claims_true_per_scenario):
                if rng.random() < fpr_i:
                    false_rej_i += 1
            false_rejections_total += false_rej_i
            scenario_fprs.append(false_rej_i / claims_true_per_scenario)

        mean_d = sum(scenario_diffs) / n_scenarios
        var_d = sum((d - mean_d) ** 2 for d in scenario_diffs) / (n_scenarios - 1)
        se_d = math.sqrt(var_d / n_scenarios)
        ci_low_recall = mean_d - t_crit * se_d
        ci_high_recall = mean_d + t_crit * se_d

        ci_low_fpr, ci_high_fpr = fpr_ci(scenario_fprs, false_rejections_total, m_true_total)
        mean_fpr = sum(scenario_fprs) / n_scenarios

        if ci_low_recall >= min_meaningful_improvement:
            r_state = "supported"
        elif ci_high_recall < min_meaningful_improvement:
            r_state = "contradicted"
        else:
            r_state = "inconclusive"

        if ci_high_fpr <= max_false_rejection_rate:
            f_state = "supported"
        elif ci_low_fpr > max_false_rejection_rate:
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

        mean_recall_est_sum += mean_d
        mean_fpr_est_sum += mean_fpr

    return {
        "n_scenarios": n_scenarios,
        "n_ref_false_claims": n_scenarios * claims_false_per_scenario,
        "n_ref_true_claims": m_true_total,
        "n_genuine_claims": m_true_total,
        "p_resolve_recall": recall_counts["supported"] / n_replicates,
        "p_resolve_false_rejection_ceiling": fpr_counts["supported"] / n_replicates,
        "p_resolve_joint": joint_counts["supported"] / n_replicates,
        "outcomes": {
            "recall": _state_summary(recall_counts, n_replicates),
            "false_rejection": _state_summary(fpr_counts, n_replicates),
            "joint": _state_summary(joint_counts, n_replicates),
        },
        "mean_estimated_recall_improvement": mean_recall_est_sum / n_replicates,
        "mean_estimated_false_rejection_rate": mean_fpr_est_sum / n_replicates,
    }


def run_precision_analysis(
    candidate_n: tuple[int, ...] = DEFAULT_CANDIDATE_N,
    *,
    claims_false_per_scenario: int = 3,
    claims_true_per_scenario: int = 4,
    min_meaningful_improvement: float = 0.10,
    max_false_rejection_rate: float = 0.05,
    target_joint_power_nominal: float = 0.80,
    target_joint_power_pessimistic: float = 0.50,
    n_replicates: int = 2000,
    seed: int = 20261116,
) -> dict[str, Any]:
    """Run development-only precision analysis across candidate scenario counts."""
    regimes = {
        "nominal": {
            "description": "Development nominal regime: moderate-to-strong recall gain, 1% false-rejection rate",
            "p_gain": 0.28,
            "p_loss": 0.03,
            "true_recall_improvement": 0.25,
            "fpr_true": 0.01,
            "scenario_sd_recall": 0.08,
            "scenario_sd_fpr": 0.015,
        },
        "pessimistic": {
            "description": "Development pessimistic regime: modest recall gain, 1.5% false-rejection rate, higher clustering",
            "p_gain": 0.23,
            "p_loss": 0.03,
            "true_recall_improvement": 0.20,
            "fpr_true": 0.015,
            "scenario_sd_recall": 0.11,
            "scenario_sd_fpr": 0.025,
        },
    }

    results_by_regime: dict[str, list[dict[str, Any]]] = {}
    for regime_idx, (regime_name, params) in enumerate(regimes.items()):
        rows = []
        for n_idx, n_val in enumerate(candidate_n):
            cell_seed = seed + regime_idx * 1000 + n_idx
            row = simulate_regime_for_n(
                n_val,
                p_gain=params["p_gain"],
                p_loss=params["p_loss"],
                fpr_true=params["fpr_true"],
                scenario_sd_recall=params["scenario_sd_recall"],
                scenario_sd_fpr=params["scenario_sd_fpr"],
                claims_false_per_scenario=claims_false_per_scenario,
                claims_true_per_scenario=claims_true_per_scenario,
                min_meaningful_improvement=min_meaningful_improvement,
                max_false_rejection_rate=max_false_rejection_rate,
                n_replicates=n_replicates,
                seed=cell_seed,
            )
            rows.append(row)
        results_by_regime[regime_name] = rows

    # Select smallest N meeting both nominal and pessimistic joint power targets
    recommended_n = None
    nom_by_n = {r["n_scenarios"]: r for r in results_by_regime["nominal"]}
    pess_by_n = {r["n_scenarios"]: r for r in results_by_regime["pessimistic"]}
    for n_val in sorted(candidate_n):
        if (
            nom_by_n[n_val]["p_resolve_joint"] >= target_joint_power_nominal
            and pess_by_n[n_val]["p_resolve_joint"] >= target_joint_power_pessimistic
        ):
            recommended_n = n_val
            break

    return {
        "schema": "veap-x2-precision-analysis/1",
        "scope": "development-only",
        "config": {
            "candidate_n": list(candidate_n),
            "claims_false_per_scenario": claims_false_per_scenario,
            "claims_true_per_scenario": claims_true_per_scenario,
            "min_meaningful_improvement": min_meaningful_improvement,
            "max_false_rejection_rate": max_false_rejection_rate,
            "target_joint_power_nominal": target_joint_power_nominal,
            "target_joint_power_pessimistic": target_joint_power_pessimistic,
            "n_replicates": n_replicates,
            "seed": seed,
        },
        "regimes": regimes,
        "results": results_by_regime,
        "recommended_n": recommended_n,
    }


def main(output_path: Path = DEFAULT_OUTPUT_PATH) -> dict[str, Any]:
    report = run_precision_analysis()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    report_data = main()
    print(f"Wrote {DEFAULT_OUTPUT_PATH} (recommended_n={report_data['recommended_n']})")
