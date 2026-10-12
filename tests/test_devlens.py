import pytest
from devlens.models import SourceDocument, Chunk
from devlens.ingestion import chunk_documents
from devlens.retrieval import VectorIndex, retrieve
from devlens.assistant import LocalProvider, answer_question, validate_citations, triage_issue, ApprovalGate, ApprovalRequired

def test_chunking_preserves_lines():
    chunks=chunk_documents([SourceDocument("x","a.py","a\nb\nc\nd\ne\n")],max_chars=5); assert chunks[0].start_line==1

def test_retrieval_and_persistence(tmp_path):
    idx=VectorIndex().build([Chunk("1","a","search.py","bm25 retrieval search",1,1),Chunk("2","b","db.py","postgres database",1,1)])
    assert retrieve(idx,"search retrieval",1)[0].chunk.path=="search.py"
    p=tmp_path/"i.json"; idx.save(p); assert retrieve(VectorIndex.load(p),"database postgres",1)[0].chunk.path=="db.py"

def test_rag_citations():
    idx=VectorIndex().build([Chunk("1","a","approval.py","Writes require explicit human approval before execution.",1,1)])
    ans=answer_question(idx,"Do writes require approval?",provider=LocalProvider()); assert "[S1]" in ans.text; assert validate_citations(ans.text,ans.evidence)["valid"]

def test_triage_and_approval():
    r=triage_issue("API returns 500","traceback on empty query",provider=LocalProvider()); assert r.category=="bug" and r.severity=="high" and r.needs_human_review
    with pytest.raises(ApprovalRequired): ApprovalGate().require(False,"comment on issue")
