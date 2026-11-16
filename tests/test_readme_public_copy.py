"""README headline wording guard (reviewer ruling, 2026-11-15)."""
import re
from pathlib import Path
from veap.governance.claims import check_public_copy

BASE = Path(__file__).resolve().parents[1]
FILES = ("README.md", "README_V06.md", "veap_studio_r03/web/index.html", "veap_studio_r03/web/app.js")


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
    body = (BASE / "veap_studio_r03/web/app.js").read_text(encoding="utf8")
    assert "independently evaluated trial" not in body
    assert "evaluated by a verifier separate from the agent" in body
