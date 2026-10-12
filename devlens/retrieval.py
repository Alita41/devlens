from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path
import numpy as np
from .models import Chunk, RetrievedChunk

TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\d+|[^\x00-\x7F]+")

class HashingEmbedder:
    def __init__(self, dim: int = 1024): self.dim = dim
    def encode_one(self, text: str):
        v = np.zeros(self.dim, dtype=np.float32)
        for token in TOKEN.findall((text or "").lower()):
            features = ["w:"+token]
            if len(token) >= 3:
                padded = "^"+token+"$"
                features += ["c:"+padded[i:i+3] for i in range(len(padded)-2)]
            for feature in features:
                raw = hashlib.blake2b(feature.encode(), digest_size=8).digest()
                x = int.from_bytes(raw, "little")
                v[x % self.dim] += -1.0 if x & (1<<63) else 1.0
        norm = float(np.linalg.norm(v))
        return v / norm if norm else v
    def encode(self, texts: list[str]):
        return np.vstack([self.encode_one(x) for x in texts]) if texts else np.empty((0,self.dim),dtype=np.float32)

class VectorIndex:
    def __init__(self, embedder: HashingEmbedder | None = None):
        self.embedder = embedder or HashingEmbedder(); self.chunks=[]; self.matrix=None; self.faiss_index=None
    @property
    def backend(self): return "faiss" if self.faiss_index is not None else "numpy"
    def build(self, chunks: list[Chunk]):
        self.chunks = list(chunks)
        self.matrix = self.embedder.encode([c.text for c in self.chunks]).astype(np.float32)
        try:
            import faiss
            idx = faiss.IndexFlatIP(self.matrix.shape[1])
            if len(self.matrix): idx.add(self.matrix)
            self.faiss_index = idx
        except ImportError:
            self.faiss_index = None
        return self
    def search(self, query: str, top_k: int = 5):
        if self.matrix is None: raise RuntimeError("index is not built")
        if not self.chunks or top_k <= 0: return []
        q = self.embedder.encode([query]).astype(np.float32); k=min(top_k,len(self.chunks))
        if self.faiss_index is not None:
            scores, ids = self.faiss_index.search(q,k); return [(int(i),float(s)) for i,s in zip(ids[0],scores[0]) if i>=0]
        scores = self.matrix @ q[0]; ids=np.argsort(-scores)[:k]; return [(int(i),float(scores[int(i)])) for i in ids]
    def save(self, path: str | Path):
        p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps({"dim":self.embedder.dim,"chunks":[c.to_dict() for c in self.chunks],"matrix":self.matrix.tolist()},ensure_ascii=False),encoding="utf-8")
    @classmethod
    def load(cls, path: str | Path):
        payload=json.loads(Path(path).read_text(encoding="utf-8")); obj=cls(HashingEmbedder(int(payload["dim"])))
        obj.chunks=[Chunk.from_dict(x) for x in payload["chunks"]]; obj.matrix=np.asarray(payload["matrix"],dtype=np.float32)
        return obj

def retrieve(index: VectorIndex, query: str, top_k: int = 5):
    return [RetrievedChunk(index.chunks[idx],score,rank,f"S{rank}") for rank,(idx,score) in enumerate(index.search(query,top_k),start=1)]
