#!/usr/bin/env python3
"""
PIHS Chart Parser
=================
Extract structured data from trade value chart images using Claude vision API.

Usage:
    python parse_pihs_chart.py --image data/raw/pihs/chart.png
    python parse_pihs_chart.py --image chart.png --output players.json
"""

import os
import sys
import json
import base64
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime

import anthropic
from PIL import Image

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Valid NFL teams for validation
VALID_NFL_TEAMS = {
    'ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE',
    'DAL', 'DEN', 'DET', 'GB', 'HOU', 'IND', 'JAX', 'KC',
    'LAC', 'LAR', 'LV', 'MIA', 'MIN', 'NE', 'NO', 'NYG',
    'NYJ', 'PHI', 'PIT', 'SEA', 'SF', 'TB', 'TEN', 'WAS',
    # Common variations
    'LA', 'JAC', 'WSH', 'GBP', 'SFO', 'TBB', 'NOR', 'NEP'
}

# Valid fantasy positions
VALID_POSITIONS = {'QB', 'RB', 'WR', 'TE', 'K', 'DST', 'DEF'}


class PIHSChartParser:
    """Parse PIHS trade value chart images using Claude vision API."""

    # Extraction prompt for the vision model
    EXTRACTION_PROMPT = """Analyze this fantasy football trade value chart and extract ALL player data visible in the image.

For EACH player you can see, extract:
- player_name: Full name exactly as shown (e.g., "Ja'Marr Chase", "CeeDee Lamb")
- position: Two or three letter position code (QB, RB, WR, TE)
- team: NFL team abbreviation (e.g., CIN, DAL, KC)
- value: The numeric trade value shown (typically 0-100 scale)
- tier: Which tier/section number they appear in (1 = highest tier)
- trend: Direction indicator if shown ("up", "down", or "stable" if no indicator)

Return the data as a JSON array. Example format:
[
  {"player_name": "Ja'Marr Chase", "position": "WR", "team": "CIN", "value": 95, "tier": 1, "trend": "stable"},
  {"player_name": "CeeDee Lamb", "position": "WR", "team": "DAL", "value": 94, "tier": 1, "trend": "up"},
  {"player_name": "Tyreek Hill", "position": "WR", "team": "MIA", "value": 88, "tier": 2, "trend": "down"}
]

Important instructions:
1. Extract ALL players visible in the chart, not just a sample
2. Maintain the order they appear (top to bottom, left to right within tiers)
3. If a value is partially obscured, make your best estimate
4. If trend arrows are not visible, use "stable"
5. Use standard 2-3 letter team abbreviations
6. Include tier number based on visual grouping in the chart
7. Return ONLY the JSON array, no other text or explanation"""

    def __init__(self, anthropic_key: str = None):
        """
        Initialize the parser.

        Args:
            anthropic_key: Anthropic API key. If not provided, uses ANTHROPIC_API_KEY env var.
        """
        self.api_key = anthropic_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable or anthropic_key parameter required")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"  # Vision-capable model

    def _encode_image(self, image_path: Path) -> Tuple[str, str]:
        """
        Encode image to base64 for API.

        Returns:
            Tuple of (base64_data, media_type)
        """
        path = Path(image_path)

        # Determine media type
        suffix = path.suffix.lower()
        media_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.webp': 'image/webp',
            '.gif': 'image/gif'
        }
        media_type = media_types.get(suffix, 'image/png')

        # Read and encode
        with open(path, 'rb') as f:
            image_data = f.read()

        base64_data = base64.standard_b64encode(image_data).decode('utf-8')

        logger.info(f"Encoded image: {path.name} ({len(image_data) / 1024:.1f} KB)")
        return base64_data, media_type

    def _resize_if_needed(self, image_path: Path, max_size: int = 4096) -> Path:
        """
        Resize image if it exceeds max dimensions.

        Returns path to resized image (may be same as input).
        """
        with Image.open(image_path) as img:
            width, height = img.size

            if width <= max_size and height <= max_size:
                return image_path

            # Calculate new dimensions
            ratio = min(max_size / width, max_size / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)

            logger.info(f"Resizing image from {width}x{height} to {new_width}x{new_height}")

            # Resize and save to temp location
            resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            resized_path = image_path.parent / f"resized_{image_path.name}"
            resized.save(resized_path, quality=95)

            return resized_path

    def parse_chart(self, image_path: Path) -> List[Dict[str, Any]]:
        """
        Extract player data from a chart image.

        Args:
            image_path: Path to the chart image file

        Returns:
            List of player dictionaries with extracted data
        """
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {path}")

        logger.info(f"Parsing chart: {path}")

        # Resize if needed for API limits
        processed_path = self._resize_if_needed(path)

        # Encode image
        base64_data, media_type = self._encode_image(processed_path)

        # Call Claude vision API
        logger.info("Calling Claude vision API...")
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=8192,  # Large to handle many players
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": base64_data
                            }
                        },
                        {
                            "type": "text",
                            "text": self.EXTRACTION_PROMPT
                        }
                    ]
                }]
            )
        except anthropic.APIError as e:
            logger.error(f"API error: {e}")
            raise

        # Extract response text
        response_text = response.content[0].text.strip()
        logger.debug(f"Raw response: {response_text[:500]}...")

        # Parse JSON from response
        try:
            # Handle potential markdown code blocks
            if response_text.startswith("```"):
                # Extract JSON from code block
                lines = response_text.split('\n')
                json_lines = []
                in_block = False
                for line in lines:
                    if line.startswith("```json"):
                        in_block = True
                        continue
                    elif line.startswith("```"):
                        in_block = False
                        continue
                    elif in_block:
                        json_lines.append(line)
                response_text = '\n'.join(json_lines)

            players = json.loads(response_text)

            if not isinstance(players, list):
                raise ValueError(f"Expected list, got {type(players)}")

            logger.info(f"Extracted {len(players)} players from chart")
            return players

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response_text[:500]}...")
            return []

    def validate_extraction(
        self,
        players: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Validate and clean extracted player data.

        Args:
            players: List of extracted player dictionaries

        Returns:
            Tuple of (valid_players, list_of_errors)
        """
        valid = []
        errors = []

        for i, player in enumerate(players):
            player_errors = []

            # Check required fields
            if not player.get('player_name'):
                player_errors.append(f"Player {i}: Missing player_name")
                continue

            name = player.get('player_name', 'Unknown')

            # Validate position
            position = player.get('position', '').upper()
            if position not in VALID_POSITIONS:
                player_errors.append(f"{name}: Invalid position '{position}'")
                # Try to fix common issues
                if position in ['DST', 'DEF', 'D/ST']:
                    player['position'] = 'DST'
                else:
                    player['position'] = None

            # Validate team
            team = player.get('team', '').upper()
            if team and team not in VALID_NFL_TEAMS:
                player_errors.append(f"{name}: Unknown team '{team}'")
                # Normalize common variations
                team_fixes = {'LA': 'LAR', 'JAC': 'JAX', 'WSH': 'WAS'}
                player['team'] = team_fixes.get(team, team)

            # Validate value
            value = player.get('value')
            if value is not None:
                try:
                    value = int(value)
                    if value < 0 or value > 150:  # Allow some buffer
                        player_errors.append(f"{name}: Value out of range ({value})")
                    player['value'] = value
                except (TypeError, ValueError):
                    player_errors.append(f"{name}: Invalid value '{value}'")
                    player['value'] = None

            # Validate tier
            tier = player.get('tier')
            if tier is not None:
                try:
                    tier = int(tier)
                    if tier < 1 or tier > 20:
                        player_errors.append(f"{name}: Tier out of range ({tier})")
                    player['tier'] = tier
                except (TypeError, ValueError):
                    player['tier'] = None

            # Normalize trend
            trend = player.get('trend', 'stable').lower()
            if trend not in ['up', 'down', 'stable']:
                trend = 'stable'
            player['trend'] = trend

            # Add to valid list if essential fields present
            if player.get('player_name') and player.get('value') is not None:
                valid.append(player)
            else:
                player_errors.append(f"{name}: Missing essential fields")

            errors.extend(player_errors)

        logger.info(f"Validation: {len(valid)} valid, {len(errors)} issues")
        return valid, errors

    def parse_and_validate(
        self,
        image_path: Path
    ) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        Parse chart and validate in one call.

        Returns:
            Tuple of (valid_players, errors)
        """
        players = self.parse_chart(image_path)
        return self.validate_extraction(players)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Parse PIHS trade value chart images"
    )
    parser.add_argument(
        '--image',
        type=Path,
        required=True,
        help='Path to chart image file'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Output JSON file (default: stdout)'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        default=True,
        help='Validate extracted data (default: True)'
    )
    parser.add_argument(
        '--no-validate',
        action='store_false',
        dest='validate',
        help='Skip validation'
    )
    parser.add_argument(
        '--api-key',
        help='Anthropic API key (or set ANTHROPIC_API_KEY)'
    )

    args = parser.parse_args()

    # Initialize parser
    try:
        chart_parser = PIHSChartParser(anthropic_key=args.api_key)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Parse chart
    try:
        players = chart_parser.parse_chart(args.image)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except anthropic.APIError as e:
        print(f"API Error: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate if requested
    errors = []
    if args.validate:
        players, errors = chart_parser.validate_extraction(players)

    # Prepare output
    output_data = {
        'extracted_at': datetime.now().isoformat(),
        'image': str(args.image),
        'player_count': len(players),
        'players': players
    }

    if errors:
        output_data['validation_errors'] = errors

    # Output results
    json_output = json.dumps(output_data, indent=2)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w') as f:
            f.write(json_output)
        print(f"Saved {len(players)} players to {args.output}")
        if errors:
            print(f"  ({len(errors)} validation warnings)")
    else:
        print(json_output)


if __name__ == "__main__":
    main()
