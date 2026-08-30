# Tests

Manual checklist for a reviewer:

1. **Health check passes.** After `docker compose --profile fixture up --build -d`, `curl http://localhost:8080/health` returns JSON containing `"status":"ok"`.
2. **CLI scrape works.** `./groktocrawl scrape https://example.com` exits 0 and prints example.com content as markdown.
3. **Async crawl completes.** POST to `/v2/crawl` returns an `id` matching `crawl_*`; polling `/v2/crawl/<JOB_ID>` eventually returns `"status":"completed"` with a non-empty `data` array.
4. **SSE stream terminates correctly.** `curl -N` with `"stream":true` emits `data: {"type":"page",...}` events and ends with a `data: {"type":"done",...}` event.
5. **Webhook events arrive in order.** A receiver registered as `webhook.url` observes `crawl.started`, one `crawl.page` per page, then `crawl.completed`, each with a distinct `webhookId`.
6. **Fixture isolation.** `docker compose ps --format json | grep -c llm-svc` returns 0 when started without the `fixture` profile (production mode).