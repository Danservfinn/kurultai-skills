"""Publish command for Kurultai CLI.

Handles skill publishing to the registry, including validation,
git operations, and registry index updates.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import click

from kurultai.config import get_config
from kurultai.publishing import (
    GitError,
    GitManager,
    PublishingChecklist,
    PublishingError,
    RegistryError,
    RegistryUpdater,
    SkillValidator,
    format_publish_success,
)


def validate_skill_for_publish(
    skill_path: Path,
    force: bool = False,
    verbose: bool = True,
) -> tuple[bool, Optional[SkillValidator], Optional[str]]:
    """Validate a skill before publishing.

    Args:
        skill_path: Path to the skill directory.
        force: Whether to force publish even if version exists.
        verbose: Whether to show progress messages.

    Returns:
        Tuple of (success, validator, error_message).
    """
    if verbose:
        click.echo("Validating skill...")

    validator = SkillValidator(skill_path)
    result = validator.validate_all()

    if not result.is_valid:
        return False, validator, result.format_report()

    if verbose and result.warnings:
        click.echo(click.style("Warnings:", fg="yellow"))
        for warning in result.warnings:
            click.echo(f"  - {warning}")
        click.echo()

    # Check version against published version
    if result.manifest and not force:
        registry = RegistryUpdater()
        published_version = registry.get_published_version(result.manifest.name)

        if published_version:
            is_newer = validator.validate_version_newer(
                result.manifest.version, published_version
            )
            if not is_newer:
                return False, validator, "\n".join(validator.result.errors)

            if verbose:
                click.echo(
                    f"Version {result.manifest.version} is newer than "
                    f"published {published_version}"
                )

    return True, validator, None


def perform_git_operations(
    skill_path: Path,
    version: str,
    dry_run: bool = False,
    verbose: bool = True,
) -> tuple[bool, Optional[str], Optional[str]]:
    """Perform git operations for publishing.

    Args:
        skill_path: Path to the skill directory.
        version: Version to tag.
        dry_run: Whether to simulate operations.
        verbose: Whether to show progress messages.

    Returns:
        Tuple of (success, tag_name, error_message).
    """
    if verbose:
        click.echo("Checking git state...")

    git = GitManager(skill_path)

    # Check if it's a git repository
    if not git.is_git_repository():
        return False, None, "Skill directory is not a git repository. Initialize with: git init"

    # Check for clean state
    is_clean, changes = git.is_clean()
    if not is_clean:
        if verbose:
            click.echo(click.style("Uncommitted changes:", fg="yellow"))
            for change in changes[:10]:  # Show first 10
                click.echo(f"  - {change}")
            if len(changes) > 10:
                click.echo(f"  ... and {len(changes) - 10} more")
        return False, None, "Working directory is not clean. Commit or stash changes first."

    if verbose:
        click.echo("Git state is clean")

    # Check for remote
    if not git.has_remote():
        return False, None, "No git remote configured. Add a remote before publishing."

    remote_url = git.get_remote_url()
    if verbose and remote_url:
        click.echo(f"Remote: {remote_url}")

    # Create tag
    tag = f"v{version}"

    if git.tag_exists(tag):
        return False, None, f"Tag {tag} already exists. Use a different version or delete the tag."

    if dry_run:
        if verbose:
            click.echo(f"[DRY RUN] Would create tag: {tag}")
            click.echo(f"[DRY RUN] Would push tag to remote")
        return True, tag, None

    try:
        if verbose:
            click.echo(f"Creating git tag: {tag}")

        created_tag = git.create_tag(version)

        if verbose:
            click.echo(f"Pushing tag to remote...")

        git.push_tag(created_tag)

        return True, created_tag, None

    except GitError as e:
        return False, None, str(e)


def update_registry(
    skill_path: Path,
    validator: SkillValidator,
    tag: str,
    dry_run: bool = False,
    verbose: bool = True,
) -> tuple[bool, Optional[str]]:
    """Update the registry index with the published skill.

    Args:
        skill_path: Path to the skill directory.
        validator: The skill validator with manifest.
        tag: The git tag created.
        dry_run: Whether to simulate operations.
        verbose: Whether to show progress messages.

    Returns:
        Tuple of (success, error_message).
    """
    if not validator.result.manifest:
        return False, "No manifest available"

    manifest = validator.result.manifest

    if verbose:
        click.echo("Updating registry index...")

    if dry_run:
        if verbose:
            click.echo(f"[DRY RUN] Would update registry index for {manifest.name}")
        return True, None

    try:
        registry = RegistryUpdater()
        git = GitManager(skill_path)

        commit_hash = git.get_commit_hash()
        remote_url = git.get_remote_url()

        skill_entry = registry.update_skill(
            manifest=manifest,
            commit_hash=commit_hash,
            remote_url=remote_url,
        )

        if verbose:
            click.echo(f"Registry index updated: {skill_entry['name']}@{skill_entry['version']}")

        return True, None

    except RegistryError as e:
        return False, str(e)


@click.command(name="publish")
@click.argument("skill_path", type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option("--registry", "-r", help="Registry URL to use")
@click.option("--dry-run", is_flag=True, help="Validate only, do not publish")
@click.option("--force", "-f", is_flag=True, help="Force publish even if version exists")
@click.option("--verbose", "-v", is_flag=True, default=True, help="Show detailed progress")
@click.option("--quiet", "-q", is_flag=True, help="Suppress progress messages")
def publish_command(
    skill_path: str,
    registry: Optional[str],
    dry_run: bool,
    force: bool,
    verbose: bool,
    quiet: bool,
):
    """Publish a skill to the registry.

    SKILL_PATH is the path to the skill directory containing skill.yaml.

    This command validates the skill, creates a git tag, and updates the
    registry index. The working directory must be clean and the skill must
    pass all validation checks.

    Examples:
        kurultai publish ./my-skill                    # Publish skill
        kurultai publish ./my-skill --dry-run          # Validate only
        kurultai publish ./my-skill --force            # Force version update
        kurultai publish ./my-skill -r https://...     # Use custom registry
    """
    # Handle quiet mode
    if quiet:
        verbose = False

    skill_path_obj = Path(skill_path).resolve()

    if verbose:
        click.echo(f"Publishing skill from: {skill_path_obj}")
        click.echo()

    checklist = PublishingChecklist()

    # Step 1: Validate skill
    success, validator, error = validate_skill_for_publish(
        skill_path_obj, force=force, verbose=verbose
    )

    if not success:
        checklist.mark_incomplete("manifest_valid", "Validation failed")
        checklist.mark_incomplete("required_files_present")
        checklist.mark_incomplete("version_valid")
        checklist.mark_incomplete("prompts_valid")

        if verbose:
            click.echo()
            click.echo(click.style("Validation failed:", fg="red", bold=True))
            click.echo(error)
            click.echo()
            click.echo("Publishing aborted.")
        else:
            click.echo(f"Error: {error}", err=True)

        sys.exit(1)

    checklist.mark_complete("manifest_valid")
    checklist.mark_complete("required_files_present")
    checklist.mark_complete("version_valid")
    checklist.mark_complete("prompts_valid")

    if not validator or not validator.result.manifest:
        click.echo("Error: Validation succeeded but no manifest available", err=True)
        sys.exit(1)

    manifest = validator.result.manifest

    if verbose:
        click.echo(f"Skill: {manifest.name}@{manifest.version}")
        click.echo()

    # Step 2: Git operations
    success, tag, error = perform_git_operations(
        skill_path_obj,
        manifest.version,
        dry_run=dry_run,
        verbose=verbose,
    )

    if not success:
        checklist.mark_incomplete("git_clean", error or "Git state invalid")
        checklist.mark_incomplete("git_tag_created")

        if verbose:
            click.echo()
            click.echo(click.style("Git operation failed:", fg="red", bold=True))
            click.echo(error)
            click.echo()
            click.echo("Publishing aborted.")
        else:
            click.echo(f"Error: {error}", err=True)

        sys.exit(1)

    checklist.mark_complete("git_clean")
    checklist.mark_complete("git_tag_created")

    # Step 3: Update registry
    success, error = update_registry(
        skill_path_obj,
        validator,
        tag or f"v{manifest.version}",
        dry_run=dry_run,
        verbose=verbose,
    )

    if not success:
        checklist.mark_incomplete("registry_updated", error or "Registry update failed")

        if verbose:
            click.echo()
            click.echo(click.style("Registry update failed:", fg="red", bold=True))
            click.echo(error)
            click.echo()
            click.echo("Publishing aborted.")
            click.echo()
            click.echo("Note: Git tag was created. You may need to clean it up manually:")
            click.echo(f"  git tag -d {tag}")
            click.echo(f"  git push origin :refs/tags/{tag}")
        else:
            click.echo(f"Error: {error}", err=True)

        sys.exit(1)

    checklist.mark_complete("registry_updated")

    # Success output
    if verbose:
        click.echo()
        click.echo(click.style("=" * 50, fg="green"))
        click.echo()

    published_url = registry if registry else get_config().registry_url
    success_message = format_publish_success(
        manifest,
        tag or f"v{manifest.version}",
        registry_url=published_url,
        dry_run=dry_run,
    )

    click.echo(success_message)

    if verbose:
        click.echo()
        click.echo(checklist.format_report())

    if dry_run:
        sys.exit(0)


if __name__ == "__main__":
    publish_command()
