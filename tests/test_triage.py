import pytest
from devlens.approval import ApprovalGate, ApprovalRequired
from devlens.llm.local import LocalProvider
from devlens.triage import triage_issue


def test_triage_is_structured_and_requires_review():
    r = triage_issue("API returns 500", "traceback on empty query", provider=LocalProvider())
    assert r.category == "bug"
    assert r.severity == "high"
    assert r.needs_human_review is True


def test_approval_gate():
    with pytest.raises(ApprovalRequired):
        ApprovalGate().require(False, "comment on issue")
    assert ApprovalGate().require(True, "comment on issue") is True
