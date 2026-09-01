# Tests

Manual checklist for `deploy-self-hosted-crawl-stack`:

1. `docker compose --profile fixture up --build -d` then `docker compose ps` shows agent-svc and fixture services running; `curl http://localhost:8080/health` returns JSON with `"status":"ok"`.
2. `./groktocrawl scrape https://example.com` exits 0 and prints example.com content as markdown.
3. `POST http://localhost:8080/v2/crawl` returns JSON containing an `id` starting with `crawl_` and `"status":"processing"`.
4. Polling `http://localhost:8080/v2/crawl/<id>` eventually returns `"status":"completed"` with `"completed"` equal to `"total"` and a non-empty `data` array.
5. With a webhook configured (e.g. webhook.site), the receiver logs `crawl.started`, one `crawl.page` per crawled page, and `crawl.completed`, each carrying a distinct `webhookId`.
6. `curl -N` with `"stream":true` emits `data:` lines of type `page` and terminates with a `done` event whose `status` is `completed`.