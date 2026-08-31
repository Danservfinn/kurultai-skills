---
name: self-hosted-web-crawl-pipeline
description: Deploy the self-hosted GroktoCrawl stack (Firecrawl-compatible) and run async crawls with webhook/SSE progress
category: infrastructure
---

# Self-hosted web crawl pipeline (GroktoCrawl)

## Goal

Deploy the GroktoCrawl Docker stack locally or in production, verify it with a health check and a smoke scrape, then run an async crawl job with webhook or SSE progress. Reconcile stranded jobs after any `agent-svc` restart.

## Inputs

- Cloned repo: `https://github.com/groktopus/groktocrawl` (contains `.env.sample`, `docker-compose.yml`, `./groktocrawl` CLI).
- For production: an OpenAI-compatible LLM provider (`LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`), a `BRAVE_API_KEY` (Brave Search API), and an `API_KEY` value for API authentication. These require external service accounts/keys.
- For local demo only: no credentials; the `fixture` Compose profile provides `llm-svc` and fixture test sites.
- Target URL(s) to scrape/crawl.
- Optional: a webhook receiver URL reachable from the host.

## Steps

1. Clone the repo and copy `.env.sample` to `.env`. For production, set `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`, `BRAVE_API_KEY`, and `API_KEY`. For the local demo, no credentials are required. Optionally tune `LLM_CALL_TIMEOUT` (default 120s; e.g. 300 for reasoning models) and `QDRANT_QUERY_TIMEOUT`/`QDRANT_CLIENT_TIMEOUT`.
2. Start the stack. Production: `docker compose up --build -d` (do NOT use the `fixture` profile — `llm-svc`, `test-site`, `tier3-fixture` are fixture-only). Local demo: `docker compose --profile fixture up --build -d`.
3. Verify health: `curl http://localhost:8080/health` must return `{"status":"ok","checks":{...}}` once all dependencies are up.
4. Smoke-test scraping: `./groktocrawl scrape https://example.com` must print example.com rendered as markdown.
5. Create an async crawl job: `curl -X POST http://localhost:8080/v2/crawl` with JSON `{"url":"...","maxDepth":2,"limit":20,"webhook":{"url":"https://your-host/hook"}}`. Capture the returned `id` (`crawl_<job_id>`). `limit` is a page cap and must be ≥ 1; omit it for unlimited.
6. Poll `curl http://localhost:8080/v2/crawl/crawl_<job_id>` until `status` is `completed`, or stream live progress with `curl -N` and `"stream":true` in the POST body. Expect webhook events `crawl.started` (before scraping), `crawl.page` (after each page), `crawl.completed` (at end), each with a unique `webhookId`; the SSE stream emits flat `page` events and a terminal `done` event.
7. After any `agent-svc` restart, reconcile jobs stranded in `processing` per the Interrupted Jobs runbook (`docs/runbooks/interrupted-jobs.md`). Async jobs are best-effort and not restart-safe: restarts do not resume work, roll back partial artifacts, or replay undelivered webhooks.

## Outputs

- Markdown-rendered page content from scrape/crawl.
- Completed crawl job data: `{"status":"completed","completed":N,"total":N,"data":[...]}`.
- Webhook events (`crawl.started`/`crawl.page`/`crawl.completed`) or an SSE stream of `page`/`done` events.

## Failure modes

- Jobs stuck in `processing` after a restart are not resumed or rolled back; undelivered webhooks are not replayed. Manual reconciliation required.
- Bot-challenge pages (e.g. Fastly JS challenges) are detected, not served as content — a near-empty result may indicate a challenge page, not a bug.
- Vector-search (Qdrant/semantic-svc) failures surface as errors, not silent empty results.
- Fixture-only services (`llm-svc`, `test-site`, `tier3-fixture`) must not run in production.
- Missing `API_KEY` when exposed beyond a trusted network: the service emits an `X-Security-Warning` header while authentication is disabled.
- Missing/invalid `LLM_API_KEY` or `BRAVE_API_KEY` causes dependent health checks and search/LLM paths to fail.

## Source

- https://github.com/groktopus/groktocrawl (README, docs/architecture.md), accessed 2026-08-31.