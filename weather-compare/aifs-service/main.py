"""
ECMWF AIFS Microservice

FastAPI application serving AIFS forecast data for the Fish weather app.
Downloads GRIB2 data from ECMWF Open Data portal and converts to JSON.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from dataclasses import asdict
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import config
from cache import forecast_cache, make_cache_key
from ecmwf_client import get_client, fetch_latest_aifs
from grib_processor import extract_forecast, get_processor

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Background task for data refresh
async def refresh_data_periodically():
    """Background task to refresh AIFS data every 6 hours."""
    while True:
        try:
            logger.info("Starting periodic AIFS data refresh...")
            await fetch_latest_aifs(force=True)
            logger.info("Periodic data refresh complete")

            # Clean up old files
            get_client().cleanup_old_files(keep_hours=24)
        except Exception as e:
            logger.error(f"Error in periodic refresh: {e}")

        # Wait for next refresh
        await asyncio.sleep(config.REFRESH_INTERVAL_HOURS * 3600)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup: fetch initial data and start background refresh
    logger.info("Starting AIFS service...")

    try:
        # Initial data fetch
        logger.info("Fetching initial AIFS data...")
        files = await fetch_latest_aifs()
        logger.info(f"Initial data loaded: {list(files.keys())}")

        # Pre-load GRIB files
        processor = get_processor()
        processor.load_files(files)
        logger.info("GRIB data loaded into memory")
    except Exception as e:
        logger.warning(f"Could not load initial data (will retry on first request): {e}")

    # Start background refresh task
    refresh_task = asyncio.create_task(refresh_data_periodically())

    yield

    # Shutdown: cancel background task
    refresh_task.cancel()
    try:
        await refresh_task
    except asyncio.CancelledError:
        pass
    logger.info("AIFS service stopped")


# Create FastAPI app
app = FastAPI(
    title="ECMWF AIFS Service",
    description="Serves ECMWF AIFS AI weather model forecasts for the Fish weather app",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with service info."""
    return {
        "service": "ECMWF AIFS Service",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "forecast": "/forecast/{lat}/{lon}",
            "cache_stats": "/cache/stats",
        },
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/forecast/{lat}/{lon}")
async def get_forecast(
    lat: float,
    lon: float,
    days: int = Query(default=10, ge=1, le=10, description="Forecast days (1-10)"),
):
    """
    Get AIFS forecast for a location.

    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        days: Number of forecast days (default 10, max 10)

    Returns:
        JSON forecast data matching Fish app's DailyData interface
    """
    # Validate coordinates
    if not -90 <= lat <= 90:
        raise HTTPException(400, "Latitude must be between -90 and 90")
    if not -180 <= lon <= 180:
        raise HTTPException(400, "Longitude must be between -180 and 180")

    # Check cache
    cache_key = make_cache_key(lat, lon, days)
    cached = forecast_cache.get(cache_key)
    if cached is not None:
        logger.debug(f"Cache hit for {cache_key}")
        return JSONResponse(content=cached)

    # Get or fetch data
    try:
        files = await fetch_latest_aifs()
        forecast = extract_forecast(files, lat, lon, days)

        # Convert to dict for JSON response
        result = asdict(forecast)

        # Cache the result
        forecast_cache.set(cache_key, result)

        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"Error getting forecast for ({lat}, {lon}): {e}")
        raise HTTPException(500, f"Failed to get AIFS forecast: {str(e)}")


@app.get("/cache/stats")
async def cache_stats():
    """Get cache statistics."""
    return forecast_cache.stats


@app.post("/cache/clear")
async def clear_cache():
    """Clear the forecast cache."""
    forecast_cache.clear()
    return {"status": "cleared"}


@app.post("/refresh")
async def refresh_data():
    """Manually trigger data refresh."""
    try:
        files = await fetch_latest_aifs(force=True)
        return {
            "status": "refreshed",
            "files": {k: str(v) for k, v in files.items()},
        }
    except Exception as e:
        raise HTTPException(500, f"Refresh failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
    )
