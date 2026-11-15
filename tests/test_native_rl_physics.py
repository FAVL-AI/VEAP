"""Verification test for native C/C++ RL physics environment, control tape replay, and telemetry."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RL_BIN = ROOT / "backend" / "rl" / "build" / "veap-rl"
TAPE_PATH = ROOT / "artifacts" / "research" / "v06-control-tape.json"
MUJOCO_REF_PATH = ROOT / "artifacts" / "research" / "v06-mujoco-locked-replay.json"
TRACE_OUT = ROOT / "artifacts" / "research" / "v06-rl-physics-replay.json"


def test_native_rl_physics_binary_builds_and_runs():
    subprocess.run(["make", "-C", str(ROOT / "backend" / "rl"), "all"], check=True)
    assert RL_BIN.is_file()


def test_frozen_control_tape_replay_and_verification(tmp_path):
    out_file = tmp_path / "replay-test.json"
    cmd = [
        str(RL_BIN),
        "replay-tape",
        str(TAPE_PATH),
        str(out_file),
        str(MUJOCO_REF_PATH),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "passed" in res.stdout

    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["schema_version"] == "veab-native-rl-replay-result/1"
    assert data["execution"] == "native_cpp_physics_rl"

    verif = data["verification"]
    assert verif["timestamps_verified"] is True
    assert verif["actions_verified"] is True
    assert verif["max_timegrid_error_s"] == 0.0
    assert verif["position_rmse_to_mujoco_m"] < 0.100  # VEAP RMSE target < 100mm
    assert verif["rmse_within_threshold"] is True


def test_physics_trace_contains_rl_observations_rewards_termination():
    assert TRACE_OUT.is_file()
    payload = json.loads(TRACE_OUT.read_text(encoding="utf-8"))

    samples = payload["trace"]["samples"]
    assert len(samples) == 25

    # Check sample 0 (initial step from reset)
    s0 = samples[0]
    assert s0["tick"] == 0
    assert s0["time_s"] == 0.0
    assert s0["position_xyz_m"] == [1.2, 1.3, 0.16]
    assert "observation" in s0
    assert s0["observation"]["x"] == 1.2
    assert s0["observation"]["y"] == 1.3
    assert "reward" in s0
    assert "cumulative_reward" in s0
    assert "termination_reason" in s0
    assert s0["termination_reason"] == "in_progress"

    # Check final sample (step 24)
    s_last = samples[-1]
    assert s_last["tick"] == 24
    assert s_last["time_s"] == 4.8
    assert s_last["truncated"] is True
    assert s_last["termination_reason"] == "tape_completed"
    assert isinstance(s_last["observation"]["dist_to_target"], float)
    assert isinstance(s_last["cumulative_reward"], float)


def test_native_physics_training_and_eval(tmp_path):
    model_path = tmp_path / "phys_test.model"
    cmd_train = [
        str(RL_BIN),
        "train-physics",
        str(model_path),
        "17",
        "100",
    ]
    res_train = subprocess.run(cmd_train, capture_output=True, text=True, check=True)
    assert "training" in res_train.stdout
    assert model_path.is_file()

    cmd_eval = [
        str(RL_BIN),
        "eval-physics",
        str(model_path),
    ]
    res_eval = subprocess.run(cmd_eval, capture_output=True, text=True, check=True)
    assert "physics_policy" in res_eval.stdout

