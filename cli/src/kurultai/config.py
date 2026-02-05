"""Configuration management for Kurultai CLI."""

import os
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field


# Default paths
KURULTAI_HOME = Path.home() / ".kurultai"
SKILLS_DIR = KURULTAI_HOME / "skills"
CONFIG_FILE = KURULTAI_HOME / "config.yaml"

# Default registry URL (placeholder)
DEFAULT_REGISTRY_URL = "https://registry.kurultai.ai/v1"


class Config(BaseModel):
    """Kurultai configuration model.

    Attributes:
        registry_url: URL of the skill registry
        skills_dir: Local directory for installed skills
        api_key: Optional API key for authenticated requests
        default_namespace: Default namespace for skill lookups
        timeout: Request timeout in seconds
    """

    registry_url: str = Field(default=DEFAULT_REGISTRY_URL, description="Skill registry URL")
    skills_dir: Path = Field(default=SKILLS_DIR, description="Local skills directory")
    api_key: Optional[str] = Field(default=None, description="API key for registry access")
    default_namespace: str = Field(default="kurultai", description="Default namespace for skills")
    timeout: int = Field(default=30, ge=1, le=300, description="Request timeout in seconds")

    class Config:
        """Pydantic configuration."""

        env_prefix = "KURULTAI_"
        arbitrary_types_allowed = True

    @classmethod
    def from_file(cls, config_path: Optional[Path] = None) -> "Config":
        """Load configuration from a YAML file.

        Args:
            config_path: Path to the config file. Defaults to ~/.kurultai/config.yaml

        Returns:
            Config instance loaded from file or defaults
        """
        import yaml

        config_path = config_path or CONFIG_FILE

        if not config_path.exists():
            return cls()

        try:
            with open(config_path, "r") as f:
                data = yaml.safe_load(f) or {}
            return cls(**data)
        except Exception as e:
            raise ConfigError(f"Failed to load config from {config_path}: {e}") from e

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables.

        Returns:
            Config instance with values from environment
        """
        env_vars = {}

        if os.getenv("KURULTAI_REGISTRY_URL"):
            env_vars["registry_url"] = os.getenv("KURULTAI_REGISTRY_URL")

        if os.getenv("KURULTAI_SKILLS_DIR"):
            env_vars["skills_dir"] = Path(os.getenv("KURULTAI_SKILLS_DIR"))

        if os.getenv("KURULTAI_API_KEY"):
            env_vars["api_key"] = os.getenv("KURULTAI_API_KEY")

        if os.getenv("KURULTAI_DEFAULT_NAMESPACE"):
            env_vars["default_namespace"] = os.getenv("KURULTAI_DEFAULT_NAMESPACE")

        if os.getenv("KURULTAI_TIMEOUT"):
            try:
                env_vars["timeout"] = int(os.getenv("KURULTAI_TIMEOUT"))
            except ValueError:
                pass

        return cls(**env_vars)

    def save(self, config_path: Optional[Path] = None) -> None:
        """Save configuration to a YAML file.

        Args:
            config_path: Path to save the config file. Defaults to ~/.kurultai/config.yaml
        """
        import yaml

        config_path = config_path or CONFIG_FILE
        ensure_directories()

        # Convert Path objects to strings for YAML serialization
        data = self.model_dump()
        data["skills_dir"] = str(data["skills_dir"])

        with open(config_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=True)


def ensure_directories() -> None:
    """Ensure Kurultai home and skills directories exist."""
    KURULTAI_HOME.mkdir(parents=True, exist_ok=True)
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)


def get_config() -> Config:
    """Get the active configuration.

    Loads configuration in the following priority order:
    1. Environment variables
    2. Config file (~/.kurultai/config.yaml)
    3. Default values

    Returns:
        Config instance
    """
    # Start with file config if it exists
    if CONFIG_FILE.exists():
        config = Config.from_file()
    else:
        config = Config()

    # Override with environment variables
    env_config = Config.from_env()

    # Merge env config (non-None values only)
    env_data = env_config.model_dump(exclude_none=True)
    for key, value in env_data.items():
        setattr(config, key, value)

    return config


class ConfigError(Exception):
    """Exception raised for configuration errors."""

    pass
