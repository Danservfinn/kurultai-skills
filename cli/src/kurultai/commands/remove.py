"""Remove command for Kurultai CLI.

Handles skill removal with dependency checking.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import List, Optional, Set

import click

from kurultai.config import SKILLS_DIR
from kurultai.models.skill import SkillManifest
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


def get_all_installed_skills() -> List[SkillManifest]:
    """Get all installed skills with valid manifests.

    Returns:
        List of SkillManifest objects.
    """
    skills: List[SkillManifest] = []

    if not SKILLS_DIR.exists():
        return skills

    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue

        manifest = get_installed_skill_manifest(skill_dir.name)
        if manifest:
            skills.append(manifest)

    return skills


def find_dependent_skills(skill_name: str) -> List[SkillManifest]:
    """Find all skills that depend on the given skill.

    Args:
        skill_name: Name of the skill to check.

    Returns:
        List of SkillManifest objects that depend on the skill.
    """
    dependents: List[SkillManifest] = []

    for manifest in get_all_installed_skills():
        if manifest.has_dependency(skill_name):
            dependents.append(manifest)

    return dependents


def remove_skill(skill_name: str, force: bool = False) -> None:
    """Remove an installed skill.

    Args:
        skill_name: Name of the skill to remove.
        force: Whether to force removal without confirmation.

    Raises:
        click.ClickException: If removal fails or is cancelled.
    """
    # Check if skill is installed
    skill_dir = get_installed_skill_path(skill_name)
    if not skill_dir:
        raise click.ClickException(f"Skill '{skill_name}' is not installed")

    # Get manifest for display
    manifest = get_installed_skill_manifest(skill_name)

    # Check for dependent skills
    dependents = find_dependent_skills(skill_name)

    if dependents and not force:
        dependent_names = [d.name for d in dependents]
        raise click.ClickException(
            f"Cannot remove '{skill_name}' because it is required by: "
            f"{', '.join(dependent_names)}. Use --force to remove anyway."
        )

    # Show what will be removed
    click.echo(f"Removing skill: {skill_name}")

    if manifest:
        click.echo(f"  Version: {manifest.version}")
        click.echo(f"  Type: {manifest.type.value}")
        click.echo(f"  Author: {manifest.author}")

    if dependents:
        click.echo(f"  Warning: {len(dependents)} dependent skill(s) will be affected:")
        for dep in dependents:
            click.echo(f"    - {dep.name}")

    # Remove the skill directory
    try:
        shutil.rmtree(skill_dir)
    except Exception as e:
        raise click.ClickException(f"Failed to remove skill directory: {e}")

    click.echo(f"Successfully removed '{skill_name}'")


@click.command(name="remove")
@click.argument("skill_name")
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force removal without checking dependencies",
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Skip confirmation prompt",
)
def remove_command(skill_name: str, force: bool, yes: bool):
    """Remove an installed skill.

    SKILL_NAME is the name of the skill to remove.

    By default, the command will check if other installed skills depend on
    the skill being removed. If dependencies exist, removal will be blocked
    unless --force is used.

    Examples:
        kurultai remove web-scraper              # Remove with confirmation
        kurultai remove web-scraper --yes        # Skip confirmation
        kurultai remove web-scraper --force      # Force removal (ignore deps)
    """
    # Check if skill exists
    skill_dir = get_installed_skill_path(skill_name)
    if not skill_dir:
        raise click.ClickException(f"Skill '{skill_name}' is not installed")

    # Get manifest for display
    manifest = get_installed_skill_manifest(skill_name)

    # Check for dependent skills
    dependents = find_dependent_skills(skill_name)

    if dependents and not force:
        dependent_names = [d.name for d in dependents]
        raise click.ClickException(
            f"Cannot remove '{skill_name}' because it is required by: "
            f"{', '.join(dependent_names)}. Use --force to remove anyway."
        )

    # Show confirmation unless --yes
    if not yes:
        click.echo(f"You are about to remove: {skill_name}")

        if manifest:
            click.echo(f"  Version: {manifest.version}")
            click.echo(f"  Author: {manifest.author}")

        if dependents:
            click.echo()
            click.echo("Warning: The following skills depend on this skill:")
            for dep in dependents:
                click.echo(f"  - {dep.name}")
            click.echo()
            click.echo("These skills may not work correctly after removal.")

        click.echo()
        if not click.confirm("Are you sure you want to remove this skill?"):
            click.echo("Aborted.")
            return

    # Perform removal
    try:
        remove_skill(skill_name, force=force)
    except click.ClickException:
        raise
    except Exception as e:
        raise click.ClickException(f"Failed to remove skill: {e}")
