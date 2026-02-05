"""Install command for Kurultai CLI.

Handles skill installation from registry, including dependency resolution
and progress reporting.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Set, Tuple

import click
import yaml

from kurultai.config import SKILLS_DIR, ensure_directories, get_config
from kurultai.dependencies import (
    DependencyGraph,
    DependencyResolver,
    DependencySource,
    ResolvedDependency,
    generate_lock_file,
)
from kurultai.exceptions import (
    CircularDependencyError,
    DependencyConflictError,
    ResolutionError,
    SkillNotFoundError,
)
from kurultai.models.skill import Dependency, SkillManifest, satisfies_constraint
from kurultai.validators import ManifestValidationError, validate_manifest


def get_registry_url(registry: Optional[str] = None) -> str:
    """Get the registry URL from config or parameter.

    Args:
        registry: Optional registry URL override.

    Returns:
        The registry URL to use.
    """
    if registry:
        return registry
    config = get_config()
    return config.registry_url


def resolve_skill_url(skill_name: str, version: Optional[str] = None, registry: Optional[str] = None) -> str:
    """Resolve a skill name to a Git repository URL.

    Args:
        skill_name: Name of the skill.
        version: Optional version constraint.
        registry: Optional registry URL.

    Returns:
        Git repository URL for the skill.

    Raises:
        click.ClickException: If the skill cannot be resolved.
    """
    registry_url = get_registry_url(registry)

    # For now, assume skills are in the format: {registry}/skills/{skill_name}.git
    # This can be extended to support different registry formats
    if skill_name.startswith("http://") or skill_name.startswith("https://"):
        return skill_name

    if skill_name.startswith("git@"):
        return skill_name

    # Try to construct a registry URL
    # Support both GitHub-style and custom registries
    if "github.com" in registry_url or "gitlab.com" in registry_url:
        # Format: https://github.com/kurultai/skills/{skill_name}.git
        return f"{registry_url}/skills/{skill_name}.git"

    # Default format
    return f"{registry_url}/skills/{skill_name}.git"


def clone_skill_repo(url: str, dest: Path, version: Optional[str] = None) -> None:
    """Clone a skill repository to the destination.

    Args:
        url: Git repository URL.
        dest: Destination directory.
        version: Optional version/tag to checkout.

    Raises:
        click.ClickException: If cloning fails.
    """
    try:
        # Clone the repository
        cmd = ["git", "clone", "--depth", "1", url, str(dest)]

        # If version is specified and not 'latest', try to clone specific tag
        if version and version != "latest":
            # Use --branch to clone specific tag/branch
            cmd = ["git", "clone", "--branch", version, "--depth", "1", url, str(dest)]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else "Unknown error"
        raise click.ClickException(f"Failed to clone skill repository: {error_msg}")
    except FileNotFoundError:
        raise click.ClickException("Git is not installed or not in PATH")


def parse_skill_manifest(skill_dir: Path) -> SkillManifest:
    """Parse and validate the skill.yaml manifest.

    Args:
        skill_dir: Directory containing the skill.

    Returns:
        Validated SkillManifest object.

    Raises:
        click.ClickException: If manifest is invalid or missing.
    """
    manifest_path = skill_dir / "skill.yaml"
    if not manifest_path.exists():
        manifest_path = skill_dir / "skill.yml"

    if not manifest_path.exists():
        raise click.ClickException(
            f"No skill.yaml manifest found in {skill_dir}"
        )

    try:
        return validate_manifest(manifest_path)
    except ManifestValidationError as e:
        raise click.ClickException(f"Invalid skill manifest: {e.message}")
    except Exception as e:
        raise click.ClickException(f"Failed to read skill manifest: {e}")


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


def is_skill_installed(skill_name: str) -> bool:
    """Check if a skill is already installed.

    Args:
        skill_name: Name of the skill.

    Returns:
        True if the skill is installed, False otherwise.
    """
    return get_installed_skill_path(skill_name) is not None


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

    try:
        return parse_skill_manifest(skill_dir)
    except click.ClickException:
        return None


def install_resolved_dependency(
    resolved: ResolvedDependency,
    progress: bool = True,
    force: bool = False,
) -> SkillManifest:
    """Install a resolved dependency.

    Args:
        resolved: The resolved dependency to install.
        progress: Whether to show progress output.
        force: Whether to force reinstall if already exists.

    Returns:
        The installed skill's manifest.
    """
    return install_skill(
        skill_name=resolved.name,
        version=resolved.version,
        registry=None,  # Use resolved URL directly
        installed=set(),
        progress=progress,
        force=force,
        resolved_url=resolved.resolved_url,
        source=resolved.source,
    )


def install_dependencies_with_resolver(
    manifest: SkillManifest,
    progress: bool = True,
    registry: Optional[str] = None,
    force: bool = False,
    no_deps: bool = False,
) -> Tuple[List[str], List[str], Optional[DependencyGraph]]:
    """Install dependencies using the dependency resolver.

    Args:
        manifest: The skill manifest containing dependencies.
        progress: Whether to show progress output.
        registry: Optional registry URL.
        force: Whether to force reinstall.
        no_deps: Whether to skip dependencies.

    Returns:
        Tuple of (successfully_installed, failed_installs, dependency_graph).
    """
    successful: List[str] = []
    failed: List[str] = []
    graph: Optional[DependencyGraph] = None

    if no_deps or not manifest.dependencies:
        return successful, failed, graph

    if progress:
        click.echo("Resolving dependencies...")

    try:
        resolver = DependencyResolver(registry_url=get_registry_url(registry))
        graph = resolver.resolve(manifest, include_optional=False)

        # Get installation order (topological sort)
        try:
            installation_order = graph.get_installation_order()
        except CircularDependencyError as e:
            if progress:
                click.echo(f"Error: {e}", err=True)
            failed.append(f"circular-dependency: {' -> '.join(e.cycle)}")
            return successful, failed, graph

        if progress and installation_order:
            click.echo(f"Installing {len(installation_order)} dependencies...")

        for dep in installation_order:
            if is_skill_installed(dep.name):
                existing = get_installed_skill_manifest(dep.name)
                if existing and not force:
                    if progress:
                        click.echo(f"  {dep.name}@{existing.version} already installed, skipping")
                    successful.append(dep.name)
                    continue
                elif existing and force:
                    if progress:
                        click.echo(f"  Reinstalling {dep.name}...")
                    remove_skill(dep.name, force=True)

            if progress:
                click.echo(f"  Installing: {dep.name}@{dep.version}")

            try:
                install_resolved_dependency(dep, progress=False, force=force)
                successful.append(dep.name)
            except click.ClickException as e:
                if progress:
                    click.echo(f"  Failed to install {dep.name}: {e}", err=True)
                failed.append(dep.name)

    except DependencyConflictError as e:
        if progress:
            click.echo(f"Error: Dependency conflict - {e}", err=True)
        failed.append(f"conflict:{e.skill_name}")
    except ResolutionError as e:
        if progress:
            click.echo(f"Error: Failed to resolve dependency - {e}", err=True)
        failed.append(f"resolution-error:{e.skill_name or 'unknown'}")
    except SkillNotFoundError as e:
        if progress:
            click.echo(f"Error: Skill not found - {e}", err=True)
        failed.append(f"not-found:{e.skill_name}")

    return successful, failed, graph


def install_dependencies(
    manifest: SkillManifest,
    installed: Set[str],
    progress: bool = True,
    registry: Optional[str] = None,
) -> Tuple[List[str], List[str]]:
    """Install dependencies recursively (legacy method).

    Args:
        manifest: The skill manifest containing dependencies.
        installed: Set of already installed skill names (to avoid duplicates).
        progress: Whether to show progress output.
        registry: Optional registry URL.

    Returns:
        Tuple of (successfully_installed, failed_installs).
    """
    successful: List[str] = []
    failed: List[str] = []

    dependencies = manifest.get_required_dependencies()

    if not dependencies:
        return successful, failed

    if progress:
        click.echo(f"Installing {len(dependencies)} dependencies...")

    for dep in dependencies:
        if dep.name in installed:
            if progress:
                click.echo(f"  {dep.name} already installed, skipping")
            continue

        if progress:
            click.echo(f"  Installing dependency: {dep.name}@{dep.version_constraint}")

        try:
            install_skill(dep.name, dep.version_constraint, registry, installed, progress)
            successful.append(dep.name)
        except click.ClickException as e:
            if progress:
                click.echo(f"  Failed to install {dep.name}: {e}", err=True)
            failed.append(dep.name)

    return successful, failed


def install_skill(
    skill_name: str,
    version: Optional[str] = None,
    registry: Optional[str] = None,
    installed: Optional[Set[str]] = None,
    progress: bool = True,
    force: bool = False,
    resolved_url: Optional[str] = None,
    source: Optional[DependencySource] = None,
) -> SkillManifest:
    """Install a skill from the registry.

    Args:
        skill_name: Name of the skill to install.
        version: Optional version constraint.
        registry: Optional registry URL.
        installed: Set of already installed skill names.
        progress: Whether to show progress output.
        force: Whether to force reinstall if already exists.
        resolved_url: Optional pre-resolved URL (from dependency resolver).
        source: Optional source type (from dependency resolver).

    Returns:
        The installed skill's manifest.

    Raises:
        click.ClickException: If installation fails.
    """
    if installed is None:
        installed = set()

    ensure_directories()

    # Check if already installed
    if is_skill_installed(skill_name):
        if not force:
            if progress:
                click.echo(f"Skill '{skill_name}' is already installed. Use --force to reinstall.")
            existing_manifest = get_installed_skill_manifest(skill_name)
            if existing_manifest:
                return existing_manifest
            raise click.ClickException(f"Skill '{skill_name}' is installed but has invalid manifest")

        if progress:
            click.echo(f"Removing existing installation of '{skill_name}'...")
        remove_skill(skill_name, force=True)

    # Resolve skill URL if not provided
    if resolved_url:
        url = resolved_url
    else:
        if progress:
            click.echo(f"Resolving skill: {skill_name}")
        url = resolve_skill_url(skill_name, version, registry)

    if progress:
        click.echo(f"Cloning from: {url}")

    # Create temporary directory for cloning
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir) / skill_name

        try:
            clone_skill_repo(url, temp_path, version)
        except click.ClickException:
            raise
        except Exception as e:
            raise click.ClickException(f"Failed to clone repository: {e}")

        # Parse and validate manifest
        if progress:
            click.echo("Validating skill manifest...")

        manifest = parse_skill_manifest(temp_path)

        # Verify skill name matches
        if manifest.name != skill_name:
            if progress:
                click.echo(
                    f"Warning: Skill name mismatch. Expected '{skill_name}', "
                    f"found '{manifest.name}'"
                )

        # Install dependencies using resolver
        dep_successful, dep_failed, graph = install_dependencies_with_resolver(
            manifest=manifest,
            progress=progress,
            registry=registry,
            force=force,
            no_deps=False,  # Always resolve dependencies
        )

        if dep_failed:
            if progress:
                click.echo(
                    f"Warning: Failed to install {len(dep_failed)} dependencies: "
                    f"{', '.join(dep_failed)}",
                    err=True,
                )

        # Move to final location
        dest_dir = SKILLS_DIR / manifest.name

        if progress:
            click.echo(f"Installing to: {dest_dir}")

        try:
            shutil.move(str(temp_path), str(dest_dir))
        except Exception as e:
            raise click.ClickException(f"Failed to install skill: {e}")

        # Mark as installed
        installed.add(manifest.name)

        if progress:
            click.echo(f"Successfully installed {manifest.name}@{manifest.version}")

        return manifest


def remove_skill(skill_name: str, force: bool = False) -> None:
    """Remove an installed skill.

    Args:
        skill_name: Name of the skill to remove.
        force: Whether to force removal without confirmation.

    Raises:
        click.ClickException: If removal fails.
    """
    skill_dir = get_installed_skill_path(skill_name)
    if not skill_dir:
        raise click.ClickException(f"Skill '{skill_name}' is not installed")

    try:
        shutil.rmtree(skill_dir)
    except Exception as e:
        raise click.ClickException(f"Failed to remove skill: {e}")


def write_lock_file_for_manifest(
    manifest: SkillManifest,
    graph: Optional[DependencyGraph] = None,
    registry: Optional[str] = None,
    lock_file_path: Optional[Path] = None,
) -> Optional[Path]:
    """Write a lock file for the installed skill.

    Args:
        manifest: The skill manifest.
        graph: Optional dependency graph from resolution.
        registry: Optional registry URL.
        lock_file_path: Path to write lock file.

    Returns:
        Path to the written lock file, or None if no dependencies.
    """
    if not manifest.dependencies:
        return None

    if lock_file_path is None:
        lock_file_path = Path("kurultai.lock")

    try:
        if graph is None:
            # Generate lock file from scratch
            return generate_lock_file(
                manifest=manifest,
                path=lock_file_path,
                registry_url=get_registry_url(registry),
            )
        else:
            # Use existing graph
            resolver = DependencyResolver(registry_url=get_registry_url(registry))
            resolved = graph.get_installation_order()
            return resolver.write_lock_file(resolved, lock_file_path)
    except Exception as e:
        click.echo(f"Warning: Failed to generate lock file: {e}", err=True)
        return None


@click.command(name="install")
@click.argument("skill_name")
@click.option("--version", "-v", default="latest", help="Version of the skill to install")
@click.option("--registry", "-r", help="Registry URL to use")
@click.option("--force", "-f", is_flag=True, help="Force reinstall if already exists")
@click.option("--no-deps", is_flag=True, help="Skip installing dependencies")
@click.option("--lock-file", "-l", is_flag=True, help="Generate lock file after installation")
@click.option("--lock-file-path", type=click.Path(), help="Path for lock file (default: kurultai.lock)")
def install_command(
    skill_name: str,
    version: str,
    registry: Optional[str],
    force: bool,
    no_deps: bool,
    lock_file: bool,
    lock_file_path: Optional[str],
):
    """Install a skill from the registry.

    SKILL_NAME is the name of the skill to install (e.g., 'web-scraper', 'data-analysis').
    It can also be a full Git URL (https://... or git@...).

    Examples:
        kurultai install web-scraper
        kurultai install web-scraper --version 1.2.0
        kurultai install https://github.com/user/skill-repo.git
        kurultai install web-scraper --force
        kurultai install web-scraper --lock-file
    """
    try:
        installed: Set[str] = set()

        manifest = install_skill(
            skill_name=skill_name,
            version=version if version != "latest" else None,
            registry=registry,
            installed=installed,
            progress=True,
            force=force,
        )

        click.echo()
        click.echo(f"Installed: {manifest.name}@{manifest.version}")
        click.echo(f"Type: {manifest.type.value}")
        click.echo(f"Author: {manifest.author}")

        if manifest.dependencies:
            click.echo(f"Dependencies: {len(manifest.dependencies)}")

        # Generate lock file if requested or if dependencies exist
        if lock_file or manifest.dependencies:
            click.echo()
            click.echo("Generating lock file...")

            lock_path = Path(lock_file_path) if lock_file_path else Path("kurultai.lock")
            result = write_lock_file_for_manifest(
                manifest=manifest,
                graph=None,  # Will be regenerated
                registry=registry,
                lock_file_path=lock_path,
            )

            if result:
                click.echo(f"Lock file written to: {result}")
            else:
                click.echo("No lock file generated (no dependencies)")

    except click.ClickException:
        raise
    except CircularDependencyError as e:
        raise click.ClickException(f"Circular dependency detected: {' -> '.join(e.cycle)}")
    except DependencyConflictError as e:
        raise click.ClickException(f"Dependency conflict: {e}")
    except ResolutionError as e:
        raise click.ClickException(f"Failed to resolve dependencies: {e}")
    except SkillNotFoundError as e:
        raise click.ClickException(f"Skill not found: {e}")
    except Exception as e:
        raise click.ClickException(f"Installation failed: {e}")
