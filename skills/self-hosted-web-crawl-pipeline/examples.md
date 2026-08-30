# Examples

## Example 1: No-credential local smoke test

**Input:** target URL `https://example.com`, no API keys available.

```
git clone https://github.com/groktopus/groktocrawl && cd groktocrawl
cp .env.sample .env
docker compose --profile fixture up --build -d
curl http://localhost:8080/health        # → {"status":"ok","checks":{...}}
./groktocrawl scrape https://example.com # → markdown of example.com
```

Then stream a small crawl:
```
curl -N -X POST http://localhost:8080/v2/crawl \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","maxDepth":1,"limit":5,"stream":true}'
```
Expect `data: {"type":"page",...}` events and a terminal `data: {"type":"done",...}` event.

## Example 2: Production crawl with webhook

**Input:** target `https://blog.kurult.ai`, production `.env` with `LLM_BASE_URL=https://api.openai.com/v1`, `LLM_API_KEY=sk-...`, `LLM_MODEL=gpt-4o`, `BRAVE_API_KEY=...`, `API_KEY=...`; webhook receiver `https://ops.kurult.ai/hook`.

```
docker compose up --build -d          # no fixture profile
curl -X POST http://localhost:8080/v2/crawl \
  -H "Content-Type: application/json" \
  -d '{"url":"https://blog.kurult.ai","maxDepth":2,"limit":20,"webhook":{"url":"https://ops.kurult.ai/hook"}}'
# → {"id":"crawl_abc123","status":"processing",...}
curl http://localhost:8080/v2/crawl/crawl_abc123
# → {"status":"completed","completed":18,"total":18,"data":[...]}
```

Receiver sees `crawl.started`, 18 × `crawl.page`, `crawl.completed`; dedupe by `webhookId`.

## Example 3: Post-restart reconciliation

**Input:** `agent-svc` container restarted mid-crawl; job `crawl_abc123` still shows `status:"processing"` after 10 minutes.

1. Confirm the job is stranded: `curl http://localhost:8080/v2/crawl/crawl_abc123` — status remains `processing` with no progress.
2. Follow `docs/runbooks/interrupted-jobs.md` to reconcile: mark the job failed/cancelled, note that partial Valkey/Qdrant artifacts may remain and undelivered webhooks will not replay.
3. Re-submit the crawl job if the data is still needed.