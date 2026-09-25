# Commands

Placeholders:
- `<url>` — target page URL
- `<query>` — natural-language extraction question for LLM mode
- `<provider>` — LiteLLM provider string, e.g. `openai/gpt-4o-mini`
- `<api_key>` — LLM provider API key
- `<n>` — numeric threshold or count

## Step 1 — install and verify

```bash
pip install -U crawl4ai
crawl4ai-setup
# fallback if browser setup fails:
python -m playwright install --with-deps chromium
crawl4ai-doctor
```

## Step 2 — CLI one-offs and LLM config

```bash
crwl <url> -o markdown
# LLM key setup for -q queries (note: subcommand is "configs"):
crwl configs set llm.provider <provider>
crwl configs set llm.api_key <api_key>
crwl <url> -q "<query>"
```

## Step 3 — programmatic crawl skeleton

```bash
cat > crawl.py <<'EOF'
import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def main():
    run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
    async with AsyncWebCrawler(config=BrowserConfig(headless=True)) as crawler:
        result = await crawler.arun(url="<url>", config=run_config)
        print(result.markdown.raw_markdown)

asyncio.run(main())
EOF
python crawl.py
```

## Step 4 — boilerplate filtering (verify filter class name if import fails)

```bash
python -c "from crawl4ai import content_filter_strategy; print([n for n in dir(content_filter_strategy) if 'Filter' in n])"
cat > crawl_fit.py <<'EOF'
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
        result = await crawler.arun(url="<url>", config=run_config)
        print(result.markdown.fit_markdown)

asyncio.run(main())
EOF
python crawl_fit.py
```

## Step 5 — CSS schema extraction (no LLM)

```bash
cat > extract_css.py <<'EOF'
import asyncio, json
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, JsonCssExtractionStrategy

schema = {
    "name": "Records",
    "baseSelector": "div.item",
    "fields": [{"name": "title", "selector": "h2", "type": "text"}],
}

async def main():
    run_config = CrawlerRunConfig(
        extraction_strategy=JsonCssExtractionStrategy(schema),
        scan_full_page=True,
        scroll_delay=0.5,
        cache_mode=CacheMode.BYPASS,
    )
    async with AsyncWebCrawler(config=BrowserConfig(headless=True)) as crawler:
        result = await crawler.arun(url="<url>", config=run_config)
        print(json.dumps(json.loads(result.extracted_content), indent=2))

asyncio.run(main())
EOF
python extract_css.py
```

## Step 6 — LLM extraction (requires OPENAI_API_KEY)

```bash
cat > extract_llm.py <<'EOF'
import os, asyncio, json
from pydantic import BaseModel, Field
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode, LLMConfig, LLMExtractionStrategy

class Record(BaseModel):
    name: str = Field(..., description="Record name.")
    value: str = Field(..., description="Record value.")

async def main():
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=LLMExtractionStrategy(
            llm_config=LLMConfig(provider="openai/gpt-4o-mini", api_token=os.getenv("OPENAI_API_KEY")),
            schema=Record.model_json_schema(),
            extraction_type="schema",
            instruction="Extract every record name with its value.",
        ),
    )
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url="<url>", config=run_config)
        print(result.extracted_content)

asyncio.run(main())
EOF
python extract_llm.py
```

## Step 7 — Docker server

```bash
export CRAWL4AI_API_TOKEN="$(openssl rand -hex 32)"
docker run -d -p 11235:11235 --name crawl4ai --shm-size=1g \
  -e CRAWL4AI_API_TOKEN="$CRAWL4AI_API_TOKEN" \
  unclecode/crawl4ai:latest
sleep 10
curl -s http://localhost:11235/md \
  -H "Authorization: Bearer $CRAWL4AI_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"url": "<url>"}' | jq -r .markdown