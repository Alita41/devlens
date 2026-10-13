from __future__ import annotations
import re
from devlens.models import RetrievedChunk


def validate_citations(text: str, evidence: list[RetrievedChunk]):
    used = set(re.findall(r"\[(S\d+)\]", text))
    valid = {e.citation_id for e in evidence}
    invalid = sorted(used - valid)
    return {"valid": not invalid, "used": sorted(used), "invalid": invalid, "available": sorted(valid)}


def citation_coverage(text: str):
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    if not sentences:
        return 0.0
    cited = sum(bool(re.search(r"\[S\d+\]", s)) for s in sentences)
    return cited / len(sentences)
