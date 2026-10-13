from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from devlens.models import Chunk
from devlens.retrieval.embeddings import HashingEmbedder


class VectorIndex:
    def __init__(self, embedder: HashingEmbedder | None = None):
        self.embedder = embedder or HashingEmbedder()
        self.chunks: list[Chunk] = []
        self.matrix: np.ndarray | None = None
        self.faiss_index = None

    @property
    def backend(self):
        return "faiss" if self.faiss_index is not None else "numpy"

    def build(self, chunks: list[Chunk]):
        self.chunks = list(chunks)
        self.matrix = self.embedder.encode([c.text for c in self.chunks]).astype(np.float32)
        try:
            import faiss
            idx = faiss.IndexFlatIP(self.matrix.shape[1])
            if len(self.matrix):
                idx.add(self.matrix)
            self.faiss_index = idx
        except ImportError:
            self.faiss_index = None
        return self

    def search(self, query: str, top_k: int = 5):
        if self.matrix is None:
            raise RuntimeError("index is not built")
        if not self.chunks or top_k <= 0:
            return []
        q = self.embedder.encode([query]).astype(np.float32)
        k = min(top_k, len(self.chunks))
        if self.faiss_index is not None:
            scores, ids = self.faiss_index.search(q, k)
            return [(int(i), float(s)) for i, s in zip(ids[0], scores[0]) if i >= 0]
        scores = self.matrix @ q[0]
        ids = np.argsort(-scores)[:k]
        return [(int(i), float(scores[int(i)])) for i in ids]

    def save(self, path: str | Path):
        if self.matrix is None:
            raise RuntimeError("index is not built")
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "dim": self.embedder.dim,
            "chunks": [c.to_dict() for c in self.chunks],
            "matrix": self.matrix.tolist(),
        }
        p.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path):
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        obj = cls(HashingEmbedder(dim=int(payload["dim"])))
        obj.chunks = [Chunk.from_dict(x) for x in payload["chunks"]]
        obj.matrix = np.asarray(payload["matrix"], dtype=np.float32)
        try:
            import faiss
            idx = faiss.IndexFlatIP(obj.matrix.shape[1])
            if len(obj.matrix):
                idx.add(obj.matrix)
            obj.faiss_index = idx
        except ImportError:
            obj.faiss_index = None
        return obj
