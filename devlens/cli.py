from __future__ import annotations
import argparse
import json
from dataclasses import asdict
from devlens.rag import answer_question
from devlens.retrieval.index import VectorIndex
from devlens.service import build_local_index, build_github_index
from devlens.triage import triage_issue


def main():
    ap = argparse.ArgumentParser(prog="devlens")
    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("index")
    p.add_argument("--path", required=True)
    p.add_argument("--out", default=".devlens/index.json")

    p = sub.add_parser("index-github")
    p.add_argument("--repo", required=True)
    p.add_argument("--out", default=".devlens/github-index.json")
    p.add_argument("--no-issues", action="store_true")
    p.add_argument("--no-prs", action="store_true")

    p = sub.add_parser("ask")
    p.add_argument("--index", default=".devlens/index.json")
    p.add_argument("--question", required=True)
    p.add_argument("--top-k", type=int, default=5)

    p = sub.add_parser("triage")
    p.add_argument("--title", required=True)
    p.add_argument("--body", default="")

    args = ap.parse_args()
    if args.command == "index":
        print(json.dumps(build_local_index(args.path, args.out), indent=2))
    elif args.command == "index-github":
        print(json.dumps(build_github_index(args.repo, args.out, not args.no_issues, not args.no_prs), indent=2))
    elif args.command == "ask":
        ans = answer_question(VectorIndex.load(args.index), args.question, args.top_k)
        print(ans.text)
        print("\nSources:")
        for e in ans.evidence:
            print(f"[{e.citation_id}] {e.chunk.path}:{e.chunk.start_line}-{e.chunk.end_line} score={e.score:.3f}")
    elif args.command == "triage":
        print(json.dumps(asdict(triage_issue(args.title, args.body)), indent=2))


if __name__ == "__main__":
    main()
