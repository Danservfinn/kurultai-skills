# Commands

Placeholders: `<TARGET_URL>` = URL to scrape/crawl; `<JOB_ID>` = crawl job id (e.g. `crawl_abc123`); `<WEBHOOK_URL>` = webhook receiver URL; `<REPO_DIR>` = local clone path.

## Step 1 — configure

```bash
git clone https://github.com/groktopus/groktocrawl <REPO_DIR> && cd <REPO_DIR>
cp .env.sample .env
# edit .env: production sets LLM_BASE_URL, LLM_API_KEY, LLM_MODEL, BRAVE_API_KEY, API_KEY
```

## Step 2 — start the stack

```bash
# production (no fixture profile)
docker compose up --build -d
# local demo
docker compose --profile fixture up --build -d
```

## Step 3 — health check

```bash
curl http://localhost:8080/health
```

## Step 4 — smoke scrape

```bash
./groktocrawl scrape https://example.com
```

## Step 5 — create async crawl job

```bash
curl -X POST http://localhost:8080/v2/crawl \
  -H "Content-Type: application/json" \
  -d '{"url":"<TARGET_URL>","maxDepth":2,"limit":20,"webhook":{"url":"<WEBHOOK_URL>"}}'
```

## Step 6 — poll or stream

```bash
curl http://localhost:8080/v2/crawl/<JOB_ID>
curl -N -X POST http://localhost:8080/v2/crawl \
  -H "Content-Type: application/json" \
  -d '{"url":"<TARGET_URL>","maxDepth":2,"limit":20,"stream":true}'
```

## Step 7 — post-restart reconciliation

```bash
# consult docs/runbooks/interrupted-jobs.md in the repo for the reconciliation procedure