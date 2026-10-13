# DevLens

**Repository search and source-cited question answering for code, documentation, issues, and pull requests.**

DevLens turns a software repository into a searchable engineering knowledge base. It ingests source files and GitHub context, chunks and indexes them, retrieves evidence for developer questions, generates source-cited answers, and triages issues into structured recommendations. An approval-check endpoint demonstrates how a future write workflow can require explicit authorization; the application does not currently execute GitHub mutations.

The project is intentionally runnable in two modes:

- **Local mode** — deterministic hashing-based retrieval and extractive answers, with no API key required. This mode does not use a learned embedding model.
- **OpenAI mode** — retrieved context is sent to the OpenAI Responses API for answer generation and issue triage. This requires an API key and a supported model name.

## What it demonstrates

- Retrieval-augmented generation (RAG) over real code/document sources
- GitHub REST API ingestion for repository files, issues, and pull-request descriptions
- LangChain text splitting when the optional dependency is installed
- Vector retrieval with optional FAISS acceleration and a NumPy fallback
- Source citations and citation validation
- Structured issue triage with confidence scores
- Approval-check API for gating prospective write operations (no write operations are implemented)
- FastAPI service + CLI
- Evaluation harness for retrieval recall and citation coverage
- Docker + GitHub Actions CI

## Architecture

```text
Local repo / GitHub API
          |
          v
   +-------------+
   |  Ingestion  |
   +------+------+ 
          |
          v
   +-------------+      optional LangChain splitter
   |   Chunking  |------------------------------+
   +------+------+                              |
          |                                     |
          v                                     |
   +-------------+      optional FAISS           |
   | VectorIndex |<------------------------------+
   +------+------+ 
          |
          v
   +-------------+
   |  Retriever  |
   +------+------+ 
          |
       evidence
          |
     +----+---------------------+
     |                          |
     v                          v
+-----------+            +---------------+
| Q&A / RAG |            | Issue Triage  |
+-----+-----+            +-------+-------+
      |                          |
      v                          v
 citations                 approval gate
      |                          |
      +------------+-------------+
                   |
                   v
              FastAPI / CLI
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

Index this repository and ask a question:

```bash
python -m devlens.cli index --path . --out .devlens/index.json
python -m devlens.cli ask --index .devlens/index.json --question "How does DevLens prevent unapproved GitHub writes?"
```

Run the API:

```bash
uvicorn devlens.api:app --host 127.0.0.1 --port 8080
```

Run the service only in a trusted environment; these development endpoints have no authentication and can read local paths.

Then:

```bash
curl -X POST http://127.0.0.1:8080/v1/index/local \
  -H 'Content-Type: application/json' \
  -d '{"path":".","index_path":".devlens/index.json"}'

curl -X POST http://127.0.0.1:8080/v1/ask \
  -H 'Content-Type: application/json' \
  -d '{"index_path":".devlens/index.json","question":"What does the approval gate do?","top_k":5}'
```

## OpenAI mode

Set an API key and select the provider:

```bash
export OPENAI_API_KEY=...
export DEVLENS_LLM_PROVIDER=openai
export DEVLENS_OPENAI_MODEL=your-supported-model
```

DevLens uses the **Responses API** through the official Python SDK. The model name is configurable so the repository is not coupled to one model release.

## GitHub ingestion

For public repositories, no token is required for basic reads, though authenticated requests have higher rate limits. For private repositories, set `GITHUB_TOKEN`.

```bash
python -m devlens.cli index-github \
  --repo owner/repository \
  --out .devlens/github-index.json
```

The GitHub ingestor fetches repository files, issue descriptions, and pull-request descriptions through the REST API. It indexes the first API page of issues and pull requests (up to 100 of each); pagination, diff ingestion, and review comments are not implemented.

## Issue triage

```bash
python -m devlens.cli triage \
  --title "Search endpoint returns 500 on empty query" \
  --body "POST /v1/search crashes when query is blank."
```

Triage returns a structured object containing:

- category
- severity
- likely component
- confidence
- rationale
- suggested labels
- whether human review is required

`ApprovalGate` is available through `/v1/approval/check` for demonstrating an explicit authorization step. There are **no GitHub write endpoints** in this version: triage produces recommendations only, and `/v1/approval/check` does not grant a lasting permission token.

## Retrieval implementation

The default retriever hashes token and character features into fixed-length vectors, which keeps the repository fully runnable offline. If `faiss-cpu` is installed, `VectorIndex` uses FAISS inner-product search; otherwise it transparently uses normalized NumPy vectors.

This fallback is deliberately described as **deterministic vector retrieval**, not as a learned semantic embedding model.

## LangChain integration

If `langchain-text-splitters` is installed, DevLens uses `RecursiveCharacterTextSplitter` for chunking. Otherwise it uses the included deterministic line-aware splitter. This keeps the base project lightweight while still providing a real LangChain integration path.

## Evaluation

```bash
python -m scripts.run_eval
```

The evaluation harness measures:

- retrieval Recall@K against small judged fixtures
- citation coverage of generated answers
- citation validity (every citation must resolve to retrieved evidence)

The two bundled queries are smoke tests for the pipeline, not an information-retrieval benchmark. For meaningful retrieval quality estimates, add a larger dataset of labeled engineering questions.

## Repository layout

```text
devlens/
  api.py                 FastAPI service
  cli.py                 command-line workflows
  models.py              typed domain models
  ingestion/
    local.py             local repository ingestion
    github.py            GitHub REST ingestion
    chunking.py          LangChain + fallback splitter
  retrieval/
    embeddings.py        deterministic hashing vectors
    index.py             FAISS/NumPy vector index
    retriever.py         top-k retrieval
  llm/
    base.py              provider interface
    local.py             zero-cost extractive provider
    openai_provider.py   OpenAI Responses API provider
  rag.py                 grounded answer generation
  triage.py              structured issue triage
  approval.py            human approval gate
  citations.py           citation validation
  evals.py               retrieval/citation metrics
scripts/run_eval.py
tests/
Dockerfile
```

## Safety / engineering decisions

- Retrieved context is treated as untrusted data, not as executable instructions.
- The prompt asks the model to answer only from provided evidence and expose uncertainty.
- Citation IDs are assigned by DevLens, not trusted from source text.
- The application performs read-only GitHub ingestion. The approval-check endpoint is a small reference gate, not a complete authorization system.
- Local mode makes tests deterministic and avoids hiding core behavior behind paid APIs.

## License

MIT
