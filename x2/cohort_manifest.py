"""Deterministic X2 407-scenario cohort manifest, policy assignment, and canonical claim ordering.

Retains the concrete 407-scenario list privately when held-out scenarios must not
be exposed in public version control, while recording its SHA-256 digest and
canonical replay-invariant claim ordering rule for the X2 protocol freeze.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

POLICY_WEIGHTS: dict[str, float] = {
    "route": 0.50,
    "greedy": 0.50,
}

TASK_FAMILIES: tuple[str, ...] = (
    "warehouse-transfer",
    "hospital-inspection",
    "campus-patrol",
    "distribution-shift",
    "absence-rejection",
)

TOTAL_SCENARIO_CAP = 407


def assign_policy(index: int, scenario_id: str, policy_weights: dict[str, float] = POLICY_WEIGHTS) -> str:
    """Deterministically assign a policy matching exact prespecified weights via SHA-256."""
    digest = hashlib.sha256(f"x2-policy-v1|{index}|{scenario_id}".encode("utf-8")).digest()
    unit = int.from_bytes(digest[:8], "big") / float(1 << 64)
    cumulative = 0.0
    for policy, weight in policy_weights.items():
        cumulative += weight
        if unit < cumulative:
            return policy
    return next(reversed(policy_weights))


def build_cohort_manifest(total_scenarios: int = TOTAL_SCENARIO_CAP) -> dict[str, Any]:
    """Build the ordered 407-scenario cohort manifest with fixed policy mix."""
    entries: list[dict[str, Any]] = []
    counts: dict[str, int] = {p: 0 for p in POLICY_WEIGHTS}
    for idx in range(total_scenarios):
        family = TASK_FAMILIES[idx % len(TASK_FAMILIES)]
        scenario_id = f"x2-{family}-{idx + 1:03d}"
        policy = assign_policy(idx, scenario_id)
        counts[policy] += 1
        entries.append(
            {
                "order_index": idx + 1,
                "scenario_id": scenario_id,
                "task_family": family,
                "policy": policy,
                "seed": 10000 + idx,
            }
        )
    payload = {
        "schema_id": "veap.x2.cohort_manifest/1",
        "total_scenario_cap": total_scenarios,
        "policy_weights": POLICY_WEIGHTS,
        "policy_counts": counts,
        "canonical_claim_order_key": ["scenario_id", "episode_id", "claim_id", "claim_seq"],
        "scenarios": entries,
    }
    canonical_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    manifest_sha256 = hashlib.sha256(canonical_bytes).hexdigest()
    return {"manifest_sha256": manifest_sha256, "manifest": payload}


def order_genuine_claims_canonically(claims: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort genuine claims deterministically regardless of file or database iteration order."""
    return sorted(
        claims,
        key=lambda c: (
            str(c["scenario_id"]),
            str(c["episode_id"]),
            str(c["claim_id"]),
            int(c.get("claim_seq", 0)),
        ),
    )


def select_blind_genuine_claim(
    claims: list[dict[str, Any]],
    scenario_id: str,
    selection_salt: str,
) -> dict[str, Any]:
    """Select one genuine claim uniformly using canonical ordering and SHA-256(selection_salt | scenario_id)."""
    ordered = order_genuine_claims_canonically(claims)
    if not ordered:
        raise ValueError(f"Scenario {scenario_id} has zero genuine claims")
    digest = hashlib.sha256(f"{selection_salt}|{scenario_id}".encode("utf-8")).digest()
    idx = int.from_bytes(digest[:8], "big") % len(ordered)
    return ordered[idx]


def main() -> None:
    root = Path(__file__).resolve().parent
    result = build_cohort_manifest()
    out_path = root / ".private_cohort_manifest.json"
    out_path.write_text(json.dumps(result["manifest"], indent=2) + "\n", encoding="utf-8")
    print(
        f"Wrote private manifest {out_path} "
        f"(total={result['manifest']['total_scenario_cap']}, "
        f"policy_counts={result['manifest']['policy_counts']}, "
        f"manifest_sha256={result['manifest_sha256']})"
    )


if __name__ == "__main__":
    main()
