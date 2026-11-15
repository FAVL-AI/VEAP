"""X1 step 4 analysis of the one-shot test records (prereg v3). Train/val never pooled with test."""
import json, hashlib, collections
from veap.x1_stats import clustered_bootstrap, wilson
R = json.load(open("x1/step3/test_records_L3.json"))
assert all(r["split"] == "test" for r in R)
B, SEED = 10_000, 0
def by(pol, gate):
    d = collections.defaultdict(list)
    for r in sorted(R, key=lambda r: (r["scenario_id"], r["seed"])):
        if r["policy"] == pol and r["gate"] == gate: d[r["scenario_id"]].append(r)
    return d
def cl(pol, gate, f):
    d = by(pol, gate); return clustered_bootstrap({k: [f(r) for r in v] for k, v in d.items()}, resamples=B, seed=SEED)
gap = lambda r: int(r["task_completed"]) - int(r["verified"])
out = {"prereg_sha256": "784382afe11be46c7863ef1a2a02f4f72a66d0cf1c57421f1830fa84f6aa10c7",
       "params_sha256": hashlib.sha256(open("X1_PARAMS.json", "rb").read()).hexdigest(),
       "records_sha256": hashlib.sha256(open("x1/step3/test_records_L3.json", "rb").read()).hexdigest(),
       "split": "test (run once)", "n_scenarios_test": 3, "seeds": "0..19", "level": "L3",
       "bootstrap": {"method": "scenario-clustered percentile bootstrap: scenarios with replacement, then seeds within each", "resamples": B, "seed": SEED}}
g = by("greedy", "off")
out["PRIMARY_greedy_gate_off_completed_minus_verified_rate"] = {**cl("greedy", "off", gap),
    "completed": sum(r["task_completed"] for v in g.values() for r in v), "verified": sum(r["verified"] for v in g.values() for r in v),
    "n_nominal": sum(len(v) for v in g.values()), "n_effective_distinct_digests": len({r["trace_sha256"] for v in g.values() for r in v})}
sec = {}
for pol in ("greedy", "route"):
    for gate in ("off", "on"):
        d = by(pol, gate)
        sec[f"{pol}__gate_{gate}"] = {"completed_rate": cl(pol, gate, lambda r: int(r["task_completed"])),
            "verified_rate": cl(pol, gate, lambda r: int(r["verified"])), "gap_rate": cl(pol, gate, gap),
            "mean_violations": cl(pol, gate, lambda r: r["safety_violations"]),
            "mean_interventions": cl(pol, gate, lambda r: r["interventions"]), "mean_steps": cl(pol, gate, lambda r: r["steps"]),
            "n_nominal": sum(len(v) for v in d.values()), "n_effective_distinct_digests": len({r["trace_sha256"] for v in d.values() for r in v})}
out["SECONDARY_route_gate_off_mean_violations"] = sec["route__gate_off"]["mean_violations"]
out["secondary_all_cells_clustered"] = sec
per = {}
for r in R:
    k = f'{r["scenario_id"]}|{r["policy"]}|gate_{r["gate"]}'; per.setdefault(k, []).append(r)
out["per_scenario_descriptive_wilson"] = {}
for k, v in sorted(per.items()):
    n = len(v); c = sum(r["task_completed"] for r in v); vf = sum(r["verified"] for r in v); gp = c - vf
    out["per_scenario_descriptive_wilson"][k] = {"n": n, "distinct_trace_digests": len({r["trace_sha256"] for r in v}),
        "completed": c, "completed_wilson95": [round(x, 4) for x in wilson(c, n)], "verified": vf, "verified_wilson95": [round(x, 4) for x in wilson(vf, n)],
        "completed_minus_verified": gp, "gap_wilson95": [round(x, 4) for x in wilson(gp, n)],
        "violations_total": sum(r["safety_violations"] for r in v), "interventions_total": sum(r["interventions"] for r in v),
        "mean_steps": round(sum(r["steps"] for r in v) / n, 2), "evaluation_valid": sum(r["evaluation_valid"] for r in v),
        "dropout_ticks_total": sum(r["perturbation"]["actuation_dropout_ticks"] for r in v)}
out["faults"] = {"injected_actuation_dropout": {"faults": "not measured", "recovered_faults": "not measured"},
    "scenario_scheduled_faults_ledger_counts": "per-record fields scenario_faults_ledger / scenario_recovered_faults_ledger cover only scenario-contract faults"}
out["limitations"] = ["The ledger cannot see the injected actuation dropout as a fault event: it is only a flag on state payloads (hashed), so the verifier's faults/recovered_faults do not count it.",
    "Test n = 3 scenarios (train 1, val 1); seeds within a scenario are not independent; CIs are scenario-clustered and coarse.",
    "C2 remains a metric demonstration: greedy ignores obstacles by construction.",
    "absence-rejection is the one absence scenario: completed = correct abstention within budget; verified = that plus verifier acceptance.",
    "Selected level L3 is the ladder ceiling; selection rule did not bind."]
json.dump(out, open("x1/step3/X1_TEST_ANALYSIS.json", "w"), indent=1)
P = out["PRIMARY_greedy_gate_off_completed_minus_verified_rate"]; print("PRIMARY", {k: P[k] for k in ("estimate","ci_low","ci_high","completed","verified","n_nominal","n_effective_distinct_digests","resamples","seed","n_clusters")})
print("SECONDARY route off viol", {k: out["SECONDARY_route_gate_off_mean_violations"][k] for k in ("estimate","ci_low","ci_high")})
for k, v in sec.items(): print(k, "comp", round(v["completed_rate"]["estimate"],4), [round(v["completed_rate"]["ci_low"],4), round(v["completed_rate"]["ci_high"],4)], "ver", round(v["verified_rate"]["estimate"],4), [round(v["verified_rate"]["ci_low"],4), round(v["verified_rate"]["ci_high"],4)], "viol", round(v["mean_violations"]["estimate"],3), [round(v["mean_violations"]["ci_low"],3), round(v["mean_violations"]["ci_high"],3)], "neff", v["n_effective_distinct_digests"])
for k, v in out["per_scenario_descriptive_wilson"].items(): print(k, v)
