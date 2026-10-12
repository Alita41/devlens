import argparse,json
from dataclasses import asdict
from .assistant import answer_question,triage_issue
from .retrieval import VectorIndex
from .service import build_local_index,build_github_index

def main():
    ap=argparse.ArgumentParser(prog="devlens"); sub=ap.add_subparsers(dest="command",required=True)
    p=sub.add_parser("index"); p.add_argument("--path",required=True); p.add_argument("--out",default=".devlens/index.json")
    p=sub.add_parser("index-github"); p.add_argument("--repo",required=True); p.add_argument("--out",default=".devlens/github-index.json"); p.add_argument("--no-issues",action="store_true")
    p=sub.add_parser("ask"); p.add_argument("--index",default=".devlens/index.json"); p.add_argument("--question",required=True); p.add_argument("--top-k",type=int,default=5)
    p=sub.add_parser("triage"); p.add_argument("--title",required=True); p.add_argument("--body",default="")
    a=ap.parse_args()
    if a.command=="index": print(json.dumps(build_local_index(a.path,a.out),indent=2))
    elif a.command=="index-github": print(json.dumps(build_github_index(a.repo,a.out,not a.no_issues),indent=2))
    elif a.command=="ask":
        ans=answer_question(VectorIndex.load(a.index),a.question,a.top_k); print(ans.text); print("\nSources:"); [print(f"[{e.citation_id}] {e.chunk.path}:{e.chunk.start_line}-{e.chunk.end_line} score={e.score:.3f}") for e in ans.evidence]
    elif a.command=="triage": print(json.dumps(asdict(triage_issue(a.title,a.body)),indent=2))
if __name__=="__main__": main()
