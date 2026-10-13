from __future__ import annotations
from devlens.citations import citation_coverage, validate_citations
from devlens.retrieval.retriever import retrieve


def recall_at_k(retrieved_paths: list[str], relevant_paths: set[str], k: int):
    if not relevant_paths:
        return 0.0
    return len(set(retrieved_paths[:k]) & relevant_paths) / len(relevant_paths)


def evaluate_queries(index, cases):
    rows = []
    for case in cases:
        evidence = retrieve(index, case["query"], case.get("k", 5))
        paths = [x.chunk.path for x in evidence]
        rows.append({"query": case["query"], "recall": recall_at_k(paths, set(case["relevant_paths"]), case.get("k", 5)), "retrieved": paths})
    return rows


def evaluate_answer(answer):
    return {
        "citation_coverage": citation_coverage(answer.text),
        "citation_validation": validate_citations(answer.text, answer.evidence),
    }
