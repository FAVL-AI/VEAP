"""Unit tests for X2 detection attribution and development-only precision analysis."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from x2.detection_attribution import (
    DEFAULT_FIXTURES_REPORT_PATH,
    attribute_detection,
    attribute_records,
    run_serialized_fixture_suite,
)
from x2.feasibility_and_monotonicity import (
    DEFAULT_REPORT_PATH as DEFAULT_FEASIBILITY_REPORT_PATH,
    clopper_pearson_upper,
    compute_planning_milestones,
    eligibility_cap_probability,
    run_exact_binomial_feasibility,
    run_monotonicity_check,
)
from x2.interval_calibration import (
    CONFIRM_SEED,
    DEFAULT_REPORT_PATH as DEFAULT_CALIBRATION_REPORT_PATH,
    DEV_SEED,
    UNEQUAL_CLUSTER_SIZES_60,
    _draw_scenario_fpr_counts,
    cluster_score_fpr_ci,
    evaluate_methods_for_cell,
    scenario_bootstrap_fpr_ci,
    scenario_clustered_fpr_ci,
)
from x2.leakage_controls import (
    DEFAULT_REPORT_PATH as DEFAULT_LEAKAGE_REPORT_PATH,
    check_endpoint_bytes,
    check_trajectory_bytes,
    run_leakage_controls,
)
from x2.precision_analysis import (
    DEFAULT_OUTPUT_PATH,
    fpr_ci,
    run_precision_analysis,
    simulate_regime_for_n,
    t_critical_95,
    wilson_ci,
)


def test_attribute_detection_separates_compliant_and_inconclusive() -> None:
    # 7 reference-false (DONE=False) claims + 2 reference-true (DONE=True) claims
    done = [False, False, False, False, False, False, False, True, True]
    traj = [
        "violating",     # 0: both violating
        "violating",     # 1: trajectory_only_compliant
        "violating",     # 2: trajectory_only_inconclusive
        "compliant",     # 3: endpoint_only_compliant
        "inconclusive",  # 4: endpoint_only_inconclusive
        "compliant",     # 5: neither violating
        "inconclusive",  # 6: neither violating (traj inconclusive, endp compliant)
        "compliant",     # 7: ref-true, compliant
        "violating",     # 8: ref-true, false rejection by traj
    ]
    endp = [
        "violating",     # 0
        "compliant",     # 1
        "inconclusive",  # 2
        "violating",     # 3
        "violating",     # 4
        "compliant",     # 5
        "compliant",     # 6
        "inconclusive",  # 7: ref-true, endp inconclusive
        "compliant",     # 8
    ]

    res = attribute_detection(done, traj, endp)

    assert res["n_total"] == 9
    assert res["n_ref_false"] == 7
    assert res["n_ref_true"] == 2
    assert res["both_violating"] == 1
    assert res["trajectory_only_compliant"] == 1
    assert res["trajectory_only_inconclusive"] == 1
    assert res["endpoint_only_compliant"] == 1
    assert res["endpoint_only_inconclusive"] == 1
    assert res["neither_violating"] == 2

    imp = res["paired_recall_improvement"]
    assert imp["gains"] == 2
    assert imp["losses"] == 2
    assert imp["count_diff"] == 0
    assert imp["rate_diff_all_claims"] == pytest.approx(0.0)
    # both_definitive on ref_false: indices 0, 1, 3, 5 -> 4 claims; (1 - 1) / 4 = 0.0
    assert res["denominators"]["both_definitive_ref_false"] == 4
    assert imp["rate_diff_both_definitive"] == pytest.approx(0.0)

    # traj_definitive_ref_false = 5 (indices 0,1,2,3,5); recall = 3/5 = 0.6
    # endp_definitive_ref_false = 6 (indices 0,1,3,4,5,6); recall = 3/6 = 0.5
    assert res["denominators"]["trajectory_definitive_ref_false"] == 5
    assert res["denominators"]["endpoint_definitive_ref_false"] == 6
    assert res["recall"]["trajectory_definitive_only"] == pytest.approx(0.6)
    assert res["recall"]["endpoint_definitive_only"] == pytest.approx(0.5)
    assert imp["unpaired_rate_diff_definitive"] == pytest.approx(0.1)

    ref_true = res["reference_true_summary"]
    assert ref_true["trajectory_false_violating"] == 1
    assert ref_true["endpoint_false_violating"] == 0
    assert ref_true["trajectory_false_rejection_rate_all"] == pytest.approx(0.5)
    assert ref_true["endpoint_inconclusive_count"] == 1


def test_attribute_detection_positive_gains_minus_losses() -> None:
    records = [
        {"done": False, "trajectory_verdict": "violating", "endpoint_verdict": "compliant"},
        {"done": False, "trajectory_verdict": "violating", "endpoint_verdict": "inconclusive"},
        {"done": False, "trajectory_verdict": "violating", "endpoint_verdict": "inconclusive"},
        {"done": False, "trajectory_verdict": "compliant", "endpoint_verdict": "violating"},
    ]
    res = attribute_records(records)
    imp = res["paired_recall_improvement"]
    assert res["trajectory_only_compliant"] == 1
    assert res["trajectory_only_inconclusive"] == 2
    assert res["endpoint_only_compliant"] == 1
    assert res["endpoint_only_inconclusive"] == 0
    assert imp["gains"] == 3
    assert imp["losses"] == 1
    assert imp["count_diff"] == 2
    assert imp["rate_diff_all_claims"] == pytest.approx(0.5)
    # both_definitive: indices 0, 3 -> (1 - 1) / 2 = 0.0
    assert imp["rate_diff_both_definitive"] == pytest.approx(0.0)


def test_attribute_detection_edge_cases_and_validation() -> None:
    empty = attribute_detection([], [], [])
    assert empty["n_total"] == 0
    assert empty["paired_recall_improvement"]["rate_diff_all_claims"] is None

    all_true = attribute_detection([True, True], ["compliant", "compliant"], ["compliant", "compliant"])
    assert all_true["n_ref_false"] == 0
    assert all_true["recall"]["trajectory_all_claims"] is None
    assert all_true["reference_true_summary"]["trajectory_false_rejection_rate_all"] == 0.0

    with pytest.raises(ValueError):
        attribute_detection([False], ["compliant", "violating"], ["compliant"])
    with pytest.raises(ValueError):
        attribute_detection([False], ["unknown"], ["compliant"])
    with pytest.raises(ValueError):
        attribute_detection([0], ["compliant"], ["compliant"])  # type: ignore[list-item]


def test_wilson_ci_and_t_critical() -> None:
    lo, hi = wilson_ci(0, 40)
    assert lo == 0.0
    assert hi > 0.05  # 0/40 cannot clear 5% ceiling

    lo2, hi2 = wilson_ci(0, 120)
    assert lo2 == 0.0
    assert hi2 < 0.05

    assert wilson_ci(0, 0) == (0.0, 1.0)
    assert t_critical_95(59) < t_critical_95(9)


def test_precision_analysis_is_deterministic_and_resolves_n60() -> None:
    r1 = run_precision_analysis(n_replicates=300, seed=42)
    r2 = run_precision_analysis(n_replicates=300, seed=42)
    assert r1 == r2
    assert r1["scope"] == "development-only"
    assert set(r1["results"].keys()) == {"nominal", "pessimistic"}

    nom = {row["n_scenarios"]: row for row in r1["results"]["nominal"]}
    pess = {row["n_scenarios"]: row for row in r1["results"]["pessimistic"]}
    # N=10 has 40 ref-true claims -> Wilson UB(0/40) > 0.05 -> 0% joint resolution
    assert nom[10]["p_resolve_false_rejection_ceiling"] == 0.0
    assert nom[10]["p_resolve_joint"] == 0.0
    # N=60 should have higher joint resolution than N=20 in both regimes
    assert nom[60]["p_resolve_joint"] > nom[20]["p_resolve_joint"]
    assert pess[60]["p_resolve_joint"] > pess[20]["p_resolve_joint"]
    # Genuine claims supporting the 5% FPR ceiling are reported for every candidate N
    assert nom[60]["n_genuine_claims"] == 240
    assert pess[10]["n_genuine_claims"] == 40


def test_cluster_aware_fpr_ci_reflects_scenario_clustering() -> None:
    unclustered = simulate_regime_for_n(
        30,
        p_gain=0.28,
        p_loss=0.03,
        fpr_true=0.015,
        scenario_sd_recall=0.08,
        scenario_sd_fpr=0.0,
        claims_false_per_scenario=3,
        claims_true_per_scenario=4,
        min_meaningful_improvement=0.10,
        max_false_rejection_rate=0.05,
        n_replicates=400,
        seed=99,
    )
    clustered = simulate_regime_for_n(
        30,
        p_gain=0.28,
        p_loss=0.03,
        fpr_true=0.015,
        scenario_sd_recall=0.08,
        scenario_sd_fpr=0.04,
        claims_false_per_scenario=3,
        claims_true_per_scenario=4,
        min_meaningful_improvement=0.10,
        max_false_rejection_rate=0.05,
        n_replicates=400,
        seed=99,
    )
    assert clustered["p_resolve_false_rejection_ceiling"] < unclustered["p_resolve_false_rejection_ceiling"]


def test_precision_report_json_matches_script_output() -> None:
    assert Path(DEFAULT_OUTPUT_PATH).exists()
    data = json.loads(Path(DEFAULT_OUTPUT_PATH).read_text(encoding="utf-8"))
    assert data["schema"] == "veap-x2-precision-analysis/1"
    assert data["scope"] == "development-only"
    assert data["recommended_n"] == 60
    assert data["config"]["candidate_n"] == [10, 15, 20, 30, 40, 60]
    n_rep = data["config"]["n_replicates"]
    for regime in ("nominal", "pessimistic"):
        for row in data["results"][regime]:
            assert "n_genuine_claims" in row
            assert row["n_genuine_claims"] == row["n_ref_true_claims"]
            for endpoint in ("recall", "false_rejection", "joint"):
                counts = row["outcomes"][endpoint]["counts"]
                rates = row["outcomes"][endpoint]["rates"]
                assert set(counts.keys()) == {"supported", "contradicted", "inconclusive"}
                assert sum(counts.values()) == n_rep
                assert sum(rates.values()) == pytest.approx(1.0)


def test_zero_false_rejection_guard_does_not_collapse_to_zero() -> None:
    lo, hi = fpr_ci([0.0] * 10, false_rejections_total=0, m_true_total=40)
    assert lo == 0.0
    assert hi > 0.05  # 0/40 must not collapse to [0, 0] or clear 5% ceiling
    assert hi == pytest.approx(wilson_ci(0, 40)[1])


def test_leakage_controls_byte_entry_points_and_report() -> None:
    # Rejects hidden reference label keys in serialized payloads
    with pytest.raises(ValueError, match="Forbidden reference label key"):
        check_trajectory_bytes(
            json.dumps({"adjudicator_done": False, "trajectory_steps": []}).encode("utf-8")
        )
    with pytest.raises(ValueError, match="Forbidden reference label key"):
        check_endpoint_bytes(
            json.dumps({"reference_label": True, "endpoint_state": None}).encode("utf-8")
        )

    report = run_leakage_controls(output_path=None)
    assert report["schema"] == "veap-x2-leakage-controls/1"
    assert report["n_pairs"] == 6
    assert report["n_episodes"] == 12
    assert report["all_controls_passed"] is True
    assert len(report["hidden_truth_pairs"]) == 3
    assert len(report["visible_history_pairs"]) == 3

    for ht in report["hidden_truth_pairs"]:
        assert ht["trajectory_bytes_match"] is True
        assert ht["endpoint_bytes_match"] is True
        assert ht["verdicts_match"] is True
        assert ht["reference_labels_differ"] is True
        assert ht["control_passed"] is True

    for vh in report["visible_history_pairs"]:
        assert vh["endpoint_bytes_match"] is True
        assert vh["trajectory_bytes_differ"] is True
        assert vh["endpoint_verdicts_match"] is True
        assert vh["trajectory_verdicts_differ"] is True
        assert vh["control_passed"] is True

    assert Path(DEFAULT_LEAKAGE_REPORT_PATH).exists()
    disk_report = json.loads(Path(DEFAULT_LEAKAGE_REPORT_PATH).read_text(encoding="utf-8"))
    assert disk_report == report


def test_interval_calibration_three_methods_and_zero_claim_exclusion() -> None:
    import random

    assert DEV_SEED != CONFIRM_SEED
    assert len(UNEQUAL_CLUSTER_SIZES_60) == 60
    assert sum(UNEQUAL_CLUSTER_SIZES_60) == 240
    assert min(UNEQUAL_CLUSTER_SIZES_60) == 1
    assert max(UNEQUAL_CLUSTER_SIZES_60) == 7

    # Scenarios with 0 genuine claims are excluded from the equal-weighted mean
    fprs, total_rej, total_claims = _draw_scenario_fpr_counts(
        random.Random(1), (0, 4, 4, 0), true_fpr=0.0, rho=0.0
    )
    assert len(fprs) == 2
    assert total_rej == 0
    assert total_claims == 8

    # Zero-event fallback for all 3 methods uses N-scenario Wilson floor (~6.02% at N=60)
    _, floor_60 = scenario_clustered_fpr_ci([0.0] * 60, total_rejections=0, zero_event_denominator=60)
    _, floor_cs = cluster_score_fpr_ci([0.0] * 60, total_rejections=0, total_claims=240)
    _, floor_sb = scenario_bootstrap_fpr_ci([0.0] * 60, total_rejections=0, boot_rng=random.Random(2), n_boot=50)
    assert floor_60 == pytest.approx(0.06017, abs=1e-4)
    assert floor_cs == pytest.approx(0.06017, abs=1e-4)
    assert floor_sb == pytest.approx(0.06017, abs=1e-4)

    # Evaluate all 3 methods on a single confirmation cell
    cell = evaluate_methods_for_cell(rho=0.25, true_fpr=0.050, n_replicates=100, n_boot=50, seed=CONFIRM_SEED)
    assert set(cell.keys()) == {"student_t", "cluster_score", "scenario_bootstrap"}
    for m, row in cell.items():
        assert row["regime_tag"] == "boundary"
        assert 0.0 <= row["coverage_95"] <= 1.0
        assert 0.0 <= row["upper_tail_miss"] <= 1.0
        assert row["coverage_95_mcse"] >= 0.0
        assert row["mean_width"] > 0.0


def test_interval_calibration_report_v2_schema_and_worst_case() -> None:
    assert Path(DEFAULT_CALIBRATION_REPORT_PATH).exists()
    disk_rep = json.loads(Path(DEFAULT_CALIBRATION_REPORT_PATH).read_text(encoding="utf-8"))
    assert disk_rep["schema"] == "veap-x2-interval-calibration/2"
    assert disk_rep["seeds"]["dev_seed"] != disk_rep["seeds"]["confirm_seed"]
    assert disk_rep["calibrated_candidates"] == []
    for m in ("student_t", "cluster_score", "scenario_bootstrap"):
        assert len(disk_rep["results_by_method"][m]) == 18  # 3 rhos x 6 true_fprs
        summary = disk_rep["worst_case_summary"][m]
        assert summary["meets_calibration_tolerance"] is False
        assert summary["min_coverage_95"] < 0.92
        assert summary["max_upper_tail_miss"] > 0.05


def test_clopper_pearson_and_exact_binomial_feasibility() -> None:
    assert clopper_pearson_upper(0, 60) > 0.05
    assert clopper_pearson_upper(0, 71) > 0.05
    assert clopper_pearson_upper(0, 72) <= 0.05
    assert clopper_pearson_upper(0, 72) == pytest.approx(1.0 - (0.025 ** (1.0 / 72.0)))

    rows = {r["n_eligible"]: r for r in run_exact_binomial_feasibility()}
    assert rows[60]["max_k_clearing_5pct"] is None
    assert rows[71]["max_k_clearing_5pct"] is None
    assert rows[60]["p_clear_at_1pct"] == 0.0
    assert rows[72]["max_k_clearing_5pct"] == 0
    assert rows[72]["p_clear_at_1pct"] == pytest.approx(0.99 ** 72)
    assert rows[72]["expected_total_scenarios"]["p_elig_80pct"] == pytest.approx(90.0)
    assert rows[150]["max_k_clearing_5pct"] == 2
    assert rows[300]["p_clear_at_1pct"] > 0.98


def test_monotonicity_check_and_feasibility_report() -> None:
    mono = run_monotonicity_check(n_boot=200, seed=20261116)
    assert mono["n_runs"] == 6
    for m in ("student_t", "cluster_score", "scenario_bootstrap"):
        assert mono["anomaly_step_counts_by_method"][m] > 0

    assert Path(DEFAULT_FEASIBILITY_REPORT_PATH).exists()
    disk_rep = json.loads(Path(DEFAULT_FEASIBILITY_REPORT_PATH).read_text(encoding="utf-8"))
    assert disk_rep["schema"] == "veap-x2-feasibility-and-monotonicity/1"
    assert len(disk_rep["exact_binomial_feasibility"]) == 11


def test_planning_milestones_and_eligibility_cap_probability() -> None:
    milestones = compute_planning_milestones()
    expected = [
        (0.01, 0.80, 142, 2, 0.8294),
        (0.01, 0.90, 173, 3, 0.9033),
        (0.02, 0.80, 312, 8, 0.8235),
        (0.02, 0.90, 390, 11, 0.9041),
    ]
    assert len(milestones) == 4
    for row, (fpr, target, n_elig, max_k, p_clear) in zip(milestones, expected):
        assert row["true_fpr"] == fpr
        assert row["target_power"] == target
        assert row["n_eligible"] == n_elig
        assert row["max_k_clearing_5pct"] == max_k
        assert row["p_clear"] == pytest.approx(p_clear, abs=1e-4)

    cap_prob = eligibility_cap_probability(cap=407, target_eligible=312, p_eligible=0.80)
    assert cap_prob == pytest.approx(0.9577, abs=1e-4)

    disk_rep = json.loads(Path(DEFAULT_FEASIBILITY_REPORT_PATH).read_text(encoding="utf-8"))
    assert disk_rep["planning_milestones"] == milestones
    assert disk_rep["eligibility_cap_check"]["p_reach_target"] == pytest.approx(0.9577, abs=1e-4)


def test_serialized_fixture_suite_and_report() -> None:
    report = run_serialized_fixture_suite(output_path=None)
    assert report["schema"] == "veap-x2-attribution-fixtures/1"
    assert report["n_fixtures"] == 6

    attr = report["attribution"]
    assert attr["n_total"] == 6
    assert attr["n_issued_claims"] == 5
    assert attr["n_no_claim_or_timeout"] == 1
    assert attr["n_ref_false"] == 4
    assert attr["n_ref_true"] == 1
    assert attr["all_episode_accounting"]["n_episodes_total"] == 6
    assert attr["all_episode_accounting"]["no_claim_rate"] == pytest.approx(1 / 6)

    assert attr["trajectory_only_compliant"] == 1
    assert attr["trajectory_only_inconclusive"] == 1
    assert attr["endpoint_only_compliant"] == 1
    assert attr["endpoint_only_inconclusive"] == 1
    assert attr["paired_recall_improvement"]["gains"] == 2
    assert attr["paired_recall_improvement"]["losses"] == 2
    assert attr["paired_recall_improvement"]["count_diff"] == 0

    ref_true = attr["reference_true_summary"]
    assert ref_true["trajectory_false_violating"] == 1
    assert ref_true["trajectory_false_rejection_rate_all"] == pytest.approx(1.0)

    # Verify serialized payloads on disk match
    assert Path(DEFAULT_FIXTURES_REPORT_PATH).exists()
    disk_report = json.loads(Path(DEFAULT_FIXTURES_REPORT_PATH).read_text(encoding="utf-8"))
    assert disk_report == report
    for fx in disk_report["fixtures"]:
        traj_payload = json.loads(fx["trajectory_input_json"])
        endp_payload = json.loads(fx["endpoint_input_json"])
        assert traj_payload["checker"] == "trajectory"
        assert endp_payload["checker"] == "endpoint"
