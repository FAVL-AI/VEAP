"""Plain-Python detection attribution for X2 trajectory vs endpoint verification.

Separates endpoint ``compliant`` and ``inconclusive`` outcomes when attributing
paired recall differences on reference-false (``DONE == False``) claims, and
computes ``paired_recall_improvement = gains - losses`` with both absolute counts
and rate differences under all-claims and definitive-only denominators.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

VALID_VERDICTS = frozenset({"compliant", "violating", "inconclusive"})
DEFAULT_FIXTURES_REPORT_PATH = Path(__file__).resolve().parent / "attribution_fixtures_report.json"


def _validate_inputs(
    adjudicator_done: Sequence[bool | None],
    trajectory_verdicts: Sequence[str],
    endpoint_verdicts: Sequence[str],
) -> None:
    if not (len(adjudicator_done) == len(trajectory_verdicts) == len(endpoint_verdicts)):
        raise ValueError(
            "adjudicator_done, trajectory_verdicts, and endpoint_verdicts must have equal length"
        )
    for idx, done in enumerate(adjudicator_done):
        if done is not None and not isinstance(done, bool):
            raise ValueError(
                f"adjudicator_done[{idx}] must be a bool or None, got {type(done).__name__}"
            )
    for idx, verdict in enumerate(trajectory_verdicts):
        if verdict not in VALID_VERDICTS:
            raise ValueError(f"trajectory_verdicts[{idx}] invalid: {verdict!r}")
    for idx, verdict in enumerate(endpoint_verdicts):
        if verdict not in VALID_VERDICTS:
            raise ValueError(f"endpoint_verdicts[{idx}] invalid: {verdict!r}")


def _safe_rate(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return numerator / denominator


def attribute_detection(
    adjudicator_done: Sequence[bool | None],
    trajectory_verdicts: Sequence[str],
    endpoint_verdicts: Sequence[str],
) -> dict[str, Any]:
    """Compute paired detection attribution and recall improvement.

    Args:
        adjudicator_done: Ground-truth ``DONE`` booleans (``False`` = reference-false claim,
            ``True`` = reference-true claim, ``None`` = timeout / no-claim episode where
            ``DONE`` was not issued).
        trajectory_verdicts: Trajectory-checker verdicts (``compliant``/``violating``/``inconclusive``).
        endpoint_verdicts: Endpoint-checker verdicts (``compliant``/``violating``/``inconclusive``).

    Returns:
        Dictionary containing separate ``compliant`` and ``inconclusive`` attribution
        counts, ``paired_recall_improvement`` (``gains - losses`` count and rate
        differences), denominator counts, inconclusive rates, reference-true
        false-rejection summary, and ``all_episode_accounting``.
    """
    _validate_inputs(adjudicator_done, trajectory_verdicts, endpoint_verdicts)

    n_total = len(adjudicator_done)
    n_no_claim_or_timeout = sum(1 for done in adjudicator_done if done is None)
    ref_false_pairs = [
        (t, e)
        for done, t, e in zip(adjudicator_done, trajectory_verdicts, endpoint_verdicts)
        if done is False
    ]
    ref_true_pairs = [
        (t, e)
        for done, t, e in zip(adjudicator_done, trajectory_verdicts, endpoint_verdicts)
        if done is True
    ]

    n_ref_false = len(ref_false_pairs)
    n_ref_true = len(ref_true_pairs)

    both_violating = 0
    trajectory_only_compliant = 0
    trajectory_only_inconclusive = 0
    endpoint_only_compliant = 0
    endpoint_only_inconclusive = 0
    neither_violating = 0

    traj_violating_false = 0
    endp_violating_false = 0
    traj_inconclusive_false = 0
    endp_inconclusive_false = 0
    traj_definitive_false = 0
    endp_definitive_false = 0
    both_definitive_false = 0

    for t, e in ref_false_pairs:
        if t == "violating":
            traj_violating_false += 1
        if e == "violating":
            endp_violating_false += 1
        if t == "inconclusive":
            traj_inconclusive_false += 1
        else:
            traj_definitive_false += 1
        if e == "inconclusive":
            endp_inconclusive_false += 1
        else:
            endp_definitive_false += 1
        if t != "inconclusive" and e != "inconclusive":
            both_definitive_false += 1

        if t == "violating" and e == "violating":
            both_violating += 1
        elif t == "violating" and e == "compliant":
            trajectory_only_compliant += 1
        elif t == "violating" and e == "inconclusive":
            trajectory_only_inconclusive += 1
        elif e == "violating" and t == "compliant":
            endpoint_only_compliant += 1
        elif e == "violating" and t == "inconclusive":
            endpoint_only_inconclusive += 1
        else:
            neither_violating += 1

    gains = trajectory_only_compliant + trajectory_only_inconclusive
    losses = endpoint_only_compliant + endpoint_only_inconclusive
    count_diff = gains - losses

    traj_recall_all = _safe_rate(traj_violating_false, n_ref_false)
    endp_recall_all = _safe_rate(endp_violating_false, n_ref_false)
    rate_diff_all = _safe_rate(count_diff, n_ref_false)

    traj_recall_def = _safe_rate(traj_violating_false, traj_definitive_false)
    endp_recall_def = _safe_rate(endp_violating_false, endp_definitive_false)
    unpaired_rate_diff_def = (
        None
        if traj_recall_def is None or endp_recall_def is None
        else traj_recall_def - endp_recall_def
    )
    paired_rate_diff_both_def = _safe_rate(
        trajectory_only_compliant - endpoint_only_compliant,
        both_definitive_false,
    )

    # Reference-true (DONE == True) false-rejection summary
    traj_false_violating = sum(1 for t, _ in ref_true_pairs if t == "violating")
    endp_false_violating = sum(1 for _, e in ref_true_pairs if e == "violating")
    traj_inconclusive_true = sum(1 for t, _ in ref_true_pairs if t == "inconclusive")
    endp_inconclusive_true = sum(1 for _, e in ref_true_pairs if e == "inconclusive")
    traj_definitive_true = n_ref_true - traj_inconclusive_true
    endp_definitive_true = n_ref_true - endp_inconclusive_true

    return {
        "n_total": n_total,
        "n_issued_claims": n_ref_false + n_ref_true,
        "n_no_claim_or_timeout": n_no_claim_or_timeout,
        "n_ref_false": n_ref_false,
        "n_ref_true": n_ref_true,
        "all_episode_accounting": {
            "n_episodes_total": n_total,
            "n_issued_claims": n_ref_false + n_ref_true,
            "n_ref_false": n_ref_false,
            "n_ref_true": n_ref_true,
            "n_no_claim_or_timeout": n_no_claim_or_timeout,
            "no_claim_rate": _safe_rate(n_no_claim_or_timeout, n_total),
        },
        "both_violating": both_violating,
        "trajectory_only_compliant": trajectory_only_compliant,
        "trajectory_only_inconclusive": trajectory_only_inconclusive,
        "endpoint_only_compliant": endpoint_only_compliant,
        "endpoint_only_inconclusive": endpoint_only_inconclusive,
        "neither_violating": neither_violating,
        "paired_recall_improvement": {
            "gains": gains,
            "losses": losses,
            "count_diff": count_diff,
            "rate_diff_all_claims": rate_diff_all,
            "rate_diff_both_definitive": paired_rate_diff_both_def,
            "unpaired_rate_diff_definitive": unpaired_rate_diff_def,
        },
        "denominators": {
            "all_ref_false": n_ref_false,
            "trajectory_definitive_ref_false": traj_definitive_false,
            "endpoint_definitive_ref_false": endp_definitive_false,
            "both_definitive_ref_false": both_definitive_false,
        },
        "recall": {
            "trajectory_all_claims": traj_recall_all,
            "endpoint_all_claims": endp_recall_all,
            "trajectory_definitive_only": traj_recall_def,
            "endpoint_definitive_only": endp_recall_def,
        },
        "inconclusive_ref_false": {
            "trajectory_count": traj_inconclusive_false,
            "endpoint_count": endp_inconclusive_false,
            "trajectory_rate": _safe_rate(traj_inconclusive_false, n_ref_false),
            "endpoint_rate": _safe_rate(endp_inconclusive_false, n_ref_false),
        },
        "reference_true_summary": {
            "n_ref_true": n_ref_true,
            "trajectory_false_violating": traj_false_violating,
            "endpoint_false_violating": endp_false_violating,
            "trajectory_false_rejection_rate_all": _safe_rate(traj_false_violating, n_ref_true),
            "endpoint_false_rejection_rate_all": _safe_rate(endp_false_violating, n_ref_true),
            "trajectory_false_rejection_rate_definitive": _safe_rate(
                traj_false_violating, traj_definitive_true
            ),
            "endpoint_false_rejection_rate_definitive": _safe_rate(
                endp_false_violating, endp_definitive_true
            ),
            "trajectory_inconclusive_count": traj_inconclusive_true,
            "endpoint_inconclusive_count": endp_inconclusive_true,
        },
    }


def attribute_records(records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Convenience wrapper accepting claim dicts with ``done``, ``trajectory_verdict``, ``endpoint_verdict``."""
    done = [r["done"] for r in records]
    traj = [r["trajectory_verdict"] for r in records]
    endp = [r["endpoint_verdict"] for r in records]
    return attribute_detection(done, traj, endp)


