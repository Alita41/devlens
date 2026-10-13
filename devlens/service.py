from __future__ import annotations
from pathlib import Path
from devlens.ingestion.local import ingest_local
from devlens.ingestion.github import GitHubIngestor
from devlens.ingestion.chunking import chunk_documents
from devlens.retrieval.index import VectorIndex


def build_local_index(path: str, out: str):
    docs = ingest_local(path)
    chunks = chunk_documents(docs)
    idx = VectorIndex().build(chunks)
    idx.save(out)
    return {"documents": len(docs), "chunks": len(chunks), "backend": idx.backend, "index_path": str(Path(out))}


def build_github_index(
    repo: str, out: str, include_issues: bool = True, include_prs: bool = True
):
    gh = GitHubIngestor()
    docs = gh.ingest_repo(repo)
    if include_issues:
        docs.extend(gh.ingest_issues(repo))
    if include_prs:
        docs.extend(gh.ingest_pull_requests(repo))
    chunks = chunk_documents(docs)
    idx = VectorIndex().build(chunks)
    idx.save(out)
    return {"documents": len(docs), "chunks": len(chunks), "backend": idx.backend, "index_path": str(Path(out))}
