---
name: pihs-scraper
description: Scrape PeakedInHighSkool (PIHS) fantasy football trade value charts and load into Neo4j. Use when fetching PIHS data, extracting player values from trade charts, refreshing dynasty/redraft values, or syncing PIHS trade values to the graph database.
---

# PIHS Fantasy Football Trade Value Scraper

Scrape trade value charts from [PeakedInHighSkool](https://peakedinhighskool.com/) and load structured data into Neo4j. Supports both dynasty (monthly) and redraft (weekly) charts in 1QB and Superflex formats.

## When to Use This Skill

- Refresh PIHS trade values in the database
- Fetch weekly redraft trade value charts
- Fetch monthly dynasty trade value charts
- Compare PIHS values to KTC values
- Track player value trends from PIHS source

## Quick Start

```bash
# Run full pipeline (fetch, parse, load)
python .claude/skills/data-ingestion/pihs-scraper/scripts/pihs_pipeline.py

# Fetch specific chart type
python .claude/skills/data-ingestion/pihs-scraper/scripts/pihs_pipeline.py --type dynasty --format superflex

# Dry run (no database writes)
python .claude/skills/data-ingestion/pihs-scraper/scripts/pihs_pipeline.py --dry-run
```

## Data Source

**Website: peakedinhighskool.com** (Recommended)
- Weekly redraft charts: https://peakedinhighskool.com/fantasy-trade-value-chart/
- Dynasty charts: https://peakedinhighskool.com/dynasty-trade-value-charts/
- Data delivered as PNG chart images
- Uses Claude vision API to extract structured data

## Workflow

### Step 1: Fetch Chart Images

Download current charts from the website. Charts are cached locally to avoid redundant fetches.

```python
from scripts.fetch_pihs_charts import PIHSChartFetcher
from pathlib import Path

fetcher = PIHSChartFetcher(cache_dir=Path("data/raw/pihs"))

# Fetch redraft chart (weekly during NFL season)
redraft_path = fetcher.fetch_redraft_chart(format="ppr")

# Fetch dynasty chart (monthly)
dynasty_path = fetcher.fetch_dynasty_chart(league_type="superflex")
```

**Cache location:** `data/raw/pihs/pihs_{type}_{format}_{date}.png`

**Cache validity:**
- Redraft: 24 hours (updates weekly on Tuesday)
- Dynasty: 7 days (updates monthly)

### Step 2: Parse with AI Vision

Extract structured data from chart images using Claude's vision API.

```python
from scripts.parse_pihs_chart import PIHSChartParser
import os

parser = PIHSChartParser(anthropic_key=os.getenv("ANTHROPIC_API_KEY"))

# Parse chart image
players = parser.parse_chart(chart_path)

# Validate extraction
valid_players, errors = parser.validate_extraction(players)
```

**Expected output format:**
```python
[
    {
        "player_name": "Ja'Marr Chase",
        "position": "WR",
        "team": "CIN",
        "value": 95,
        "tier": 1,
        "trend": "stable"
    },
    {
        "player_name": "CeeDee Lamb",
        "position": "WR",
        "team": "DAL",
        "value": 94,
        "tier": 1,
        "trend": "up"
    }
]
```

### Step 3: Load to Neo4j

Create PIHSValue nodes and link to existing Player nodes.

```python
from scripts.load_pihs_neo4j import PIHSLoader

loader = PIHSLoader(use_railway=True)  # Or False for local Neo4j

# Load parsed data
count = loader.load_players(
    players=valid_players,
    chart_type="dynasty",
    league_type="superflex",
    chart_date="2025-12-20"
)

print(f"Loaded {count} players")
```

### Step 4: Query PIHS Data

After loading, query PIHS values in Neo4j:

```cypher
-- Get all PIHS dynasty values
MATCH (pv:PIHSValue)
WHERE pv.chart_type = 'dynasty'
RETURN pv.player_name, pv.position, pv.pihs_value, pv.tier
ORDER BY pv.pihs_value DESC
LIMIT 50

-- Compare PIHS to KTC values
MATCH (p:Player)-[:HAS_PIHS_VALUE]->(pv:PIHSValue)
WHERE p.ktc_value IS NOT NULL AND pv.chart_type = 'dynasty'
RETURN p.name,
       p.ktc_value as ktc,
       pv.pihs_value as pihs,
       p.ktc_value - pv.pihs_value as diff
ORDER BY ABS(p.ktc_value - pv.pihs_value) DESC
LIMIT 20

-- Find trending players (PIHS trend up)
MATCH (pv:PIHSValue)
WHERE pv.trend = 'up'
RETURN pv.player_name, pv.position, pv.pihs_value, pv.tier
ORDER BY pv.pihs_value DESC
```

## Full Pipeline

For automated data refresh, use the orchestrator:

```python
from scripts.pihs_pipeline import PIHSPipeline

pipeline = PIHSPipeline()

results = pipeline.run(
    chart_types=["redraft", "dynasty"],
    league_types=["superflex", "1qb"],
    force_refresh=False  # Set True to bypass cache
)

print(f"Charts fetched: {results['charts_fetched']}")
print(f"Players extracted: {results['players_extracted']}")
print(f"Nodes created: {results['nodes_created']}")
print(f"Match rate: {results['match_rate']:.1%}")
```

## Neo4j Schema

### PIHSValue Node
```cypher
(:PIHSValue {
    player_name: STRING,        // Full player name
    player_id: STRING,          // Resolved gsis_id or sleeper_id
    pihs_value: INTEGER,        // Trade value (0-100 scale)
    tier: INTEGER,              // Tier number (1-10)
    chart_type: STRING,         // "redraft" or "dynasty"
    league_type: STRING,        // "1qb" or "superflex"
    scoring_format: STRING,     // "ppr", "half_ppr", "std"
    position: STRING,           // QB, RB, WR, TE
    team: STRING,               // Team abbreviation
    trend: STRING,              // "up", "down", "stable"
    chart_date: DATE,           // Date of chart
    season: INTEGER,            // NFL season year
    extracted_at: DATETIME      // Extraction timestamp
})
```

### Relationship
```cypher
(p:Player)-[:HAS_PIHS_VALUE]->(pv:PIHSValue)
```

## Scheduling

| Chart Type | Frequency | When to Run | Cron |
|------------|-----------|-------------|------|
| Redraft | Weekly | Tuesday 6 AM during NFL season (Sep-Feb) | `0 6 * 9-2 2` |
| Dynasty | Monthly | 1st of each month at 6 AM | `0 6 1 * *` |

## Environment Variables

Required environment variables (set in your `.env` file):

```bash
# Required API keys and database credentials
ANTHROPIC_API_KEY=your_anthropic_api_key_here
NEO4J_URI=bolt://your-neo4j-host:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password_here
```

**To use**: Run scripts from your project directory:

```bash
python ~/.claude/skills/data-ingestion/pihs-scraper/scripts/pihs_pipeline.py
```

## Error Handling

### Chart Fetch Failures
If the website is unavailable or chart URLs change:
1. Check if website structure changed
2. Update `fetch_pihs_charts.py` selectors
3. Use cached data if available

### Vision Extraction Errors
If AI extraction returns invalid data:
1. Check chart image quality
2. Review extraction prompt in `parse_pihs_chart.py`
3. Validate against expected tier/value ranges

### Player Matching Failures
If players don't match existing database:
1. Check name normalization (Jr., III, etc.)
2. Review unmatched players list
3. Update `player_matching.md` with new variations

## Dependencies

```
requests>=2.28.0
beautifulsoup4>=4.12.0
anthropic>=0.18.0
pandas>=2.0.0
neo4j>=5.0.0
tenacity>=8.0.0
Pillow>=10.0.0
python-dotenv>=1.0.0
```

## Reference Documentation

- [references/chart_format.md](references/chart_format.md) - Chart layout and tier structure
- [references/player_matching.md](references/player_matching.md) - Name resolution strategies

## Integration with ktcvaluehog

This skill integrates with the ktcvaluehog project:
- Uses `BaseIngester` pattern from `scripts/data_jobs/base_ingester.py`
- Uses `IDResolver` for player matching from `src/loaders/id_resolver.py`
- Creates nodes compatible with existing Player schema
- Can be scheduled alongside KTC data refreshes