def _build_serialized_fixture_pairs() -> list[dict[str, Any]]:
    """Construct the 6 reviewer-specified JSON-serialized checker input pairs."""
    raw_fixtures = [
        {
            "fixture_id": "F1_trajectory_only_compliant",
            "description": "DONE=False, trajectory=violating, endpoint=compliant (trajectory-only gain, compliant)",
            "adjudicator_done": False,
            "trajectory_payload": {
                "schema": "veap-x2-checker-input/1",
                "checker": "trajectory",
                "episode_id": "ep_f1",
                "claim_issued": True,
                "trajectory_steps": [
                    {"t": 0, "x": 0.0, "y": 0.0, "min_clearance_m": 0.40},
                    {"t": 1, "x": 1.0, "y": 0.1, "min_clearance_m": -0.02},
                    {"t": 2, "x": 2.0, "y": 0.0, "min_clearance_m": 0.35},
                ],
                "verdict": "violating",
            },
            "endpoint_payload": {
                "schema": "veap-x2-checker-input/1",
                "checker": "endpoint",
                "episode_id": "ep_f1",
                "claim_issued": True,
                "endpoint_state": {"t": 2, "x": 2.0, "y": 0.0, "min_clearance_m": 0.35},
                "verdict": "compliant",
            },
        },
        {
            "fixture_id": "F2_trajectory_only_inconclusive",
            "description": "DONE=False, trajectory=violating, endpoint=inconclusive (trajectory-only gain, inconclusive)",
            "adjudicator_done": False,
            "trajectory_payload": {
                "schema": "veap-x2-checker-input/1",
                "checker": "trajectory",
                "episode_id": "ep_f2",
                "claim_issued": True,
                "trajectory_steps": [
                    {"t": 0, "x": 0.0, "y": 0.0, "min_clearance_m": 0.30},
                    {"t": 1, "x": 1.1, "y": 0.2, "min_clearance_m": -0.05},
                    {"t": 2, "x": 1.9, "y": 0.1, "min_clearance_m": None},
                ],
                "verdict": "violating",
            },
            "endpoint_payload": {
                "schema": "veap-x2-checker-input/1",
                "checker": "endpoint",
                "episode_id": "ep_f2",
                "claim_issued": True,
                "endpoint_state": {"t": 2, "x": 1.9, "y": 0.1, "min_clearance_m": None, "sensor_occluded": True},
                "verdict": "inconclusive",
            },
        },
        {
            "fixture_id": "F3_endpoint_only_compliant",
            "description": "DONE=False, trajectory=compliant, endpoint=violating (endpoint-only loss, compliant)",
            "adjudicator_done": False,
            "trajectory_payload": {
                "schema": "veap-x2-checker-input/1",
                "checker": "trajectory",
                "episode_id": "ep_f3",
                "claim_issued": True,
                "trajectory_steps": [
                    {"t": 0, "x": 0.0, "y": 0.0, "min_clearance_m": 0.25},
                    {"t": 1, "x": 0.9, "y": 0.0, "min_clearance_m": 0.20},
                    {"t": 2, "x": 1.5, "y": 0.0, "min_clearance_m": 0.18},
                ],
                "verdict": "compliant",
            },
            "endpoint_payload": {
                "schema": "veap-x2-checker-input/1",
                "checker": "endpoint",
                "episode_id": "ep_f3",
                "claim_issued": True,
                "endpoint_state": {"t": 2, "x": 1.5, "y": 0.0, "goal_reached": False},
                "verdict": "violating",
            },
        },
        {
            "fixture_id": "F4_endpoint_only_inconclusive",
            "description": "DONE=False, trajectory=inconclusive, endpoint=violating (endpoint-only loss, inconclusive)",
            "adjudicator_done": False,
            "trajectory_payload": {
                "schema": "veap-x2-checker-input/1",
                "checker": "trajectory",
                "episode_id": "ep_f4",
                "claim_issued": True,
                "trajectory_steps": [
                    {"t": 0, "x": 0.0, "y": 0.0, "min_clearance_m": 0.22},
                    {"t": 1, "x": 0.8, "y": 0.1, "min_clearance_m": None},
                ],
                "verdict": "inconclusive",
            },
            "endpoint_payload": {
                "schema": "veap-x2-checker-input/1",
                "checker": "endpoint",
                "episode_id": "ep_f4",
                "claim_issued": True,
                "endpoint_state": {"t": 2, "x": 1.4, "y": 0.2, "goal_reached": False},
                "verdict": "violating",
            },
        },
        {
            "fixture_id": "F5_false_rejection_on_ref_true",
            "description": "DONE=True, trajectory=violating, endpoint=compliant (false rejection on reference-true claim)",
            "adjudicator_done": True,
            "trajectory_payload": {
                "schema": "veap-x2-checker-input/1",
                "checker": "trajectory",
                "episode_id": "ep_f5",
                "claim_issued": True,
                "trajectory_steps": [
                    {"t": 0, "x": 0.0, "y": 0.0, "min_clearance_m": 0.12},
                    {"t": 1, "x": 1.0, "y": 0.0, "min_clearance_m": 0.04},
                    {"t": 2, "x": 2.0, "y": 0.0, "min_clearance_m": 0.15},
                ],
                "verdict": "violating",
            },
            "endpoint_payload": {
                "schema": "veap-x2-checker-input/1",
                "checker": "endpoint",
                "episode_id": "ep_f5",
                "claim_issued": True,
                "endpoint_state": {"t": 2, "x": 2.0, "y": 0.0, "goal_reached": True},
                "verdict": "compliant",
            },
        },
        {
            "fixture_id": "F6_timeout_no_claim_episode",
            "description": "Timeout / no-claim episode (DONE not issued -> excluded from DONE-false denominator, tracked in all-episode accounting)",
            "adjudicator_done": None,
            "trajectory_payload": {
                "schema": "veap-x2-checker-input/1",
                "checker": "trajectory",
                "episode_id": "ep_f6",
                "claim_issued": False,
                "episode_status": "timeout_no_claim",
                "trajectory_steps": [
                    {"t": 0, "x": 0.0, "y": 0.0, "min_clearance_m": 0.30},
                ],
                "verdict": "inconclusive",
            },
            "endpoint_payload": {
                "schema": "veap-x2-checker-input/1",
                "checker": "endpoint",
                "episode_id": "ep_f6",
                "claim_issued": False,
                "episode_status": "timeout_no_claim",
                "endpoint_state": None,
                "verdict": "inconclusive",
            },
        },
    ]

    serialized_fixtures: list[dict[str, Any]] = []
    for item in raw_fixtures:
        serialized_fixtures.append(
            {
                "fixture_id": item["fixture_id"],
                "description": item["description"],
                "adjudicator_done": item["adjudicator_done"],
                "trajectory_input_json": json.dumps(item["trajectory_payload"], sort_keys=True),
                "endpoint_input_json": json.dumps(item["endpoint_payload"], sort_keys=True),
            }
        )
    return serialized_fixtures


