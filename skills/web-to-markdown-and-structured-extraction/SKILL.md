---
name: web-to-markdown-and-structured-extraction
description: Crawl any website into clean LLM-ready Markdown and extract structured JSON data using Crawl4AI (Python library, crwl CLI, or self-hosted Docker server)
category: content
---

# Web-to-Markdown and Structured Extraction with Crawl4AI

## Goal

Fetch any website with Crawl4AI and produce (a) clean, LLM-ready Markdown, optionally stripped of boilerplate, and (b) structured JSON records via CSS/XPath schemas or an LLM extraction strategy. Usable from Python, the `crwl` CLI, or a self-hosted Docker server.

## Inputs

- Target URL(s).
- Optional extraction schema (`baseSelector` + CSS/XPath field selectors) or a Pydantic model for LLM extraction.
- Optional LLM provider config (requires an API key, e.g. `OPENAI_API_KEY`, for `LLMExtractionStrategy` or CLI `-q` queries).
- Optional content-filter query for BM25 filtering.
- For the Docker path: ability to run Docker and generate a token.

## Steps

1. Install and verify. Run `pip install -U crawl4ai && crawl4ai-setup`. If browser setup fails, run `python -m playwright install --with-deps chromium`. Verify the installation with `crawl4ai-doctor`.

2. For quick one-off use, run the CLI:
   - Markdown output: `crwl <url> -o markdown`
   - LLM-assisted query: `crwl <url> -q "Extract all product prices"` — this requires configuring an LLM first via `crwl configs set llm.provider <provider>` and `crwl configs set llm.api_key <key>`.
   Note: deep crawling (multi-page BFS/DFS) is not exposed as documented CLI flags; do it programmatically (step 4).

3. For programmatic use, write a Python script that instantiates `AsyncWebCrawler` (optionally with `BrowserConfig(headless=True)`), builds a `CrawlerRunConfig`, calls `result = await crawler.arun(url=..., config=run_config)`, and reads `result.markdown` (raw Markdown) or `result.markdown.raw_markdown`.

4. To strip boilerplate (menus, footers), attach a markdown generator with a pruning filter: `DefaultMarkdownGenerator(content_filter=PruningContentFilter(threshold=0.48, threshold_type="fixed", min_word_threshold=0))`, and read `result.markdown.fit_markdown`. For query-focused extraction use `BM25ContentFilter(user_query=...)` instead. If `PruningContentFilter` is not importable in your installed version, run `python -c "from crawl4ai import content_filter_strategy; print(dir(content_filter_strategy))"` to list the actual filter classes before proceeding.

5. For structured data without an LLM, define a schema dict (`baseSelector` plus `fields` with CSS selectors and `type` of `text`/`list`/etc.), set `extraction_strategy=JsonCssExtractionStrategy(schema)` on `CrawlerRunConfig`, enable `scan_full_page=True` and `scroll_delay=0.5` for infinite-scroll or lazy-loading pages, then parse with `json.loads(result.extracted_content)`. Use `JsonXPathExtractionStrategy` for XPath selectors.

6. For LLM-based extraction, set `extraction_strategy=LLMExtractionStrategy(llm_config=LLMConfig(provider="openai/gpt-4o-mini", api_token=os.getenv("OPENAI_API_KEY")), schema=PydanticModel.model_json_schema(), extraction_type="schema", instruction="...")` and read `result.extracted_content`. Any provider LiteLLM supports works (e.g. `"ollama/llama3.3"` with `api_token="no-token"`). Requires the provider's API key.

7. Alternatively, run the Docker server: generate a token with `openssl rand -hex 32`, start `docker run -d -p 11235:11235 -e CRAWL4AI_API_TOKEN=$TOKEN --shm-size=1g unclecode/crawl4ai:latest` (allow ~10 s startup), then `curl -s http://localhost:11235/md -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"url": "..."}' | jq -r .markdown`. Other endpoints: `/html`, `/crawl`, `/screenshot`, `/pdf`, `/execute_js`. Dashboard at `http://localhost:11235/dashboard`.

## Outputs

- `raw_markdown` and `fit_markdown` per page (clean Markdown with headings, tables, code blocks).
- Structured JSON records in `result.extracted_content` (from CSS/XPath or LLM strategies).
- Optional screenshots and PDFs via the Docker endpoints or `CrawlerRunConfig`.

## Failure modes

- Browser setup fails on systems missing Playwright system dependencies — fix with `python -m playwright install --with-deps chromium`.
- JS-heavy or infinite-scroll pages miss content unless `scan_full_page=True` with a `scroll_delay`.
- Sites with bot detection fail — try `magic=True`, `enable_stealth`, persistent browser profiles (`user_data_dir` + `use_persistent_context`), or proxies.
- LLM extraction and `crwl -q` fail without a valid provider API key; configure with `crwl configs set llm.provider` / `crwl configs set llm.api_key`.
- Docker API (since v0.8.0) requires the Bearer token on every endpoint and blocks `file://` URLs and hooks by default for security; do not rely on hook execution or local-file crawling through the server without verifying your server version's release notes.
- CSS selector schemas break silently when the target site changes its markup — re-inspect the page and update `baseSelector`/`fields`.
- Filter class names vary across versions; verify importable names with `dir(crawl4ai.content_filter_strategy)` if an import fails.

## Source

https://github.com/unclecode/crawl4ai (readme, retrieved 2026-09-25); Docker security behavior per docs/RELEASE_NOTES_v0.8.0.md — verify against your installed version's release notes.