# Tests

Manual checklist a reviewer can run against a deployed stack:

1. `curl http://localhost:8080/health` returns JSON containing `"status":"ok"`.
2. `./groktocrawl scrape https://example.com` exits 0 and prints markdown containing "Example Domain".
3. `curl -X POST http://localhost:8080/v2/crawl -d '{"url":"https://example.com","maxDepth":1,"limit":5}'` returns a JSON body with an `id` starting with `crawl_` and `"status":"processing"`.
4. Polling `curl http://localhost:8080/v2/crawl/<id>` eventually returns `"status":"completed"` with a non-empty `data` array.
5. With `"stream":true`, `curl -N` emits at least one `data: {"type":"page",...}` line and a terminal `data: {"type":"done",...}` line.
6. With a webhook receiver (e.g. `nc -l 9000` behind an HTTP echo), the receiver observes `crawl.started` and `crawl.completed` events, each carrying a unique `webhookId`.