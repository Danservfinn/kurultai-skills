---
name: self-hosted-web-crawl-pipeline
description: Deploy a self-hosted Firecrawl-compatible crawling stack (GroktoCrawl) via Docker Compose and run async crawls with polling, SSE streaming, and webhook progress tracking
category: infrastructure
---

# Self-hosted web crawl pipeline (GroktoCrawl)

## Goal

Stand up a self-hosted GroktoCrawl stack (Firecrawl v2-compatible API), verify health, run an async crawl job against a target URL, and track progress via polling, SSE stream, or webhook events. Includes post-restart reconciliation of stranded jobs.

## Inputs

- Target URL(s) to crawl
- For production: `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` (OpenAI-compatible provider), `BRAVE_API_KEY` (web search), `API_KEY` (API authentication)
- Optional webhook receiver URL reachable from the Docker host
- For a no-credential smoke test: none (fixture profile)

## Steps

1. Clone the repo and configure the environment:
   ```bash
   git clone https://github.com/groktopus/groktocrawl
   cd groktocrawl
   cp .env.sample .env
   ```
   - Production: edit `.env` to set `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`, `BRAVE_API_KEY`, and `API_KEY`. Optionally raise `LLM_CALL_TIMEOUT` (default 120s; e.g. 300 for reasoning models).
   - Local demo: leave defaults; no credentials required.

2. Start the stack:
   - Production: `docker compose up --build -d` (do NOT enable the `fixture` profile; `llm-svc`, `test-site`, `tier3-fixture` are fixture-only).
   - Local demo: `docker compose --profile fixture up --build -d`.

3. Verify health:
   ```bash
   curl http://localhost:8080/health
   ./groktocrawl scrape https://example.com
   ```
   Health must return `{"status":"ok","checks":{...}}`; the scrape must print example.com as markdown.

4. Create an async crawl job:
   ```bash
   curl -X POST http://localhost:8080/v2/crawl \
     -H "Content-Type: application/json" \
     -d '{"url":"<TARGET_URL>","maxDepth":2,"limit":20,"webhook":{"url":"<WEBHOOK_URL>"}}'
   ```
   Capture the returned `id` (`crawl_<job_id>`). `limit` is a page cap (≥1); omit for unlimited.

5. Track progress — choose one:
   - Poll: `curl http://localhost:8080/v2/crawl/crawl_<job_id>` until `status` is `completed`; the record then contains `data: [...]`.
   - SSE stream (runs the crawl in the response): `curl -N -X POST http://localhost:8080/v2/crawl -H "Content-Type: application/json" -d '{"url":"<TARGET_URL>","maxDepth":2,"limit":20,"stream":true}'` — emits `page` events and a terminal `done` event.

6. Handle webhook events at the receiver: `crawl.started` (before scraping), `crawl.page` (after each page), `crawl.completed` (at end). Each carries a unique `webhookId`; deduplicate on it. Omit the `events` filter to receive all event types.

7. After any `agent-svc` restart or crash, reconcile jobs stranded in `processing` per the Interrupted Jobs runbook (`docs/runbooks/interrupted-jobs.md`). Async jobs are not restart-safe: no resume, no rollback of partial Valkey/Qdrant artifacts, no webhook replay.

## Outputs

- Markdown-rendered page content per crawled URL (in `data` array or SSE `page` events)
- Completed crawl job record: `{"status":"completed","completed":N,"total":N,"data":[...]}`
- Webhook events `crawl.started` / `crawl.page` / `crawl.completed` with unique `webhookId`s

## Failure modes

- Jobs stuck in `processing` after a crash/restart are not resumed or reclaimed; undelivered webhooks are not replayed — manual reconciliation required.
- Partial artifacts written to Valkey/Qdrant are not rolled back.
- Bot-challenge pages (e.g. Fastly JS challenges) are detected and not served as content; low-yield pages may warn on partial extraction.
- Vector-search (Qdrant) backend failures surface as errors, not silent empty results.
- Fixture-only services (`llm-svc`, `test-site`, `tier3-fixture`) must not run in production.
- Missing `API_KEY` in production: service emits `X-Security-Warning` header; set `API_KEY` before exposing outside a trusted network.

## Source

- https://github.com/groktopus/groktocrawl (README, docs/architecture.md), retrieved 2026-08-30