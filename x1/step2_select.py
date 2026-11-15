"""X1 step 2 selection (prereg v3 M2'): train+val ONLY, seeds 0..19, levels L0..L3."""
import json, collections, sys
from veap.spec import list_scenarios
from veap.sim import run_episode
from veap.verifier import verify_bundle
from veap.x1_perturb import LADDER
SEEDS = list(range(20))
scen = [s for s in list_scenarios() if s.split in ("train", "validation")]
assert all(s.split != "test" for s in scen)
out = {"spec_sha256": "784382afe11be46c7863ef1a2a02f4f72a66d0cf1c57421f1830fa84f6aa10c7", "seeds": SEEDS,
       "scenarios": {s.id: s.split for s in scen}, "levels": {}}
for lvl, p in LADDER.items():
    cells = collections.defaultdict(list); recs = []
    for s in scen:
        for seed in SEEDS:
            for policy in ("greedy", "route"):
                for shield in (False, True):
                    b = run_episode(s, policy, seed, shield, perturbation=p)
                    r = verify_bundle(b)
                    rec = {"scenario_id": s.id, "split": s.split, "seed": seed, "policy": policy, "gate": "on" if shield else "off",
                           "trace_sha256": b["manifest"]["ledger_root_sha256"], "scenario_sha256": b["manifest"]["scenario_sha256"],
                           "task_completed": r["task_completed"], "verified": r["verified"], "safety_violations": r["safety_violations"],
                           "interventions": r["interventions"], "steps": r["steps"], "evaluation_valid": r["evaluation_valid"],
                           "failure_reasons": r["failure_reasons"][:5], "perturbation": b["manifest"]["perturbation"]}
                    recs.append(rec); cells[f"{s.id}|{s.split}|{policy}|{rec['gate']}"].append(rec)
    rg = [r for r in recs if r["policy"] == "route" and r["gate"] == "on"]
    a_k = sum(r["verified"] for r in rg)
    cell_tab = {k: {"n": len(v), "distinct_trace_digests": len({r["trace_sha256"] for r in v}),
                    "completed": sum(r["task_completed"] for r in v), "verified": sum(r["verified"] for r in v),
                    "violations": sum(r["safety_violations"] for r in v), "interventions": sum(r["interventions"] for r in v)}
                for k, v in sorted(cells.items())}
    min_distinct = min(c["distinct_trace_digests"] for c in cell_tab.values())
    out["levels"][lvl] = {"params": p.as_dict(), "cond_a_route_gate_on_verified": f"{a_k}/{len(rg)}", "cond_a_pass": a_k >= 36 and len(rg) == 40,
                          "cond_b_min_distinct": f"{min_distinct}/20", "cond_b_pass": min_distinct >= 15, "cells": cell_tab,
                          "start_fallback_nominal_runs": sum(r["perturbation"]["start_fallback_nominal"] for r in recs)}
    out["levels"][lvl]["qualifies"] = out["levels"][lvl]["cond_a_pass"] and out["levels"][lvl]["cond_b_pass"]
    json.dump(recs, open(f"x1/step2/records_{lvl}.json", "w"))
q = [l for l in LADDER if l != "L0" and out["levels"][l]["qualifies"]]
out["selected_level"] = max(q, key=lambda l: list(LADDER).index(l)) if q else None
out["rule"] = "largest level with (a) route+gate-on verified >= 36/40 and (b) every train/val cell >= 15/20 distinct digests; never the greedy gap"
qs = [l for l in LADDER if out["levels"][l]["qualifies"]]
out["qualifying_levels"] = qs
out["monotone_qualification"] = all(list(LADDER).index(b) - list(LADDER).index(a) == 1 for a, b in zip(qs, qs[1:]))
json.dump(out, open("x1/step2/selection.json", "w"), indent=1)
for l, v in out["levels"].items():
    print(l, "a:", v["cond_a_route_gate_on_verified"], v["cond_a_pass"], "| b min distinct:", v["cond_b_min_distinct"], v["cond_b_pass"], "| qualifies:", v["qualifies"], "| start_fallback:", v["start_fallback_nominal_runs"])
    for k, c in v["cells"].items(): print("   ", k, c)
print("selected:", out["selected_level"], "qualifying:", qs, "contiguous:", out["monotone_qualification"])
