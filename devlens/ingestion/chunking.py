from __future__ import annotations
from devlens.models import SourceDocument, Chunk


def _fallback_chunks(text: str, max_chars: int = 1800, overlap_lines: int = 4):
    lines = text.splitlines()
    if not lines:
        return []
    out = []
    start = 0
    while start < len(lines):
        end = start
        size = 0
        while end < len(lines) and (size + len(lines[end]) + 1 <= max_chars or end == start):
            size += len(lines[end]) + 1
            end += 1
        out.append((start + 1, end, "\n".join(lines[start:end])))
        if end >= len(lines):
            break
        start = max(start + 1, end - overlap_lines)
    return out


def chunk_documents(docs: list[SourceDocument], max_chars: int = 1800) -> list[Chunk]:
    chunks = []
    for doc in docs:
        split_rows = None
        try:
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            splitter = RecursiveCharacterTextSplitter(chunk_size=max_chars, chunk_overlap=min(240, max_chars // 6), add_start_index=True)
            split_rows = []
            lines = doc.text.splitlines()
            for part in splitter.create_documents([doc.text]):
                text = part.page_content
                char_start = int(part.metadata.get("start_index", 0))
                start_line = doc.text[:char_start].count("\n") + 1
                end_line = start_line + text.count("\n")
                split_rows.append((start_line, end_line, text))
        except ImportError:
            split_rows = _fallback_chunks(doc.text, max_chars=max_chars)

        for i, (start, end, text) in enumerate(split_rows):
            cid = f"{doc.source_id}#chunk-{i}"
            chunks.append(Chunk(chunk_id=cid, source_id=doc.source_id, path=doc.path, text=text, start_line=start, end_line=end, url=doc.url))
    return chunks
