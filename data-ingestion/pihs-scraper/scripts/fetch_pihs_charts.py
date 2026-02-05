#!/usr/bin/env python3
"""
PIHS Chart Fetcher
==================
Download trade value chart images from peakedinhighskool.com.

Supports:
- Redraft weekly charts (PPR, Half-PPR, Standard)
- Dynasty monthly charts (Superflex, 1QB)

Usage:
    python fetch_pihs_charts.py --type redraft --format ppr
    python fetch_pihs_charts.py --type dynasty --league superflex
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PIHSChartFetcher:
    """Fetch trade value chart images from PeakedInHighSkool."""

    # Base URLs
    BASE_URL = "https://peakedinhighskool.com"
    REDRAFT_URL = "https://peakedinhighskool.com/fantasy-trade-value-chart/"
    DYNASTY_URL = "https://peakedinhighskool.com/dynasty-trade-value-charts/"

    # User agent to avoid blocking
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://peakedinhighskool.com/',
    }

    # Cache validity (hours)
    REDRAFT_CACHE_HOURS = 24
    DYNASTY_CACHE_HOURS = 168  # 7 days

    def __init__(self, cache_dir: Path = None):
        """
        Initialize the chart fetcher.

        Args:
            cache_dir: Directory to cache downloaded charts
        """
        self.cache_dir = Path(cache_dir or "data/raw/pihs")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def _get_cache_path(
        self,
        chart_type: str,
        format_or_league: str,
        date: datetime = None
    ) -> Path:
        """Generate cache file path for a chart."""
        date = date or datetime.now()
        date_str = date.strftime("%Y-%m-%d")
        filename = f"pihs_{chart_type}_{format_or_league}_{date_str}.png"
        return self.cache_dir / filename

    def _is_cache_valid(self, cache_path: Path, chart_type: str) -> bool:
        """Check if cached chart is still valid."""
        if not cache_path.exists():
            return False

        # Get file modification time
        mtime = datetime.fromtimestamp(cache_path.stat().st_mtime)
        age_hours = (datetime.now() - mtime).total_seconds() / 3600

        # Check against cache validity period
        if chart_type == "redraft":
            return age_hours < self.REDRAFT_CACHE_HOURS
        else:
            return age_hours < self.DYNASTY_CACHE_HOURS

    def _find_latest_cache(self, chart_type: str, format_or_league: str) -> Optional[Path]:
        """Find the most recent cached chart of a given type."""
        pattern = f"pihs_{chart_type}_{format_or_league}_*.png"
        cache_files = sorted(self.cache_dir.glob(pattern), reverse=True)
        return cache_files[0] if cache_files else None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type(requests.RequestException)
    )
    def _fetch_page(self, url: str) -> str:
        """Fetch a webpage with retry logic."""
        logger.info(f"Fetching page: {url}")
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        return response.text

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type(requests.RequestException)
    )
    def _download_image(self, url: str, save_path: Path) -> Path:
        """Download an image with retry logic."""
        logger.info(f"Downloading image: {url}")
        response = self.session.get(url, timeout=60, stream=True)
        response.raise_for_status()

        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"Saved to: {save_path}")
        return save_path

    def _extract_chart_urls(self, html: str, chart_type: str) -> List[Dict[str, str]]:
        """
        Extract chart image URLs from page HTML.

        Returns list of dicts with 'url', 'format', and 'description'.
        """
        soup = BeautifulSoup(html, 'html.parser')
        charts = []

        # Look for chart images - check all img tags
        img_tags = soup.find_all('img')

        for img in img_tags:
            # Check multiple attributes for image URL
            src = img.get('src', '') or img.get('data-src', '') or img.get('data-lazy-src', '')
            srcset = img.get('srcset', '') or img.get('data-srcset', '')
            alt = img.get('alt', '').lower()

            # Skip placeholder/data URIs
            if src.startswith('data:'):
                # Try srcset instead
                if srcset:
                    # Parse srcset to get highest resolution
                    parts = srcset.split(',')
                    for part in parts:
                        url_part = part.strip().split(' ')[0]
                        if url_part and not url_part.startswith('data:'):
                            src = url_part
                            break
                else:
                    continue

            if not src or src.startswith('data:'):
                continue

            # Look for WordPress CDN pattern (i0.wp.com) or chart-related keywords
            is_wp_cdn = 'wp.com' in src or 'wp-content/uploads' in src
            is_chart_keyword = any(keyword in src.lower() or keyword in alt for keyword in [
                'trade', 'value', 'chart', 'ppr', 'superflex', 'sf', '1qb',
                'dynasty', 'redraft', 'fantasy', 'standard', 'half'
            ])

            # Check if it's an image file
            is_image = any(ext in src.lower() for ext in ['.png', '.jpg', '.jpeg', '.webp'])

            if is_image and (is_wp_cdn or is_chart_keyword):
                # Determine format from URL or alt text
                format_type = self._detect_format(src, alt)

                # Clean up the URL
                chart_url = src if src.startswith('http') else urljoin(self.BASE_URL, src)

                charts.append({
                    'url': chart_url,
                    'format': format_type,
                    'description': alt or 'Trade Value Chart'
                })
                logger.debug(f"Found chart: {format_type} - {chart_url[:80]}...")

        # Also check for links to chart images
        link_tags = soup.find_all('a', href=True)
        for link in link_tags:
            href = link.get('href', '')
            if any(ext in href.lower() for ext in ['.png', '.jpg', '.webp']):
                if any(kw in href.lower() for kw in ['chart', 'value', 'ppr', 'standard', 'dynasty']):
                    format_type = self._detect_format(href, link.get_text())
                    charts.append({
                        'url': href if href.startswith('http') else urljoin(self.BASE_URL, href),
                        'format': format_type,
                        'description': link.get_text() or 'Trade Value Chart'
                    })

        # Deduplicate by URL
        seen = set()
        unique_charts = []
        for chart in charts:
            if chart['url'] not in seen:
                seen.add(chart['url'])
                unique_charts.append(chart)

        logger.info(f"Found {len(unique_charts)} chart images")
        return unique_charts

    def _detect_format(self, url: str, text: str) -> str:
        """Detect chart format from URL or text."""
        combined = (url + ' ' + text).lower()

        if 'superflex' in combined or 'sf' in combined or '2qb' in combined:
            return 'superflex'
        elif '1qb' in combined or 'oneqb' in combined:
            return '1qb'
        elif 'half' in combined or '0.5' in combined or 'hppr' in combined:
            return 'half_ppr'
        elif 'standard' in combined or 'std' in combined:
            return 'standard'
        elif 'ppr' in combined:
            return 'ppr'
        else:
            return 'unknown'

    def fetch_redraft_chart(
        self,
        format: str = "ppr",
        force_refresh: bool = False
    ) -> Optional[Path]:
        """
        Fetch the current redraft trade value chart.

        Args:
            format: Scoring format - "ppr", "half_ppr", or "standard"
            force_refresh: If True, bypass cache

        Returns:
            Path to downloaded chart image, or None if failed
        """
        cache_path = self._get_cache_path("redraft", format)

        # Check cache
        if not force_refresh and self._is_cache_valid(cache_path, "redraft"):
            logger.info(f"Using cached chart: {cache_path}")
            return cache_path

        try:
            # Fetch page and extract chart URLs
            html = self._fetch_page(self.REDRAFT_URL)
            charts = self._extract_chart_urls(html, "redraft")

            # Find matching format
            matching = [c for c in charts if c['format'] == format or c['format'] == 'unknown']

            if not matching:
                # Fall back to any available chart
                matching = charts

            if not matching:
                logger.warning("No chart images found on redraft page")
                # Try to return cached version
                cached = self._find_latest_cache("redraft", format)
                if cached:
                    logger.info(f"Returning stale cache: {cached}")
                    return cached
                return None

            # Download the first matching chart
            chart_url = matching[0]['url']
            return self._download_image(chart_url, cache_path)

        except Exception as e:
            logger.error(f"Error fetching redraft chart: {e}")
            # Try to return cached version
            cached = self._find_latest_cache("redraft", format)
            if cached:
                logger.info(f"Returning stale cache after error: {cached}")
                return cached
            return None

    def fetch_dynasty_chart(
        self,
        league_type: str = "superflex",
        force_refresh: bool = False
    ) -> Optional[Path]:
        """
        Fetch the current dynasty trade value chart.

        Args:
            league_type: "superflex" or "1qb"
            force_refresh: If True, bypass cache

        Returns:
            Path to downloaded chart image, or None if failed
        """
        cache_path = self._get_cache_path("dynasty", league_type)

        # Check cache
        if not force_refresh and self._is_cache_valid(cache_path, "dynasty"):
            logger.info(f"Using cached chart: {cache_path}")
            return cache_path

        try:
            # Fetch page and extract chart URLs
            html = self._fetch_page(self.DYNASTY_URL)
            charts = self._extract_chart_urls(html, "dynasty")

            # Find matching league type
            matching = [c for c in charts if c['format'] == league_type]

            if not matching:
                # Fall back to any available chart
                matching = charts

            if not matching:
                logger.warning("No chart images found on dynasty page")
                cached = self._find_latest_cache("dynasty", league_type)
                if cached:
                    logger.info(f"Returning stale cache: {cached}")
                    return cached
                return None

            # Download the first matching chart
            chart_url = matching[0]['url']
            return self._download_image(chart_url, cache_path)

        except Exception as e:
            logger.error(f"Error fetching dynasty chart: {e}")
            cached = self._find_latest_cache("dynasty", league_type)
            if cached:
                logger.info(f"Returning stale cache after error: {cached}")
                return cached
            return None

    def fetch_all_charts(self, force_refresh: bool = False) -> Dict[str, Path]:
        """
        Fetch all available chart types.

        Returns:
            Dict mapping chart identifiers to file paths
        """
        results = {}

        # Redraft charts
        for format in ["ppr", "half_ppr", "standard"]:
            path = self.fetch_redraft_chart(format=format, force_refresh=force_refresh)
            if path:
                results[f"redraft_{format}"] = path

        # Dynasty charts
        for league in ["superflex", "1qb"]:
            path = self.fetch_dynasty_chart(league_type=league, force_refresh=force_refresh)
            if path:
                results[f"dynasty_{league}"] = path

        return results

    def list_cached_charts(self) -> List[Dict[str, str]]:
        """List all cached charts with metadata."""
        charts = []
        for path in self.cache_dir.glob("pihs_*.png"):
            # Parse filename
            parts = path.stem.split('_')
            if len(parts) >= 4:
                chart_type = parts[1]
                format_league = parts[2]
                date_str = parts[3]

                mtime = datetime.fromtimestamp(path.stat().st_mtime)
                age_hours = (datetime.now() - mtime).total_seconds() / 3600

                charts.append({
                    'path': str(path),
                    'chart_type': chart_type,
                    'format': format_league,
                    'date': date_str,
                    'age_hours': round(age_hours, 1),
                    'size_kb': round(path.stat().st_size / 1024, 1)
                })

        return sorted(charts, key=lambda x: x['date'], reverse=True)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Fetch PIHS trade value charts"
    )
    parser.add_argument(
        '--type',
        choices=['redraft', 'dynasty', 'all'],
        default='all',
        help='Chart type to fetch'
    )
    parser.add_argument(
        '--format',
        choices=['ppr', 'half_ppr', 'standard'],
        default='ppr',
        help='Scoring format for redraft charts'
    )
    parser.add_argument(
        '--league',
        choices=['superflex', '1qb'],
        default='superflex',
        help='League type for dynasty charts'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force refresh, bypass cache'
    )
    parser.add_argument(
        '--cache-dir',
        type=Path,
        default=Path("data/raw/pihs"),
        help='Directory to cache charts'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List cached charts and exit'
    )

    args = parser.parse_args()

    fetcher = PIHSChartFetcher(cache_dir=args.cache_dir)

    if args.list:
        charts = fetcher.list_cached_charts()
        if charts:
            print("\nCached PIHS Charts:")
            print("-" * 80)
            for chart in charts:
                print(f"  {chart['chart_type']:8} {chart['format']:10} {chart['date']} "
                      f"({chart['age_hours']}h old, {chart['size_kb']}KB)")
        else:
            print("No cached charts found.")
        return

    if args.type == 'all':
        results = fetcher.fetch_all_charts(force_refresh=args.force)
        print(f"\nFetched {len(results)} charts:")
        for key, path in results.items():
            print(f"  {key}: {path}")
    elif args.type == 'redraft':
        path = fetcher.fetch_redraft_chart(format=args.format, force_refresh=args.force)
        if path:
            print(f"Redraft chart saved to: {path}")
        else:
            print("Failed to fetch redraft chart")
            sys.exit(1)
    else:  # dynasty
        path = fetcher.fetch_dynasty_chart(league_type=args.league, force_refresh=args.force)
        if path:
            print(f"Dynasty chart saved to: {path}")
        else:
            print("Failed to fetch dynasty chart")
            sys.exit(1)


if __name__ == "__main__":
    main()
