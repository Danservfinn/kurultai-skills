# Commands

Placeholders: `<TARGET_URL>` = URL to scrape/crawl; `<JOB_ID>` = crawl job id (e.g. `crawl_abc123`); `<WEBHOOK_URL>` = webhook receiver endpoint.

## Step 1 — Configure

```bash
cp .env.sample .env
# For production, edit .env and set:
#   LLM_BASE_URL, LLM_API_KEY, LLM_MODEL, BRAVE_API_KEY, API_KEY
```

## Step 2 — Start the stack

```bash
# Local demo (fixture profile)
docker compose --profile fixture up --build -d

# Production (no fixture profile)
docker compose up --build -d
```

## Step 3 — Health check

```bash
curl http://localhost:8080/health
```

## Step 4 — Scrape smoke test

```bash
./groktocrawl scrape <TARGET_URL>
```

## Step 5 — Create async crawl job

```bash
curl -X POST http://localhost:8080/v2/crawl \
  -H "Content-Type: application/json" \
  -d '{"url":"<TARGET_URL>","maxDepth":2,"limit":20,"webhook":{"url":"<WEBHOOK_URL>"}}'
```

## Step 6 — Poll or stream

```bash
# Poll
curl http://localhost:8080/v2/crawl/<JOB_ID>

# SSE stream (runs crawl in the response)
curl -N -X POST http://localhost:8080/v2/crawl \
  -H "Content-Type: application/json" \
  -d '{"url":"<TARGET_URL>","maxDepth":2,"limit":20,"stream":true}'
```

## Step 7 — Restart recovery / diagnostics

```bash
docker compose ps
curl http://localhost:8080/v2/crawl/<JOB_ID>   # check for stranded "processing" jobs
# Reconcile per docs/runbooks/interrupted-jobs.md