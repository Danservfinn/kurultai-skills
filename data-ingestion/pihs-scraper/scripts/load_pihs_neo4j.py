#!/usr/bin/env python3
"""
PIHS Neo4j Loader
=================
Load parsed PIHS trade value data into Neo4j graph database.

Creates PIHSValue nodes and links them to existing Player nodes.

Usage:
    python load_pihs_neo4j.py --input players.json
    python load_pihs_neo4j.py --input players.json --chart-type dynasty --league superflex
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Tuple

import httpx
from dotenv import load_dotenv

# Try to import neo4j, but it's optional for HTTP mode
try:
    from neo4j import GraphDatabase
    HAS_NEO4J_DRIVER = True
except ImportError:
    HAS_NEO4J_DRIVER = False

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


class PIHSLoader:
    """Load PIHS trade value data into Neo4j via HTTP Transaction API."""

    # Railway HTTP Transaction API endpoint
    RAILWAY_HTTP_URL = "https://sparkling-commitment-production.up.railway.app/db/neo4j/tx/commit"

    # Schema creation queries
    SCHEMA_QUERIES = [
        # Unique constraint on composite key
        """
        CREATE CONSTRAINT pihs_unique IF NOT EXISTS
        FOR (pv:PIHSValue)
        REQUIRE (pv.player_name, pv.chart_date, pv.chart_type, pv.league_type) IS UNIQUE
        """,
        # Indexes for common queries
        """
        CREATE INDEX pihs_player_idx IF NOT EXISTS
        FOR (pv:PIHSValue) ON (pv.player_name)
        """,
        """
        CREATE INDEX pihs_date_idx IF NOT EXISTS
        FOR (pv:PIHSValue) ON (pv.chart_date)
        """,
        """
        CREATE INDEX pihs_type_idx IF NOT EXISTS
        FOR (pv:PIHSValue) ON (pv.chart_type)
        """,
        """
        CREATE INDEX pihs_position_idx IF NOT EXISTS
        FOR (pv:PIHSValue) ON (pv.position)
        """,
    ]

    # Node creation query with MERGE for idempotency
    MERGE_NODE_QUERY = """
    MERGE (pv:PIHSValue {
        player_name: $player_name,
        chart_date: date($chart_date),
        chart_type: $chart_type,
        league_type: $league_type
    })
    SET pv.player_id = $player_id,
        pv.pihs_value = $pihs_value,
        pv.tier = $tier,
        pv.position = $position,
        pv.team = $team,
        pv.trend = $trend,
        pv.scoring_format = $scoring_format,
        pv.season = $season,
        pv.extracted_at = datetime()
    RETURN pv.player_name as name
    """

    # Link to existing Player nodes
    LINK_PLAYER_QUERY = """
    MATCH (pv:PIHSValue)
    WHERE pv.chart_date = date($chart_date)
      AND pv.chart_type = $chart_type
      AND pv.league_type = $league_type
    MATCH (p:Player)
    WHERE toLower(p.name) = toLower(pv.player_name)
       OR p.sleeper_id = pv.player_id
       OR p.gsis_id = pv.player_id
    MERGE (p)-[:HAS_PIHS_VALUE]->(pv)
    RETURN count(*) as linked
    """

    # Player ID resolution query
    RESOLVE_PLAYER_QUERY = """
    MATCH (p:Player)
    WHERE toLower(p.name) CONTAINS toLower($name_part)
      AND ($position IS NULL OR p.position = $position)
    RETURN p.name as name,
           p.gsis_id as gsis_id,
           p.sleeper_id as sleeper_id,
           p.position as position,
           p.team as team
    LIMIT 5
    """

    # Check for existing data query
    CHECK_EXISTING_QUERY = """
    MATCH (pv:PIHSValue)
    WHERE pv.chart_type = $chart_type AND pv.league_type = $league_type
    RETURN max(pv.chart_date) as latest_date, count(pv) as count
    """

    def __init__(
        self,
        uri: str = None,
        user: str = None,
        password: str = None,
        use_railway: bool = True,
        use_http: bool = True
    ):
        """
        Initialize the loader.

        Args:
            uri: Neo4j URI (default from env)
            user: Neo4j username (default from env)
            password: Neo4j password (default from env)
            use_railway: If True, use Railway production credentials
            use_http: If True, use HTTP Transaction API (required for Railway external access)
        """
        self.use_http = use_http
        self.use_railway = use_railway

        if use_railway:
            self.http_url = self.RAILWAY_HTTP_URL
            self.bolt_uri = "bolt://sparkling-commitment-production.up.railway.app:7687"
            self.user = user or os.getenv("NEO4J_USER", "neo4j")
            self.password = password or os.getenv("NEO4J_PASSWORD", "dynastyedge2025")
        else:
            self.http_url = uri or "http://localhost:7474/db/neo4j/tx/commit"
            self.bolt_uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
            self.user = user or os.getenv("NEO4J_USER", "neo4j")
            self.password = password or os.getenv("NEO4J_PASSWORD", "password")

        self._driver = None
        self._http_client = None
        self.stats = {
            'nodes_created': 0,
            'nodes_updated': 0,
            'players_linked': 0,
            'unmatched': [],
            'skipped_existing': False
        }

    def _execute_http(self, query: str, parameters: Dict = None) -> List[Dict]:
        """Execute a Cypher query via HTTP Transaction API."""
        statement = {"statement": query}
        if parameters:
            statement["parameters"] = parameters

        response = httpx.post(
            self.http_url,
            json={"statements": [statement]},
            auth=(self.user, self.password),
            headers={"Content-Type": "application/json"},
            timeout=60.0,
        )
        response.raise_for_status()
        data = response.json()

        # Check for Neo4j errors
        if data.get("errors"):
            error = data["errors"][0]
            raise Exception(f"Neo4j error: {error.get('message', 'Unknown error')}")

        # Parse results into list of dicts
        results = []
        if data.get("results") and data["results"][0].get("data"):
            columns = data["results"][0]["columns"]
            for row_data in data["results"][0]["data"]:
                row = row_data["row"]
                results.append(dict(zip(columns, row)))

        return results

    def _execute_query(self, query: str, parameters: Dict = None) -> List[Dict]:
        """Execute a query using either HTTP or Bolt."""
        if self.use_http:
            return self._execute_http(query, parameters)
        else:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                return [dict(record) for record in result]

    @property
    def driver(self):
        """Lazy Bolt driver initialization (only if not using HTTP)."""
        if self._driver is None and not self.use_http:
            if not HAS_NEO4J_DRIVER:
                raise ImportError("neo4j driver not installed. Use use_http=True or install neo4j package.")
            logger.info(f"Connecting to Neo4j: {self.bolt_uri}")
            self._driver = GraphDatabase.driver(
                self.bolt_uri,
                auth=(self.user, self.password)
            )
            self._driver.verify_connectivity()
            logger.info("Connected to Neo4j")
        return self._driver

    def close(self):
        """Close the driver connection."""
        if self._driver:
            self._driver.close()
            self._driver = None

    def create_schema(self) -> None:
        """Create indexes and constraints for PIHSValue nodes."""
        logger.info("Creating PIHS schema...")
        for query in self.SCHEMA_QUERIES:
            try:
                self._execute_query(query)
            except Exception as e:
                # Ignore "already exists" errors
                if "already exists" not in str(e).lower():
                    logger.warning(f"Schema query warning: {e}")

        logger.info("Schema created/verified")

    def check_existing_data(self, chart_type: str, league_type: str) -> Optional[str]:
        """
        Check if we already have data for this chart type.

        Returns:
            Latest chart date string if exists, None otherwise
        """
        try:
            results = self._execute_query(
                self.CHECK_EXISTING_QUERY,
                {'chart_type': chart_type, 'league_type': league_type}
            )
            if results and results[0].get('latest_date'):
                return results[0]['latest_date']
        except Exception as e:
            logger.warning(f"Error checking existing data: {e}")
        return None

    def resolve_player_id(
        self,
        player_name: str,
        position: str = None
    ) -> Optional[str]:
        """
        Try to resolve a player name to a gsis_id or sleeper_id.

        Args:
            player_name: Player name to match
            position: Optional position to filter

        Returns:
            Resolved player ID or None
        """
        # Normalize name for matching
        name_parts = player_name.lower().replace("'", "").replace(".", "").split()

        if len(name_parts) < 2:
            return None

        # Try last name first (most unique)
        last_name = name_parts[-1]

        try:
            matches = self._execute_query(
                self.RESOLVE_PLAYER_QUERY,
                {'name_part': last_name, 'position': position}
            )

            if len(matches) == 1:
                # Unique match
                match = matches[0]
                logger.debug(f"Matched {player_name} -> {match['name']}")
                return match.get('gsis_id') or match.get('sleeper_id')

            elif len(matches) > 1:
                # Multiple matches - try full name
                for match in matches:
                    if match['name'].lower() == player_name.lower():
                        return match.get('gsis_id') or match.get('sleeper_id')

                # Try first name + last name match
                first_name = name_parts[0]
                for match in matches:
                    match_parts = match['name'].lower().split()
                    if len(match_parts) >= 2:
                        if first_name == match_parts[0] and last_name == match_parts[-1]:
                            return match.get('gsis_id') or match.get('sleeper_id')
        except Exception as e:
            logger.debug(f"Error resolving player {player_name}: {e}")

        return None

    def load_players(
        self,
        players: List[Dict[str, Any]],
        chart_type: str,
        league_type: str,
        scoring_format: str = "ppr",
        chart_date: str = None,
        dry_run: bool = False
    ) -> int:
        """
        Load player data into Neo4j.

        Args:
            players: List of player dictionaries from parser
            chart_type: "redraft" or "dynasty"
            league_type: "superflex" or "1qb"
            scoring_format: "ppr", "half_ppr", or "standard"
            chart_date: ISO date string (default: today)
            dry_run: If True, don't write to database

        Returns:
            Number of nodes created/updated
        """
        if not players:
            logger.warning("No players to load")
            return 0

        chart_date = chart_date or date.today().isoformat()
        season = int(chart_date[:4])

        logger.info(f"Loading {len(players)} players ({chart_type}/{league_type}/{scoring_format})")

        if dry_run:
            logger.info("DRY RUN - no database changes will be made")
            for player in players[:10]:
                logger.info(f"  Would load: {player.get('player_name')} = {player.get('value')}")
            return 0

        # Ensure schema exists
        self.create_schema()

        count = 0
        for player in players:
            player_name = player.get('player_name')
            if not player_name:
                continue

            # Try to resolve player ID
            player_id = self.resolve_player_id(
                player_name,
                player.get('position')
            )

            if not player_id:
                self.stats['unmatched'].append(player_name)

            # Prepare parameters
            params = {
                'player_name': player_name,
                'player_id': player_id,
                'chart_date': chart_date,
                'chart_type': chart_type,
                'league_type': league_type,
                'scoring_format': scoring_format,
                'pihs_value': player.get('value'),
                'tier': player.get('tier'),
                'position': player.get('position'),
                'team': player.get('team'),
                'trend': player.get('trend', 'stable'),
                'season': season
            }

            try:
                result = self._execute_query(self.MERGE_NODE_QUERY, params)
                if result:
                    count += 1
            except Exception as e:
                logger.error(f"Error loading {player_name}: {e}")
                continue

        self.stats['nodes_created'] = count
        logger.info(f"Loaded {count} PIHSValue nodes")

        # Link to Player nodes
        linked = self._link_to_players(chart_date, chart_type, league_type)
        self.stats['players_linked'] = linked

        return count

    def _link_to_players(
        self,
        chart_date: str,
        chart_type: str,
        league_type: str
    ) -> int:
        """Create relationships from Player nodes to PIHSValue nodes."""
        logger.info("Linking PIHSValue nodes to Player nodes...")

        try:
            results = self._execute_query(
                self.LINK_PLAYER_QUERY,
                {
                    'chart_date': chart_date,
                    'chart_type': chart_type,
                    'league_type': league_type
                }
            )
            linked = results[0]['linked'] if results else 0
        except Exception as e:
            logger.error(f"Error linking players: {e}")
            linked = 0

        logger.info(f"Linked {linked} players")
        return linked

    def get_stats(self) -> Dict[str, Any]:
        """Get loading statistics."""
        stats = self.stats.copy()
        stats['match_rate'] = 1.0 - (len(stats['unmatched']) / max(1, stats['nodes_created']))
        return stats

    def load_from_file(
        self,
        json_path: Path,
        chart_type: str = None,
        league_type: str = None,
        **kwargs
    ) -> int:
        """
        Load players from a JSON file.

        Args:
            json_path: Path to JSON file from parser
            chart_type: Override chart type
            league_type: Override league type

        Returns:
            Number of nodes created
        """
        with open(json_path) as f:
            data = json.load(f)

        players = data.get('players', data if isinstance(data, list) else [])

        # Try to infer chart type from filename if not provided
        if not chart_type:
            name = json_path.stem.lower()
            if 'dynasty' in name:
                chart_type = 'dynasty'
            elif 'redraft' in name:
                chart_type = 'redraft'
            else:
                chart_type = 'dynasty'  # Default

        if not league_type:
            name = json_path.stem.lower()
            if 'sf' in name or 'superflex' in name:
                league_type = 'superflex'
            elif '1qb' in name:
                league_type = '1qb'
            else:
                league_type = 'superflex'  # Default

        return self.load_players(players, chart_type, league_type, **kwargs)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Load PIHS trade value data into Neo4j"
    )
    parser.add_argument(
        '--input',
        type=Path,
        required=True,
        help='Input JSON file with parsed player data'
    )
    parser.add_argument(
        '--chart-type',
        choices=['redraft', 'dynasty'],
        help='Chart type (inferred from filename if not specified)'
    )
    parser.add_argument(
        '--league',
        choices=['superflex', '1qb'],
        help='League type (inferred from filename if not specified)'
    )
    parser.add_argument(
        '--format',
        choices=['ppr', 'half_ppr', 'standard'],
        default='ppr',
        help='Scoring format'
    )
    parser.add_argument(
        '--date',
        help='Chart date (ISO format, default: today)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without writing to database'
    )
    parser.add_argument(
        '--local',
        action='store_true',
        help='Use local Neo4j instead of Railway'
    )
    parser.add_argument(
        '--uri',
        help='Neo4j URI (overrides default)'
    )

    args = parser.parse_args()

    # Initialize loader
    loader = PIHSLoader(
        uri=args.uri,
        use_railway=not args.local
    )

    try:
        # Load data
        count = loader.load_from_file(
            args.input,
            chart_type=args.chart_type,
            league_type=args.league,
            scoring_format=args.format,
            chart_date=args.date,
            dry_run=args.dry_run
        )

        # Print stats
        stats = loader.get_stats()
        print(f"\nLoading complete:")
        print(f"  Nodes created/updated: {stats['nodes_created']}")
        print(f"  Players linked: {stats['players_linked']}")
        print(f"  Match rate: {stats['match_rate']:.1%}")

        if stats['unmatched']:
            print(f"\n  Unmatched players ({len(stats['unmatched'])}):")
            for name in stats['unmatched'][:10]:
                print(f"    - {name}")
            if len(stats['unmatched']) > 10:
                print(f"    ... and {len(stats['unmatched']) - 10} more")

    finally:
        loader.close()


if __name__ == "__main__":
    main()
