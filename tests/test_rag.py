from devlens.citations import validate_citations
from devlens.llm.local import LocalProvider
from devlens.models import Chunk
from devlens.rag import answer_question
from devlens.retrieval.index import VectorIndex


def test_local_rag_emits_valid_citations():
    idx = VectorIndex().build([Chunk("1", "a", "approval.py", "Writes require explicit human approval before execution.", 1, 1)])
    ans = answer_question(idx, "Do writes require approval?", provider=LocalProvider())
    assert "[S1]" in ans.text
    assert validate_citations(ans.text, ans.evidence)["valid"]
