from dataclasses import asdict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .assistant import ApprovalGate, ApprovalRequired, answer_question, triage_issue
from .retrieval import VectorIndex
from .service import build_local_index, build_github_index

app=FastAPI(title="DevLens API",version="0.1.0")
class LocalIndexRequest(BaseModel): path:str; index_path:str=".devlens/index.json"
class GitHubIndexRequest(BaseModel): repo:str; index_path:str=".devlens/github-index.json"; include_issues:bool=True
class AskRequest(BaseModel): index_path:str=".devlens/index.json"; question:str=Field(min_length=1); top_k:int=Field(default=5,ge=1,le=20)
class TriageRequest(BaseModel): title:str; body:str=""
class ApprovalRequest(BaseModel): action:str; approved:bool=False
@app.get("/v1/health")
def health(): return {"status":"ok"}
@app.post("/v1/index/local")
def index_local(req:LocalIndexRequest):
    try:return build_local_index(req.path,req.index_path)
    except Exception as e: raise HTTPException(status_code=400,detail=str(e))
@app.post("/v1/index/github")
def index_github(req:GitHubIndexRequest):
    try:return build_github_index(req.repo,req.index_path,req.include_issues)
    except Exception as e: raise HTTPException(status_code=400,detail=str(e))
@app.post("/v1/ask")
def ask(req:AskRequest):
    try:
        ans=answer_question(VectorIndex.load(req.index_path),req.question,req.top_k)
        return {"answer":ans.text,"provider":ans.provider,"citations":ans.citations,"evidence":[{"citation_id":x.citation_id,"path":x.chunk.path,"start_line":x.chunk.start_line,"end_line":x.chunk.end_line,"score":x.score,"url":x.chunk.url} for x in ans.evidence]}
    except Exception as e: raise HTTPException(status_code=400,detail=str(e))
@app.post("/v1/triage")
def triage(req:TriageRequest): return asdict(triage_issue(req.title,req.body))
@app.post("/v1/approval/check")
def approval(req:ApprovalRequest):
    try: ApprovalGate().require(req.approved,req.action); return {"approved":True,"action":req.action}
    except ApprovalRequired as e: raise HTTPException(status_code=403,detail=str(e))
