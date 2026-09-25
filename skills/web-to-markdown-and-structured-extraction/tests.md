# Manual Tests

1. `pip install -U crawl4ai && crawl4ai-setup && crawl4ai-doctor` exits 0 and reports the browser as installed.
2. `crwl https://news.ycombinator.com -o markdown` prints Markdown containing post titles from the page.
3. `crwl configs set llm.provider openai/gpt-4o-mini && crwl configs set llm.api_key $OPENAI_API_KEY` succeeds, then `crwl <url> -q "<query>"` returns an answer (fails cleanly with an error if the key is missing/invalid).
4. Running the Example 2 script against `https://quotes.toscrape.com/scroll` prints `Extracted N quotes` with N > 0, and each record has `text`, `author`, `tags` keys.
5. With the Docker server running, `curl -s http://localhost:11235/md -H "Authorization: Bearer $CRAWL4AI_API_TOKEN" -H "Content-Type: application/json" -d '{"url": "https://news.ycombinator.com"}' | jq -r .markdown` returns non-empty Markdown; the same request without the Bearer header is rejected.
6. `python -c "from crawl4ai.content_filter_strategy import PruningContentFilter"` succeeds; if it fails, `python -c "from crawl4ai import content_filter_strategy; print(dir(content_filter_strategy))"` lists the actual filter classes and the skill's step 4 is updated accordingly.