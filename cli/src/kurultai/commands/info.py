"""Info command for Kurultai CLI.

Handles displaying detailed information about skills.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import click
import requests

from kurultai.config import SKILLS_DIR, get_config
from kurultai.models.skill import Dependency, SkillManifest, SkillType
from kurultai.validators import validate_manifest


def get_installed_skill_path(skill_name: str) -> Optional[Path]:
    """Get the path to an installed skill if it exists.

    Args:
        skill_name: Name of the skill.

    Returns:
        Path to the skill directory if installed, None otherwise.
    """
    skill_dir = SKILLS_DIR / skill_name
    if skill_dir.exists() and skill_dir.is_dir():
        return skill_dir
    return None


def get_installed_skill_manifest(skill_name: str) -> Optional[SkillManifest]:
    """Get the manifest of an installed skill.

    Args:
        skill_name: Name of the skill.

    Returns:
        SkillManifest if found and valid, None otherwise.
    """
    skill_dir = get_installed_skill_path(skill_name)
    if not skill_dir:
        return None

    manifest_path = skill_dir / "skill.yaml"
    if not manifest_path.exists():
        manifest_path = skill_dir / "skill.yml"

    if not manifest_path.exists():
        return None

    try:
        return validate_manifest(manifest_path)
    except Exception:
        return None


def fetch_skill_from_registry(
    skill_name: str, registry: Optional[str] = None
) -> Optional[SkillManifest]:
    """Fetch skill information from the registry.

    Args:
        skill_name: Name of the skill.
        registry: Optional registry URL override.

    Returns:
        SkillManifest if found, None otherwise.
    """
    config = get_config()
    registry_url = registry or config.registry_url

    try:
        # Try to fetch skill info from registry
        skill_url = f"{registry_url}/skills/{skill_name}.json"
        response = requests.get(skill_url, timeout=config.timeout)

        if response.status_code == 200:
            data = response.json()
            return SkillManifest.model_validate(data)

        return None
    except Exception:
        return None


def format_skill_info(manifest: SkillManifest) -> str:
    """Format skill information for display.

    Args:
        manifest: The skill manifest.

    Returns:
        Formatted string.
    """
    lines = []

    lines.append(f"Name: {manifest.name}")
    lines.append(f"Version: {manifest.version}")
    lines.append(f"Type: {manifest.type.value}")
    lines.append(f"Author: {manifest.author}")
    lines.append("")
    lines.append(f"Description: {manifest.description}")

    if manifest.entry_point:
        lines.append("")
        lines.append(f"Entry Point: {manifest.entry_point}")

    if manifest.prompts_dir:
        lines.append(f"Prompts Directory: {manifest.prompts_dir}")

    if manifest.tags:
        lines.append("")
        lines.append(f"Tags: {', '.join(manifest.tags)}")

    if manifest.homepage:
        lines.append(f"Homepage: {manifest.homepage}")

    if manifest.repository:
        lines.append(f"Repository: {manifest.repository}")

    if manifest.dependencies:
        lines.append("")
        lines.append("Dependencies:")

        required = manifest.get_required_dependencies()
        optional = manifest.get_optional_dependencies()

        if required:
            for dep in required:
                lines.append(f"  - {dep.name}@{dep.version_constraint}")

        if optional:
            lines.append("")
            lines.append("Optional Dependencies:")
            for dep in optional:
                lines.append(f"  - {dep.name}@{dep.version_constraint}")

    return "\n".join(lines)


def format_skill_info_json(manifest: SkillManifest) -> str:
    """Format skill information as JSON.

    Args:
        manifest: The skill manifest.

    Returns:
        JSON string.
    """
    data = manifest.to_yaml_dict()
    return json.dumps(data, indent=2)


def get_skill_info(
    skill_name: str, registry: Optional[str] = None
) -> Optional[SkillManifest]:
    """Get skill information from installed skills or registry.

    Args:
        skill_name: Name of the skill.
        registry: Optional registry URL override.

    Returns:
        SkillManifest if found, None otherwise.
    """
    # First try to get from installed skills
    manifest = get_installed_skill_manifest(skill_name)
    if manifest:
        return manifest

    # Then try to fetch from registry
    manifest = fetch_skill_from_registry(skill_name, registry)
    if manifest:
        return manifest

    return None


@click.command(name="info")
@click.argument("skill_name")
@click.option(
    "--json", "-j", "output_json", is_flag=True, help="Output in JSON format"
)
@click.option(
    "--registry", "-r", help="Registry URL to use for fetching skill info"
)
def info_command(skill_name: str, output_json: bool, registry: Optional[str]):
    """Display detailed information about a skill.

    SKILL_NAME is the name of the skill to get information about.

    The command first checks installed skills, then queries the registry
    if the skill is not installed locally.

    Examples:
        kurultai info web-scraper           # Show info for web-scraper
        kurultai info web-scraper --json    # Output as JSON
        kurultai info web-scraper -r https://...  # Use custom registry
    """
    # Check if skill is installed
    is_installed = get_installed_skill_path(skill_name) is not None

    # Get skill info
    manifest = get_skill_info(skill_name, registry)

    if not manifest:
        # Skill not found
        if is_installed:
            raise click.ClickException(
                f"Skill '{skill_name}' is installed but has an invalid manifest."
            )
        else:
            raise click.ClickException(
                f"Skill '{skill_name}' not found. "
                f"Use 'kurultai list --available' to see available skills."
            )

    # Output in requested format
    if output_json:
        click.echo(format_skill_info_json(manifest))
    else:
        if is_installed:
            click.echo(f"[Installed] {manifest.name}@{manifest.version}")
        else:
            click.echo(f"[Registry] {manifest.name}@{manifest.version}")
        click.echo()
        click.echo(format_skill_info(manifest))
