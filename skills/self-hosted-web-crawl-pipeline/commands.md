# Commands

Placeholders: `<TARGET_URL>` (URL to crawl), `<WEBHOOK_URL>` (webhook receiver), `<JOB_ID>` (id returned by crawl POST, prefixed `crawl_`). Run all commands from the repo root unless noted.

## Step 1 — Clone and configure

```bash
git clone https://github.com/groktopus/groktocrawl
cd groktocrawl
cp .env.sample .env
# Production: edit .env — set LLM_BASE_URL, LLM_API_KEY, LLM_MODEL, BRAVE_API_KEY, API_KEY
```

## Step 2 — Start the stack

```bash
# Production
docker compose up --build -d
# Local demo (fixture profile; never in production)
docker compose --profile fixture up --build -d
```

## Step 3 — Verify health

```bash
curl http://localhost:8080/health
./groktocrawl scrape https://example.com
```

## Step 4 — Create async crawl job

```bash
curl -X POST http://localhost:8080/v2/crawl \
  -H "Content-Type: application/json" \
  -d '{"url":"<TARGET_URL>","maxDepth":2,"limit":20,"webhook":{"url":"<WEBHOOK_URL>"}}'
```

## Step 5a — Poll job status

```bash
curl http://localhost:8080/v2/crawl/<JOB_ID>
```

## Step 5b — SSE stream

```bash
curl -N -X POST http://localhost:8080/v2/crawl \
  -H "Content-Type: application/json" \
  -d '{"url":"<TARGET_URL>","maxDepth":2,"limit":20,"stream":true}'
```

## Step 7 — Inspect stranded job after restart

```bash
curl http://localhost:8080/v2/crawl/<JOB_ID>
# then follow docs/runbooks/interrupted-jobs.md