def run_serialized_fixture_suite(
    output_path: Path | None = DEFAULT_FIXTURES_REPORT_PATH,
) -> dict[str, Any]:
    """Run the 6 serialized fixture pairs through attribution and optionally write JSON report."""
    fixtures = _build_serialized_fixture_pairs()
    adjudicator_done: list[bool | None] = []
    trajectory_verdicts: list[str] = []
    endpoint_verdicts: list[str] = []
    decoded_fixtures: list[dict[str, Any]] = []

    for fx in fixtures:
        traj_obj = json.loads(fx["trajectory_input_json"])
        endp_obj = json.loads(fx["endpoint_input_json"])
        adjudicator_done.append(fx["adjudicator_done"])
        trajectory_verdicts.append(traj_obj["verdict"])
        endpoint_verdicts.append(endp_obj["verdict"])
        decoded_fixtures.append(
            {
                "fixture_id": fx["fixture_id"],
                "description": fx["description"],
                "adjudicator_done": fx["adjudicator_done"],
                "trajectory_verdict": traj_obj["verdict"],
                "endpoint_verdict": endp_obj["verdict"],
                "trajectory_input_json": fx["trajectory_input_json"],
                "endpoint_input_json": fx["endpoint_input_json"],
            }
        )

    attribution = attribute_detection(adjudicator_done, trajectory_verdicts, endpoint_verdicts)
    report = {
        "schema": "veap-x2-attribution-fixtures/1",
        "n_fixtures": len(decoded_fixtures),
        "fixtures": decoded_fixtures,
        "attribution": attribution,
    }
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    suite_report = run_serialized_fixture_suite()
    print(
        f"Wrote {DEFAULT_FIXTURES_REPORT_PATH} "
        f"(n_fixtures={suite_report['n_fixtures']}, "
        f"n_ref_false={suite_report['attribution']['n_ref_false']}, "
        f"n_no_claim_or_timeout={suite_report['attribution']['n_no_claim_or_timeout']})"
    )
