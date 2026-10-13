from __future__ import annotations
import base64
import os
from urllib.parse import quote
import httpx
from devlens.models import SourceDocument
from devlens.ingestion.local import DEFAULT_EXTENSIONS


class GitHubIngestor:
    def __init__(self, token: str | None = None, timeout: float = 20.0):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.timeout = timeout

    @property
    def headers(self):
        h = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    def _get(self, url: str):
        with httpx.Client(timeout=self.timeout, headers=self.headers, follow_redirects=True) as client:
            r = client.get(url)
            r.raise_for_status()
            return r.json()

    def ingest_repo(self, repo: str, ref: str | None = None, max_files: int = 300) -> list[SourceDocument]:
        meta = self._get(f"https://api.github.com/repos/{repo}")
        ref = ref or meta.get("default_branch", "main")
        tree = self._get(f"https://api.github.com/repos/{repo}/git/trees/{quote(ref, safe='')}?recursive=1")
        docs = []
        for item in tree.get("tree", []):
            if len(docs) >= max_files:
                break
            if item.get("type") != "blob":
                continue
            path = item.get("path", "")
            suffix = "." + path.rsplit(".", 1)[-1].lower() if "." in path else ""
            if suffix not in DEFAULT_EXTENSIONS and path.rsplit("/", 1)[-1] not in {"Dockerfile", "Makefile"}:
                continue
            if item.get("size", 0) > 250_000:
                continue
            payload = self._get(f"https://api.github.com/repos/{repo}/contents/{quote(path, safe='/')}?ref={quote(ref, safe='')}")
            if payload.get("encoding") != "base64":
                continue
            try:
                text = base64.b64decode(payload["content"]).decode("utf-8")
            except Exception:
                continue
            url = f"https://github.com/{repo}/blob/{ref}/{path}"
            docs.append(SourceDocument(source_id=f"github:{repo}:{path}", path=path, text=text, kind="github_file", url=url, metadata={"repo": repo, "ref": ref}))
        return docs

    def ingest_issues(self, repo: str, state: str = "open", limit: int = 100) -> list[SourceDocument]:
        issues = self._get(f"https://api.github.com/repos/{repo}/issues?state={state}&per_page={min(limit,100)}")
        docs = []
        for issue in issues[:limit]:
            if "pull_request" in issue:
                continue
            number = issue["number"]
            text = f"# {issue.get('title','')}\n\n{issue.get('body') or ''}"
            docs.append(SourceDocument(source_id=f"github:{repo}:issue:{number}", path=f"issues/{number}.md", text=text, kind="github_issue", url=issue.get("html_url"), metadata={"number": number, "state": issue.get("state")}))
        return docs

    def ingest_pull_requests(self, repo: str, state: str = "open", limit: int = 100) -> list[SourceDocument]:
        """Index PR descriptions; diffs and review threads are intentionally out of scope."""
        limit = max(0, min(limit, 100))
        if limit == 0:
            return []
        pulls = self._get(
            f"https://api.github.com/repos/{repo}/pulls?state={state}&per_page={limit}"
        )
        docs = []
        for pull in pulls[:limit]:
            number = pull["number"]
            title = pull.get("title", "")
            body = pull.get("body") or ""
            text = f"# {title}\n\n{body}"
            docs.append(
                SourceDocument(
                    source_id=f"github:{repo}:pr:{number}",
                    path=f"pulls/{number}.md",
                    text=text,
                    kind="github_pull_request",
                    url=pull.get("html_url"),
                    metadata={"number": number, "state": pull.get("state")},
                )
            )
        return docs
