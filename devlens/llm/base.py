from __future__ import annotations
from typing import Protocol
from devlens.models import RetrievedChunk, TriageResult


class LLMProvider(Protocol):
    name: str
    def answer(self, question: str, evidence: list[RetrievedChunk]) -> tuple[str, list[str]]: ...
    def triage(self, title: str, body: str) -> TriageResult: ...
