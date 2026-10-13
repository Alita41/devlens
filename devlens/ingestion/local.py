from __future__ import annotations
from pathlib import Path
from devlens.models import SourceDocument

DEFAULT_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".cpp", ".cc", ".c", ".h", ".hpp",
    ".go", ".rs", ".rb", ".php", ".md", ".txt", ".rst", ".toml", ".yaml", ".yml", ".json",
}
SKIP_DIRS = {".git", ".venv", "node_modules", "dist", "build", "__pycache__", ".pytest_cache"}


def ingest_local(path: str | Path, max_file_bytes: int = 250_000) -> list[SourceDocument]:
    root = Path(path).resolve()
    if not root.exists():
        raise FileNotFoundError(root)
    files = [root] if root.is_file() else sorted(p for p in root.rglob("*") if p.is_file())
    docs = []
    for file in files:
        if any(part in SKIP_DIRS for part in file.parts):
            continue
        if file.suffix.lower() not in DEFAULT_EXTENSIONS and file.name not in {"Dockerfile", "Makefile"}:
            continue
        try:
            if file.stat().st_size > max_file_bytes:
                continue
            text = file.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        rel = str(file.relative_to(root if root.is_dir() else root.parent))
        docs.append(SourceDocument(source_id=f"local:{rel}", path=rel, text=text, kind="file"))
    return docs
