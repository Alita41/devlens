from __future__ import annotations
import json
import tempfile
from pathlib import Path
from devlens.ingestion.local import ingest_local
from devlens.ingestion.chunking import chunk_documents
from devlens.retrieval.index import VectorIndex
from devlens.rag import answer_question
from devlens.evals import evaluate_queries, evaluate_answer
from devlens.llm.local import LocalProvider


def main():
    root = Path(__file__).resolve().parents[1]
    docs = ingest_local(root / "eval/fixture_repo")
    idx = VectorIndex().build(chunk_documents(docs, max_chars=800))
    cases = json.loads((root / "eval/cases.json").read_text())
    retrieval = evaluate_queries(idx, cases)
    answer = answer_question(idx, "Where is human approval enforced?", top_k=3, provider=LocalProvider())
    result = {"retrieval": retrieval, "answer": evaluate_answer(answer)}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
