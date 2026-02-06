#!/usr/bin/env python3
"""
PIHS Data Job for GitHub Actions
=================================
Fetches PIHS trade values and loads to Neo4j, with update checking.

Designed to run in CI/CD environment with proper exit codes:
- Exit 0: Success or skipped (already up to date)
- Exit 1: Failure

Usage:
    python pihs_job.py                  # Run with update check
    python pihs_job.py --force          # Force refresh
    python pihs_job.py --dry-run        # Preview only
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from datetime import date, datetime

# Add parent directory to path for local imports
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

# Load environment variables - try multiple locations
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
    load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_for_updates(chart_type: str, league_type: str) -> bool:
    """
    Check if we need to fetch new data.

    Returns True if we should fetch (no data or outdated).
    """
    from load_pihs_neo4j import PIHSLoader

    loader = PIHSLoader(use_railway=True, use_http=True)

    try:
        latest_date = loader.check_existing_data(chart_type, league_type)

        if latest_date is None:
            logger.info(f"No existing PIHS data found for {chart_type}/{league_type}")
            return True

        # Parse the latest date
        today = date.today()

        # Handle Neo4j date format (might be ISO string or date object)
        if isinstance(latest_date, str):
            # Remove any time component
            latest_date = latest_date.split('T')[0]
            latest = date.fromisoformat(latest_date)
        else:
            latest = latest_date

        # Check if data is from today
        if latest >= today:
            logger.info(f"PIHS data already up to date (latest: {latest})")
            return False

        # For redraft, update if data is older than 1 day during NFL season
        # For dynasty, update if data is older than 7 days
        age_days = (today - latest).days

        if chart_type == "redraft":
            if age_days >= 1:
                logger.info(f"Redraft data is {age_days} days old, will refresh")
                return True
        else:  # dynasty
            if age_days >= 7:
                logger.info(f"Dynasty data is {age_days} days old, will refresh")
                return True

        logger.info(f"Data is recent ({age_days} days old), skipping refresh")
        return False

    except Exception as e:
        logger.warning(f"Error checking existing data: {e}")
        # On error, proceed with fetch
        return True
    finally:
        loader.close()


def run_pipeline(
    chart_type: str = "redraft",
    league_type: str = "superflex",
    scoring_format: str = "ppr",
    force: bool = False,
    dry_run: bool = False
) -> bool:
    """
    Run the PIHS pipeline.

    Returns True on success, False on failure.
    """
    from pihs_pipeline import PIHSPipeline

    # Check for updates unless forced
    if not force and not dry_run:
        needs_update = check_for_updates(chart_type, league_type)
        if not needs_update:
            logger.info("Skipping PIHS refresh - data is current")
            return True

    logger.info(f"Starting PIHS pipeline: {chart_type}/{league_type}/{scoring_format}")

    try:
        pipeline = PIHSPipeline(
            use_railway=True
        )

        stats = pipeline.run(
            chart_types=[chart_type],
            league_types=[league_type],
            scoring_formats=[scoring_format],
            force_refresh=force,
            dry_run=dry_run
        )

        # Log results
        logger.info("=" * 50)
        logger.info("PIHS Pipeline Results:")
        logger.info(f"  Charts fetched: {stats['charts_fetched']}")
        logger.info(f"  Charts parsed: {stats['charts_parsed']}")
        logger.info(f"  Players extracted: {stats['players_extracted']}")
        logger.info(f"  Nodes created: {stats['nodes_created']}")
        logger.info(f"  Players linked: {stats['players_linked']}")

        if stats['errors']:
            logger.warning(f"  Errors: {len(stats['errors'])}")

        # Success if we parsed at least one chart
        return stats['charts_parsed'] > 0

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        return False
    finally:
        pipeline.cleanup()


def main():
    parser = argparse.ArgumentParser(description="PIHS Data Job")
    parser.add_argument(
        '--type',
        choices=['redraft', 'dynasty'],
        default='redraft',
        help='Chart type to fetch'
    )
    parser.add_argument(
        '--league',
        choices=['superflex', '1qb'],
        default='superflex',
        help='League type'
    )
    parser.add_argument(
        '--format',
        choices=['ppr', 'half_ppr', 'standard'],
        default='ppr',
        help='Scoring format (redraft only)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force refresh even if data is current'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview without database changes'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable debug logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Check for required API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        logger.error("ANTHROPIC_API_KEY not set")
        sys.exit(1)

    success = run_pipeline(
        chart_type=args.type,
        league_type=args.league,
        scoring_format=args.format,
        force=args.force,
        dry_run=args.dry_run
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
