from __future__ import annotations
import hashlib
import re
import numpy as np

TOKEN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*|\d+|[^\x00-\x7F]+")


class HashingEmbedder:
    """Deterministic local embedding for offline/reproducible retrieval tests."""
    def __init__(self, dim: int = 1024):
        self.dim = dim

    @staticmethod
    def _hash(feature: str):
        b = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
        x = int.from_bytes(b, "little")
        return x, -1.0 if x & (1 << 63) else 1.0

    def encode_one(self, text: str) -> np.ndarray:
        tokens = TOKEN.findall((text or "").lower())
        v = np.zeros(self.dim, dtype=np.float32)
        feats = []
        for t in tokens:
            feats.append("w:" + t)
            if len(t) >= 3:
                padded = "^" + t + "$"
                feats.extend("c:" + padded[i:i+3] for i in range(len(padded)-2))
        for feat in feats:
            h, sign = self._hash(feat)
            v[h % self.dim] += sign
        norm = float(np.linalg.norm(v))
        return v / norm if norm else v

    def encode(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, self.dim), dtype=np.float32)
        return np.vstack([self.encode_one(x) for x in texts])
