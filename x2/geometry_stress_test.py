"""Reproducible 20,000-case stress test for overlap-aware obstacle distance ranges.

Runs three comparators on the exact same seeded 20,000 cases against the exact
same reference clearances:
  1. ``old_verifier_rect``: legacy ``veap/verifier.py`` ``_distance_to_rect``
     (returns 0.0 inside rectangles) with ``[nom - u, nom + u]`` range.
  2. ``naive_range``: naive zero-clamped clearance range
     (``max(0.0, unsigned_d - robot_radius - pos_uncertainty)``).
  3. ``fixed_verifier``: corrected ``veap/verifier.py`` helpers
     (``clearance_range_to_circle`` and ``clearance_range_to_rect``).
"""
from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from veap.verifier import (
    clearance_range_to_circle,
    clearance_range_to_rect,
    signed_distance_to_circle,
    signed_distance_to_rect,
)

TOTAL_CASES = 20_000
SEED = 20261116
TOL = 1e-12
REPORT_PATH = Path(__file__).resolve().parent / "geometry_stress_report.json"

COMPARATORS = ("old_verifier_rect", "naive_range", "fixed_verifier")


def old_verifier_circle_range(
    x: float,
    y: float,
    cx: float,
    cy: float,
    obstacle_radius: float,
    robot_radius: float,
    pos_uncertainty: float,
) -> tuple[float, float]:
    """Legacy circle clearance without lower-bound 0-clamp on center distance."""
    nom = math.hypot(x - cx, y - cy) - obstacle_radius - robot_radius
    return nom - pos_uncertainty, nom + pos_uncertainty


def old_verifier_rect_range(
    x: float,
    y: float,
    r: dict,
    robot_radius: float,
    pos_uncertainty: float,
) -> tuple[float, float]:
    """Legacy veap/verifier.py _distance_to_rect (0.0 inside rect) + [nom - u, nom + u]."""
    dx = max(r["x1"] - x, 0.0, x - r["x2"])
    dy = max(r["y1"] - y, 0.0, y - r["y2"])
    nom = math.hypot(dx, dy) - robot_radius
    return nom - pos_uncertainty, nom + pos_uncertainty


def naive_circle_clearance_range(
    x: float,
    y: float,
    cx: float,
    cy: float,
    obstacle_radius: float,
    robot_radius: float,
    pos_uncertainty: float,
) -> tuple[float, float]:
    """Naive range: unsigned obstacle distance + zero-clamped lower bound."""
    unsigned_d = max(0.0, math.hypot(x - cx, y - cy) - obstacle_radius)
    nom = unsigned_d - robot_radius
    return max(0.0, nom - pos_uncertainty), nom + pos_uncertainty


def naive_rect_clearance_range(
    x: float,
    y: float,
    r: dict,
    robot_radius: float,
    pos_uncertainty: float,
) -> tuple[float, float]:
    """Naive range: unsigned rect distance + zero-clamped lower bound."""
    dx = max(r["x1"] - x, 0.0, x - r["x2"])
    dy = max(r["y1"] - y, 0.0, y - r["y2"])
    unsigned_d = math.hypot(dx, dy)
    nom = unsigned_d - robot_radius
    return max(0.0, nom - pos_uncertainty), nom + pos_uncertainty


def _sample_disk_points(
    rng: random.Random, x: float, y: float, u: float, n_random: int = 8
) -> list[tuple[float, float]]:
    pts = [(x, y)]
    if u == 0.0:
        return pts
    for k in range(8):
        ang = k * math.pi / 4.0
        pts.append((x + u * math.cos(ang), y + u * math.sin(ang)))
    for _ in range(n_random):
        ang = rng.uniform(0.0, 2.0 * math.pi)
        rad = u * math.sqrt(rng.random())
        pts.append((x + rad * math.cos(ang), y + rad * math.sin(ang)))
    return pts


