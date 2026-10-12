from pathlib import Path
from .ingestion import ingest_local, chunk_documents, GitHubIngestor
from .retrieval import VectorIndex

def build_local_index(path: str, out: str):
    docs=ingest_local(path); chunks=chunk_documents(docs); idx=VectorIndex().build(chunks); idx.save(out)
    return {"documents":len(docs),"chunks":len(chunks),"backend":idx.backend,"index_path":str(Path(out))}

def build_github_index(repo: str, out: str, include_issues: bool=True):
    gh=GitHubIngestor(); docs=gh.ingest_repo(repo); docs.extend(gh.ingest_issues(repo) if include_issues else []); chunks=chunk_documents(docs); idx=VectorIndex().build(chunks); idx.save(out)
    return {"documents":len(docs),"chunks":len(chunks),"backend":idx.backend,"index_path":str(Path(out))}
