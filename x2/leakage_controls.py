"""Paired-input leakage controls for X2 trajectory and endpoint checkers.

Provides standalone byte-level checker entry points (``check_trajectory_bytes`` and
``check_endpoint_bytes``) that reject any hidden reference-label keys, and runs
6 paired-input controls (3 hidden-truth pairs + 3 visible-history pairs = 12 episodes)
writing ``x2/leakage_controls_report.json``.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

FORBIDDEN_LABEL_KEYS = frozenset(
    {"adjudicator_done", "reference_label", "ground_truth", "done", "label"}
)
DEFAULT_REPORT_PATH = Path(__file__).resolve().parent / "leakage_controls_report.json"


def _assert_no_forbidden_keys(obj: Any, path: str = "$") -> None:
    if isinstance(obj, dict):
        for key, value in obj.items():
            if str(key).lower() in FORBIDDEN_LABEL_KEYS:
                raise ValueError(f"Forbidden reference label key {key!r} found at {path}")
            _assert_no_forbidden_keys(value, f"{path}.{key}")
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            _assert_no_forbidden_keys(item, f"{path}[{idx}]")


def _decode_and_guard_payload(payload: bytes) -> dict[str, Any]:
    if not isinstance(payload, bytes):
        raise TypeError(f"Checker entry point requires serialized JSON bytes, got {type(payload).__name__}")
    data = json.loads(payload.decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Top-level serialized checker payload must be a JSON object")
    _assert_no_forbidden_keys(data)
    return data


def sha256_hex(payload: bytes) -> str:
    """Return lowercase SHA-256 hex digest of serialized ``payload`` bytes."""
    return hashlib.sha256(payload).hexdigest()


def check_trajectory_bytes(payload: bytes) -> str:
    """Evaluate trajectory compliance solely from serialized JSON ``bytes``."""
    data = _decode_and_guard_payload(payload)
    steps = data.get("trajectory_steps")
    if not isinstance(steps, list) or len(steps) == 0:
        return "inconclusive"

    max_speed_mps = float(data.get("max_speed_mps", 1.5))
    has_incomplete = False

    for step in steps:
        if not isinstance(step, dict):
            return "inconclusive"
        if step.get("in_keepout_zone") is True:
            return "violating"
        clearance = step.get("min_clearance_m")
        if clearance is not None and float(clearance) < 0.0:
            return "violating"
        speed = step.get("speed_mps")
        if speed is not None and float(speed) > max_speed_mps:
            return "violating"
        if (
            step.get("missing_command") is True
            or step.get("sensor_occluded") is True
            or clearance is None
            or speed is None
        ):
            has_incomplete = True

    return "inconclusive" if has_incomplete else "compliant"


def check_endpoint_bytes(payload: bytes) -> str:
    """Evaluate endpoint compliance solely from serialized JSON ``bytes``."""
    data = _decode_and_guard_payload(payload)
    state = data.get("endpoint_state")
    if not isinstance(state, dict):
        return "inconclusive"
    if state.get("sensor_occluded") is True:
        return "inconclusive"
    clearance = state.get("min_clearance_m")
    if clearance is None:
        return "inconclusive"
    if state.get("in_keepout_zone") is True or float(clearance) < 0.0:
        return "violating"
    if state.get("goal_reached") is False:
        return "violating"
    return "compliant"


def _serialize(obj: dict[str, Any]) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def run_leakage_controls(
    output_path: Path | None = DEFAULT_REPORT_PATH,
) -> dict[str, Any]:
    """Run 3 hidden-truth pairs and 3 visible-history pairs through byte-only checkers."""
    # 3 hidden-truth pairs: identical bytes to both checkers across A and B; reference labels differ.
    ht_specs = [
        (
            "HT1",
            "Identical compliant telemetry; hidden reference label differs (True vs False)",
            {
                "max_speed_mps": 1.5,
                "trajectory_steps": [
                    {"t": 0, "min_clearance_m": 0.30, "speed_mps": 1.0, "in_keepout_zone": False},
                    {"t": 1, "min_clearance_m": 0.25, "speed_mps": 1.1, "in_keepout_zone": False},
                ],
            },
            {
                "endpoint_state": {
                    "t": 1,
                    "min_clearance_m": 0.25,
                    "in_keepout_zone": False,
                    "goal_reached": True,
                }
            },
            True,
            False,
        ),
        (
            "HT2",
            "Identical trajectory-violating / endpoint-compliant telemetry; hidden reference label differs",
            {
                "max_speed_mps": 1.5,
                "trajectory_steps": [
                    {"t": 0, "min_clearance_m": 0.30, "speed_mps": 1.0, "in_keepout_zone": False},
                    {"t": 1, "min_clearance_m": -0.04, "speed_mps": 1.0, "in_keepout_zone": True},
                    {"t": 2, "min_clearance_m": 0.28, "speed_mps": 0.9, "in_keepout_zone": False},
                ],
            },
            {
                "endpoint_state": {
                    "t": 2,
                    "min_clearance_m": 0.28,
                    "in_keepout_zone": False,
                    "goal_reached": True,
                }
            },
            False,
            True,
        ),
        (
            "HT3",
            "Identical occluded/inconclusive trajectory telemetry; hidden reference label differs",
            {
                "max_speed_mps": 1.5,
                "trajectory_steps": [
                    {"t": 0, "min_clearance_m": 0.30, "speed_mps": 1.0, "in_keepout_zone": False},
                    {"t": 1, "min_clearance_m": None, "speed_mps": 1.0, "sensor_occluded": True},
                ],
            },
            {
                "endpoint_state": {
                    "t": 2,
                    "min_clearance_m": 0.22,
                    "in_keepout_zone": False,
                    "goal_reached": True,
                }
            },
            False,
            True,
        ),
    ]

    hidden_truth_pairs: list[dict[str, Any]] = []
    for pair_id, desc, traj_obj, endp_obj, ref_a, ref_b in ht_specs:
        traj_bytes_a = _serialize(traj_obj)
        traj_bytes_b = _serialize(traj_obj)
        endp_bytes_a = _serialize(endp_obj)
        endp_bytes_b = _serialize(endp_obj)

        traj_verdict_a = check_trajectory_bytes(traj_bytes_a)
        traj_verdict_b = check_trajectory_bytes(traj_bytes_b)
        endp_verdict_a = check_endpoint_bytes(endp_bytes_a)
        endp_verdict_b = check_endpoint_bytes(endp_bytes_b)

        traj_sha_a, traj_sha_b = sha256_hex(traj_bytes_a), sha256_hex(traj_bytes_b)
        endp_sha_a, endp_sha_b = sha256_hex(endp_bytes_a), sha256_hex(endp_bytes_b)

        passed = (
            traj_sha_a == traj_sha_b
            and endp_sha_a == endp_sha_b
            and traj_verdict_a == traj_verdict_b
            and endp_verdict_a == endp_verdict_b
            and ref_a != ref_b
        )
        if not passed:
            raise AssertionError(f"Hidden-truth leakage control failed for {pair_id}")

        hidden_truth_pairs.append(
            {
                "pair_id": pair_id,
                "description": desc,
                "episode_a": {
                    "reference_label": ref_a,
                    "trajectory_sha256": traj_sha_a,
                    "endpoint_sha256": endp_sha_a,
                    "trajectory_verdict": traj_verdict_a,
                    "endpoint_verdict": endp_verdict_a,
                },
                "episode_b": {
                    "reference_label": ref_b,
                    "trajectory_sha256": traj_sha_b,
                    "endpoint_sha256": endp_sha_b,
                    "trajectory_verdict": traj_verdict_b,
                    "endpoint_verdict": endp_verdict_b,
                },
                "trajectory_bytes_match": traj_sha_a == traj_sha_b,
                "endpoint_bytes_match": endp_sha_a == endp_sha_b,
                "verdicts_match": (traj_verdict_a == traj_verdict_b and endp_verdict_a == endp_verdict_b),
                "reference_labels_differ": ref_a != ref_b,
                "control_passed": passed,
            }
        )

    # 3 visible-history pairs: identical endpoint bytes; trajectory bytes differ at prespecified event.
    shared_endpoint = {
        "endpoint_state": {
            "t": 2,
            "min_clearance_m": 0.30,
            "in_keepout_zone": False,
            "goal_reached": True,
        }
    }
    vh_specs = [
        (
            "VH1",
            "keepout_zone_intrusion",
            "Keep-out zone intrusion at t=1 in episode B; endpoint identical",
            {
                "max_speed_mps": 1.5,
                "trajectory_steps": [
                    {"t": 0, "min_clearance_m": 0.35, "speed_mps": 1.0, "in_keepout_zone": False},
                    {"t": 1, "min_clearance_m": 0.25, "speed_mps": 1.0, "in_keepout_zone": False},
                    {"t": 2, "min_clearance_m": 0.30, "speed_mps": 0.8, "in_keepout_zone": False},
                ],
            },
            {
                "max_speed_mps": 1.5,
                "trajectory_steps": [
                    {"t": 0, "min_clearance_m": 0.35, "speed_mps": 1.0, "in_keepout_zone": False},
                    {"t": 1, "min_clearance_m": -0.05, "speed_mps": 1.0, "in_keepout_zone": True},
                    {"t": 2, "min_clearance_m": 0.30, "speed_mps": 0.8, "in_keepout_zone": False},
                ],
            },
        ),
        (
            "VH2",
            "mid_trajectory_overspeed",
            "Mid-trajectory overspeed (2.4 m/s > 1.5 m/s) at t=1 in episode B; endpoint identical",
            {
                "max_speed_mps": 1.5,
                "trajectory_steps": [
                    {"t": 0, "min_clearance_m": 0.35, "speed_mps": 1.0, "in_keepout_zone": False},
                    {"t": 1, "min_clearance_m": 0.25, "speed_mps": 1.2, "in_keepout_zone": False},
                    {"t": 2, "min_clearance_m": 0.30, "speed_mps": 0.8, "in_keepout_zone": False},
                ],
            },
            {
                "max_speed_mps": 1.5,
                "trajectory_steps": [
                    {"t": 0, "min_clearance_m": 0.35, "speed_mps": 1.0, "in_keepout_zone": False},
                    {"t": 1, "min_clearance_m": 0.25, "speed_mps": 2.4, "in_keepout_zone": False},
                    {"t": 2, "min_clearance_m": 0.30, "speed_mps": 0.8, "in_keepout_zone": False},
                ],
            },
        ),
        (
            "VH3",
            "missing_command_gap",
            "Missing command gap at t=1 in episode B; endpoint identical",
            {
                "max_speed_mps": 1.5,
                "trajectory_steps": [
                    {"t": 0, "min_clearance_m": 0.35, "speed_mps": 1.0, "in_keepout_zone": False},
                    {"t": 1, "min_clearance_m": 0.25, "speed_mps": 1.0, "missing_command": False},
                    {"t": 2, "min_clearance_m": 0.30, "speed_mps": 0.8, "in_keepout_zone": False},
                ],
            },
            {
                "max_speed_mps": 1.5,
                "trajectory_steps": [
                    {"t": 0, "min_clearance_m": 0.35, "speed_mps": 1.0, "in_keepout_zone": False},
                    {"t": 1, "min_clearance_m": 0.25, "speed_mps": 1.0, "missing_command": True},
                    {"t": 2, "min_clearance_m": 0.30, "speed_mps": 0.8, "in_keepout_zone": False},
                ],
            },
        ),
    ]

    visible_history_pairs: list[dict[str, Any]] = []
    for pair_id, event_name, desc, traj_a, traj_b in vh_specs:
        traj_bytes_a = _serialize(traj_a)
        traj_bytes_b = _serialize(traj_b)
        endp_bytes_a = _serialize(shared_endpoint)
        endp_bytes_b = _serialize(shared_endpoint)

        traj_verdict_a = check_trajectory_bytes(traj_bytes_a)
        traj_verdict_b = check_trajectory_bytes(traj_bytes_b)
        endp_verdict_a = check_endpoint_bytes(endp_bytes_a)
        endp_verdict_b = check_endpoint_bytes(endp_bytes_b)

        traj_sha_a, traj_sha_b = sha256_hex(traj_bytes_a), sha256_hex(traj_bytes_b)
        endp_sha_a, endp_sha_b = sha256_hex(endp_bytes_a), sha256_hex(endp_bytes_b)

        passed = (
            endp_sha_a == endp_sha_b
            and traj_sha_a != traj_sha_b
            and endp_verdict_a == endp_verdict_b
            and traj_verdict_a != traj_verdict_b
        )
        if not passed:
            raise AssertionError(f"Visible-history leakage control failed for {pair_id}")

        visible_history_pairs.append(
            {
                "pair_id": pair_id,
                "prespecified_event": event_name,
                "description": desc,
                "episode_a": {
                    "trajectory_sha256": traj_sha_a,
                    "endpoint_sha256": endp_sha_a,
                    "trajectory_verdict": traj_verdict_a,
                    "endpoint_verdict": endp_verdict_a,
                },
                "episode_b": {
                    "trajectory_sha256": traj_sha_b,
                    "endpoint_sha256": endp_sha_b,
                    "trajectory_verdict": traj_verdict_b,
                    "endpoint_verdict": endp_verdict_b,
                },
                "endpoint_bytes_match": endp_sha_a == endp_sha_b,
                "trajectory_bytes_differ": traj_sha_a != traj_sha_b,
                "endpoint_verdicts_match": endp_verdict_a == endp_verdict_b,
                "trajectory_verdicts_differ": traj_verdict_a != traj_verdict_b,
                "control_passed": passed,
            }
        )

    all_passed = all(p["control_passed"] for p in hidden_truth_pairs + visible_history_pairs)
    report = {
        "schema": "veap-x2-leakage-controls/1",
        "n_pairs": len(hidden_truth_pairs) + len(visible_history_pairs),
        "n_episodes": 2 * (len(hidden_truth_pairs) + len(visible_history_pairs)),
        "all_controls_passed": all_passed,
        "hidden_truth_pairs": hidden_truth_pairs,
        "visible_history_pairs": visible_history_pairs,
    }
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    rep = run_leakage_controls()
    print(
        f"Wrote {DEFAULT_REPORT_PATH} "
        f"(n_pairs={rep['n_pairs']}, n_episodes={rep['n_episodes']}, all_controls_passed={rep['all_controls_passed']})"
    )
