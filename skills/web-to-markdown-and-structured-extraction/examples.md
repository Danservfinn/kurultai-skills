# Examples

## Example 1: Clean, filtered Markdown from a wiki page

Input: `https://en.wikipedia.org/wiki/Web_crawler`; goal is boilerplate-free Markdown for RAG.

```python
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

async def main():
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        markdown_generator=DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(threshold=0.48, threshold_type="fixed", min_word_threshold=0)
        ),
    )
    async with AsyncWebCrawler(config=BrowserConfig(headless=True)) as crawler:
        result = await crawler.arun(url="https://en.wikipedia.org/wiki/Web_crawler", config=run_config)
        print(len(result.markdown.raw_markdown), "chars raw")
        print(len(result.markdown.fit_markdown), "chars filtered")

asyncio.run(main())
```

If the `PruningContentFilter` import fails, list available filters first:
`python -c "from crawl4ai import content_filter_strategy; print(dir(content_filter_strategy))"`.

## Example 2: Structured quotes from an infinite-scroll page (no LLM)

Input: `https://quotes.toscrape.com/scroll`; extract text, author, tags as JSON.

```python
import asyncio, json
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, JsonCssExtractionStrategy

schema = {
    "name": "Quotes",
    "baseSelector": "div.quote",
    "fields": [
        {"name": "text", "selector": "span.text", "type": "text"},
        {"name": "author", "selector": "small.author", "type": "text"},
        {"name": "tags", "selector": "a.tag", "type": "list", "fields": [{"name": "tag", "type": "text"}]},
    ],
}

async def main():
    run_config = CrawlerRunConfig(
        extraction_strategy=JsonCssExtractionStrategy(schema),
        scan_full_page=True,
        scroll_delay=0.5,
        cache_mode=CacheMode.BYPASS,
    )
    async with AsyncWebCrawler(config=BrowserConfig(headless=True)) as crawler:
        result = await crawler.arun(url="https://quotes.toscrape.com/scroll", config=run_config)
        quotes = json.loads(result.extracted_content)
        print(f"Extracted {len(quotes)} quotes")

asyncio.run(main())
```

## Example 3: Docker server, one page to Markdown

Input: `https://news.ycombinator.com`; no Python script wanted.

```bash
export CRAWL4AI_API_TOKEN="$(openssl rand -hex 32)"
docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g \
  -e CRAWL4AI_API_TOKEN="$CRAWL4AI_API_TOKEN" unclecode/crawl4ai:latest
# wait ~10 s for startup
curl -s http://localhost:11235/md \
  -H "Authorization: Bearer $CRAWL4AI_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://news.ycombinator.com"}' | jq -r .markdown
```

For an LLM-assisted CLI query instead (requires key setup first):
```bash
crwl configs set llm.provider openai/gpt-4o-mini
crwl configs set llm.api_key "$OPENAI_API_KEY"
crwl https://www.example.com/products -q "Extract all product prices"