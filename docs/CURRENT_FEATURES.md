# Current Feature Inventory

## Repository

- Name: `AI-SDK-HAYSTACK`
- SDK: Haystack
- Positioning: Composable retrieval and NLP pipelines for production intelligence.

## Implemented Today

- Mission routing with shared support-agent fallback.
- FastAPI API surface and CLI smoke runner.
- Haystack Pipeline initialization path.
- Dockerfile, CI workflow, pytest contract tests, and skill documentation.
- Repository metadata for portfolio and GitHub Pages positioning.

## Not Yet Implemented

- Add document-store adapters and retrieval components.
- Introduce query relevance tests and evaluation fixtures.
- Add ingestion pipelines for files, URLs, and knowledge bases.

## Verification Contract

- The local runner must complete without crashing when optional SDK credentials are missing.
- The API contract must return routing and verification fields.
- Tests must prove mission routing and a security-focused SENTINEL route.
