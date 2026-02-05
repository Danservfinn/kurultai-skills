"""Publishing utilities for Kurultai CLI.

This module provides comprehensive skill validation, git operations,
and registry management for publishing skills to the Kurultai registry.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

from kurultai.config import KURULTAI_HOME, get_config
from kurultai.exceptions import KurultaiError
from kurultai.models.skill import SkillManifest, compare_versions, validate_semver
from kurultai.validators import ManifestValidationError, validate_manifest


class PublishingError(KurultaiError):
    """Exception raised when skill publishing fails."""

    pass


class ValidationError(KurultaiError):
    """Exception raised when skill validation fails."""

    pass


class GitError(KurultaiError):
    """Exception raised when git operations fail."""

    pass


class RegistryError(KurultaiError):
    """Exception raised when registry operations fail."""

    pass


@dataclass
class ValidationResult:
    """Result of skill validation.

    Attributes:
        is_valid: Whether validation passed
        errors: List of validation error messages
        warnings: List of validation warnings
        manifest: The validated manifest (if successful)
    """

    is_valid: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    manifest: Optional[SkillManifest] = None

    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)

    def format_report(self) -> str:
        """Format validation report as a string."""
        lines = []

        if self.is_valid and not self.warnings:
            lines.append("Validation passed!")
        elif self.is_valid:
            lines.append("Validation passed with warnings.")
        else:
            lines.append(f"Validation failed with {len(self.errors)} error(s):")

        if self.errors:
            lines.append("")
            lines.append("Errors:")
            for i, error in enumerate(self.errors, 1):
                lines.append(f"  {i}. {error}")

        if self.warnings:
            lines.append("")
            lines.append("Warnings:")
            for i, warning in enumerate(self.warnings, 1):
                lines.append(f"  {i}. {warning}")

        return "\n".join(lines)


class SkillValidator:
    """Comprehensive skill validation for publishing.

    Validates skill manifests, required files, semantic versions,
    and prompt quality before publishing.
    """

    # Required files for a skill package
    REQUIRED_FILES = ["skill.yaml", "README.md"]

    # Recommended files for a skill package
    RECOMMENDED_FILES = ["LICENSE", "CHANGELOG.md", ".gitignore"]

    # Maximum file sizes (in bytes)
    MAX_PROMPT_SIZE = 100 * 1024  # 100KB
    MAX_TOTAL_SIZE = 10 * 1024 * 1024  # 10MB

    def __init__(self, skill_path: Path):
        """Initialize the validator.

        Args:
            skill_path: Path to the skill directory.
        """
        self.skill_path = Path(skill_path).resolve()
        self.result = ValidationResult()

    def validate_all(self) -> ValidationResult:
        """Run all validation checks.

        Returns:
            ValidationResult with all errors and warnings.
        """
        self.result = ValidationResult()

        # Basic path validation
        if not self._validate_path():
            return self.result

        # Validate manifest exists and is valid
        manifest = self._validate_manifest()
        if not manifest:
            return self.result

        self.result.manifest = manifest

        # Validate required files
        self._validate_required_files()

        # Validate semantic version
        self._validate_semantic_version()

        # Validate prompts
        self._validate_prompts()

        # Validate total size
        self._validate_size_limits()

        # Check for security issues
        self._validate_security()

        # Set final validity
        self.result.is_valid = len(self.result.errors) == 0

        return self.result

    def _validate_path(self) -> bool:
        """Validate the skill path exists and is a directory.

        Returns:
            True if path is valid, False otherwise.
        """
        if not self.skill_path.exists():
            self.result.add_error(f"Skill path does not exist: {self.skill_path}")
            return False

        if not self.skill_path.is_dir():
            self.result.add_error(f"Skill path is not a directory: {self.skill_path}")
            return False

        return True

    def _validate_manifest(self) -> Optional[SkillManifest]:
        """Validate the skill.yaml manifest file.

        Returns:
            Validated SkillManifest or None if invalid.
        """
        manifest_path = self.skill_path / "skill.yaml"
        if not manifest_path.exists():
            manifest_path = self.skill_path / "skill.yml"

        if not manifest_path.exists():
            self.result.add_error("Missing required file: skill.yaml")
            return None

        try:
            manifest = validate_manifest(manifest_path)
            return manifest
        except ManifestValidationError as e:
            self.result.add_error(f"Invalid manifest: {e.message}")
            if e.errors:
                for error in e.errors:
                    if isinstance(error, dict):
                        field = error.get("field", "unknown")
                        msg = error.get("message", str(error))
                        self.result.add_error(f"  - [{field}] {msg}")
            return None
        except Exception as e:
            self.result.add_error(f"Failed to read manifest: {e}")
            return None

    def _validate_required_files(self) -> None:
        """Validate all required files are present."""
        for filename in self.REQUIRED_FILES:
            file_path = self.skill_path / filename
            if not file_path.exists():
                self.result.add_error(f"Missing required file: {filename}")

        # Check recommended files (warnings only)
        for filename in self.RECOMMENDED_FILES:
            file_path = self.skill_path / filename
            if not file_path.exists():
                self.result.add_warning(f"Missing recommended file: {filename}")

    def _validate_semantic_version(self) -> None:
        """Validate the version is a proper semantic version."""
        if not self.result.manifest:
            return

        version = self.result.manifest.version

        if not validate_semver(version):
            self.result.add_error(
                f"Invalid semantic version: '{version}'. "
                "Expected format: MAJOR.MINOR.PATCH[-prerelease][+build]"
            )

    def _validate_prompts(self) -> None:
        """Validate prompt files for quality and syntax."""
        if not self.result.manifest:
            return

        prompts_dir = self.skill_path / self.result.manifest.prompts_dir

        if not prompts_dir.exists():
            # Prompts directory is optional
            return

        if not prompts_dir.is_dir():
            self.result.add_error(
                f"Prompts path exists but is not a directory: {prompts_dir}"
            )
            return

        # Find all prompt files
        prompt_files = list(prompts_dir.glob("*.md"))

        if not prompt_files:
            self.result.add_warning(
                f"No prompt files found in {self.result.manifest.prompts_dir}/"
            )
            return

        for prompt_file in prompt_files:
            # Check file size
            size = prompt_file.stat().st_size
            if size > self.MAX_PROMPT_SIZE:
                self.result.add_error(
                    f"Prompt file too large: {prompt_file.name} ({size} bytes, "
                    f"max {self.MAX_PROMPT_SIZE} bytes)"
                )

            # Validate prompt content
            try:
                content = prompt_file.read_text(encoding="utf-8")
                self._validate_prompt_content(prompt_file.name, content)
            except Exception as e:
                self.result.add_error(
                    f"Failed to read prompt file {prompt_file.name}: {e}"
                )

    def _validate_prompt_content(self, filename: str, content: str) -> None:
        """Validate the content of a prompt file.

        Args:
            filename: Name of the prompt file.
            content: Content of the prompt file.
        """
        # Check for empty prompts
        if not content.strip():
            self.result.add_error(f"Prompt file is empty: {filename}")
            return

        # Check for very short prompts
        if len(content.strip()) < 50:
            self.result.add_warning(f"Prompt file is very short: {filename}")

        # Check for common syntax issues
        # Unclosed code blocks
        code_block_count = content.count("```")
        if code_block_count % 2 != 0:
            self.result.add_warning(f"Unclosed code block in {filename}")

        # Check for potentially problematic patterns
        problematic_patterns = [
            (r"\{\{[^}]*\}", "template syntax"),
            (r"<%.*%>", "ERB syntax"),
            (r"\$\{[^}]*\}", "shell variable syntax"),
        ]

        for pattern, description in problematic_patterns:
            if re.search(pattern, content):
                self.result.add_warning(
                    f"{filename} contains {description} which may cause issues"
                )

    def _validate_size_limits(self) -> None:
        """Validate the total package size is within limits."""
        total_size = 0

        for file_path in self.skill_path.rglob("*"):
            if file_path.is_file():
                try:
                    total_size += file_path.stat().st_size
                except Exception:
                    pass

        if total_size > self.MAX_TOTAL_SIZE:
            self.result.add_error(
                f"Total package size ({total_size} bytes) exceeds maximum "
                f"({self.MAX_TOTAL_SIZE} bytes)"
            )

    def _validate_security(self) -> None:
        """Validate the skill for security issues."""
        # Check for dangerous files
        dangerous_patterns = [
            "*.exe",
            "*.dll",
            "*.so",
            "*.dylib",
            "*.bin",
            "__pycache__",
            "*.pyc",
            ".env",
            "*.key",
            "*.pem",
            "*.crt",
        ]

        for pattern in dangerous_patterns:
            matches = list(self.skill_path.rglob(pattern))
            if matches:
                for match in matches:
                    self.result.add_warning(
                        f"Potentially sensitive file found: {match.relative_to(self.skill_path)}"
                    )

        # Check for secrets in files
        secret_patterns = [
            (r"(?i)(api[_-]?key|apikey)\s*[=:]\s*['\"][^'\"]+['\"]", "API key"),
            (r"(?i)(password|passwd|pwd)\s*[=:]\s*['\"][^'\"]+['\"]", "password"),
            (r"(?i)(secret|token)\s*[=:]\s*['\"][^'\"]+['\"]", "secret/token"),
            (r"(?i)private[_-]?key\s*[=:]", "private key"),
        ]

        for file_path in self.skill_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in [
                ".py",
                ".js",
                ".ts",
                ".yaml",
                ".yml",
                ".json",
                ".sh",
                ".md",
            ]:
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    for pattern, description in secret_patterns:
                        if re.search(pattern, content):
                            self.result.add_error(
                                f"Potential {description} found in {file_path.relative_to(self.skill_path)}. "
                                "Remove secrets before publishing."
                            )
                except Exception:
                    pass

    def validate_version_newer(
        self, current_version: str, published_version: Optional[str] = None
    ) -> bool:
        """Validate that the current version is newer than published.

        Args:
            current_version: The version being published.
            published_version: The currently published version (if any).

        Returns:
            True if version is valid for publishing.
        """
        if not published_version:
            return True

        try:
            comparison = compare_versions(current_version, published_version)
            if comparison <= 0:
                self.result.add_error(
                    f"Version {current_version} is not newer than published "
                    f"version {published_version}. Use --force to override."
                )
                return False
            return True
        except ValueError as e:
            self.result.add_error(f"Version comparison failed: {e}")
            return False


class GitManager:
    """Git operations for skill publishing.

    Manages git state verification, tagging, and pushing for skill releases.
    """

    def __init__(self, skill_path: Path):
        """Initialize the git manager.

        Args:
            skill_path: Path to the skill directory.
        """
        self.skill_path = Path(skill_path).resolve()
        self._git_available = self._check_git_available()

    def _check_git_available(self) -> bool:
        """Check if git is available in PATH.

        Returns:
            True if git is available, False otherwise.
        """
        try:
            subprocess.run(
                ["git", "--version"],
                capture_output=True,
                check=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _run_git(
        self, args: List[str], check: bool = True, cwd: Optional[Path] = None
    ) -> subprocess.CompletedProcess:
        """Run a git command.

        Args:
            args: Git command arguments.
            check: Whether to raise on non-zero exit.
            cwd: Working directory (defaults to skill_path).

        Returns:
            CompletedProcess instance.

        Raises:
            GitError: If git command fails.
        """
        if not self._git_available:
            raise GitError("Git is not installed or not in PATH")

        cmd = ["git"] + args
        working_dir = cwd or self.skill_path

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=check,
                cwd=working_dir,
            )
            return result
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else e.stdout.strip()
            raise GitError(f"Git command failed: {error_msg}")
        except Exception as e:
            raise GitError(f"Git command failed: {e}")

    def is_git_repository(self) -> bool:
        """Check if the skill path is a git repository.

        Returns:
            True if it's a git repository, False otherwise.
        """
        try:
            result = self._run_git(["rev-parse", "--git-dir"], check=False)
            return result.returncode == 0
        except GitError:
            return False

    def has_remote(self) -> bool:
        """Check if the repository has a remote configured.

        Returns:
            True if a remote exists, False otherwise.
        """
        try:
            result = self._run_git(["remote"], check=False)
            return bool(result.stdout.strip())
        except GitError:
            return False

    def get_remote_url(self) -> Optional[str]:
        """Get the origin remote URL.

        Returns:
            Remote URL or None if not set.
        """
        try:
            result = self._run_git(["remote", "get-url", "origin"], check=False)
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except GitError:
            return None

    def is_clean(self) -> Tuple[bool, List[str]]:
        """Check if the working directory is clean.

        Returns:
            Tuple of (is_clean, list of uncommitted changes).
        """
        try:
            # Check for staged changes
            result = self._run_git(["diff", "--cached", "--name-only"], check=False)
            staged = result.stdout.strip().split("\n") if result.stdout.strip() else []

            # Check for unstaged changes
            result = self._run_git(["diff", "--name-only"], check=False)
            unstaged = result.stdout.strip().split("\n") if result.stdout.strip() else []

            # Check for untracked files
            result = self._run_git(
                ["ls-files", "--others", "--exclude-standard"], check=False
            )
            untracked = result.stdout.strip().split("\n") if result.stdout.strip() else []

            all_changes = [f for f in staged + unstaged + untracked if f]
            return len(all_changes) == 0, all_changes

        except GitError:
            return False, ["Unable to check git status"]

    def get_current_branch(self) -> Optional[str]:
        """Get the current branch name.

        Returns:
            Branch name or None if not on a branch.
        """
        try:
            result = self._run_git(["branch", "--show-current"], check=False)
            if result.returncode == 0:
                return result.stdout.strip() or None
            return None
        except GitError:
            return None

    def tag_exists(self, tag: str) -> bool:
        """Check if a tag already exists.

        Args:
            tag: Tag name to check.

        Returns:
            True if tag exists, False otherwise.
        """
        try:
            result = self._run_git(["rev-parse", "--verify", f"refs/tags/{tag}"], check=False)
            return result.returncode == 0
        except GitError:
            return False

    def create_tag(self, version: str, message: Optional[str] = None) -> str:
        """Create a git tag for the version.

        Args:
            version: The version string (e.g., "1.0.0").
            message: Optional tag message.

        Returns:
            The tag name created.

        Raises:
            GitError: If tag creation fails.
        """
        tag = f"v{version}"

        if self.tag_exists(tag):
            raise GitError(f"Tag {tag} already exists")

        tag_message = message or f"Release version {version}"

        try:
            self._run_git(["tag", "-a", tag, "-m", tag_message])
            return tag
        except GitError:
            raise

    def push_tag(self, tag: str, remote: str = "origin") -> None:
        """Push a tag to the remote.

        Args:
            tag: Tag name to push.
            remote: Remote name (default: origin).

        Raises:
            GitError: If push fails.
        """
        try:
            self._run_git(["push", remote, tag])
        except GitError:
            raise

    def get_commit_hash(self, ref: str = "HEAD") -> Optional[str]:
        """Get the commit hash for a reference.

        Args:
            ref: Git reference (default: HEAD).

        Returns:
            Commit hash or None if not found.
        """
        try:
            result = self._run_git(["rev-parse", ref], check=False)
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except GitError:
            return None


class RegistryUpdater:
    """Registry index management for skill publishing.

    Updates the local and remote registry index with skill information.
    """

    def __init__(self, registry_path: Optional[Path] = None):
        """Initialize the registry updater.

        Args:
            registry_path: Path to the local registry index.
                Defaults to ~/.kurultai/registry.
        """
        if registry_path:
            self.registry_path = Path(registry_path)
        else:
            self.registry_path = KURULTAI_HOME / "registry"

        self.skills_file = self.registry_path / "skills.json"
        self._ensure_registry_dir()

    def _ensure_registry_dir(self) -> None:
        """Ensure the registry directory exists."""
        self.registry_path.mkdir(parents=True, exist_ok=True)

    def _load_skills_index(self) -> Dict[str, Any]:
        """Load the skills index from disk.

        Returns:
            Dictionary containing the skills index.
        """
        if not self.skills_file.exists():
            return {"version": "1.0.0", "skills": {}, "updated_at": None}

        try:
            with open(self.skills_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise RegistryError(f"Failed to parse skills.json: {e}")
        except Exception as e:
            raise RegistryError(f"Failed to read skills.json: {e}")

    def _save_skills_index(self, index: Dict[str, Any]) -> None:
        """Save the skills index to disk.

        Args:
            index: Dictionary containing the skills index.
        """
        try:
            index["updated_at"] = datetime.utcnow().isoformat() + "Z"

            with open(self.skills_file, "w", encoding="utf-8") as f:
                json.dump(index, f, indent=2, sort_keys=True)
        except Exception as e:
            raise RegistryError(f"Failed to write skills.json: {e}")

    def get_skill_info(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a skill from the registry.

        Args:
            skill_name: Name of the skill.

        Returns:
            Skill information dictionary or None if not found.
        """
        index = self._load_skills_index()
        return index["skills"].get(skill_name)

    def get_published_version(self, skill_name: str) -> Optional[str]:
        """Get the currently published version of a skill.

        Args:
            skill_name: Name of the skill.

        Returns:
            Published version string or None if not published.
        """
        info = self.get_skill_info(skill_name)
        if info:
            return info.get("version")
        return None

    def update_skill(
        self,
        manifest: SkillManifest,
        commit_hash: Optional[str] = None,
        remote_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update or add a skill to the registry index.

        Args:
            manifest: The skill manifest.
            commit_hash: Optional git commit hash.
            remote_url: Optional git remote URL.

        Returns:
            Updated skill entry.
        """
        index = self._load_skills_index()

        skill_entry = {
            "name": manifest.name,
            "version": manifest.version,
            "description": manifest.description,
            "author": manifest.author,
            "type": manifest.type.value,
            "tags": manifest.tags,
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }

        if manifest.homepage:
            skill_entry["homepage"] = manifest.homepage

        if manifest.repository:
            skill_entry["repository"] = manifest.repository
        elif remote_url:
            skill_entry["repository"] = remote_url

        if commit_hash:
            skill_entry["commit_hash"] = commit_hash

        if manifest.dependencies:
            skill_entry["dependencies"] = manifest.dependencies

        # Add version history
        if manifest.name in index["skills"]:
            old_entry = index["skills"][manifest.name]
            if "version_history" in old_entry:
                skill_entry["version_history"] = old_entry["version_history"]
            else:
                skill_entry["version_history"] = []

            # Add previous version to history
            if old_entry.get("version") != manifest.version:
                skill_entry["version_history"].append({
                    "version": old_entry["version"],
                    "updated_at": old_entry.get("updated_at"),
                })
                # Keep only last 10 versions
                skill_entry["version_history"] = skill_entry["version_history"][-10:]
        else:
            skill_entry["version_history"] = []

        index["skills"][manifest.name] = skill_entry
        self._save_skills_index(index)

        return skill_entry

    def remove_skill(self, skill_name: str) -> bool:
        """Remove a skill from the registry index.

        Args:
            skill_name: Name of the skill to remove.

        Returns:
            True if skill was removed, False if not found.
        """
        index = self._load_skills_index()

        if skill_name not in index["skills"]:
            return False

        del index["skills"][skill_name]
        self._save_skills_index(index)

        return True

    def list_skills(self) -> List[Dict[str, Any]]:
        """List all skills in the registry.

        Returns:
            List of skill entry dictionaries.
        """
        index = self._load_skills_index()
        return list(index["skills"].values())


class PublishingChecklist:
    """Publishing checklist validation.

    Ensures all prerequisites are met before publishing.
    """

    CHECKLIST_ITEMS = [
        "manifest_valid",
        "required_files_present",
        "version_valid",
        "prompts_valid",
        "git_clean",
        "git_tag_created",
        "registry_updated",
    ]

    def __init__(self):
        """Initialize the checklist."""
        self.items: Dict[str, bool] = {item: False for item in self.CHECKLIST_ITEMS}
        self.messages: Dict[str, str] = {}

    def mark_complete(self, item: str, message: str = "") -> None:
        """Mark a checklist item as complete.

        Args:
            item: Name of the checklist item.
            message: Optional message about the completion.
        """
        if item in self.items:
            self.items[item] = True
            if message:
                self.messages[item] = message

    def mark_incomplete(self, item: str, message: str = "") -> None:
        """Mark a checklist item as incomplete.

        Args:
            item: Name of the checklist item.
            message: Optional message about why it's incomplete.
        """
        if item in self.items:
            self.items[item] = False
            if message:
                self.messages[item] = message

    def is_complete(self) -> bool:
        """Check if all checklist items are complete.

        Returns:
            True if all items are complete, False otherwise.
        """
        return all(self.items.values())

    def get_incomplete_items(self) -> List[str]:
        """Get list of incomplete checklist items.

        Returns:
            List of incomplete item names.
        """
        return [item for item, complete in self.items.items() if not complete]

    def format_report(self) -> str:
        """Format the checklist as a string.

        Returns:
            Formatted checklist report.
        """
        lines = ["Publishing Checklist:"]

        for item in self.CHECKLIST_ITEMS:
            status = "[x]" if self.items[item] else "[ ]"
            message = self.messages.get(item, "")
            line = f"  {status} {item.replace('_', ' ').title()}"
            if message:
                line += f" - {message}"
            lines.append(line)

        return "\n".join(lines)


def get_published_url(skill_name: str, version: str, registry_url: Optional[str] = None) -> str:
    """Generate the published URL for a skill.

    Args:
        skill_name: Name of the skill.
        version: Version of the skill.
        registry_url: Optional registry URL.

    Returns:
        Published URL string.
    """
    if not registry_url:
        config = get_config()
        registry_url = config.registry_url

    # Format: https://registry.kurultai.ai/v1/skills/{skill_name}/{version}
    return f"{registry_url}/skills/{skill_name}/{version}"


def format_publish_success(
    manifest: SkillManifest,
    tag: str,
    registry_url: Optional[str] = None,
    dry_run: bool = False,
) -> str:
    """Format the success message for publishing.

    Args:
        manifest: The published skill manifest.
        tag: The git tag created.
        registry_url: Optional registry URL.
        dry_run: Whether this was a dry run.

    Returns:
        Formatted success message.
    """
    lines = []

    if dry_run:
        lines.append("=" * 50)
        lines.append("DRY RUN - No changes were made")
        lines.append("=" * 50)
        lines.append("")

    lines.append(f"Successfully published {manifest.name}@{manifest.version}!")
    lines.append("")
    lines.append(f"  Name: {manifest.name}")
    lines.append(f"  Version: {manifest.version}")
    lines.append(f"  Type: {manifest.type.value}")
    lines.append(f"  Author: {manifest.author}")
    lines.append(f"  Git Tag: {tag}")
    lines.append("")

    published_url = get_published_url(manifest.name, manifest.version, registry_url)
    lines.append(f"Published URL: {published_url}")
    lines.append("")

    lines.append("Next steps:")
    lines.append(f"  1. Verify the tag: git show {tag}")
    lines.append(f"  2. Install the skill: kurultai install {manifest.name}@{manifest.version}")
    lines.append(f"  3. View skill info: kurultai info {manifest.name}")

    if manifest.repository:
        lines.append("")
        lines.append(f"Repository: {manifest.repository}")

    return "\n".join(lines)
