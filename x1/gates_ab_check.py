import copy, math
from veap.spec import load_scenario, digest
from veap.sim import run_episode
from veap.ledger import check_chain
from veap.verifier import verify_bundle, _clearance
from veap.x1_perturb import LADDER
s = load_scenario("warehouse-transfer")  # validation split, not test
b = run_episode(s, "greedy", 0, False, perturbation=LADDER["L3"])
ev = b["events"]
drops = [i for i, e in enumerate(ev) if e["kind"] == "state" and e["payload"].get("x1_actuation_dropout")]
i = drops[0]; e = ev[i]
print("A dropout_state_events", len(drops), "manifest_dropout_ticks", b["manifest"]["perturbation"]["actuation_dropout_ticks"])
print("A event", i, "hash", e["hash"], "recomputed_with_flag", digest({k: v for k, v in e.items() if k != "hash"}) == e["hash"])
t = copy.deepcopy(ev); del t[i]["payload"]["x1_actuation_dropout"]
print("A recomputed_without_flag_equals_hash", digest({k: v for k, v in t[i].items() if k != "hash"}) == e["hash"])
print("A check_chain_original", check_chain(ev), "| flag_stripped", check_chain(t))
print("A root", b["manifest"]["ledger_root_sha256"], "== last hash", ev[-1]["hash"] == b["manifest"]["ledger_root_sha256"])
# B: compare observation vs state; violations recomputed from STATE poses only
r = verify_bundle(b)
st = {e["tick"]: e["payload"] for e in ev if e["kind"] == "state"}
ob = {e["tick"]: e["payload"] for e in ev if e["kind"] == "observation"}
dev = max(math.hypot(ob[k]["x"] - st[k-1]["x"], ob[k]["y"] - st[k-1]["y"]) for k in ob if k-1 in st)
ps = b["manifest"]["scenario"]
from veap.spec import Scenario
S = Scenario.model_validate(ps)
point_hits_state = sum(len(_clearance(p["x"], p["y"], S)[1]) for p in st.values())
point_hits_obs = sum(len(_clearance(p["x"], p["y"], S)[1]) for p in ob.values())
print("B verifier_violations", r["safety_violations"], "| point hits on state poses", point_hits_state, "| on observations", point_hits_obs, "| max |obs - true pose prior tick| m", round(dev, 4))
t2 = copy.deepcopy(b)
for e2 in t2["events"]:
    if e2["kind"] == "observation": e2["payload"]["x"] += 5.0
print("B note: verifier loop ignores observation x/y (only target_present/sensor_ok read)")
