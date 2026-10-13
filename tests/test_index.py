from devlens.models import Chunk
from devlens.retrieval.index import VectorIndex
from devlens.retrieval.retriever import retrieve


def test_retrieval_prefers_matching_chunk(tmp_path):
    chunks = [
        Chunk("1", "a", "search.py", "bm25 retrieval ranking search engine", 1, 1),
        Chunk("2", "b", "db.py", "postgres transaction database migration", 1, 1),
    ]
    idx = VectorIndex().build(chunks)
    rows = retrieve(idx, "search retrieval", 1)
    assert rows[0].chunk.path == "search.py"
    p = tmp_path / "idx.json"
    idx.save(p)
    loaded = VectorIndex.load(p)
    assert retrieve(loaded, "database postgres", 1)[0].chunk.path == "db.py"
