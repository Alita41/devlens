from __future__ import annotations
import re
from devlens.models import RetrievedChunk, TriageResult


class LocalProvider:
    name = "local-extractive"

    def answer(self, question: str, evidence: list[RetrievedChunk]):
        if not evidence:
            return "I could not find supporting evidence in the indexed sources.", []
        q_terms = set(re.findall(r"\w+", question.lower()))
        sentences = []
        for item in evidence:
            candidates = re.split(r"(?<=[.!?])\s+|\n+", item.chunk.text)
            scored = sorted(candidates, key=lambda s: len(q_terms & set(re.findall(r"\w+", s.lower()))), reverse=True)
            best = next((s.strip() for s in scored if s.strip()), item.chunk.text[:300].strip())
            sentences.append(f"{best} [{item.citation_id}]")
        return " ".join(sentences[:3]), [x.citation_id for x in evidence[:3]]

    def triage(self, title: str, body: str):
        text = f"{title} {body}".lower()
        if any(x in text for x in ["security", "vulnerability", "secret", "token leak"]):
            category, severity, component = "security", "high", "security"
        elif any(x in text for x in ["500", "crash", "exception", "traceback"]):
            category, severity, component = "bug", "high", "backend"
        elif any(x in text for x in ["slow", "latency", "timeout", "performance"]):
            category, severity, component = "performance", "medium", "backend"
        elif any(x in text for x in ["docs", "readme", "documentation"]):
            category, severity, component = "documentation", "low", "docs"
        else:
            category, severity, component = "bug", "medium", "unknown"
        return TriageResult(category, severity, component, 0.62, "Deterministic local heuristic; confirm before applying repository changes.", [category, f"severity:{severity}", f"area:{component}"], True)
