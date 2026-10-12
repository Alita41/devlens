# DevLens

**AI engineering knowledge assistant for source-cited RAG over repositories, docs, issues, and PR context.**

DevLens turns a software repository into a searchable engineering knowledge base. It ingests local or GitHub-hosted source files, chunks and indexes them, retrieves evidence for developer questions, generates source-cited answers, and triages issues into structured recommendations with an explicit human-approval gate before repository write actions.

## Highlights

- RAG over source code and engineering documentation
- GitHub REST ingestion for repository files and issues
- Deterministic vector retrieval with optional FAISS acceleration
- Source-cited answers with citation validation
- Structured issue triage with confidence and suggested labels
- Human-in-the-loop approval gate for repository mutations
- Local zero-cost provider plus optional OpenAI Responses API provider
- FastAPI service and CLI
- Docker and GitHub Actions CI
- Deterministic tests and smoke evaluation

## Architecture

```text
Local repo / GitHub API -> ingestion -> chunking -> vector index -> retrieval
                                                       |            |
                                                       v            v
                                                  cited Q&A     issue triage
                                                       \            /
                                                        approval gate
                                                            |
                                                       FastAPI / CLI
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python scripts/run_eval.py
```

Index a local repository and ask a question:

```bash
python -m devlens.cli index --path . --out .devlens/index.json
python -m devlens.cli ask --index .devlens/index.json --question "How does DevLens prevent unapproved writes?"
```

Run the API:

```bash
uvicorn devlens.api:app --host 0.0.0.0 --port 8080
```

## GitHub ingestion

```bash
python -m devlens.cli index-github --repo owner/repository --out .devlens/github-index.json
```

Public repositories work without a token for basic reads. Set `GITHUB_TOKEN` for authenticated/private-repository access.

## OpenAI mode

```bash
export OPENAI_API_KEY=...
export DEVLENS_LLM_PROVIDER=openai
export DEVLENS_OPENAI_MODEL=<responses-api-model>
```

The model name is deliberately configurable. Local mode remains the default so the project can be tested without paid API access.

## Safety and grounding

Retrieved repository content is treated as untrusted data rather than instructions. Generated answers may only cite evidence IDs assigned by DevLens, citations are validated before returning a response, and repository mutations require explicit human approval.


## License

MIT
