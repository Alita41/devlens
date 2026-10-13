from devlens.ingestion.chunking import chunk_documents
from devlens.models import SourceDocument


def test_chunking_preserves_line_ranges():
    doc = SourceDocument("x", "a.py", "a\nb\nc\nd\ne\n")
    chunks = chunk_documents([doc], max_chars=5)
    assert chunks
    assert chunks[0].start_line == 1
    assert chunks[0].end_line >= chunks[0].start_line
