from __future__ import annotations
from devlens.providers import get_provider


def triage_issue(title: str, body: str, provider=None):
    provider = provider or get_provider()
    result = provider.triage(title, body)
    if not 0 <= result.confidence <= 1:
        raise ValueError("triage confidence must be in [0,1]")
    if not result.needs_human_review:
        raise ValueError("DevLens requires human review for issue actions")
    return result
