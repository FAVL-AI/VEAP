"""X1 seed-driven perturbation ladder (pre-registration v3, M2').

One 1-D ladder scales all four knobs together. Every random draw comes from a
per-knob stream derived from (seed, knob) via SHA-256, so the legacy
``random.Random(seed)`` stream used by scenario faults is never consumed here.
Level L0 is all-zero and reproduces the legacy trace digests exactly.
"""
from __future__ import annotations
import hashlib
import random
from dataclasses import dataclass, asdict

SCHEMA = "veap-x1-perturb/1"
SUITE_VERSION = "v0.7-x1"


@dataclass(frozen=True)
class Perturbation:
    level: str
    start_pose_sigma_m: float      # Gaussian sigma, per axis, on the start (x, y)
    obstacle_jitter_m: float       # uniform half-width, per axis, on each circular obstacle centre
    obs_noise_sigma_m: float       # Gaussian sigma, per axis, on every observed (x, y)
    actuation_dropout_p: float     # per-tick Bernoulli p that the applied command is zeroed

    def as_dict(self) -> dict:
        return {"schema": SCHEMA, "suite_version": SUITE_VERSION, **asdict(self)}


# Exactly the M2' table in X1_PREREG_v3.md (sha256 784382af...10c7).
LADDER: dict[str, Perturbation] = {
    "L0": Perturbation("L0", 0.0, 0.0, 0.0, 0.0),
    "L1": Perturbation("L1", 0.05, 0.05, 0.02, 0.05),
    "L2": Perturbation("L2", 0.10, 0.10, 0.05, 0.10),
    "L3": Perturbation("L3", 0.20, 0.20, 0.10, 0.15),
}

START_RESAMPLE_LIMIT = 1000


def stream(seed: int, knob: str) -> random.Random:
    h = hashlib.sha256(f"{SCHEMA}|seed={seed}|knob={knob}".encode()).digest()
    return random.Random(int.from_bytes(h[:8], "big"))


def perturb_scenario(s, p: Perturbation, seed: int):
    """Return (perturbed scenario, info). Obstacles jittered first, then a clear start is sampled."""
    from .sim import _clear  # local import avoids a cycle
    info = {"start_resamples": 0, "start_fallback_nominal": False}
    if p.obstacle_jitter_m > 0:
        r = stream(seed, "obstacle_jitter")
        obstacles = [o.model_copy(update={"x": round(o.x + r.uniform(-p.obstacle_jitter_m, p.obstacle_jitter_m), 6),
                                          "y": round(o.y + r.uniform(-p.obstacle_jitter_m, p.obstacle_jitter_m), 6)})
                     for o in s.obstacles]
        s = s.model_copy(update={"obstacles": obstacles})
    if p.start_pose_sigma_m > 0:
        r = stream(seed, "start_pose")
        for i in range(START_RESAMPLE_LIMIT):
            x = round(s.start.x + r.gauss(0.0, p.start_pose_sigma_m), 6)
            y = round(s.start.y + r.gauss(0.0, p.start_pose_sigma_m), 6)
            if 0 <= x <= s.width and 0 <= y <= s.height and _clear(s, x, y):
                s = s.model_copy(update={"start": s.start.model_copy(update={"x": x, "y": y})})
                info["start_resamples"] = i
                break
        else:
            info["start_fallback_nominal"] = True
    # Re-validate the contract so the perturbed scenario is a legal immutable Scenario.
    s = type(s).model_validate(s.model_dump(mode="json", exclude_none=True))
    return s, info
