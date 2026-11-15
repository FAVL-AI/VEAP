"""README headline wording guard (reviewer ruling, 2026-11-15)."""
import re
from pathlib import Path
from veap.governance.claims import check_public_copy

BASE = Path(__file__).resolve().parents[1]
FILES = ("README.md", "README_V06.md")


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
    assert "'README.md'" in src and "'README_V06.md'" in src
    assert check_public_copy(BASE)["valid"]
