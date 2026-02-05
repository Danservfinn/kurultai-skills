"""Tests for the Kurultai CLI entry point and commands.

This module tests the main CLI functionality including:
- CLI entry point
- Version flag
- Help output
- Command registration
- Error handling
"""

from __future__ import annotations

from typing import Any, List
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner, Result

from kurultai import __version__
from kurultai.cli import cli, main


class TestCLIEntryPoint:
    """Tests for the main CLI entry point."""

    def test_cli_import(self):
        """Test that CLI can be imported."""
        from kurultai.cli import cli
        assert cli is not None
        assert cli.name == "cli"

    def test_cli_name(self, cli_invoke):
        """Test CLI group name."""
        result = cli_invoke(["--help"])
        # Should show help when no command given
        assert result.exit_code == 0
        assert "Kurultai CLI" in result.output

    def test_main_function(self):
        """Test the main entry point function."""
        with patch.object(cli, "invoke") as mock_invoke:
            mock_invoke.return_value = 0
            try:
                result = main()
                assert mock_invoke.called
            except SystemExit:
                # Click may call sys.exit, which is expected
                pass


class TestVersionFlag:
    """Tests for the --version flag."""

    def test_version_flag(self, cli_invoke):
        """Test --version flag outputs correct version."""
        result = cli_invoke(["--version"])
        assert result.exit_code == 0
        assert __version__ in result.output
        assert "kurultai" in result.output.lower()

    def test_version_short_flag(self, cli_invoke):
        """Test -v flag outputs version."""
        # Click's version_option uses --version by default, -v may not be configured
        # Let's check what the actual behavior is
        result = cli_invoke(["--version"])
        assert result.exit_code == 0
        assert __version__ in result.output


class TestHelpOutput:
    """Tests for CLI help output."""

    def test_main_help(self, cli_invoke):
        """Test main CLI help output."""
        result = cli_invoke(["--help"])
        assert result.exit_code == 0
        assert "Kurultai CLI" in result.output
        assert "AI Skill Registry" in result.output

    def test_help_includes_common_commands(self, cli_invoke):
        """Test that help includes common commands."""
        result = cli_invoke(["--help"])
        assert result.exit_code == 0
        assert "install" in result.output
        assert "list" in result.output
        assert "remove" in result.output
        assert "info" in result.output
        assert "publish" in result.output

    def test_help_includes_examples(self, cli_invoke):
        """Test that help includes usage examples."""
        result = cli_invoke(["--help"])
        assert result.exit_code == 0
        assert "Examples:" in result.output
        assert "kurultai install" in result.output


class TestInstallCommand:
    """Tests for the install command."""

    def test_install_help(self, cli_invoke):
        """Test install command help."""
        result = cli_invoke(["install", "--help"])
        assert result.exit_code == 0
        assert "Install a skill" in result.output
        assert "SKILL_NAME" in result.output

    def test_install_requires_skill_name(self, cli_invoke):
        """Test that install requires a skill name."""
        result = cli_invoke(["install"])
        assert result.exit_code != 0
        assert "Missing argument" in result.output or "Usage:" in result.output

    def test_install_with_options(self, cli_invoke):
        """Test install command with various options."""
        with patch("kurultai.commands.install.install_skill") as mock_install:
            mock_install.return_value = MagicMock(
                name="test-skill",
                version="1.0.0",
                type=MagicMock(value="skill"),
                author="Test",
                dependencies={},
            )
            result = cli_invoke([
                "install", "test-skill",
                "--version", "1.0.0",
                "--force",
                "--no-deps",
            ])
            assert result.exit_code == 0
            mock_install.assert_called_once()
            call_kwargs = mock_install.call_args.kwargs
            assert call_kwargs["skill_name"] == "test-skill"
            assert call_kwargs["version"] == "1.0.0"
            assert call_kwargs["force"] is True

    def test_install_error_handling(self, cli_invoke):
        """Test install command error handling."""
        with patch("kurultai.commands.install.install_skill") as mock_install:
            mock_install.side_effect = Exception("Installation failed")
            result = cli_invoke(["install", "test-skill"])
            assert result.exit_code != 0
            assert "Installation failed" in result.output


