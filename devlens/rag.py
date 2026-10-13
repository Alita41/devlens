from __future__ import annotations
from devlens.citations import validate_citations
from devlens.models import Answer
from devlens.providers import get_provider
from devlens.retrieval.retriever import retrieve


def answer_question(index, question: str, top_k: int = 5, provider=None):
    evidence = retrieve(index, question, top_k=top_k)
    provider = provider or get_provider()
    text, citations = provider.answer(question, evidence)
    check = validate_citations(text, evidence)
    if not check["valid"]:
        raise ValueError(f"provider emitted invalid citations: {check['invalid']}")
    return Answer(text=text, citations=citations, evidence=evidence, provider=provider.name)
