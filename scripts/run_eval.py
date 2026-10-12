from devlens.models import Chunk
from devlens.retrieval import VectorIndex,retrieve
from devlens.assistant import LocalProvider,answer_question,citation_coverage,validate_citations
import json

def main():
    chunks=[Chunk("1","a","approval.py","Repository writes require explicit human approval.",1,1),Chunk("2","b","retrieval.md","Vector retrieval uses normalized hashing vectors and a NumPy fallback.",1,1)]
    idx=VectorIndex().build(chunks)
    cases=[("human approval repository writes","approval.py"),("vector retrieval fallback","retrieval.md")]
    retrieval=[{"query":q,"hit":retrieve(idx,q,1)[0].chunk.path==path} for q,path in cases]
    ans=answer_question(idx,"Where is human approval enforced?",provider=LocalProvider())
    result={"retrieval":retrieval,"answer":{"citation_coverage":citation_coverage(ans.text),"citation_validation":validate_citations(ans.text,ans.evidence)}}
    print(json.dumps(result,indent=2))
if __name__=="__main__": main()
