---
name: deploy-self-hosted-crawl-stack
description: Stand up a self-hosted Firecrawl-compatible crawling API (GroktoCrawl) via Docker, verify health and scraping, and run a verified async crawl with webhook or SSE progress
category: infrastructure
---

# Deploy self-hosted crawl stack (GroktoCrawl)

## Goal

Deploy the GroktoCrawl self-hosted web data platform via Docker Compose, verify readiness and scraping, then run a verified async crawl job using either webhook delivery or SSE streaming, and reconcile any jobs stranded by restarts.

## Inputs

- A clone of https://github.com/groktopus/groktocrawl (contains `.env.sample`, `docker-compose.yml`, `./groktocrawl` CLI).
- A target URL to crawl (e.g. `https://example.com`).
- For the local fixture smoke test: no credentials required.
- For production: `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` (OpenAI-compatible LLM), `BRAVE_API_KEY` (web search), `API_KEY` (API authentication). Optional: `SLOPSEARX_MCP_AUTH_TOKEN` if the `mcp` profile is enabled.
- Docker and Docker Compose on the host.

## Steps

1. Copy `.env.sample` to `.env`. Leave credentials empty for the local fixture smoke test. For production, set `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`, `BRAVE_API_KEY`, and `API_KEY`.
2. Start the stack: `docker compose --profile fixture up --build -d` for the local demo, or `docker compose up --build -d` for production (do NOT include the `fixture` profile in production — `llm-svc`, `test-site`, and `tier3-fixture` are fixture-only).
3. Verify readiness: `curl http://localhost:8080/health` must return `{"status":"ok","checks":{...}}`. Retry if dependencies are still starting.
4. Smoke-test scraping: `./groktocrawl scrape https://example.com` must print the page rendered as markdown.
5. Create an async crawl job: `POST http://localhost:8080/v2/crawl` with a JSON body containing `url`, `maxDepth`, `limit` (must be ≥ 1; omit for unlimited), and optionally `"webhook": {"url": "..."}` or `"stream": true`. Capture the returned `id` (format `crawl_<job_id>`).
6. Either poll `curl http://localhost:8080/v2/crawl/<job_id>` until `status` is `"completed"`, or stream live progress with `curl -N` and `"stream": true`, receiving SSE `page` events and a terminal `done` event.
7. Verify webhook delivery: `crawl.started` before scraping, one `crawl.page` per page, `crawl.completed` at the end — each with a unique `webhookId`. If the service restarted mid-job, reconcile jobs stranded in `processing` per `docs/runbooks/interrupted-jobs.md` (async jobs are not restart-safe; no resume, rollback, or webhook replay).

## Outputs

- Running API on port 8080.
- Markdown rendering of scraped pages (stdout of `./groktocrawl scrape`).
- Completed crawl job with page data (JSON from polling, or SSE stream).
- Webhook events: `crawl.started`, `crawl.page` per page, `crawl.completed`.

## Failure modes

- Fixture-only services (`llm-svc`, `test-site`) accidentally started in production — omit the `fixture` profile when running production.
- Health check fails initially because dependencies are not yet up — retry until `status` is `ok`.
- Async jobs lost or stranded in `processing` after a restart; no resume or webhook replay — reconcile per the Interrupted Jobs runbook.
- Qdrant/semantic failures on the vector path (scrapes still succeed; indexing is best effort). Browser-tier scrapes may be blocked by bot challenges (e.g. Fastly JS challenges); the scraper detects and reports these.
- Missing or invalid `LLM_API_KEY`/`BRAVE_API_KEY`/`API_KEY` in production mode.

## Source

- https://github.com/groktopus/groktocrawl (README, docs/architecture.md, docs/runbooks/interrupted-jobs.md), retrieved 2026-09-01.