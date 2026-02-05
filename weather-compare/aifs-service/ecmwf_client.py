"""
ECMWF Open Data Client for AIFS Forecasts

Downloads AIFS forecast data from ECMWF's open data portal.
Data is available under CC-BY-4.0 license at https://data.ecmwf.int/forecasts/
"""

import os
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import logging

from ecmwf.opendata import Client

logger = logging.getLogger(__name__)

# Data directory for GRIB files
DATA_DIR = Path(os.getenv("AIFS_DATA_DIR", "/tmp/aifs_data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)


class AIFSClient:
    """Client for downloading ECMWF AIFS forecast data."""

    def __init__(self):
        self.client = Client(source="ecmwf")
        self._last_download: Optional[datetime] = None
        self._current_file: Optional[Path] = None

    def _get_latest_forecast_time(self) -> tuple[datetime, int]:
        """
        Determine the latest available forecast cycle.
        AIFS runs at 00z, 06z, 12z, 18z with ~6 hour delay.
        """
        now = datetime.utcnow()
        # Account for ~6 hour processing delay
        available_time = now - timedelta(hours=7)

        # Find the latest 6-hourly cycle
        hour = (available_time.hour // 6) * 6
        forecast_date = available_time.replace(hour=hour, minute=0, second=0, microsecond=0)

        return forecast_date, hour

    def _get_cache_path(self, forecast_date: datetime, param: str) -> Path:
        """Get the cache file path for a specific forecast and parameter."""
        date_str = forecast_date.strftime("%Y%m%d%H")
        return DATA_DIR / f"aifs_{date_str}_{param}.grib2"

    async def download_forecast(
        self,
        params: list[str] = ["tp", "sf", "2t"],
        steps: list[int] = None,
        force: bool = False,
    ) -> dict[str, Path]:
        """
        Download AIFS forecast data for specified parameters.

        Args:
            params: Weather parameters to download
                - tp: Total precipitation (m)
                - sf: Snowfall (m of water equivalent)
                - 2t: 2m temperature (K)
            steps: Forecast hours (default: 0-240 in 6h steps for 10 days)
            force: Force re-download even if cached

        Returns:
            Dict mapping parameter names to file paths
        """
        if steps is None:
            # 10-day forecast in 6-hour steps
            steps = list(range(0, 241, 6))

        forecast_date, hour = self._get_latest_forecast_time()
        logger.info(f"Fetching AIFS forecast from {forecast_date} (hour={hour})")

        files = {}

        for param in params:
            cache_path = self._get_cache_path(forecast_date, param)

            # Check cache
            if not force and cache_path.exists():
                logger.info(f"Using cached {param} data: {cache_path}")
                files[param] = cache_path
                continue

            # Download from ECMWF
            logger.info(f"Downloading AIFS {param} data...")
            try:
                # Run sync download in thread pool
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self._download_param(forecast_date, hour, param, steps, cache_path),
                )
                files[param] = cache_path
                logger.info(f"Downloaded {param} to {cache_path}")
            except Exception as e:
                logger.error(f"Failed to download {param}: {e}")
                # Try to use older cached data
                older_files = sorted(DATA_DIR.glob(f"aifs_*_{param}.grib2"), reverse=True)
                if older_files:
                    files[param] = older_files[0]
                    logger.warning(f"Using older cache: {older_files[0]}")

        self._last_download = datetime.utcnow()
        return files

    def _download_param(
        self,
        forecast_date: datetime,
        hour: int,
        param: str,
        steps: list[int],
        target: Path,
    ):
        """Synchronous download of a single parameter."""
        self.client.retrieve(
            date=forecast_date.strftime("%Y%m%d"),
            time=hour,
            model="aifs",
            type="fc",
            param=param,
            step=steps,
            target=str(target),
        )

    async def get_latest_files(self) -> dict[str, Path]:
        """
        Get paths to latest forecast files, downloading if necessary.
        """
        forecast_date, _ = self._get_latest_forecast_time()

        # Check if we have current data
        tp_path = self._get_cache_path(forecast_date, "tp")
        sf_path = self._get_cache_path(forecast_date, "sf")
        t2_path = self._get_cache_path(forecast_date, "2t")

        if tp_path.exists() and sf_path.exists() and t2_path.exists():
            return {"tp": tp_path, "sf": sf_path, "2t": t2_path}

        # Download fresh data
        return await self.download_forecast()

    def cleanup_old_files(self, keep_hours: int = 24):
        """Remove forecast files older than keep_hours."""
        cutoff = datetime.utcnow() - timedelta(hours=keep_hours)

        for file in DATA_DIR.glob("aifs_*.grib2"):
            try:
                # Parse date from filename
                date_str = file.stem.split("_")[1]
                file_date = datetime.strptime(date_str, "%Y%m%d%H")
                if file_date < cutoff:
                    file.unlink()
                    logger.info(f"Cleaned up old file: {file}")
            except (IndexError, ValueError) as e:
                logger.warning(f"Could not parse date from {file}: {e}")


# Singleton client instance
_client: Optional[AIFSClient] = None


def get_client() -> AIFSClient:
    """Get or create the singleton AIFS client."""
    global _client
    if _client is None:
        _client = AIFSClient()
    return _client


async def fetch_latest_aifs(force: bool = False) -> dict[str, Path]:
    """Convenience function to fetch latest AIFS data."""
    client = get_client()
    return await client.download_forecast(force=force)
