from veap.sim import run_episode
from veap.spec import list_scenarios, load_scenario
from veap.verifier import verify_bundle
from veap.x1_perturb import LADDER
from veap.x1_stats import clustered_bootstrap, wilson


def test_ladder_matches_prereg_v3_table():
    rows = {k: (p.start_pose_sigma_m, p.obstacle_jitter_m, p.obs_noise_sigma_m, p.actuation_dropout_p) for k, p in LADDER.items()}
    assert rows == {"L0": (0, 0, 0, 0), "L1": (0.05, 0.05, 0.02, 0.05),
                    "L2": (0.10, 0.10, 0.05, 0.10), "L3": (0.20, 0.20, 0.10, 0.15)}


def test_l0_reproduces_legacy_trace_digests():
    for s in list_scenarios():
        for policy in ("greedy", "route"):
            for shield in (False, True):
                a = run_episode(s, policy, 1, shield)
                b = run_episode(s, policy, 1, shield, perturbation=LADDER["L0"])
                assert a["manifest"]["ledger_root_sha256"] == b["manifest"]["ledger_root_sha256"]
                assert b["manifest"]["nominal_scenario_sha256"] == a["manifest"]["scenario_sha256"]


def test_perturbed_runs_are_deterministic_and_seed_dependent():
    s = load_scenario("campus-patrol")
    a = run_episode(s, "route", 3, True, perturbation=LADDER["L2"])
    b = run_episode(s, "route", 3, True, perturbation=LADDER["L2"])
    c = run_episode(s, "route", 4, True, perturbation=LADDER["L2"])
    assert a["manifest"]["ledger_root_sha256"] == b["manifest"]["ledger_root_sha256"]
    assert a["manifest"]["ledger_root_sha256"] != c["manifest"]["ledger_root_sha256"]


def test_perturbed_bundles_keep_trace_integrity():
    for level in ("L1", "L3"):
        for s in list_scenarios():
            for seed in (0, 7):
                bundle = run_episode(s, "route", seed, True, perturbation=LADDER[level])
                report = verify_bundle(bundle)
                bad = [r for r in report["failure_reasons"] if r != "task postcondition unfulfilled"]
                assert report["trace_integrity"] and not bad, (level, s.id, seed, bad)


def test_dropout_ticks_apply_zero_velocity():
    s = load_scenario("campus-patrol")
    bundle = run_episode(s, "route", 0, True, perturbation=LADDER["L3"])
    drops = [e for e in bundle["events"] if e["kind"] == "state" and e["payload"].get("x1_actuation_dropout")]
    assert drops and all(e["payload"]["vx"] == 0 and e["payload"]["vy"] == 0 for e in drops)
    assert bundle["manifest"]["perturbation"]["actuation_dropout_ticks"] == len(drops)


def test_clustered_bootstrap_and_wilson():
    r = clustered_bootstrap({"a": [1, 1, 1], "b": [0, 0, 0]}, resamples=2000, seed=0)
    assert r["estimate"] == 0.5 and r["ci_low"] == 0.0 and r["ci_high"] == 1.0
    r2 = clustered_bootstrap({"a": [1, 1], "b": [1, 1]}, resamples=500)
    assert r2["ci_low"] == r2["ci_high"] == 1.0
    lo, hi = wilson(36, 40)
    assert 0.76 < lo < 0.78 and 0.96 < hi < 0.97
