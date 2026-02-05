"""List command for Kurultai CLI.

Handles listing installed and available skills.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import click
import yaml

from kurultai.config import SKILLS_DIR, get_config
from kurultai.models.skill import SkillManifest
from kurultai.registry import RegistryClient, get_registry_client
from kurultai.validators import validate_manifest


def get_installed_skills() -> List[SkillManifest]:
    """Get all installed skills with their manifests.

    Returns:
        List of SkillManifest objects for installed skills.
    """
    skills: List[SkillManifest] = []

    if not SKILLS_DIR.exists():
        return skills

    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue

        # Look for skill.yaml
        manifest_path = skill_dir / "skill.yaml"
        if not manifest_path.exists():
            manifest_path = skill_dir / "skill.yml"

        if not manifest_path.exists():
            continue

        try:
            manifest = validate_manifest(manifest_path)
            skills.append(manifest)
        except Exception:
            # Skip invalid manifests
            continue

    # Sort by name
    skills.sort(key=lambda s: s.name)
    return skills


def fetch_available_skills(
    registry: Optional[str] = None,
    query: Optional[str] = None,
    skill_type: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> List[dict]:
    """Fetch available skills from the registry.

    Args:
        registry: Optional registry URL override.
        query: Optional search query.
        skill_type: Optional skill type filter.
        tags: Optional tags filter.

    Returns:
        List of skill dictionaries from the registry.
    """
    client = get_registry_client()

    try:
        if query:
            # Use search functionality
            skills = client.search(query, filters={"type": skill_type, "tags": tags})
        else:
            # Use list functionality
            skills = client.list_skills(skill_type=skill_type, tags=tags)

        # Convert to dict format for compatibility
        return [skill.to_dict() for skill in skills]
    except Exception:
        # If registry fails, return empty list
        return []


def format_table(
    headers: List[str],
    rows: List[List[str]],
    min_widths: Optional[List[int]] = None,
) -> str:
    """Format data as a text table.

    Args:
        headers: Column headers.
        rows: Table rows.
        min_widths: Minimum width for each column.

    Returns:
        Formatted table string.
    """
    if not rows:
        return ""

    # Calculate column widths
    num_cols = len(headers)
    widths = [len(h) for h in headers]

    for row in rows:
        for i, cell in enumerate(row):
            if i < num_cols:
                widths[i] = max(widths[i], len(cell))

    # Apply minimum widths
    if min_widths:
        for i, min_w in enumerate(min_widths):
            if i < num_cols:
                widths[i] = max(widths[i], min_w)

    # Build table
    lines = []

    # Header row
    header_cells = [headers[i].ljust(widths[i]) for i in range(num_cols)]
    lines.append("  ".join(header_cells))

    # Separator
    separator = ["-" * w for w in widths]
    lines.append("  ".join(separator))

    # Data rows
    for row in rows:
        row_cells = []
        for i in range(num_cols):
            cell = row[i] if i < len(row) else ""
            row_cells.append(cell.ljust(widths[i]))
        lines.append("  ".join(row_cells))

    return "\n".join(lines)


def list_installed_skills() -> None:
    """List all installed skills."""
    skills = get_installed_skills()

    if not skills:
        click.echo("No skills installed.")
        click.echo(f"Skills are installed in: {SKILLS_DIR}")
        return

    click.echo(f"Installed skills ({len(skills)}):")
    click.echo()

    headers = ["NAME", "VERSION", "TYPE", "AUTHOR"]
    rows = [
        [s.name, s.version, s.type.value, s.author]
        for s in skills
    ]

    table = format_table(headers, rows, min_widths=[20, 12, 10, 20])
    click.echo(table)

    click.echo()
    click.echo(f"Location: {SKILLS_DIR}")


def list_available_skills(
    registry: Optional[str] = None,
    query: Optional[str] = None,
    skill_type: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> None:
    """List available skills from the registry.

    Args:
        registry: Optional registry URL override.
        query: Optional search query.
        skill_type: Optional skill type filter.
        tags: Optional tags filter.
    """
    config = get_config()
    registry_url = registry or config.registry_url

    click.echo(f"Fetching available skills from: {registry_url}")
    if query:
        click.echo(f"Search query: '{query}'")
    click.echo()

    skills = fetch_available_skills(registry, query, skill_type, tags)

    if not skills:
        if query:
            click.echo(f"No skills found matching '{query}'.")
        else:
            click.echo("No skills found in registry or unable to connect.")
            click.echo()
            click.echo("Note: This feature requires a registry server.")
            click.echo("You can still install skills directly from Git URLs:")
            click.echo("  kurultai install https://github.com/user/skill-repo.git")
        return

    click.echo(f"Available skills ({len(skills)}):")
    click.echo()

    headers = ["NAME", "VERSION", "TYPE", "DESCRIPTION"]
    rows = []

    for skill in skills:
        name = skill.get("name", "unknown")
        version = skill.get("version", "-")
        skill_type_val = skill.get("type", "skill")
        description = skill.get("description", "")[:40]
        if len(skill.get("description", "")) > 40:
            description += "..."

        rows.append([name, version, skill_type_val, description])

    table = format_table(headers, rows, min_widths=[20, 12, 10, 40])
    click.echo(table)


def list_skills_with_details() -> None:
    """List installed skills with detailed information."""
    skills = get_installed_skills()

    if not skills:
        click.echo("No skills installed.")
        return

    click.echo(f"Installed skills ({len(skills)}):")
    click.echo()

    for skill in skills:
        click.echo(f"  {skill.name}@{skill.version}")
        click.echo(f"    Type: {skill.type.value}")
        click.echo(f"    Author: {skill.author}")
        click.echo(f"    Description: {skill.description}")

        if skill.tags:
            click.echo(f"    Tags: {', '.join(skill.tags)}")

        if skill.dependencies:
            deps_str = ", ".join(
                f"{name}@{constraint}"
                for name, constraint in skill.dependencies.items()
            )
            click.echo(f"    Dependencies: {deps_str}")

        click.echo()


def search_registry(
    query: str,
    registry: Optional[str] = None,
    skill_type: Optional[str] = None,
    tags: Optional[List[str]] = None,
) -> None:
    """Search the skill registry.

    Args:
        query: Search query string.
        registry: Optional registry URL override.
        skill_type: Optional skill type filter.
        tags: Optional tags filter.
    """
    config = get_config()
    registry_url = registry or config.registry_url

    click.echo(f"Searching registry at: {registry_url}")
    click.echo(f"Query: '{query}'")
    click.echo()

    client = get_registry_client()

    try:
        # Use fuzzy search for better results
        results = client.fuzzy_search(
            query,
            max_results=20,
            min_score=0.1,
        )

        # Apply additional filters
        if skill_type or tags:
            filtered_results = []
            for skill, score in results:
                if skill_type and skill.type != skill_type:
                    continue
                if tags:
                    required_tags = set(t.lower() for t in tags)
                    skill_tags = set(t.lower() for t in skill.tags)
                    if not required_tags.issubset(skill_tags):
                        continue
                filtered_results.append((skill, score))
            results = filtered_results

        if not results:
            click.echo(f"No skills found matching '{query}'.")
            click.echo()
            click.echo("Try:")
            click.echo("  - Using different keywords")
            click.echo("  - Searching by tag: kurultai list --available --tags <tag>")
            click.echo("  - Listing all skills: kurultai list --available")
            return

        click.echo(f"Found {len(results)} skill(s) matching '{query}':")
        click.echo()

        headers = ["NAME", "VERSION", "TYPE", "RELEVANCE", "DESCRIPTION"]
        rows = []

        for skill, score in results:
            description = skill.description[:35]
            if len(skill.description) > 35:
                description += "..."

            # Format relevance as percentage
            relevance = f"{int(score * 100)}%"

            rows.append([
                skill.name,
                skill.version,
                skill.type,
                relevance,
                description,
            ])

        table = format_table(headers, rows, min_widths=[20, 12, 10, 10, 38])
        click.echo(table)

        click.echo()
        click.echo("To install a skill:")
        click.echo("  kurultai install <name>")

    except Exception as e:
        click.echo(f"Error searching registry: {e}")


@click.command(name="list")
@click.option(
    "--available",
    "-a",
    is_flag=True,
    help="Show available skills from registry instead of installed",
)
@click.option(
    "--installed",
    "-i",
    is_flag=True,
    help="Show only installed skills (default behavior)",
)
@click.option(
    "--registry",
    "-r",
    help="Registry URL to use for fetching available skills",
)
@click.option(
    "--detailed",
    "-d",
    is_flag=True,
    help="Show detailed information for installed skills",
)
@click.option(
    "--search",
    "-s",
    help="Search for skills by name, description, or tags",
)
@click.option(
    "--type",
    "skill_type",
    type=click.Choice(["engine", "skill", "workflow"]),
    help="Filter by skill type",
)
@click.option(
    "--tags",
    "-t",
    help="Filter by tags (comma-separated)",
)
def list_command(
    available: bool,
    installed: bool,
    registry: Optional[str],
    detailed: bool,
    search: Optional[str],
    skill_type: Optional[str],
    tags: Optional[str],
):
    """List installed or available skills.

    By default, lists installed skills. Use --available to see skills
    that can be installed from the registry. Use --search to find
    specific skills.

    Examples:
        kurultai list                      # List installed skills
        kurultai list --available          # List available skills from registry
        kurultai list --search "review"    # Search for code review skills
        kurultai list -a --type skill      # List only skills (not engines)
        kurultai list -a --tags "horde"    # List skills with 'horde' tag
        kurultai list --detailed           # Show detailed info for installed skills
        kurultai list -a -r https://...    # Use custom registry
    """
    # Parse tags
    tag_list = [t.strip() for t in tags.split(",")] if tags else None

    if search:
        # Search mode
        search_registry(search, registry, skill_type, tag_list)
    elif available:
        list_available_skills(registry, skill_type=skill_type, tags=tag_list)
    elif detailed:
        list_skills_with_details()
    else:
        list_installed_skills()
