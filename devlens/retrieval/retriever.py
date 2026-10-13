from __future__ import annotations
from devlens.models import RetrievedChunk
from devlens.retrieval.index import VectorIndex


def retrieve(index: VectorIndex, query: str, top_k: int = 5) -> list[RetrievedChunk]:
    rows = index.search(query, top_k=top_k)
    out = []
    for rank, (idx, score) in enumerate(rows, start=1):
        out.append(RetrievedChunk(chunk=index.chunks[idx], score=score, rank=rank, citation_id=f"S{rank}"))
    return out
