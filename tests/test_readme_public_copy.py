"""README headline wording guard (reviewer ruling, 2026-11-15)."""
import re
from pathlib import Path
from veap.governance.claims import check_public_copy

BASE = Path(__file__).resolve().parents[1]
FILES = ("README.md", "README_V06.md", "web/index.html", "web/app.js")


def test_old_independent_verification_phrase_absent():
    for name in FILES:
        body = (BASE / name).read_text(encoding="utf8")
        assert not re.search(r"(?i)independent verification", body), f"{name} reintroduces 'independent verification'"


def test_readme_headline_uses_separate_verifier_wording():
    body = (BASE / "README.md").read_text(encoding="utf8")
    assert "failed verification by a verifier separate from the agent in 34 of 60 runs" in body
    headline = next(line for line in body.splitlines() if "34 of 60 runs" in line and "toy benchmark" in line)
    assert "agent-independent" not in headline


def test_public_copy_scan_covers_readmes_and_passes():
    import inspect
    src = inspect.getsource(check_public_copy)
    for name in FILES:
        assert f"'{name}'" in src, f"{name} missing from check_public_copy scan list"
    assert check_public_copy(BASE)["valid"]


def test_app_js_old_trial_phrase_absent():
    body = (BASE / "web/app.js").read_text(encoding="utf8")
    assert "independently evaluated trial" not in body
    assert "evaluated by a verifier separate from the agent" in body


def _scan_one(tmp_path, text):
    (tmp_path / "copy.md").write_text(text, encoding="utf8")
    return check_public_copy(tmp_path, files=["copy.md"])


def test_stale_v06_gate_count_phrase_rejected(tmp_path):
    import pytest
    for text in ("v0.6 release gate FAILED 18/20.", "the gate failed 18 / 20 (insp-07, insp-08)"):
        with pytest.raises(ValueError, match="ambiguous v0.6 gate count"):
            _scan_one(tmp_path, text)


def test_corrected_v06_gate_wording_accepted(tmp_path):
    text = ("release gate FAILED (gate_passed = false): 18 of 20 cross-engine pairs met the criteria; "
            "2 failed (insp-07, insp-08)\n## v0.6 replay — gate FAILED; 18 of 20 pairs passed, 2 failed\n")
    assert _scan_one(tmp_path, text)["valid"]


def test_v06_count_guard_ignores_historical_records():
    # The steplog and the step-5 forbidden-grep record keep the old phrase verbatim (append-only history);
    # they are not public copy, so the scan must still pass with them present.
    for name in ("logs/STEPLOG.md", "x1/step5/forbidden_grep.txt"):
        assert re.search(r"(?i)failed 18/20", (BASE / name).read_text(encoding="utf8")), name
    assert check_public_copy(BASE)["valid"]
    for name in FILES:
        assert not re.search(r"(?i)failed\s+18\s*/\s*20", (BASE / name).read_text(encoding="utf8")), name
