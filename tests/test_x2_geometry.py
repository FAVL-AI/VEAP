"""Tests for overlap-aware obstacle distance and clearance-range helpers."""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from veap.spec import Circle, Point, Rect, Scenario
from veap.verifier import (
    _clearance,
    _distance_to_rect,
    clearance_range_to_circle,
    clearance_range_to_rect,
    signed_distance_to_circle,
    signed_distance_to_rect,
)
from x2.geometry_stress_test import run_stress_test


def _make_scenario(robot_radius: float = 0.22, forbidden_zones: list[Rect] | None = None) -> Scenario:
    return Scenario(
        id="geom-test-1",
        title="Geometry test",
        description="Test scenario for signed clearance under overlap",
        family="navigation",
        split="test",
        width=10.0,
        height=10.0,
        robot_radius=robot_radius,
        start=Point(x=1.0, y=1.0, label="start"),
        waypoints=[Point(x=9.0, y=9.0, label="goal")],
        obstacles=[Circle(x=5.0, y=5.0, radius=1.0, label="pillar")],
        forbidden_zones=forbidden_zones or [],
    )


def test_signed_distance_to_circle():
    assert signed_distance_to_circle(3.0, 0.0, 0.0, 0.0, 1.0) == pytest.approx(2.0)
    assert signed_distance_to_circle(1.0, 0.0, 0.0, 0.0, 1.0) == pytest.approx(0.0)
    assert signed_distance_to_circle(0.4, 0.0, 0.0, 0.0, 1.0) == pytest.approx(-0.6)
    assert signed_distance_to_circle(0.0, 0.0, 0.0, 0.0, 1.0) == pytest.approx(-1.0)
    with pytest.raises(ValueError):
        signed_distance_to_circle(0.0, 0.0, 0.0, 0.0, 0.0)


def test_signed_distance_to_rect_and_legacy_helper():
    rect = {"x1": 2.0, "y1": 2.0, "x2": 6.0, "y2": 8.0}
    # Outside edge & corner
    assert signed_distance_to_rect(1.0, 5.0, rect) == pytest.approx(1.0)
    assert signed_distance_to_rect(0.0, 0.0, rect) == pytest.approx(math.hypot(2.0, 2.0))
    # On boundary
    assert signed_distance_to_rect(2.0, 5.0, rect) == pytest.approx(0.0)
    # Strictly inside: negative penetration depth, not clamped to 0
    assert signed_distance_to_rect(3.0, 5.0, rect) == pytest.approx(-1.0)
    assert signed_distance_to_rect(4.0, 5.0, rect) == pytest.approx(-2.0)
    # _distance_to_rect delegates to signed_distance_to_rect
    assert _distance_to_rect(4.0, 5.0, rect) == pytest.approx(-2.0)


def test_verifier_clearance_inside_forbidden_zone_and_tiny_robot():
    zone = Rect(x1=2.0, y1=2.0, x2=6.0, y2=6.0, label="keepout")
    # Normal robot deep inside keepout zone: clearance is -2.0 - 0.22 = -2.22
    s = _make_scenario(robot_radius=0.22, forbidden_zones=[zone])
    clearance, hazards = _clearance(4.0, 4.0, s)
    assert clearance == pytest.approx(-2.22)
    assert "forbidden zone: keepout" in hazards

    # Tiny robot (r <= EPS=0.0008) deep inside keepout zone must still trigger hazard
    s_tiny = _make_scenario(robot_radius=0.0005, forbidden_zones=[zone])
    clearance_tiny, hazards_tiny = _clearance(4.0, 4.0, s_tiny)
    assert clearance_tiny == pytest.approx(-2.0005)
    assert "forbidden zone: keepout" in hazards_tiny


def test_clearance_range_to_circle_overlap_and_uncertainty():
    # Clear case
    c_min, c_max = clearance_range_to_circle(4.0, 0.0, 0.0, 0.0, 1.0, robot_radius=0.2, pos_uncertainty=0.3)
    assert (c_min, c_max) == pytest.approx((2.5, 3.1))

    # Estimated center near obstacle center: uncertainty exceeds center distance
    # Minimum possible center distance is 0.0, not (0.1 - 0.5) = -0.4
    c_min, c_max = clearance_range_to_circle(0.1, 0.0, 0.0, 0.0, 1.0, robot_radius=0.2, pos_uncertainty=0.5)
    assert c_min == pytest.approx(-1.2)
    assert c_max == pytest.approx(-0.6)

    # Partial uncertainty overlap
    c_min, c_max = clearance_range_to_circle(1.4, 0.0, 0.0, 0.0, 1.0, robot_radius=0.2, pos_uncertainty=0.5)
    assert c_min < 0.0 <= c_max


def test_clearance_range_to_rect_overlap_and_uncertainty():
    rect = {"x1": 0.0, "y1": 0.0, "x2": 4.0, "y2": 4.0}
    # Deep inside rectangle: guaranteed overlap even with large uncertainty
    c_min, c_max = clearance_range_to_rect(2.0, 2.0, rect, robot_radius=0.2, pos_uncertainty=0.5)
    assert c_min == pytest.approx(-2.2)  # capped by inradius 2.0 + robot_radius 0.2
    assert c_max == pytest.approx(-1.5 - 0.2)

    # Outside rectangle, uncertainty reaches inside
    c_min, c_max = clearance_range_to_rect(-0.3, 2.0, rect, robot_radius=0.2, pos_uncertainty=0.5)
    assert c_min == pytest.approx(-0.4)
    assert c_max == pytest.approx(0.6)


def test_stress_runner_zero_errors_and_reconciliation_table():
    summary = run_stress_test(n_cases=2000, seed=12345)
    assert summary["fixed_errors"] == 0
    assert summary["naive_errors"] > 0
    assert summary["old_verifier_rect_errors"] > 0

    report_path = Path(__file__).resolve().parent.parent / "x2" / "geometry_stress_report.json"
    assert report_path.exists()
    report = json.loads(report_path.read_text())
    assert report["total_cases"] == 20000
    assert report["fixed_errors"] == 0
    assert report["fixed_error_rate"] == "0/20,000"
    assert report["naive_errors"] > 0
    assert report["old_verifier_rect_errors"] > 0

    table = report["reconciliation_table"]
    for shape in ("circle", "rect"):
        assert set(table[shape].keys()) == {"overlap", "non_overlap", "total"}
        for bucket_name in ("overlap", "non_overlap", "total"):
            bucket = table[shape][bucket_name]
            assert {
                "cases",
                "old_verifier_rect_errors",
                "naive_range_errors",
                "fixed_verifier_errors",
            } <= set(bucket.keys())
            assert bucket["fixed_verifier_errors"] == 0
        assert table[shape]["total"]["cases"] == (
            table[shape]["overlap"]["cases"] + table[shape]["non_overlap"]["cases"]
        )
        assert table[shape]["total"]["cases"] == 10000

    assert table["rect"]["overlap"]["old_verifier_rect_errors"] > 0
    assert table["overall"]["cases"] == 20000
    assert table["overall"]["fixed_verifier_errors"] == 0
