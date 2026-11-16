"""Deterministic X2 407-scenario cohort manifests, policy assignment, and canonical claim ordering.

Separates:
1. ``build_cohort_manifest`` (development/baseline-only cohort: ``route`` / ``greedy``).
2. ``build_confirmatory_manifest`` (confirmatory X2 cohort: ``rrt_replan`` / ``ppo``
   with 407 distinct environment instances generated via ``perturb_scenario`` at L3
   and bound by ``geometry_sha256`` derived from ``test_salt``).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from veap.spec import canonical, digest as spec_digest, load_scenario
from veap.x1_perturb import LADDER, perturb_scenario

POLICY_WEIGHTS: dict[str, float] = {
    "route": 0.50,
    "greedy": 0.50,
}

CONFIRMATORY_POLICY_WEIGHTS: dict[str, float] = {
    "rrt_replan": 0.50,
    "ppo": 0.50,
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
    """Build the development/baseline-only 407-row cohort manifest (route/greedy)."""
    entries: list[dict[str, Any]] = []
    counts: dict[str, int] = {p: 0 for p in POLICY_WEIGHTS}
    for idx in range(total_scenarios):
        family = TASK_FAMILIES[idx % len(TASK_FAMILIES)]
        scenario_id = f"x2-{family}-{idx + 1:03d}"
        policy = assign_policy(idx, scenario_id, POLICY_WEIGHTS)
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
        "cohort_role": "dev_baseline_only",
        "total_scenario_cap": total_scenarios,
        "policy_weights": POLICY_WEIGHTS,
        "policy_counts": counts,
        "canonical_claim_order_key": ["scenario_id", "episode_id", "claim_id", "claim_seq"],
        "scenarios": entries,
    }
    canonical_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    manifest_sha256 = hashlib.sha256(canonical_bytes).hexdigest()
    return {"manifest_sha256": manifest_sha256, "manifest": payload}


def build_confirmatory_manifest(
    test_salt: str,
    total_scenarios: int = TOTAL_SCENARIO_CAP,
    perturbation_level: str = "L3",
    policy_weights: dict[str, float] = CONFIRMATORY_POLICY_WEIGHTS,
) -> dict[str, Any]:
    """Build the confirmatory 407-instance X2 cohort manifest bound to distinct environment geometries.

    Each row derives an independent perturbation seed from ``sha256(test_salt | order_index | family)``,
    generates a distinct perturbed scenario instance via ``perturb_scenario``, and records its
    ``geometry_sha256`` so all 407 entries represent distinct environment instances.
    """
    pert = LADDER[perturbation_level]
    base_cache = {family: load_scenario(family) for family in TASK_FAMILIES}
    entries: list[dict[str, Any]] = []
    counts: dict[str, int] = {p: 0 for p in policy_weights}
    unique_geometries: set[str] = set()

    for idx in range(total_scenarios):
        family = TASK_FAMILIES[idx % len(TASK_FAMILIES)]
        scenario_id = f"x2-{family}-{idx + 1:03d}"
        inst_hash = hashlib.sha256(f"{test_salt}|{idx + 1}|{family}".encode("utf-8")).digest()
        instance_seed = int.from_bytes(inst_hash[:8], "big") & 0xFFFFFFFF
        perturbed, pinfo = perturb_scenario(base_cache[family], pert, instance_seed)
        geom_sha = spec_digest(perturbed.model_dump(mode="json"))
        unique_geometries.add(geom_sha)

        policy = assign_policy(idx, scenario_id, policy_weights)
        counts[policy] += 1
        entries.append(
            {
                "order_index": idx + 1,
                "scenario_id": scenario_id,
                "task_family": family,
                "perturbation_level": perturbation_level,
                "instance_seed": instance_seed,
                "geometry_sha256": geom_sha,
                "start_resamples": pinfo["start_resamples"],
                "policy": policy,
            }
        )

    payload = {
        "schema_id": "veap.x2.confirmatory_cohort_manifest/1",
        "cohort_role": "confirmatory",
        "total_scenario_cap": total_scenarios,
        "perturbation_level": perturbation_level,
        "policy_weights": policy_weights,
        "policy_counts": counts,
        "unique_geometry_count": len(unique_geometries),
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
    dev_res = build_cohort_manifest()
    dev_path = root / ".private_cohort_manifest.json"
    dev_path.write_text(json.dumps(dev_res["manifest"], indent=2) + "\n", encoding="utf-8")

    conf_preview = build_confirmatory_manifest("dev-preview-only-not-sealed")
    print(
        f"Dev baseline manifest: total={dev_res['manifest']['total_scenario_cap']}, "
        f"policy_counts={dev_res['manifest']['policy_counts']}, "
        f"sha256={dev_res['manifest_sha256']}"
    )
    print(
        f"Confirmatory generator preview (dev salt): total={conf_preview['manifest']['total_scenario_cap']}, "
        f"unique_geometries={conf_preview['manifest']['unique_geometry_count']}, "
        f"policy_counts={conf_preview['manifest']['policy_counts']}"
    )


if __name__ == "__main__":
    main()
