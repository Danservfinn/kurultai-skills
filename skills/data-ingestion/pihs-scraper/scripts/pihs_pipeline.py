#!/usr/bin/env python3
"""
PIHS Data Pipeline
==================
Full ETL pipeline for PeakedInHighSkool trade value data.

Orchestrates: Fetch -> Parse -> Load workflow.

Usage:
    python pihs_pipeline.py                           # Run full pipeline
    python pihs_pipeline.py --type dynasty            # Dynasty only
    python pihs_pipeline.py --type redraft --dry-run  # Preview redraft
    python pihs_pipeline.py --force                   # Force refresh
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime, date
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv

# Import local modules
from fetch_pihs_charts import PIHSChartFetcher
from parse_pihs_chart import PIHSChartParser
from load_pihs_neo4j import PIHSLoader

# Load environment variables - check multiple locations
env_paths = [
    Path.home() / "ktcvaluehog" / ".env",
    Path("/Users/kurultai/ktcvaluehog/.env"),
    Path.cwd() / ".env",
]
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        break
else:
    load_dotenv()  # Try default

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PIHSPipeline:
    """
    Full ETL pipeline for PIHS trade value data.

    Workflow:
    1. Fetch chart images from website
    2. Parse with AI vision to extract structured data
    3. Load into Neo4j graph database
    """

    def __init__(
        self,
        cache_dir: Path = None,
        anthropic_key: str = None,
        use_railway: bool = True
    ):
        """
        Initialize the pipeline.

        Args:
            cache_dir: Directory for caching chart images
            anthropic_key: Anthropic API key for vision parsing
            use_railway: Use Railway Neo4j (True) or local (False)
        """
        self.cache_dir = Path(cache_dir or "data/raw/pihs")
        self.output_dir = Path("data/processed/pihs")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.fetcher = PIHSChartFetcher(cache_dir=self.cache_dir)
        self.parser = PIHSChartParser(anthropic_key=anthropic_key)
        self.loader = PIHSLoader(use_railway=use_railway)

        # Pipeline statistics
        self.stats = {
            'charts_fetched': 0,
            'charts_parsed': 0,
            'players_extracted': 0,
            'nodes_created': 0,
            'players_linked': 0,
            'errors': [],
            'start_time': None,
            'end_time': None
        }

    def run(
        self,
        chart_types: List[str] = None,
        league_types: List[str] = None,
        scoring_formats: List[str] = None,
        force_refresh: bool = False,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Execute the full pipeline.

        Args:
            chart_types: List of chart types ["dynasty", "redraft"]
            league_types: List of league types ["superflex", "1qb"]
            scoring_formats: List of scoring formats (for redraft)
            force_refresh: Force re-fetch even if cached
            dry_run: Don't write to database

        Returns:
            Pipeline statistics dictionary
        """
        self.stats['start_time'] = datetime.now()

        # Defaults
        chart_types = chart_types or ["dynasty", "redraft"]
        league_types = league_types or ["superflex"]
        scoring_formats = scoring_formats or ["ppr"]

        logger.info(f"Starting PIHS pipeline")
        logger.info(f"  Chart types: {chart_types}")
        logger.info(f"  League types: {league_types}")
        logger.info(f"  Force refresh: {force_refresh}")
        logger.info(f"  Dry run: {dry_run}")

        chart_date = date.today().isoformat()

        for chart_type in chart_types:
            for league_type in league_types:
                # Determine scoring formats (only for redraft)
                formats = scoring_formats if chart_type == "redraft" else ["ppr"]

                for scoring_format in formats:
                    try:
                        self._process_chart(
                            chart_type=chart_type,
                            league_type=league_type,
                            scoring_format=scoring_format,
                            chart_date=chart_date,
                            force_refresh=force_refresh,
                            dry_run=dry_run
                        )
                    except Exception as e:
                        error_msg = f"Error processing {chart_type}/{league_type}: {e}"
                        logger.error(error_msg)
                        self.stats['errors'].append(error_msg)

        self.stats['end_time'] = datetime.now()
        self._log_summary()

        return self.stats

    def _process_chart(
        self,
        chart_type: str,
        league_type: str,
        scoring_format: str,
        chart_date: str,
        force_refresh: bool,
        dry_run: bool
    ) -> None:
        """Process a single chart through the pipeline."""
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {chart_type} / {league_type} / {scoring_format}")
        logger.info(f"{'='*60}")

        # Step 1: Fetch chart
        logger.info("Step 1: Fetching chart...")
        if chart_type == "dynasty":
            chart_path = self.fetcher.fetch_dynasty_chart(
                league_type=league_type,
                force_refresh=force_refresh
            )
        else:
            chart_path = self.fetcher.fetch_redraft_chart(
                format=scoring_format,
                force_refresh=force_refresh
            )

        if not chart_path:
            raise Exception(f"Failed to fetch {chart_type} chart")

        self.stats['charts_fetched'] += 1
        logger.info(f"  Chart saved: {chart_path}")

        # Step 2: Parse chart with AI vision
        logger.info("Step 2: Parsing chart with AI vision...")
        players, errors = self.parser.parse_and_validate(chart_path)

        if not players:
            raise Exception(f"No players extracted from chart")

        self.stats['charts_parsed'] += 1
        self.stats['players_extracted'] += len(players)
        self.stats['errors'].extend(errors)

        logger.info(f"  Extracted {len(players)} players")
        if errors:
            logger.warning(f"  {len(errors)} validation warnings")

        # Save parsed data
        output_file = self.output_dir / f"pihs_{chart_type}_{league_type}_{chart_date}.json"
        self._save_parsed_data(players, output_file, chart_path, chart_type, league_type)
        logger.info(f"  Saved to: {output_file}")

        # Step 3: Load to Neo4j
        logger.info("Step 3: Loading to Neo4j...")
        if dry_run:
            logger.info("  DRY RUN - skipping database load")
            return

        count = self.loader.load_players(
            players=players,
            chart_type=chart_type,
            league_type=league_type,
            scoring_format=scoring_format,
            chart_date=chart_date
        )

        loader_stats = self.loader.get_stats()
        self.stats['nodes_created'] += loader_stats['nodes_created']
        self.stats['players_linked'] += loader_stats['players_linked']

        logger.info(f"  Loaded {count} nodes")
        logger.info(f"  Linked {loader_stats['players_linked']} to Player nodes")

    def _save_parsed_data(
        self,
        players: List[Dict],
        output_path: Path,
        source_path: Path,
        chart_type: str,
        league_type: str
    ) -> None:
        """Save parsed player data to JSON file."""
        data = {
            'extracted_at': datetime.now().isoformat(),
            'source_image': str(source_path),
            'chart_type': chart_type,
            'league_type': league_type,
            'player_count': len(players),
            'players': players
        }

        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

    def _log_summary(self) -> None:
        """Log pipeline summary."""
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()

        logger.info(f"\n{'='*60}")
        logger.info("PIHS Pipeline Complete")
        logger.info(f"{'='*60}")
        logger.info(f"  Duration: {duration:.1f} seconds")
        logger.info(f"  Charts fetched: {self.stats['charts_fetched']}")
        logger.info(f"  Charts parsed: {self.stats['charts_parsed']}")
        logger.info(f"  Players extracted: {self.stats['players_extracted']}")
        logger.info(f"  Nodes created: {self.stats['nodes_created']}")
        logger.info(f"  Players linked: {self.stats['players_linked']}")

        if self.stats['errors']:
            logger.warning(f"  Errors/Warnings: {len(self.stats['errors'])}")

        # Calculate match rate
        if self.stats['nodes_created'] > 0:
            match_rate = self.stats['players_linked'] / self.stats['nodes_created']
            logger.info(f"  Match rate: {match_rate:.1%}")

    def cleanup(self) -> None:
        """Clean up resources."""
        self.loader.close()


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PIHS Fantasy Football Data Pipeline"
    )
    parser.add_argument(
        '--type',
        choices=['dynasty', 'redraft', 'all'],
        default='all',
        help='Chart type to process'
    )
    parser.add_argument(
        '--league',
        choices=['superflex', '1qb', 'both'],
        default='superflex',
        help='League type to process'
    )
    parser.add_argument(
        '--format',
        choices=['ppr', 'half_ppr', 'standard'],
        default='ppr',
        help='Scoring format for redraft charts'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force refresh, bypass cache'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Parse charts but do not write to database'
    )
    parser.add_argument(
        '--local',
        action='store_true',
        help='Use local Neo4j instead of Railway'
    )
    parser.add_argument(
        '--cache-dir',
        type=Path,
        default=Path("data/raw/pihs"),
        help='Cache directory for chart images'
    )
    parser.add_argument(
        '--api-key',
        help='Anthropic API key (or set ANTHROPIC_API_KEY)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Determine chart types
    if args.type == 'all':
        chart_types = ['dynasty', 'redraft']
    else:
        chart_types = [args.type]

    # Determine league types
    if args.league == 'both':
        league_types = ['superflex', '1qb']
    else:
        league_types = [args.league]

    # Initialize and run pipeline
    pipeline = PIHSPipeline(
        cache_dir=args.cache_dir,
        anthropic_key=args.api_key,
        use_railway=not args.local
    )

    try:
        stats = pipeline.run(
            chart_types=chart_types,
            league_types=league_types,
            scoring_formats=[args.format],
            force_refresh=args.force,
            dry_run=args.dry_run
        )

        # Exit with error if there were failures
        if stats['errors'] and stats['charts_parsed'] == 0:
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("\nPipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)
    finally:
        pipeline.cleanup()


if __name__ == "__main__":
    main()
