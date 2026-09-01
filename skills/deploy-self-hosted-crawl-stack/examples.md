# Examples

## Example 1: Local fixture smoke test with SSE streaming

Input: fresh clone of groktocrawl on a macOS laptop, target URL `https://example.com`, no credentials.

```bash
cp .env.sample .env
docker compose --profile fixture up --build -d
curl http://localhost:8080/health
# → {"status":"ok","checks":{...}}

./groktocrawl scrape https://example.com
# → example.com content as markdown

curl -N -X POST http://localhost:8080/v2/crawl \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com","maxDepth":2,"limit":20,"stream":true}'
# → data: {"type":"page","url":...,"markdown":...}
#   data: {"type":"done","id":...,"status":"completed","pages":N,...}
```

Expected: terminal `done` event with `status":"completed"`.

## Example 2: Production crawl with webhook

Input: production `.env` with `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`, `BRAVE_API_KEY`, `API_KEY` set; webhook receiver at `https://ops.example.com/hook`; target `https://docs.example.com`.

```bash
cp .env.sample .env
# edit .env with real credentials
docker compose up --build -d          # no fixture profile
curl http://localhost:8080/health

JOB=$(curl -s -X POST http://localhost:8080/v2/crawl \
  -H "Content-Type: application/json" \
  -d '{"url":"https://docs.example.com","maxDepth":2,"limit":20,"webhook":{"url":"https://ops.example.com/hook"}}' \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')

curl http://localhost:8080/v2/crawl/$JOB
# → {"status":"completed","completed":20,"total":20,"data":[ ... ]}
```

Expected: webhook receiver logs one `crawl.started`, one `crawl.page` per page, one `crawl.completed`, each with a unique `webhookId`.

## Example 3: Restart strands a job in processing

Input: crawl job created as above; `agent-svc` container restarted mid-crawl.

```bash
docker compose restart agent-svc
curl http://localhost:8080/v2/crawl/$JOB
# → {"status":"processing", ...}  (stranded; no recovery pass)
```

Action: reconcile per `docs/runbooks/interrupted-jobs.md` — the job will not resume, partial artifacts persist, and undelivered webhooks are not replayed. Re-run the crawl as a new job.