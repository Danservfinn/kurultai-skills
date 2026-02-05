"""Registry client for Kurultai CLI.

Provides functionality to search, list, and retrieve skills from the registry.
"""

from __future__ import annotations

import fnmatch
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin

import requests

from kurultai.config import get_config
from kurultai.exceptions import KurultaiError


class RegistryError(KurultaiError):
    """Error related to registry operations."""

    pass


@dataclass
class SkillDependency:
    """Represents a skill dependency."""

    name: str
    version_constraint: str
    required: bool = True

    @classmethod
    def from_dict(cls, data: dict) -> SkillDependency:
        """Create from dictionary."""
        if isinstance(data, str):
            # Simple string format: "name@version" or "name"
            if "@" in data:
                name, version = data.split("@", 1)
                return cls(name=name.strip(), version_constraint=version.strip())
            return cls(name=data.strip(), version_constraint="*")

        return cls(
            name=data["name"],
            version_constraint=data.get("version_constraint", "*"),
            required=data.get("required", True),
        )


@dataclass
class RegistrySkill:
    """Represents a skill in the registry."""

    name: str
    version: str
    description: str
    author: str
    type: str
    repository: str
    tags: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    dependencies: List[SkillDependency] = field(default_factory=list)
    entry_point: str = "prompts/main.md"
    min_kurultai_version: str = "0.1.0"
    license: str = "MIT"
    homepage: Optional[str] = None
    config: Optional[dict] = None

    @classmethod
    def from_dict(cls, data: dict) -> RegistrySkill:
        """Create from dictionary."""
        deps = [
            SkillDependency.from_dict(d) if isinstance(d, dict) else SkillDependency.from_dict(d)
            for d in data.get("dependencies", [])
        ]

        return cls(
            name=data["name"],
            version=data["version"],
            description=data["description"],
            author=data["author"],
            type=data["type"],
            repository=data["repository"],
            tags=data.get("tags", []),
            keywords=data.get("keywords", []),
            dependencies=deps,
            entry_point=data.get("entry_point", "prompts/main.md"),
            min_kurultai_version=data.get("min_kurultai_version", "0.1.0"),
            license=data.get("license", "MIT"),
            homepage=data.get("homepage"),
            config=data.get("config"),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        result = {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "type": self.type,
            "repository": self.repository,
            "tags": self.tags,
            "keywords": self.keywords,
            "dependencies": [
                {"name": d.name, "version_constraint": d.version_constraint, "required": d.required}
                for d in self.dependencies
            ],
            "entry_point": self.entry_point,
            "min_kurultai_version": self.min_kurultai_version,
            "license": self.license,
        }
        if self.homepage:
            result["homepage"] = self.homepage
        if self.config:
            result["config"] = self.config
        return result

    def matches_search(self, query: str) -> bool:
        """Check if skill matches a search query.

        Args:
            query: Search query string.

        Returns:
            True if skill matches the query.
        """
        query_lower = query.lower()

        # Check name
        if query_lower in self.name.lower():
            return True

        # Check description
        if query_lower in self.description.lower():
            return True

        # Check tags
        for tag in self.tags:
            if query_lower in tag.lower():
                return True

        # Check keywords
        for keyword in self.keywords:
            if query_lower in keyword.lower():
                return True

        # Check author
        if query_lower in self.author.lower():
            return True

        return False

    def get_search_score(self, query: str) -> float:
        """Calculate search relevance score.

        Higher scores indicate better matches.

        Args:
            query: Search query string.

        Returns:
            Relevance score between 0 and 1.
        """
        query_lower = query.lower()
        scores = []

        # Exact name match (highest priority)
        if self.name.lower() == query_lower:
            scores.append(1.0)
        elif self.name.lower().startswith(query_lower):
            scores.append(0.9)
        elif query_lower in self.name.lower():
            scores.append(0.8)

        # Tag matches (high priority)
        for tag in self.tags:
            if tag.lower() == query_lower:
                scores.append(0.85)
            elif query_lower in tag.lower():
                scores.append(0.7)

        # Keyword matches
        for keyword in self.keywords:
            if keyword.lower() == query_lower:
                scores.append(0.8)
            elif query_lower in keyword.lower():
                scores.append(0.6)

        # Description match
        if query_lower in self.description.lower():
            scores.append(0.5)

        # Author match
        if query_lower in self.author.lower():
            scores.append(0.3)

        return max(scores) if scores else 0.0


class RegistryIndex:
    """Manages the registry index with caching and validation."""

    SCHEMA_VERSION = "1.0.0"

    def __init__(self, index_path: Optional[Path] = None):
        """Initialize the registry index.

        Args:
            index_path: Path to local index file. If None, uses default location.
        """
        self.index_path = index_path or self._get_default_index_path()
        self._skills: Dict[str, List[RegistrySkill]] = {}
        self._all_skills: List[RegistrySkill] = []
        self._schema_version: str = ""
        self._metadata: dict = {}
        self._loaded = False

    @staticmethod
    def _get_default_index_path() -> Path:
        """Get the default index path."""
        # Look for index in registry directory relative to package
        # The registry is at <repo>/kurultai/cli/registry/
        # __file__ is at <repo>/kurultai/cli/src/kurultai/registry.py
        package_dir = Path(__file__).parent.parent.parent
        registry_dir = package_dir / "registry"
        return registry_dir / "skills.json"

    def load(self, force: bool = False) -> None:
        """Load the registry index.

        Args:
            force: Force reload even if already loaded.
        """
        if self._loaded and not force:
            return

        if not self.index_path.exists():
            raise RegistryError(f"Registry index not found: {self.index_path}")

        try:
            with open(self.index_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise RegistryError(f"Invalid JSON in registry index: {e}")
        except Exception as e:
            raise RegistryError(f"Failed to load registry index: {e}")

        self._validate_schema(data)

        self._schema_version = data.get("schema_version", "unknown")
        self._metadata = data.get("metadata", {})

        # Parse skills
        self._all_skills = []
        self._skills = {}

        for skill_data in data.get("skills", []):
            try:
                skill = RegistrySkill.from_dict(skill_data)
                self._all_skills.append(skill)

                # Index by name for version lookup
                if skill.name not in self._skills:
                    self._skills[skill.name] = []
                self._skills[skill.name].append(skill)
            except Exception as e:
                # Skip invalid skills but log the error
                print(f"Warning: Failed to parse skill: {e}")
                continue

        # Sort versions for each skill (newest first)
        for name in self._skills:
            self._skills[name].sort(
                key=lambda s: self._version_key(s.version), reverse=True
            )

        self._loaded = True

    def _validate_schema(self, data: dict) -> None:
        """Validate the index schema.

        Args:
            data: Parsed JSON data.

        Raises:
            RegistryError: If schema is invalid.
        """
        if "schema_version" not in data:
            raise RegistryError("Registry index missing schema_version")

        if "skills" not in data:
            raise RegistryError("Registry index missing skills array")

        if not isinstance(data["skills"], list):
            raise RegistryError("Registry index skills must be an array")

        # Check schema version compatibility
        version = data["schema_version"]
        if not version.startswith("1."):
            raise RegistryError(f"Unsupported schema version: {version}")

    @staticmethod
    def _version_key(version: str) -> Tuple[int, ...]:
        """Convert version string to sortable tuple.

        Args:
            version: Version string (e.g., "1.2.3").

        Returns:
            Tuple of integers for sorting.
        """
        try:
            # Remove leading 'v' if present
            version = version.lstrip("v")
            parts = version.split(".")
            return tuple(int(p) for p in parts[:3])
        except (ValueError, AttributeError):
            return (0, 0, 0)

    def get_skill(self, name: str, version: Optional[str] = None) -> Optional[RegistrySkill]:
        """Get a specific skill from the registry.

        Args:
            name: Skill name.
            version: Specific version or None for latest.

        Returns:
            RegistrySkill if found, None otherwise.
        """
        self.load()

        if name not in self._skills:
            return None

        versions = self._skills[name]

        if version is None:
            return versions[0] if versions else None

        # Find matching version
        for skill in versions:
            if skill.version == version:
                return skill

        return None

    def get_latest_version(self, name: str) -> Optional[str]:
        """Get the latest version of a skill.

        Args:
            name: Skill name.

        Returns:
            Latest version string or None if not found.
        """
        self.load()

        if name not in self._skills or not self._skills[name]:
            return None

        return self._skills[name][0].version

    def list_skills(
        self,
        skill_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        author: Optional[str] = None,
    ) -> List[RegistrySkill]:
        """List skills with optional filtering.

        Args:
            skill_type: Filter by skill type (engine/skill/workflow).
            tags: Filter by tags (skills must have all specified tags).
            author: Filter by author.

        Returns:
            List of matching skills.
        """
        self.load()

        results = self._all_skills.copy()

        # Apply type filter
        if skill_type:
            results = [s for s in results if s.type == skill_type]

        # Apply tag filters
        if tags:
            tag_set = set(t.lower() for t in tags)
            results = [
                s for s in results if tag_set.issubset(set(t.lower() for t in s.tags))
            ]

        # Apply author filter
        if author:
            author_lower = author.lower()
            results = [s for s in results if author_lower in s.author.lower()]

        return results

    def search(self, query: str) -> List[Tuple[RegistrySkill, float]]:
        """Search skills by query.

        Args:
            query: Search query string.

        Returns:
            List of (skill, score) tuples sorted by relevance.
        """
        self.load()

        results = []
        for skill in self._all_skills:
            score = skill.get_search_score(query)
            if score > 0:
                results.append((skill, score))

        # Sort by score (descending)
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def get_all_skills(self) -> List[RegistrySkill]:
        """Get all skills in the registry.

        Returns:
            List of all skills.
        """
        self.load()
        return self._all_skills.copy()

    def get_schema_version(self) -> str:
        """Get the registry schema version.

        Returns:
            Schema version string.
        """
        self.load()
        return self._schema_version

    def get_metadata(self) -> dict:
        """Get registry metadata.

        Returns:
            Metadata dictionary.
        """
        self.load()
        return self._metadata.copy()


class RegistryClient:
    """Client for interacting with the Kurultai skill registry."""

    def __init__(
        self,
        index_path: Optional[Path] = None,
        registry_url: Optional[str] = None,
        cache_dir: Optional[Path] = None,
    ):
        """Initialize the registry client.

        Args:
            index_path: Path to local registry index.
            registry_url: URL of remote registry.
            cache_dir: Directory for caching registry data.
        """
        self.index = RegistryIndex(index_path)
        self.registry_url = registry_url or get_config().registry_url
        self.cache_dir = cache_dir or Path.home() / ".kurultai" / "registry_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache_file = self.cache_dir / "skills.json"
        self._cache_ttl = 3600  # 1 hour cache TTL

    def search(
        self,
        query: str,
        filters: Optional[dict] = None,
    ) -> List[RegistrySkill]:
        """Search for skills in the registry.

        Args:
            query: Search query string.
            filters: Optional filters:
                - type: Skill type filter
                - tags: List of required tags
                - author: Author filter

        Returns:
            List of matching skills sorted by relevance.
        """
        filters = filters or {}

        # Get search results with scores
        results = self.index.search(query)

        # Apply additional filters
        filtered_results = []
        for skill, score in results:
            # Type filter
            if "type" in filters and skill.type != filters["type"]:
                continue

            # Tag filter
            if "tags" in filters:
                required_tags = set(t.lower() for t in filters["tags"])
                skill_tags = set(t.lower() for t in skill.tags)
                if not required_tags.issubset(skill_tags):
                    continue

            # Author filter
            if "author" in filters:
                if filters["author"].lower() not in skill.author.lower():
                    continue

            filtered_results.append((skill, score))

        # Return just the skills (scores used for sorting)
        return [skill for skill, _ in filtered_results]

    def list_skills(
        self,
        skill_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        author: Optional[str] = None,
    ) -> List[RegistrySkill]:
        """List all skills with optional filtering.

        Args:
            skill_type: Filter by skill type (engine/skill/workflow).
            tags: Filter by tags.
            author: Filter by author.

        Returns:
            List of matching skills.
        """
        return self.index.list_skills(
            skill_type=skill_type,
            tags=tags,
            author=author,
        )

    def get_skill(self, name: str, version: Optional[str] = None) -> Optional[RegistrySkill]:
        """Get detailed information for a skill.

        Args:
            name: Skill name.
            version: Specific version or None for latest.

        Returns:
            RegistrySkill if found, None otherwise.
        """
        return self.index.get_skill(name, version)

    def get_latest_version(self, name: str) -> Optional[str]:
        """Get the latest version of a skill.

        Args:
            name: Skill name.

        Returns:
            Latest version string or None if not found.
        """
        return self.index.get_latest_version(name)

    def check_for_updates(
        self,
        installed_skills: List[dict],
    ) -> List[dict]:
        """Check for available updates for installed skills.

        Args:
            installed_skills: List of installed skill dicts with 'name' and 'version'.

        Returns:
            List of available updates with 'name', 'current_version', 'latest_version'.
        """
        updates = []

        for installed in installed_skills:
            name = installed.get("name")
            current_version = installed.get("version")

            if not name or not current_version:
                continue

            latest = self.get_latest_version(name)
            if latest and latest != current_version:
                # Simple version comparison (could use semver library)
                if self._is_newer_version(latest, current_version):
                    updates.append({
                        "name": name,
                        "current_version": current_version,
                        "latest_version": latest,
                    })

        return updates

    @staticmethod
    def _is_newer_version(version1: str, version2: str) -> bool:
        """Check if version1 is newer than version2.

        Args:
            version1: First version string.
            version2: Second version string.

        Returns:
            True if version1 is newer.
        """
        def parse_version(v: str) -> Tuple[int, ...]:
            v = v.lstrip("v")
            try:
                return tuple(int(x) for x in v.split(".")[:3])
            except (ValueError, AttributeError):
                return (0, 0, 0)

        return parse_version(version1) > parse_version(version2)

    def fetch_remote_index(self) -> bool:
        """Fetch the latest index from remote registry.

        Returns:
            True if successful, False otherwise.
        """
        try:
            index_url = urljoin(self.registry_url, "skills.json")
            response = requests.get(index_url, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Validate before saving
            self.index._validate_schema(data)

            # Save to cache
            with open(self._cache_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            # Reload index from cache
            self.index.index_path = self._cache_file
            self.index.load(force=True)

            return True
        except requests.RequestException:
            return False
        except Exception:
            return False

    def get_registry_info(self) -> dict:
        """Get information about the registry.

        Returns:
            Dictionary with registry metadata.
        """
        return {
            "schema_version": self.index.get_schema_version(),
            "registry_url": self.registry_url,
            "total_skills": len(self.index.get_all_skills()),
            "metadata": self.index.get_metadata(),
            "cache_file": str(self._cache_file),
            "cache_exists": self._cache_file.exists(),
        }

    def fuzzy_search(
        self,
        query: str,
        max_results: int = 10,
        min_score: float = 0.1,
    ) -> List[Tuple[RegistrySkill, float]]:
        """Perform fuzzy search on skills.

        Uses a combination of exact matching, prefix matching, and
        substring matching with relevance scoring.

        Args:
            query: Search query string.
            max_results: Maximum number of results to return.
            min_score: Minimum relevance score threshold.

        Returns:
            List of (skill, score) tuples sorted by relevance.
        """
        results = self.index.search(query)

        # Filter by minimum score
        results = [(s, score) for s, score in results if score >= min_score]

        # Limit results
        return results[:max_results]

    def search_by_pattern(
        self,
        pattern: str,
        field: str = "name",
    ) -> List[RegistrySkill]:
        """Search skills using glob pattern matching.

        Args:
            pattern: Glob pattern (e.g., "horde-*", "*review*").
            field: Field to match against (name, description, author).

        Returns:
            List of matching skills.
        """
        all_skills = self.index.get_all_skills()
        results = []

        for skill in all_skills:
            if field == "name":
                value = skill.name
            elif field == "description":
                value = skill.description
            elif field == "author":
                value = skill.author
            else:
                continue

            if fnmatch.fnmatch(value.lower(), pattern.lower()):
                results.append(skill)

        return results

    def get_dependencies(
        self,
        name: str,
        version: Optional[str] = None,
        recursive: bool = False,
    ) -> List[SkillDependency]:
        """Get dependencies for a skill.

        Args:
            name: Skill name.
            version: Specific version or None for latest.
            recursive: Whether to fetch transitive dependencies.

        Returns:
            List of dependencies.
        """
        skill = self.get_skill(name, version)
        if not skill:
            return []

        deps = skill.dependencies.copy()

        if recursive:
            seen = {name}
            to_process = [(d.name, d.version_constraint) for d in deps]

            while to_process:
                dep_name, dep_version = to_process.pop(0)
                if dep_name in seen:
                    continue
                seen.add(dep_name)

                dep_skill = self.get_skill(dep_name)
                if dep_skill:
                    for d in dep_skill.dependencies:
                        deps.append(d)
                        to_process.append((d.name, d.version_constraint))

        return deps


# Singleton instance for reuse
_registry_client: Optional[RegistryClient] = None


def get_registry_client() -> RegistryClient:
    """Get the global registry client instance.

    Returns:
        RegistryClient instance.
    """
    global _registry_client
    if _registry_client is None:
        _registry_client = RegistryClient()
    return _registry_client
