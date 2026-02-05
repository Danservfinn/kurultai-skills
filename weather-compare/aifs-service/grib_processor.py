"""
GRIB2 Processor for AIFS Forecast Data

Converts GRIB2 files to JSON format matching Fish app's DailyData interface.
Uses xarray and cfgrib for efficient GRIB2 parsing.
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict

import numpy as np
import xarray as xr

logger = logging.getLogger(__name__)


@dataclass
class DailyForecast:
    """Daily forecast data matching Fish app's DailyData interface."""

    date: str
    snowfall_sum: Optional[float]
    precipitation_sum: Optional[float]
    temp_max: Optional[float]
    temp_min: Optional[float]


@dataclass
class AIFSForecast:
    """Complete AIFS forecast response."""

    lat: float
    lon: float
    model: str
    daily: list[dict]
    last_updated: str
    forecast_horizon: int


class GRIBProcessor:
    """Process GRIB2 files and extract point forecasts."""

    def __init__(self):
        self._tp_data: Optional[xr.Dataset] = None
        self._sf_data: Optional[xr.Dataset] = None
        self._t2_data: Optional[xr.Dataset] = None
        self._loaded_files: dict[str, Path] = {}

    def load_files(self, files: dict[str, Path]) -> None:
        """
        Load GRIB2 files into memory.

        Args:
            files: Dict mapping param names to file paths
        """
        if "tp" in files and files["tp"] != self._loaded_files.get("tp"):
            logger.info(f"Loading precipitation data from {files['tp']}")
            self._tp_data = xr.open_dataset(
                files["tp"],
                engine="cfgrib",
                backend_kwargs={"indexpath": ""},
            )
            self._loaded_files["tp"] = files["tp"]

        if "sf" in files and files["sf"] != self._loaded_files.get("sf"):
            logger.info(f"Loading snowfall data from {files['sf']}")
            self._sf_data = xr.open_dataset(
                files["sf"],
                engine="cfgrib",
                backend_kwargs={"indexpath": ""},
            )
            self._loaded_files["sf"] = files["sf"]

        if "2t" in files and files["2t"] != self._loaded_files.get("2t"):
            logger.info(f"Loading temperature data from {files['2t']}")
            self._t2_data = xr.open_dataset(
                files["2t"],
                engine="cfgrib",
                backend_kwargs={"indexpath": ""},
            )
            self._loaded_files["2t"] = files["2t"]

    def _find_nearest_point(
        self, ds: xr.Dataset, lat: float, lon: float
    ) -> tuple[float, float]:
        """Find nearest grid point to requested coordinates."""
        # Normalize longitude to 0-360 if needed
        if "longitude" in ds.coords:
            lon_coord = "longitude"
            lat_coord = "latitude"
        else:
            lon_coord = "lon"
            lat_coord = "lat"

        lons = ds[lon_coord].values
        lats = ds[lat_coord].values

        # Handle longitude wrapping (ECMWF uses 0-360)
        query_lon = lon if lon >= 0 else lon + 360

        # Find nearest indices
        lon_idx = np.abs(lons - query_lon).argmin()
        lat_idx = np.abs(lats - lat).argmin()

        return lat_idx, lon_idx

    def _extract_point_timeseries(
        self, ds: xr.Dataset, lat: float, lon: float, var_name: str
    ) -> list[tuple[datetime, float]]:
        """Extract time series for a single point."""
        lat_idx, lon_idx = self._find_nearest_point(ds, lat, lon)

        # Get coordinate names
        if "longitude" in ds.coords:
            point_data = ds[var_name].isel(longitude=lon_idx, latitude=lat_idx)
        else:
            point_data = ds[var_name].isel(lon=lon_idx, lat=lat_idx)

        # Extract time and values
        times = point_data.valid_time.values if "valid_time" in point_data.coords else point_data.time.values
        values = point_data.values

        result = []
        for t, v in zip(times, values):
            dt = np.datetime64(t, "ns").astype("datetime64[s]").astype(datetime)
            result.append((dt, float(v) if not np.isnan(v) else None))

        return result

    def _aggregate_to_daily(
        self,
        timeseries: list[tuple[datetime, float]],
        agg_type: str = "sum",
    ) -> dict[str, float]:
        """
        Aggregate 6-hourly data to daily values.

        Args:
            timeseries: List of (datetime, value) tuples
            agg_type: "sum", "max", or "min"

        Returns:
            Dict mapping date strings to aggregated values
        """
        daily = {}

        for dt, value in timeseries:
            date_str = dt.strftime("%Y-%m-%d")
            if date_str not in daily:
                daily[date_str] = []
            if value is not None:
                daily[date_str].append(value)

        result = {}
        for date_str, values in daily.items():
            if not values:
                result[date_str] = None
            elif agg_type == "sum":
                result[date_str] = sum(values)
            elif agg_type == "max":
                result[date_str] = max(values)
            elif agg_type == "min":
                result[date_str] = min(values)

        return result

    def extract_forecast(
        self, lat: float, lon: float, days: int = 10
    ) -> AIFSForecast:
        """
        Extract daily forecast for a location.

        Args:
            lat: Latitude (-90 to 90)
            lon: Longitude (-180 to 180)
            days: Number of forecast days (max 10)

        Returns:
            AIFSForecast object with daily data
        """
        days = min(days, 10)  # AIFS max is 10 days

        daily_data = {}

        # Extract precipitation (tp is cumulative, convert to daily)
        if self._tp_data is not None:
            try:
                tp_series = self._extract_point_timeseries(
                    self._tp_data, lat, lon, "tp"
                )
                # Convert from meters to mm and aggregate
                tp_mm = [(dt, v * 1000 if v else None) for dt, v in tp_series]
                daily_data["precip"] = self._aggregate_to_daily(tp_mm, "sum")
            except Exception as e:
                logger.error(f"Error extracting precipitation: {e}")
                daily_data["precip"] = {}

        # Extract snowfall (sf is cumulative, convert to daily)
        if self._sf_data is not None:
            try:
                sf_series = self._extract_point_timeseries(
                    self._sf_data, lat, lon, "sf"
                )
                # Convert from meters water equivalent to cm snow (roughly 10:1 ratio)
                sf_cm = [(dt, v * 1000 * 10 if v else None) for dt, v in sf_series]
                daily_data["snow"] = self._aggregate_to_daily(sf_cm, "sum")
            except Exception as e:
                logger.error(f"Error extracting snowfall: {e}")
                daily_data["snow"] = {}

        # Extract temperature (2t)
        if self._t2_data is not None:
            try:
                t2_series = self._extract_point_timeseries(
                    self._t2_data, lat, lon, "t2m"
                )
                # Convert from Kelvin to Celsius
                t2_c = [(dt, v - 273.15 if v else None) for dt, v in t2_series]
                daily_data["temp_max"] = self._aggregate_to_daily(t2_c, "max")
                daily_data["temp_min"] = self._aggregate_to_daily(t2_c, "min")
            except Exception as e:
                logger.error(f"Error extracting temperature: {e}")
                daily_data["temp_max"] = {}
                daily_data["temp_min"] = {}

        # Build daily forecast list
        all_dates = set()
        for param_data in daily_data.values():
            all_dates.update(param_data.keys())

        sorted_dates = sorted(all_dates)[:days]

        daily_forecasts = []
        for date_str in sorted_dates:
            forecast = DailyForecast(
                date=date_str,
                snowfall_sum=daily_data.get("snow", {}).get(date_str),
                precipitation_sum=daily_data.get("precip", {}).get(date_str),
                temp_max=daily_data.get("temp_max", {}).get(date_str),
                temp_min=daily_data.get("temp_min", {}).get(date_str),
            )
            daily_forecasts.append(asdict(forecast))

        return AIFSForecast(
            lat=lat,
            lon=lon,
            model="ecmwf_aifs",
            daily=daily_forecasts,
            last_updated=datetime.utcnow().isoformat() + "Z",
            forecast_horizon=days,
        )


# Singleton processor instance
_processor: Optional[GRIBProcessor] = None


def get_processor() -> GRIBProcessor:
    """Get or create the singleton GRIB processor."""
    global _processor
    if _processor is None:
        _processor = GRIBProcessor()
    return _processor


def extract_forecast(
    files: dict[str, Path], lat: float, lon: float, days: int = 10
) -> AIFSForecast:
    """
    Convenience function to extract forecast from files.

    Args:
        files: Dict mapping param names to GRIB2 file paths
        lat: Latitude
        lon: Longitude
        days: Number of forecast days

    Returns:
        AIFSForecast object
    """
    processor = get_processor()
    processor.load_files(files)
    return processor.extract_forecast(lat, lon, days)
