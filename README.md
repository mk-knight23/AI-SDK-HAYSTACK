# AI-SDK-HAYSTACK

Composable retrieval and NLP pipelines for production intelligence.

## Current Features

- Mission routing with shared support-agent fallback.
- FastAPI API surface and CLI smoke runner.
- Haystack Pipeline initialization path.
- Dockerfile, CI workflow, pytest contract tests, and skill documentation.
- Repository metadata for portfolio and GitHub Pages positioning.

## Existing Runtime Flow

1. A user sends a mission through the CLI or `POST /run`.
2. The shared Agents Army router scores the mission against agent skills.
3. The adapter selects a primary agent and support agents.
4. The Haystack integration validates the framework-specific execution path.
5. The response returns routing, support agents, result text, and verification notes.

## SDK-Specific Implementation

Instantiates a Haystack Pipeline as the foundation for retrieval/NLP workflows.

## Repository Structure

- `app.py`: framework adapter and mission execution entrypoint.
- `api.py`: FastAPI health and run endpoints.
- `runner.py`: local CLI demo runner.
- `core/agents_army_core/`: shared routing, mission models, registry, and instruction rendering.
- `tests/`: contract tests for routing and verification behavior.
- `.github/workflows/ci.yml`: automated pytest checks.
- `Dockerfile`: container packaging for API deployment.
- `SKILLSET.md`: skills represented by this SDK adapter.

## Run Locally

```bash
python3 -m pip install -r requirements.txt
python3 runner.py --mission "build secure api, add tests, and deploy"
```

## Run As An API

```bash
uvicorn api:app --host 0.0.0.0 --port 8000
```

```bash
curl http://localhost:8000/health
curl -X POST http://localhost:8000/run \
  -H "content-type: application/json" \
  -d '{"mission":"secure audit and deploy an AI workflow"}'
```

## Test

```bash
python3 -m pytest
```

## Required Skill Set

See `SKILLSET.md` for the full skill matrix. At a high level this repository demonstrates:

- Haystack integration.
- Agent routing and mission planning.
- API design with clear input/output contracts.
- CI-backed verification.
- Secure environment-based configuration.

## Upgrade Roadmap

- Add document-store adapters and retrieval components.
- Introduce query relevance tests and evaluation fixtures.
- Add ingestion pipelines for files, URLs, and knowledge bases.

## Clean Repository Policy

Generated files such as `__pycache__/`, `.pytest_cache/`, local `.env` files, and dependency folders are ignored. Source, docs, tests, and deployment assets are intentionally kept in the repository.
