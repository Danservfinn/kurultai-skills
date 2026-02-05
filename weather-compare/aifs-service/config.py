"""
Configuration for AIFS microservice.
"""

import os
from pathlib import Path

# Service configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# CORS configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

# Data storage
DATA_DIR = Path(os.getenv("AIFS_DATA_DIR", "/tmp/aifs_data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Cache configuration
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 1 hour default
CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", "1000"))

# ECMWF configuration
ECMWF_SOURCE = os.getenv("ECMWF_SOURCE", "ecmwf")

# Background refresh (hours)
REFRESH_INTERVAL_HOURS = int(os.getenv("REFRESH_INTERVAL_HOURS", "6"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