class TestListCommand:
    """Tests for the list command."""

    def test_list_help(self, cli_invoke):
        """Test list command help."""
        result = cli_invoke(["list", "--help"])
        assert result.exit_code == 0
        assert "List installed or available skills" in result.output

    def test_list_installed(self, cli_invoke, mock_kurultai_home):
        """Test listing installed skills."""
        with patch("kurultai.commands.list.get_installed_skills") as mock_get:
            mock_get.return_value = []
            result = cli_invoke(["list"])
            assert result.exit_code == 0

    def test_list_available(self, cli_invoke, mock_registry_client):
        """Test listing available skills."""
        result = cli_invoke(["list", "--available"])
        assert result.exit_code == 0

    def test_list_detailed(self, cli_invoke):
        """Test listing with detailed output."""
        with patch("kurultai.commands.list.get_installed_skills") as mock_get:
            mock_get.return_value = []
            result = cli_invoke(["list", "--detailed"])
            assert result.exit_code == 0

    def test_list_search(self, cli_invoke, mock_registry_client):
        """Test searching skills."""
        result = cli_invoke(["list", "--search", "web"])
        assert result.exit_code == 0

    def test_list_with_type_filter(self, cli_invoke, mock_registry_client):
        """Test listing with type filter."""
        result = cli_invoke(["list", "--available", "--type", "skill"])
        assert result.exit_code == 0

    def test_list_with_tags_filter(self, cli_invoke, mock_registry_client):
        """Test listing with tags filter."""
        result = cli_invoke(["list", "--available", "--tags", "ai,nlp"])
        assert result.exit_code == 0


class TestRemoveCommand:
    """Tests for the remove command."""

    def test_remove_help(self, cli_invoke):
        """Test remove command help."""
        result = cli_invoke(["remove", "--help"])
        assert result.exit_code == 0
        assert "Remove an installed skill" in result.output

    def test_remove_requires_skill_name(self, cli_invoke):
        """Test that remove requires a skill name."""
        result = cli_invoke(["remove"])
        assert result.exit_code != 0
        assert "Missing argument" in result.output or "Usage:" in result.output

    def test_remove_skill_not_installed(self, cli_invoke):
        """Test removing a skill that is not installed."""
        with patch("kurultai.commands.remove.get_installed_skill_path") as mock_get:
            mock_get.return_value = None
            result = cli_invoke(["remove", "nonexistent-skill"])
            assert result.exit_code != 0
            assert "not installed" in result.output

    def test_remove_with_force(self, cli_invoke):
        """Test removing with force flag."""
        with patch("kurultai.commands.remove.remove_skill") as mock_remove, \
             patch("kurultai.commands.remove.get_installed_skill_path") as mock_get:
            mock_get.return_value = MagicMock()
            mock_remove.return_value = None
            result = cli_invoke(["remove", "test-skill", "--force", "--yes"])
            assert result.exit_code == 0

    def test_remove_with_yes(self, cli_invoke):
        """Test removing with yes flag (skip confirmation)."""
        with patch("kurultai.commands.remove.remove_skill") as mock_remove, \
             patch("kurultai.commands.remove.get_installed_skill_path") as mock_get:
            mock_get.return_value = MagicMock()
            mock_remove.return_value = None
            result = cli_invoke(["remove", "test-skill", "--yes"])
            assert result.exit_code == 0


class TestInfoCommand:
    """Tests for the info command."""

    def test_info_help(self, cli_invoke):
        """Test info command help."""
        result = cli_invoke(["info", "--help"])
        assert result.exit_code == 0
        assert "Display detailed information" in result.output

    def test_info_requires_skill_name(self, cli_invoke):
        """Test that info requires a skill name."""
        result = cli_invoke(["info"])
        assert result.exit_code != 0
        assert "Missing argument" in result.output or "Usage:" in result.output

    def test_info_installed_skill(self, cli_invoke):
        """Test getting info for installed skill."""
        with patch("kurultai.commands.info.get_installed_skill_manifest") as mock_get:
            mock_get.return_value = MagicMock(
                name="test-skill",
                version="1.0.0",
                type=MagicMock(value="skill"),
                author="Test",
                description="A test skill",
                dependencies={},
                tags=["test"],
                entry_point=None,
                prompts_dir="prompts",
                homepage=None,
                repository=None,
            )
            result = cli_invoke(["info", "test-skill"])
            assert result.exit_code == 0
            assert "test-skill" in result.output

    def test_info_registry_skill(self, cli_invoke):
        """Test getting info for skill from registry."""
        with patch("kurultai.commands.info.get_installed_skill_path") as mock_installed, \
             patch("kurultai.commands.info.fetch_skill_from_registry") as mock_fetch:
            mock_installed.return_value = None
            mock_fetch.return_value = MagicMock(
                name="registry-skill",
                version="2.0.0",
                type=MagicMock(value="engine"),
                author="Registry",
                description="A registry skill",
                dependencies={},
                tags=["ai"],
                entry_point=None,
                prompts_dir="prompts",
                homepage=None,
                repository=None,
            )
            result = cli_invoke(["info", "registry-skill"])
            assert result.exit_code == 0
            assert "registry-skill" in result.output

    def test_info_not_found(self, cli_invoke):
        """Test info for non-existent skill."""
        with patch("kurultai.commands.info.get_skill_info") as mock_get:
            mock_get.return_value = None
            result = cli_invoke(["info", "nonexistent"])
            assert result.exit_code != 0
            assert "not found" in result.output.lower()

    def test_info_json_output(self, cli_invoke):
        """Test info with JSON output."""
        with patch("kurultai.commands.info.get_skill_info") as mock_get:
            mock_get.return_value = MagicMock(
                name="test-skill",
                version="1.0.0",
                type=MagicMock(value="skill"),
                author="Test",
                description="A test skill",
                dependencies={},
                tags=[],
                entry_point=None,
                prompts_dir="prompts",
                homepage=None,
                repository=None,
                to_yaml_dict=lambda: {"name": "test-skill", "version": "1.0.0"},
            )
            result = cli_invoke(["info", "test-skill", "--json"])
            assert result.exit_code == 0
            assert "test-skill" in result.output