def _check_case(
    c_min: float,
    c_max: float,
    true_clearances: list[float],
) -> str | None:
    if c_min > c_max + TOL:
        return "inverted_range"
    for c_true in true_clearances:
        if c_true < c_min - TOL:
            return "lower_bound_violated"
        if c_true > c_max + TOL:
            return "upper_bound_violated"
        if c_true < -TOL and c_min >= 0.0:
            return "missed_overlap"
    if c_max < -TOL and any(c_true >= 0.0 for c_true in true_clearances):
        return "false_guaranteed_overlap"
    if c_min >= 0.0 and any(c_true < -TOL for c_true in true_clearances):
        return "false_guaranteed_clear"
    return None


def _empty_bucket() -> dict[str, int]:
    return {
        "cases": 0,
        "old_verifier_rect_errors": 0,
        "naive_range_errors": 0,
        "fixed_verifier_errors": 0,
    }


def run_stress_test(n_cases: int = TOTAL_CASES, seed: int = SEED) -> dict:
    rng = random.Random(seed)
    circle_cases = n_cases // 2
    rect_cases = n_cases - circle_cases

    table = {
        "circle": {"overlap": _empty_bucket(), "non_overlap": _empty_bucket()},
        "rect": {"overlap": _empty_bucket(), "non_overlap": _empty_bucket()},
    }
    breakdowns: dict[str, dict[str, int]] = {name: {} for name in COMPARATORS}

    for idx in range(n_cases):
        is_circle = idx < circle_cases
        shape = "circle" if is_circle else "rect"
        robot_radius = rng.uniform(0.05, 0.6)
        pos_uncertainty = rng.uniform(0.0, 1.5)

        if is_circle:
            cx = rng.uniform(-5.0, 5.0)
            cy = rng.uniform(-5.0, 5.0)
            obs_r = rng.uniform(0.2, 3.0)
            if rng.random() < 0.6:
                ang = rng.uniform(0.0, 2.0 * math.pi)
                dist = rng.uniform(0.0, obs_r + robot_radius + pos_uncertainty + 0.1)
                x = cx + dist * math.cos(ang)
                y = cy + dist * math.sin(ang)
            else:
                x = rng.uniform(-8.0, 8.0)
                y = rng.uniform(-8.0, 8.0)

            samples = _sample_disk_points(rng, x, y, pos_uncertainty)
            d_c = math.hypot(x - cx, y - cy)
            if d_c > 0.0 and pos_uncertainty > 0.0:
                ux, uy = (x - cx) / d_c, (y - cy) / d_c
                samples.append((x + pos_uncertainty * ux, y + pos_uncertainty * uy))
                step_in = min(pos_uncertainty, d_c)
                samples.append((x - step_in * ux, y - step_in * uy))

            true_clearances = [
                signed_distance_to_circle(px, py, cx, cy, obs_r) - robot_radius
                for px, py in samples
            ]
            ranges = {
                "old_verifier_rect": old_verifier_circle_range(
                    x, y, cx, cy, obs_r, robot_radius, pos_uncertainty
                ),
                "naive_range": naive_circle_clearance_range(
                    x, y, cx, cy, obs_r, robot_radius, pos_uncertainty
                ),
                "fixed_verifier": clearance_range_to_circle(
                    x, y, cx, cy, obs_r, robot_radius, pos_uncertainty
                ),
            }
        else:
            x1 = rng.uniform(-5.0, 2.0)
            y1 = rng.uniform(-5.0, 2.0)
            w = rng.uniform(0.3, 5.0)
            h = rng.uniform(0.3, 5.0)
            rect = {"x1": x1, "y1": y1, "x2": x1 + w, "y2": y1 + h}
            if rng.random() < 0.6:
                pad = robot_radius + pos_uncertainty + 0.1
                x = rng.uniform(x1 - pad, x1 + w + pad)
                y = rng.uniform(y1 - pad, y1 + h + pad)
            else:
                x = rng.uniform(-8.0, 8.0)
                y = rng.uniform(-8.0, 8.0)

            samples = _sample_disk_points(rng, x, y, pos_uncertainty)
            true_clearances = [
                signed_distance_to_rect(px, py, rect) - robot_radius
                for px, py in samples
            ]
            ranges = {
                "old_verifier_rect": old_verifier_rect_range(
                    x, y, rect, robot_radius, pos_uncertainty
                ),
                "naive_range": naive_rect_clearance_range(
                    x, y, rect, robot_radius, pos_uncertainty
                ),
                "fixed_verifier": clearance_range_to_rect(
                    x, y, rect, robot_radius, pos_uncertainty
                ),
            }

        overlap_key = "overlap" if any(c < 0.0 for c in true_clearances) else "non_overlap"
        bucket = table[shape][overlap_key]
        bucket["cases"] += 1

        for name in COMPARATORS:
            c_min, c_max = ranges[name]
            err = _check_case(c_min, c_max, true_clearances)
            if err is not None:
                bucket[f"{name}_errors"] += 1
                breakdowns[name][err] = breakdowns[name].get(err, 0) + 1

    for shape in ("circle", "rect"):
        ov = table[shape]["overlap"]
        no = table[shape]["non_overlap"]
        table[shape]["total"] = {
            "cases": ov["cases"] + no["cases"],
            "old_verifier_rect_errors": ov["old_verifier_rect_errors"] + no["old_verifier_rect_errors"],
            "naive_range_errors": ov["naive_range_errors"] + no["naive_range_errors"],
            "fixed_verifier_errors": ov["fixed_verifier_errors"] + no["fixed_verifier_errors"],
        }

    c_tot = table["circle"]["total"]
    r_tot = table["rect"]["total"]
    overlap_cases = table["circle"]["overlap"]["cases"] + table["rect"]["overlap"]["cases"]
    non_overlap_cases = table["circle"]["non_overlap"]["cases"] + table["rect"]["non_overlap"]["cases"]
    overall = {
        "cases": n_cases,
        "overlap_cases": overlap_cases,
        "non_overlap_cases": non_overlap_cases,
        "old_verifier_rect_errors": c_tot["old_verifier_rect_errors"] + r_tot["old_verifier_rect_errors"],
        "naive_range_errors": c_tot["naive_range_errors"] + r_tot["naive_range_errors"],
        "fixed_verifier_errors": c_tot["fixed_verifier_errors"] + r_tot["fixed_verifier_errors"],
    }
    table["overall"] = overall

    return {
        "seed": seed,
        "total_cases": n_cases,
        "circle_cases": circle_cases,
        "rect_cases": rect_cases,
        "overlap_cases": overlap_cases,
        "non_overlap_cases": non_overlap_cases,
        "old_verifier_rect_errors": overall["old_verifier_rect_errors"],
        "old_verifier_rect_error_rate": f"{overall['old_verifier_rect_errors']}/{n_cases:,}",
        "naive_errors": overall["naive_range_errors"],
        "naive_error_rate": f"{overall['naive_range_errors']}/{n_cases:,}",
        "fixed_errors": overall["fixed_verifier_errors"],
        "fixed_error_rate": f"{overall['fixed_verifier_errors']}/{n_cases:,}",
        "breakdowns": breakdowns,
        "reconciliation_table": table,
    }


def format_reconciliation_table(report: dict) -> str:
    t = report["reconciliation_table"]
    rows = [
        ("circle / overlap", t["circle"]["overlap"]),
        ("circle / non_overlap", t["circle"]["non_overlap"]),
        ("circle / total", t["circle"]["total"]),
        ("rect / overlap", t["rect"]["overlap"]),
        ("rect / non_overlap", t["rect"]["non_overlap"]),
        ("rect / total", t["rect"]["total"]),
        ("overall", t["overall"]),
    ]
    header = (
        f"{'Slice':<22} | {'Cases':>7} | {'old_verifier_rect':>17} | "
        f"{'naive_range':>11} | {'fixed_verifier':>14}"
    )
    sep = "-" * len(header)
    lines = [header, sep]
    for label, row in rows:
        lines.append(
            f"{label:<22} | {row['cases']:>7,} | "
            f"{row['old_verifier_rect_errors']:>17,} | "
            f"{row['naive_range_errors']:>11,} | "
            f"{row['fixed_verifier_errors']:>14,}"
        )
    return "\n".join(lines)


def main() -> int:
    report = run_stress_test()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(format_reconciliation_table(report))
    print(f"Report written to {REPORT_PATH}")
    return 0 if report["fixed_errors"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
