"""Pytest fixtures for Kurultai CLI tests."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional
from unittest.mock import MagicMock, patch

import pytest
import yaml
from click.testing import CliRunner

from kurultai.cli import cli
from kurultai.config import Config
from kurultai.models.skill import SkillManifest, SkillType
from kurultai.registry import RegistryClient, RegistryIndex, RegistrySkill


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create a Click CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def cli_invoke(cli_runner: CliRunner):
    """Create a helper function to invoke CLI commands."""
    def _invoke(args: List[str], **kwargs) -> Any:
        """Invoke the CLI with given arguments."""
        return cli_runner.invoke(cli, args, **kwargs)
    return _invoke


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def temp_cwd(temp_dir: Path) -> Generator[Path, None, None]:
    """Change to a temporary directory for testing."""
    original_cwd = os.getcwd()
    os.chdir(temp_dir)
    yield temp_dir
    os.chdir(original_cwd)


@pytest.fixture
def mock_skills_dir(temp_dir: Path) -> Path:
    """Create a mock skills directory."""
    skills_dir = temp_dir / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    return skills_dir


@pytest.fixture
def mock_kurultai_home(temp_dir: Path) -> Generator[Path, None, None]:
    """Mock the Kurultai home directory."""
    kurultai_home = temp_dir / ".kurultai"
    kurultai_home.mkdir(parents=True, exist_ok=True)

    with patch("kurultai.config.KURULTAI_HOME", kurultai_home), \
         patch("kurultai.config.SKILLS_DIR", kurultai_home / "skills"):
        yield kurultai_home


@pytest.fixture
def mock_config(temp_dir: Path) -> Generator[Config, None, None]:
    """Create a mock configuration."""
    config = Config(
        registry_url="https://registry.kurultai.ai/v1",
        skills_dir=temp_dir / "skills",
        api_key=None,
        default_namespace="kurultai",
        timeout=30,
    )

    with patch("kurultai.config.get_config", return_value=config):
        yield config


@pytest.fixture
def valid_skill_manifest() -> Dict[str, Any]:
    """Return a valid skill manifest dictionary."""
    return {
        "name": "test-skill",
        "version": "1.0.0",
        "description": "A test skill for validation purposes",
        "author": "Test Author",
        "type": "skill",
        "tags": ["test", "example"],
    }


@pytest.fixture
def valid_engine_manifest() -> Dict[str, Any]:
    """Return a valid engine manifest dictionary."""
    return {
        "name": "test-engine",
        "version": "2.0.0",
        "description": "A test engine for processing AI tasks",
        "author": "Engine Team",
        "type": "engine",
        "entry_point": "src/engine.py",
        "dependencies": {
            "base-skill": ">=1.0.0",
        },
        "tags": ["engine", "ai"],
    }


@pytest.fixture
def valid_workflow_manifest() -> Dict[str, Any]:
    """Return a valid workflow manifest dictionary."""
    return {
        "name": "test-workflow",
        "version": "1.5.0",
        "description": "A test workflow for automating tasks",
        "author": "Workflow Team",
        "type": "workflow",
        "entry_point": "workflow.yaml",
        "dependencies": {
            "step-1": ">=1.0.0",
            "step-2": "^2.0.0",
        },
        "tags": ["workflow", "automation"],
    }


@pytest.fixture
def create_skill_dir(temp_dir: Path) -> Generator:
    """Factory fixture to create skill directories."""
    created_dirs: List[Path] = []

    def _create(
        name: str,
        manifest: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, str]] = None,
    ) -> Path:
        skill_dir = temp_dir / "skills" / name
        skill_dir.mkdir(parents=True, exist_ok=True)

        # Create manifest
        if manifest:
            manifest_path = skill_dir / "skill.yaml"
            with open(manifest_path, "w") as f:
                yaml.dump(manifest, f, default_flow_style=False)

        # Create additional files
        if files:
            for filename, content in files.items():
                file_path = skill_dir / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)

        created_dirs.append(skill_dir)
        return skill_dir

    yield _create

    # Cleanup
    for skill_dir in created_dirs:
        if skill_dir.exists():
            import shutil
            shutil.rmtree(skill_dir)


@pytest.fixture
def mock_registry_index(temp_dir: Path) -> Generator[Path, None, None]:
    """Create a mock registry index file."""
    registry_dir = temp_dir / "registry"
    registry_dir.mkdir(parents=True, exist_ok=True)

    index_data = {
        "schema_version": "1.0.0",
        "metadata": {
            "name": "Kurultai Registry",
            "description": "Test registry",
        },
        "skills": [
            {
                "name": "web-scraper",
                "version": "1.2.0",
                "description": "Scrape web pages for data extraction",
                "author": "Kurultai Team",
                "type": "skill",
                "repository": "https://github.com/kurultai/web-scraper",
                "tags": ["web", "scraping"],
            },
            {
                "name": "data-analyzer",
                "version": "2.0.0",
                "description": "Analyze data with AI models",
                "author": "Data Team",
                "type": "engine",
                "repository": "https://github.com/kurultai/data-analyzer",
                "tags": ["data", "analysis"],
            },
            {
                "name": "sentiment-workflow",
                "version": "1.0.0",
                "description": "Complete sentiment analysis workflow",
                "author": "NLP Team",
                "type": "workflow",
                "repository": "https://github.com/kurultai/sentiment-workflow",
                "dependencies": [
                    {"name": "data-analyzer", "version_constraint": ">=2.0.0"},
                ],
                "tags": ["nlp", "sentiment"],
            },
        ],
    }

    index_path = registry_dir / "skills.json"
    with open(index_path, "w") as f:
        json.dump(index_data, f, indent=2)

    yield index_path


@pytest.fixture
def mock_registry_client(mock_registry_index: Path) -> Generator[RegistryClient, None, None]:
    """Create a mock registry client."""
    client = RegistryClient(index_path=mock_registry_index)

    with patch("kurultai.registry.get_registry_client", return_value=client):
        yield client


@pytest.fixture
def mock_git_available() -> Generator[None, None, None]:
    """Mock git as available."""
    with patch("kurultai.commands.install.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="git version 2.0.0")
        yield


@pytest.fixture
def mock_git_clone() -> Generator[MagicMock, None, None]:
    """Mock git clone command."""
    with patch("kurultai.commands.install.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        yield mock_run


@pytest.fixture
def mock_requests() -> Generator[MagicMock, None, None]:
    """Mock requests library."""
    with patch("kurultai.commands.info.requests") as mock_req:
        yield mock_req


@pytest.fixture
def sample_lock_file() -> Dict[str, Any]:
    """Return a sample lock file structure."""
    return {
        "version": "1.0.0",
        "generated_at": "2024-01-01T00:00:00Z",
        "dependencies": [
            {
                "name": "dep1",
                "version": "1.0.0",
                "source": "registry",
                "resolved_url": "https://registry.kurultai.ai/skills/dep1",
                "checksum": "abc123",
                "dependencies": [],
            },
            {
                "name": "dep2",
                "version": "2.0.0",
                "source": "registry",
                "resolved_url": "https://registry.kurultai.ai/skills/dep2",
                "checksum": "def456",
                "dependencies": ["dep1"],
            },
        ],
    }


@pytest.fixture
def invalid_manifests() -> Dict[str, Dict[str, Any]]:
    """Return a dictionary of invalid manifests for testing."""
    return {
        "missing_name": {
            "version": "1.0.0",
            "description": "A test skill",
            "author": "Test",
            "type": "skill",
        },
        "missing_version": {
            "name": "test-skill",
            "description": "A test skill",
            "author": "Test",
            "type": "skill",
        },
        "missing_description": {
            "name": "test-skill",
            "version": "1.0.0",
            "author": "Test",
            "type": "skill",
        },
        "missing_author": {
            "name": "test-skill",
            "version": "1.0.0",
            "description": "A test skill",
            "type": "skill",
        },
        "missing_type": {
            "name": "test-skill",
            "version": "1.0.0",
            "description": "A test skill",
            "author": "Test",
        },
        "invalid_name": {
            "name": "Invalid Name",
            "version": "1.0.0",
            "description": "A test skill",
            "author": "Test",
            "type": "skill",
        },
        "invalid_version": {
            "name": "test-skill",
            "version": "not-a-version",
            "description": "A test skill",
            "author": "Test",
            "type": "skill",
        },
        "short_description": {
            "name": "test-skill",
            "version": "1.0.0",
            "description": "Short",
            "author": "Test",
            "type": "skill",
        },
        "invalid_type": {
            "name": "test-skill",
            "version": "1.0.0",
            "description": "A test skill",
            "author": "Test",
            "type": "invalid",
        },
    }


@pytest.fixture
def version_constraints() -> Dict[str, Dict[str, Any]]:
    """Return version constraints test data."""
    return {
        "caret": {
            "constraint": "^1.0.0",
            "matching": ["1.0.0", "1.2.0", "1.0.5"],
            "non_matching": ["2.0.0", "0.9.0"],
        },
        "tilde": {
            "constraint": "~1.0.0",
            "matching": ["1.0.0", "1.0.5"],
            "non_matching": ["1.1.0", "2.0.0"],
        },
        "gte": {
            "constraint": ">=1.0.0",
            "matching": ["1.0.0", "1.1.0", "2.0.0"],
            "non_matching": ["0.9.0"],
        },
        "gt": {
            "constraint": ">1.0.0",
            "matching": ["1.0.1", "1.1.0", "2.0.0"],
            "non_matching": ["1.0.0", "0.9.0"],
        },
        "lte": {
            "constraint": "<=1.0.0",
            "matching": ["1.0.0", "0.9.0", "0.9.9"],
            "non_matching": ["1.0.1", "1.1.0"],
        },
        "lt": {
            "constraint": "<1.0.0",
            "matching": ["0.9.0", "0.9.9"],
            "non_matching": ["1.0.0", "1.0.1"],
        },
        "exact": {
            "constraint": "1.0.0",
            "matching": ["1.0.0"],
            "non_matching": ["1.0.1", "1.1.0", "2.0.0"],
        },
    }