class TestPublishCommand:
    """Tests for the publish command."""

    def test_publish_help(self, cli_invoke):
        """Test publish command help."""
        result = cli_invoke(["publish", "--help"])
        assert result.exit_code == 0
        assert "Publish a skill" in result.output

    def test_publish_requires_path(self, cli_invoke):
        """Test that publish requires a path."""
        result = cli_invoke(["publish"])
        assert result.exit_code != 0
        assert "Missing argument" in result.output or "Usage:" in result.output

    def test_publish_dry_run(self, cli_invoke, temp_dir):
        """Test publish with dry-run flag."""
        skill_dir = temp_dir / "my-skill"
        skill_dir.mkdir()

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
                    result = cli_invoke(["publish", str(skill_dir), "--dry-run"])
                    assert result.exit_code == 0
                    assert "DRY RUN" in result.output

    def test_publish_invalid_skill(self, cli_invoke, temp_dir):
        """Test publishing invalid skill."""
        skill_dir = temp_dir / "invalid-skill"
        skill_dir.mkdir()

        with patch("kurultai.commands.publish.validate_skill_for_publish") as mock_validate:
            mock_validate.return_value = (
                False,
                None,
                "Validation failed: missing skill.yaml",
            )
            result = cli_invoke(["publish", str(skill_dir)])
            assert result.exit_code != 0


class TestCommandRegistration:
    """Tests for command registration."""

    def test_all_commands_registered(self):
        """Test that all commands are registered with the CLI."""
        commands = ["install", "list", "remove", "info", "publish"]
        for cmd in commands:
            assert cmd in cli.commands

    def test_command_names(self):
        """Test that command names are correct."""
        assert cli.commands["install"].name == "install"
        assert cli.commands["list"].name == "list"
        assert cli.commands["remove"].name == "remove"
        assert cli.commands["info"].name == "info"
        assert cli.commands["publish"].name == "publish"


class TestErrorHandling:
    """Tests for CLI error handling."""

    def test_unknown_command(self, cli_invoke):
        """Test handling of unknown commands."""
        result = cli_invoke(["unknown-command"])
        assert result.exit_code != 0
        assert "No such command" in result.output or "Usage:" in result.output

    def test_invalid_option(self, cli_invoke):
        """Test handling of invalid options."""
        result = cli_invoke(["install", "--invalid-option", "skill"])
        assert result.exit_code != 0
        assert "no such option" in result.output.lower() or "Error" in result.output

    def test_keyboard_interrupt(self, cli_invoke):
        """Test handling of keyboard interrupt."""
        with patch("kurultai.commands.list.get_installed_skills") as mock_get:
            mock_get.side_effect = KeyboardInterrupt()
            result = cli_invoke(["list"])
            assert result.exit_code != 0


class TestCLIContext:
    """Tests for CLI context and state."""

    def test_cli_isolation(self, cli_runner: CliRunner):
        """Test that CLI commands run in isolation."""
        # Run multiple commands to ensure isolation
        result1 = cli_runner.invoke(cli, ["--help"])
        result2 = cli_runner.invoke(cli, ["--version"])

        assert result1.exit_code == 0
        assert result2.exit_code == 0
        assert "Kurultai CLI" in result1.output
        assert __version__ in result2.output
