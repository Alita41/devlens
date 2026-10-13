from devlens.ingestion.github import GitHubIngestor
from devlens.service import build_github_index


def test_pull_request_descriptions_are_ingested_without_misrepresenting_diffs(monkeypatch):
    ingestor = GitHubIngestor()

    def fake_get(url):
        assert "/pulls?" in url
        return [{"number": 12, "title": "Fix response status", "body": "Add a regression test", "state": "open", "html_url": "https://github.com/demo/repo/pull/12"}]

    monkeypatch.setattr(ingestor, "_get", fake_get)
    docs = ingestor.ingest_pull_requests("demo/repo")
    assert len(docs) == 1
    assert docs[0].path == "pulls/12.md"
    assert "regression test" in docs[0].text
    assert docs[0].kind == "github_pull_request"


def test_pull_request_ingestion_can_be_disabled(monkeypatch, tmp_path):
    from devlens.ingestion import github as gh
    from devlens.models import SourceDocument

    monkeypatch.setattr(gh.GitHubIngestor, "ingest_repo", lambda self, repo: [SourceDocument("f", "doc.md", "Search uses hashing vectors")])
    monkeypatch.setattr(gh.GitHubIngestor, "ingest_issues", lambda self, repo: [])

    def error_if_called(self, repo):
        raise AssertionError("PR ingestion should be disabled")

    monkeypatch.setattr(gh.GitHubIngestor, "ingest_pull_requests", error_if_called)
    result = build_github_index("demo/repo", str(tmp_path / "index.json"), include_prs=False)
    assert result["documents"] == 1
