"""X1 step 3: ONE-SHOT test split, frozen L3 (X1_PARAMS 7924e78e), seeds 0..19, both policies, gate off/on."""
import json, hashlib, os, sys
from veap.spec import list_scenarios
from veap.sim import run_episode
from veap.verifier import verify_bundle
from veap.x1_perturb import LADDER, Perturbation
OUT = "x1/step3/test_records_L3.json"
if os.path.exists(OUT): sys.exit("REFUSE: test output already exists; one-shot only")
P = json.load(open("X1_PARAMS.json"))
assert hashlib.sha256(open("X1_PARAMS.json", "rb").read()).hexdigest() == "7924e78ec25fd5b52b27d49e229d310533c3e3fe6ea6efdd79b5141df0c3cd94"
p = LADDER[P["selected_level"]]
assert p.as_dict() == P["perturbation"]
for f, h in P["code_sha256"].items(): assert hashlib.sha256(open(f, "rb").read()).hexdigest() == h, f
scen = [s for s in list_scenarios() if s.split == "test"]
recs = []
for s in scen:
    for seed in P["step3"]["seeds"]:
        for policy in ("greedy", "route"):
            for shield in (False, True):
                b = run_episode(s, policy, seed, shield, perturbation=p)
                r = verify_bundle(b)
                recs.append({"scenario_id": s.id, "split": s.split, "family": s.family, "seed": seed, "policy": policy,
                             "gate": "on" if shield else "off", "trace_sha256": b["manifest"]["ledger_root_sha256"],
                             "scenario_sha256": b["manifest"]["scenario_sha256"], "nominal_scenario_sha256": b["manifest"]["nominal_scenario_sha256"],
                             "task_completed": r["task_completed"], "verified": r["verified"], "safety_violations": r["safety_violations"],
                             "interventions": r["interventions"], "steps": r["steps"], "evaluation_valid": r["evaluation_valid"],
                             "scenario_faults_ledger": r["faults"], "scenario_recovered_faults_ledger": r["recovered_faults"],
                             "failure_reasons": r["failure_reasons"][:5], "perturbation": b["manifest"]["perturbation"]})
os.makedirs("x1/step3", exist_ok=True)
json.dump(recs, open(OUT, "x"), indent=0)
print("test records:", len(recs), "scenarios:", [s.id for s in scen])
