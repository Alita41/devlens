from __future__ import annotations
import base64
import os
from pathlib import Path
from urllib.parse import quote
import httpx
from .models import SourceDocument, Chunk

EXTENSIONS = {".py",".js",".ts",".tsx",".jsx",".java",".cpp",".cc",".c",".h",".hpp",".go",".rs",".rb",".php",".md",".txt",".rst",".toml",".yaml",".yml",".json"}
SKIP_DIRS = {".git",".venv","node_modules","dist","build","__pycache__",".pytest_cache"}

def ingest_local(path: str | Path, max_file_bytes: int = 250_000) -> list[SourceDocument]:
    root = Path(path).resolve()
    if not root.exists(): raise FileNotFoundError(root)
    files = [root] if root.is_file() else sorted(p for p in root.rglob("*") if p.is_file())
    docs = []
    for file in files:
        if any(part in SKIP_DIRS for part in file.parts): continue
        if file.suffix.lower() not in EXTENSIONS and file.name not in {"Dockerfile","Makefile"}: continue
        try:
            if file.stat().st_size > max_file_bytes: continue
            text = file.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        rel = str(file.relative_to(root if root.is_dir() else root.parent))
        docs.append(SourceDocument(f"local:{rel}", rel, text))
    return docs

def chunk_documents(docs: list[SourceDocument], max_chars: int = 1800, overlap_lines: int = 4) -> list[Chunk]:
    chunks = []
    for doc in docs:
        lines = doc.text.splitlines()
        start = 0
        i = 0
        while start < len(lines):
            end, size = start, 0
            while end < len(lines) and (size + len(lines[end]) + 1 <= max_chars or end == start):
                size += len(lines[end]) + 1
                end += 1
            text = "\n".join(lines[start:end])
            chunks.append(Chunk(f"{doc.source_id}#chunk-{i}", doc.source_id, doc.path, text, start+1, end, doc.url))
            if end >= len(lines): break
            start = max(start + 1, end - overlap_lines)
            i += 1
    return chunks

class GitHubIngestor:
    def __init__(self, token: str | None = None, timeout: float = 20.0):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.timeout = timeout
    @property
    def headers(self):
        h = {"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28"}
        if self.token: h["Authorization"] = f"Bearer {self.token}"
        return h
    def _get(self, url: str):
        with httpx.Client(timeout=self.timeout, headers=self.headers, follow_redirects=True) as client:
            r = client.get(url); r.raise_for_status(); return r.json()
    def ingest_repo(self, repo: str, ref: str | None = None, max_files: int = 300):
        meta = self._get(f"https://api.github.com/repos/{repo}")
        ref = ref or meta.get("default_branch", "main")
        tree = self._get(f"https://api.github.com/repos/{repo}/git/trees/{quote(ref, safe='')}?recursive=1")
        docs = []
        for item in tree.get("tree", []):
            if len(docs) >= max_files: break
            if item.get("type") != "blob": continue
            path = item.get("path", "")
            suffix = "." + path.rsplit(".",1)[-1].lower() if "." in path else ""
            if suffix not in EXTENSIONS and path.rsplit("/",1)[-1] not in {"Dockerfile","Makefile"}: continue
            if item.get("size",0) > 250_000: continue
            payload = self._get(f"https://api.github.com/repos/{repo}/contents/{quote(path,safe='/')}?ref={quote(ref,safe='')}")
            if payload.get("encoding") != "base64": continue
            try: text = base64.b64decode(payload["content"]).decode("utf-8")
            except Exception: continue
            docs.append(SourceDocument(f"github:{repo}:{path}", path, text, "github_file", f"https://github.com/{repo}/blob/{ref}/{path}", {"repo":repo,"ref":ref}))
        return docs
    def ingest_issues(self, repo: str, state: str = "open", limit: int = 100):
        issues = self._get(f"https://api.github.com/repos/{repo}/issues?state={state}&per_page={min(limit,100)}")
        return [SourceDocument(f"github:{repo}:issue:{i['number']}", f"issues/{i['number']}.md", f"# {i.get('title','')}\n\n{i.get('body') or ''}", "github_issue", i.get("html_url")) for i in issues[:limit] if "pull_request" not in i]
