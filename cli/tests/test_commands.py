"""Integration tests for CLI commands.

This module tests command integration with mock registry:
- Install command with mock registry
- List command (installed and available)
- Remove command
- Info command
- Publish command with dry-run
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Generator, List
from unittest.mock import MagicMock, patch

import pytest
import yaml
from click.testing import CliRunner

from kurultai.cli import cli
from kurultai.models.skill import SkillManifest, SkillType


class TestInstallCommand:
    """Integration tests for install command."""

    def test_install_from_registry(self, cli_runner: CliRunner, temp_dir: Path, mock_kurultai_home: Path):
        """Test installing a skill from registry."""
        with patch("kurultai.commands.install.install_skill") as mock_install:
            from kurultai.models.skill import SkillManifest, SkillType

            mock_install.return_value = SkillManifest(
                name="web-scraper",
                version="1.0.0",
                description="A web scraper skill",
                author="Test",
                type=SkillType.SKILL,
            )

            result = cli_runner.invoke(cli, ["install", "web-scraper"])
            assert result.exit_code == 0
            mock_install.assert_called_once()

    def test_install_with_version(self, cli_runner: CliRunner, mock_kurultai_home: Path):
        """Test installing a specific version."""
        with patch("kurultai.commands.install.install_skill") as mock_install:
            mock_install.return_value = MagicMock(
                name="test-skill",
                version="1.2.0",
                type=MagicMock(value="skill"),
                author="Test",
                dependencies={},
            )

            result = cli_runner.invoke(cli, ["install", "test-skill", "--version", "1.2.0"])
            assert result.exit_code == 0
            mock_install.assert_called_once()
            call_kwargs = mock_install.call_args.kwargs
            assert call_kwargs["version"] == "1.2.0"

    def test_install_from_url(self, cli_runner: CliRunner, mock_kurultai_home: Path):
        """Test installing from a Git URL."""
        with patch("kurultai.commands.install.install_skill") as mock_install:
            mock_install.return_value = MagicMock(
                name="custom-skill",
                version="1.0.0",
                type=MagicMock(value="skill"),
                author="Test",
                dependencies={},
            )

            url = "https://github.com/user/custom-skill.git"
            result = cli_runner.invoke(cli, ["install", url])
            assert result.exit_code == 0
            mock_install.assert_called_once()

    def test_install_force(self, cli_runner: CliRunner, mock_kurultai_home: Path):
        """Test installing with force flag."""
        with patch("kurultai.commands.install.install_skill") as mock_install:
            mock_install.return_value = MagicMock(
                name="test-skill",
                version="1.0.0",
                type=MagicMock(value="skill"),
                author="Test",
                dependencies={},
            )

            result = cli_runner.invoke(cli, ["install", "test-skill", "--force"])
            assert result.exit_code == 0
            mock_install.assert_called_once()
            call_kwargs = mock_install.call_args.kwargs
            assert call_kwargs["force"] is True

    def test_install_no_deps(self, cli_runner: CliRunner, mock_kurultai_home: Path):
        """Test installing without dependencies."""
        with patch("kurultai.commands.install.install_skill") as mock_install:
            mock_install.return_value = MagicMock(
                name="test-skill",
                version="1.0.0",
                type=MagicMock(value="skill"),
                author="Test",
                dependencies={},
            )

            result = cli_runner.invoke(cli, ["install", "test-skill", "--no-deps"])
            assert result.exit_code == 0

    def test_install_with_lock_file(self, cli_runner: CliRunner, mock_kurultai_home: Path):
        """Test installing with lock file generation."""
        with patch("kurultai.commands.install.install_skill") as mock_install, \
             patch("kurultai.commands.install.write_lock_file_for_manifest") as mock_lock:

            mock_install.return_value = MagicMock(
                name="test-skill",
                version="1.0.0",
                type=MagicMock(value="skill"),
                author="Test",
                dependencies={"dep1": "^1.0.0"},
            )
            mock_lock.return_value = Path("kurultai.lock")

            result = cli_runner.invoke(cli, ["install", "test-skill", "--lock-file"])
            assert result.exit_code == 0
            mock_lock.assert_called_once()

    def test_install_skill_not_found(self, cli_runner: CliRunner, mock_kurultai_home: Path):
        """Test installing a non-existent skill."""
        with patch("kurultai.commands.install.clone_skill_repo") as mock_clone:
            from click import ClickException
            mock_clone.side_effect = ClickException("Skill not found")

            result = cli_runner.invoke(cli, ["install", "nonexistent-skill"])
            assert result.exit_code != 0


class TestListCommand:
    """Integration tests for list command."""

    def test_list_installed_empty(self, cli_runner: CliRunner, mock_kurultai_home: Path):
        """Test listing when no skills are installed."""
        result = cli_runner.invoke(cli, ["list"])
        assert result.exit_code == 0
        assert "No skills installed" in result.output or "Installed skills" in result.output

    def test_list_installed_with_skills(self, cli_runner: CliRunner, mock_kurultai_home: Path, create_skill_dir):
        """Test listing installed skills."""
        create_skill_dir(
            "test-skill",
            manifest={
                "name": "test-skill",
                "version": "1.0.0",
                "description": "A test skill",
                "author": "Test",
                "type": "skill",
            },
        )

        with patch("kurultai.commands.list.SKILLS_DIR", mock_kurultai_home / "skills"):
            result = cli_runner.invoke(cli, ["list"])
            assert result.exit_code == 0

    def test_list_available(self, cli_runner: CliRunner, mock_registry_client):
        """Test listing available skills from registry."""
        result = cli_runner.invoke(cli, ["list", "--available"])
        assert result.exit_code == 0

    def test_list_detailed(self, cli_runner: CliRunner, mock_kurultai_home: Path, create_skill_dir):
        """Test listing with detailed information."""
        create_skill_dir(
            "test-skill",
            manifest={
                "name": "test-skill",
                "version": "1.0.0",
                "description": "A test skill",
                "author": "Test",
                "type": "skill",
            },
        )

        with patch("kurultai.commands.list.SKILLS_DIR", mock_kurultai_home / "skills"):
            result = cli_runner.invoke(cli, ["list", "--detailed"])
            assert result.exit_code == 0

    def test_list_search(self, cli_runner: CliRunner, mock_registry_client):
        """Test searching skills."""
        result = cli_runner.invoke(cli, ["list", "--search", "web"])
        assert result.exit_code == 0

    def test_list_with_type_filter(self, cli_runner: CliRunner, mock_registry_client):
        """Test listing with type filter."""
        result = cli_runner.invoke(cli, ["list", "--available", "--type", "engine"])
        assert result.exit_code == 0

    def test_list_with_tags_filter(self, cli_runner: CliRunner, mock_registry_client):
        """Test listing with tags filter."""
        result = cli_runner.invoke(cli, ["list", "--available", "--tags", "ai"])
        assert result.exit_code == 0


class TestRemoveCommand:
    """Integration tests for remove command."""

    def test_remove_skill(self, cli_runner: CliRunner, temp_dir: Path, create_skill_dir):
        """Test removing an installed skill."""
        skills_dir = temp_dir / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)

        create_skill_dir(
            "test-skill",
            manifest={
                "name": "test-skill",
                "version": "1.0.0",
                "description": "A test skill",
                "author": "Test",
                "type": "skill",
            },
        )

        with patch("kurultai.commands.remove.SKILLS_DIR", skills_dir):
            result = cli_runner.invoke(cli, ["remove", "test-skill", "--yes"])
            assert result.exit_code == 0
            assert "Successfully removed" in result.output

    def test_remove_skill_not_installed(self, cli_runner: CliRunner, mock_kurultai_home: Path):
        """Test removing a skill that is not installed."""
        with patch("kurultai.commands.remove.SKILLS_DIR", mock_kurultai_home / "skills"):
            result = cli_runner.invoke(cli, ["remove", "nonexistent-skill"])
            assert result.exit_code != 0
            assert "not installed" in result.output

    def test_remove_with_force(self, cli_runner: CliRunner, temp_dir: Path, create_skill_dir):
        """Test removing with force flag."""
        skills_dir = temp_dir / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)

        create_skill_dir(
            "test-skill",
            manifest={
                "name": "test-skill",
                "version": "1.0.0",
                "description": "A test skill",
                "author": "Test",
                "type": "skill",
            },
        )

        with patch("kurultai.commands.remove.SKILLS_DIR", skills_dir):
            result = cli_runner.invoke(cli, ["remove", "test-skill", "--force", "--yes"])
            assert result.exit_code == 0

    def test_remove_with_dependents(self, cli_runner: CliRunner, temp_dir: Path, create_skill_dir):
        """Test removing a skill that has dependents."""
        skills_dir = temp_dir / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)

        create_skill_dir(
            "base-skill",
            manifest={
                "name": "base-skill",
                "version": "1.0.0",
                "description": "A base skill",
                "author": "Test",
                "type": "skill",
            },
        )

        create_skill_dir(
            "dependent-skill",
            manifest={
                "name": "dependent-skill",
                "version": "1.0.0",
                "description": "A dependent skill",
                "author": "Test",
                "type": "skill",
                "dependencies": {"base-skill": "^1.0.0"},
            },
        )

        with patch("kurultai.commands.remove.SKILLS_DIR", skills_dir):
            result = cli_runner.invoke(cli, ["remove", "base-skill"])
            assert result.exit_code != 0
            assert "required by" in result.output.lower() or "dependent" in result.output.lower()


class TestInfoCommand:
    """Integration tests for info command."""

    def test_info_installed_skill(self, cli_runner: CliRunner, temp_dir: Path, create_skill_dir):
        """Test getting info for installed skill."""
        skills_dir = temp_dir / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)

        create_skill_dir(
            "test-skill",
            manifest={
                "name": "test-skill",
                "version": "1.0.0",
                "description": "A test skill",
                "author": "Test Author",
                "type": "skill",
                "tags": ["test"],
            },
        )

        with patch("kurultai.commands.info.SKILLS_DIR", skills_dir):
            result = cli_runner.invoke(cli, ["info", "test-skill"])
            assert result.exit_code == 0
            assert "test-skill" in result.output
            assert "Test Author" in result.output

    def test_info_registry_skill(self, cli_runner: CliRunner, mock_registry_client):
        """Test getting info for skill from registry."""
        with patch("kurultai.commands.info.fetch_skill_from_registry") as mock_fetch:
            mock_fetch.return_value = MagicMock(
                name="web-scraper",
                version="1.0.0",
                type=MagicMock(value="skill"),
                author="Test",
                description="A web scraper skill",
                dependencies=[],
                tags=[],
                entry_point=None,
                prompts_dir="prompts",
                homepage=None,
                repository=None,
            )
            result = cli_runner.invoke(cli, ["info", "web-scraper"])
            assert result.exit_code == 0

    def test_info_not_found(self, cli_runner: CliRunner, mock_kurultai_home: Path):
        """Test info for non-existent skill."""
        with patch("kurultai.commands.info.SKILLS_DIR", mock_kurultai_home / "skills"):
            result = cli_runner.invoke(cli, ["info", "nonexistent"])
            assert result.exit_code != 0
            assert "not found" in result.output.lower()

    def test_info_json_output(self, cli_runner: CliRunner, temp_dir: Path, create_skill_dir):
        """Test info with JSON output."""
        skills_dir = temp_dir / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)

        create_skill_dir(
            "test-skill",
            manifest={
                "name": "test-skill",
                "version": "1.0.0",
                "description": "A test skill",
                "author": "Test",
                "type": "skill",
            },
        )

        with patch("kurultai.commands.info.SKILLS_DIR", skills_dir):
            result = cli_runner.invoke(cli, ["info", "test-skill", "--json"])
            assert result.exit_code == 0
            # Should be valid JSON
            data = json.loads(result.output)
            assert data["name"] == "test-skill"


class TestPublishCommand:
    """Integration tests for publish command."""

    def test_publish_dry_run(self, cli_runner: CliRunner, temp_dir: Path):
        """Test publish with dry-run flag."""
        skill_dir = temp_dir / "my-skill"
        skill_dir.mkdir()

        # Create a valid skill.yaml
        manifest = {
            "name": "my-skill",
            "version": "1.0.0",
            "description": "A test skill for publishing",
            "author": "Test Author",
            "type": "skill",
        }
        with open(skill_dir / "skill.yaml", "w") as f:
            yaml.dump(manifest, f)

        with patch("kurultai.commands.publish.validate_skill_for_publish") as mock_validate:
            mock_validate.return_value = (
                True,
                MagicMock(
                    result=MagicMock(
                        manifest=MagicMock(
                            name="my-skill",
                            version="1.0.0",
                        )
                    )
                ),
                None,
            )
            with patch("kurultai.commands.publish.perform_git_operations") as mock_git:
                mock_git.return_value = (True, "v1.0.0", None)
                with patch("kurultai.commands.publish.update_registry") as mock_registry:
                    mock_registry.return_value = (True, None)
                    result = cli_runner.invoke(cli, ["publish", str(skill_dir), "--dry-run"])
                    assert result.exit_code == 0
                    assert "DRY RUN" in result.output

    def test_publish_invalid_skill(self, cli_runner: CliRunner, temp_dir: Path):
        """Test publishing invalid skill."""
        skill_dir = temp_dir / "invalid-skill"
        skill_dir.mkdir()

        with patch("kurultai.commands.publish.validate_skill_for_publish") as mock_validate:
            mock_validate.return_value = (
                False,
                None,
                "Validation failed: missing skill.yaml",
            )
            result = cli_runner.invoke(cli, ["publish", str(skill_dir)])
            assert result.exit_code != 0

    def test_publish_quiet(self, cli_runner: CliRunner, temp_dir: Path):
        """Test publish with quiet flag."""
        skill_dir = temp_dir / "my-skill"
        skill_dir.mkdir()

        manifest = {
            "name": "my-skill",
            "version": "1.0.0",
            "description": "A test skill for publishing",
            "author": "Test Author",
            "type": "skill",
        }
        with open(skill_dir / "skill.yaml", "w") as f:
            yaml.dump(manifest, f)

        with patch("kurultai.commands.publish.validate_skill_for_publish") as mock_validate:
            mock_validate.return_value = (
                True,
                MagicMock(
                    result=MagicMock(
                        manifest=MagicMock(
                            name="my-skill",
                            version="1.0.0",
                        )
                    )
                ),
                None,
            )
            with patch("kurultai.commands.publish.perform_git_operations") as mock_git:
                mock_git.return_value = (True, "v1.0.0", None)
                with patch("kurultai.commands.publish.update_registry") as mock_registry:
                    mock_registry.return_value = (True, None)
                    result = cli_runner.invoke(cli, ["publish", str(skill_dir), "--quiet", "--dry-run"])
                    assert result.exit_code == 0

    def test_publish_force(self, cli_runner: CliRunner, temp_dir: Path):
        """Test publish with force flag."""
        skill_dir = temp_dir / "my-skill"
        skill_dir.mkdir()

        manifest = {
            "name": "my-skill",
            "version": "1.0.0",
            "description": "A test skill for publishing",
            "author": "Test Author",
            "type": "skill",
        }
        with open(skill_dir / "skill.yaml", "w") as f:
            yaml.dump(manifest, f)

        with patch("kurultai.commands.publish.validate_skill_for_publish") as mock_validate:
            mock_validate.return_value = (
                True,
                MagicMock(
                    result=MagicMock(
                        manifest=MagicMock(
                            name="my-skill",
                            version="1.0.0",
                        )
                    )
                ),
                None,
            )
            with patch("kurultai.commands.publish.perform_git_operations") as mock_git:
                mock_git.return_value = (True, "v1.0.0", None)
                with patch("kurultai.commands.publish.update_registry") as mock_registry:
                    mock_registry.return_value = (True, None)
                    result = cli_runner.invoke(cli, ["publish", str(skill_dir), "--force", "--dry-run"])
                    assert result.exit_code == 0


class TestCommandIntegration:
    """Integration tests for command workflows."""

    def test_install_list_remove_workflow(self, cli_runner: CliRunner, mock_kurultai_home: Path):
        """Test the full install-list-remove workflow."""
        skills_dir = mock_kurultai_home / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)

        with patch("kurultai.commands.install.SKILLS_DIR", skills_dir), \
             patch("kurultai.commands.list.SKILLS_DIR", skills_dir), \
             patch("kurultai.commands.remove.SKILLS_DIR", skills_dir):

            # Install
            with patch("kurultai.commands.install.clone_skill_repo") as mock_clone, \
                 patch("kurultai.commands.install.parse_skill_manifest") as mock_parse:

                skill_dir = skills_dir / "test-skill"
                skill_dir.mkdir(parents=True, exist_ok=True)
                manifest_path = skill_dir / "skill.yaml"
                manifest_path.write_text(yaml.dump({
                    "name": "test-skill",
                    "version": "1.0.0",
                    "description": "A test skill",
                    "author": "Test",
                    "type": "skill",
                }))

                mock_parse.return_value = MagicMock(
                    name="test-skill",
                    version="1.0.0",
                    type=MagicMock(value="skill"),
                    author="Test",
                    dependencies={},
                )

                result = cli_runner.invoke(cli, ["install", "test-skill"])
                assert result.exit_code == 0

            # List
            result = cli_runner.invoke(cli, ["list"])
            assert result.exit_code == 0

            # Remove
            result = cli_runner.invoke(cli, ["remove", "test-skill", "--yes"])
            assert result.exit_code == 0

    def test_info_after_install(self, cli_runner: CliRunner, temp_dir: Path, create_skill_dir):
        """Test getting info after installing a skill."""
        skills_dir = temp_dir / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)

        create_skill_dir(
            "test-skill",
            manifest={
                "name": "test-skill",
                "version": "1.0.0",
                "description": "A test skill",
                "author": "Test",
                "type": "skill",
            },
        )

        with patch("kurultai.commands.info.SKILLS_DIR", skills_dir):
            result = cli_runner.invoke(cli, ["info", "test-skill"])
            assert result.exit_code == 0
            assert "test-skill" in result.output


class TestErrorHandling:
    """Tests for command error handling."""

    def test_command_not_found(self, cli_runner: CliRunner):
        """Test handling of unknown commands."""
        result = cli_runner.invoke(cli, ["unknown-command"])
        assert result.exit_code != 0

    def test_invalid_arguments(self, cli_runner: CliRunner):
        """Test handling of invalid arguments."""
        result = cli_runner.invoke(cli, ["install", "--invalid-option", "skill"])
        assert result.exit_code != 0

    def test_missing_required_arguments(self, cli_runner: CliRunner):
        """Test handling of missing required arguments."""
        result = cli_runner.invoke(cli, ["install"])
        assert result.exit_code != 0

    def test_invalid_skill_name(self, cli_runner: CliRunner):
        """Test handling of invalid skill name."""
        result = cli_runner.invoke(cli, ["info", ""])
        assert result.exit_code != 0
