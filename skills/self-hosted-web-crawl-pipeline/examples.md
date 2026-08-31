# Examples

## Example 1: Local demo smoke test (fixture profile, no credentials)

```
Input:
  repo: groktopus/groktocrawl, cloned to ~/groktocrawl
  mode: local demo (fixture profile)
  target: https://example.com

Actions:
  cp .env.sample .env
  docker compose --profile fixture up --build -d
  curl http://localhost:8080/health
  ./groktocrawl scrape https://example.com

Expected output:
  health → {"status":"ok","checks":{...}}
  scrape → example.com rendered as markdown
```

## Example 2: Production async crawl with webhook

```
Input:
  .env with LLM_BASE_URL=https://api.openai.com/v1, LLM_API_KEY=sk-..., LLM_MODEL=gpt-4o,
        BRAVE_API_KEY=BSA..., API_KEY=<random 32-char string>
  target: https://example.com, maxDepth 2, limit 20
  webhook: https://ops.example.internal/hook

Actions:
  docker compose up --build -d   # no fixture profile
  curl http://localhost:8080/health
  curl -X POST http://localhost:8080/v2/crawl -H "Content-Type: application/json" \
    -d '{"url":"https://example.com","maxDepth":2,"limit":20,"webhook":{"url":"https://ops.example.internal/hook"}}'
  # → {"id":"crawl_abc123","status":"processing",...}
  curl http://localhost:8080/v2/crawl/crawl_abc123   # poll until completed

Expected output:
  webhook receiver sees crawl.started, one crawl.page per page, crawl.completed
  final poll → {"status":"completed","completed":N,"total":N,"data":[...]}
```

## Example 3: SSE streaming crawl and post-restart reconciliation

```
Input:
  running stack, target https://example.com

Actions:
  curl -N -X POST http://localhost:8080/v2/crawl -H "Content-Type: application/json" \
    -d '{"url":"https://example.com","maxDepth":2,"limit":20,"stream":true}'

Expected output:
  data: {"type":"page","url":...,"markdown":...}
  ...
  data: {"type":"done","id":...,"status":"completed","pages":N,...}

Follow-up: if agent-svc restarted mid-job, list jobs stranded in "processing"
and reconcile per docs/runbooks/interrupted-jobs.md — they will not resume on
their own and pending webhooks will not be replayed.