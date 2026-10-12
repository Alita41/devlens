from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any

@dataclass(frozen=True)
class SourceDocument:
    source_id: str
    path: str
    text: str
    kind: str = "file"
    url: str | None = None
    metadata: dict[str, Any] | None = None

@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    source_id: str
    path: str
    text: str
    start_line: int
    end_line: int
    url: str | None = None
    def to_dict(self): return asdict(self)
    @classmethod
    def from_dict(cls, data): return cls(**data)

@dataclass(frozen=True)
class RetrievedChunk:
    chunk: Chunk
    score: float
    rank: int
    citation_id: str

@dataclass(frozen=True)
class Answer:
    text: str
    citations: list[str]
    evidence: list[RetrievedChunk]
    provider: str

@dataclass(frozen=True)
class TriageResult:
    category: str
    severity: str
    component: str
    confidence: float
    rationale: str
    suggested_labels: list[str]
    needs_human_review: bool = True
