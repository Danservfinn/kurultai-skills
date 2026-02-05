"""Dependency resolution module for Kurultai CLI.

This module provides comprehensive dependency resolution capabilities including:
- Dependency graph construction and topological sorting
- Semver version range support (^, ~, >=, <=, >, <, =)
- Circular dependency detection
- Version conflict detection
- Lock file generation and management
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from kurultai.config import KURULTAI_HOME
from kurultai.exceptions import (
    CircularDependencyError,
    DependencyConflictError,
    LockFileError,
    ResolutionError,
    SkillNotFoundError,
)
from kurultai.models.skill import Dependency, SkillManifest, satisfies_constraint


class DependencySource(str, Enum):
    """Source type for resolved dependencies."""

    REGISTRY = "registry"
    GIT = "git"
    LOCAL = "local"


@dataclass(frozen=True)
class ResolvedDependency:
    """Represents a fully resolved dependency.

    Attributes:
        name: Skill name
        version: Resolved exact version
        source: Source type (registry, git, local)
        resolved_url: URL to fetch the skill from
        checksum: Optional checksum for verification
        dependencies: List of dependency names this skill depends on
    """

    name: str
    version: str
    source: DependencySource
    resolved_url: str
    checksum: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "version": self.version,
            "source": self.source.value,
            "resolved_url": self.resolved_url,
            "checksum": self.checksum,
            "dependencies": self.dependencies,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ResolvedDependency":
        """Create from dictionary."""
        return cls(
            name=data["name"],
            version=data["version"],
            source=DependencySource(data["source"]),
            resolved_url=data["resolved_url"],
            checksum=data.get("checksum"),
            dependencies=data.get("dependencies", []),
        )

    def __hash__(self) -> int:
        """Make hashable for use in sets."""
        return hash((self.name, self.version, self.source))


@dataclass
class DependencyNode:
    """Node in the dependency graph.

    Attributes:
        name: Skill name
        version_constraint: Original version constraint
        resolved_version: Resolved exact version
        parent: Parent node that required this dependency
        children: Child dependencies
    """

    name: str
    version_constraint: str
    resolved_version: Optional[str] = None
    parent: Optional["DependencyNode"] = None
    children: List["DependencyNode"] = field(default_factory=list)

    @property
    def path(self) -> List[str]:
        """Get the dependency path from root to this node."""
        if self.parent is None:
            return [self.name]
        return self.parent.path + [self.name]


class DependencyGraph:
    """Dependency graph for building and analyzing dependency trees.

    This class manages the dependency tree structure, performs topological
    sorting for installation order, and detects version conflicts.
    """

    def __init__(self) -> None:
        """Initialize an empty dependency graph."""
        self.nodes: Dict[str, DependencyNode] = {}
        self.edges: Dict[str, Set[str]] = defaultdict(set)
        self._conflicts: Dict[str, List[Tuple[str, List[str]]]] = defaultdict(list)
        self._resolved: Dict[str, ResolvedDependency] = {}

    def add_node(
        self,
        name: str,
        version_constraint: str,
        resolved_version: Optional[str] = None,
        parent: Optional[DependencyNode] = None,
    ) -> DependencyNode:
        """Add a node to the dependency graph.

        Args:
            name: Skill name
            version_constraint: Version constraint
            resolved_version: Resolved exact version
            parent: Parent node that required this dependency

        Returns:
            The created or existing node
        """
        # Check for version conflicts
        if name in self.nodes:
            existing = self.nodes[name]
            if existing.version_constraint != version_constraint:
                self._conflicts[name].append((version_constraint, parent.path if parent else []))
        else:
            node = DependencyNode(
                name=name,
                version_constraint=version_constraint,
                resolved_version=resolved_version,
                parent=parent,
            )
            self.nodes[name] = node

            if parent:
                self.edges[parent.name].add(name)

            return node

        return self.nodes[name]

    def add_edge(self, from_name: str, to_name: str) -> None:
        """Add an edge between two nodes.

        Args:
            from_name: Source node name
            to_name: Target node name
        """
        self.edges[from_name].add(to_name)

    def set_resolved(self, name: str, resolved: ResolvedDependency) -> None:
        """Set the resolved dependency for a node.

        Args:
            name: Skill name
            resolved: Resolved dependency information
        """
        self._resolved[name] = resolved
        if name in self.nodes:
            self.nodes[name].resolved_version = resolved.version

    def get_resolved(self, name: str) -> Optional[ResolvedDependency]:
        """Get the resolved dependency for a node.

        Args:
            name: Skill name

        Returns:
            Resolved dependency or None
        """
        return self._resolved.get(name)

    def has_conflict(self, name: str) -> bool:
        """Check if a skill has version conflicts.

        Args:
            name: Skill name

        Returns:
            True if there are conflicts, False otherwise
        """
        return name in self._conflicts

    def get_conflicts(self) -> Dict[str, List[Tuple[str, List[str]]]]:
        """Get all version conflicts.

        Returns:
            Dictionary mapping skill names to list of conflicting
            version constraints and their resolution paths
        """
        return dict(self._conflicts)

    def detect_cycles(self) -> Optional[List[str]]:
        """Detect circular dependencies using DFS.

        Returns:
            List of skill names forming a cycle, or None if no cycles
        """
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {name: WHITE for name in self.nodes}
        path: List[str] = []

        def dfs(node_name: str) -> Optional[List[str]]:
            color[node_name] = GRAY
            path.append(node_name)

            for neighbor in self.edges.get(node_name, set()):
                if color[neighbor] == GRAY:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    return path[cycle_start:] + [neighbor]
                elif color[neighbor] == WHITE:
                    result = dfs(neighbor)
                    if result:
                        return result

            path.pop()
            color[node_name] = BLACK
            return None

        for node_name in self.nodes:
            if color[node_name] == WHITE:
                cycle = dfs(node_name)
                if cycle:
                    return cycle

        return None

    def topological_sort(self) -> List[str]:
        """Perform topological sort for installation order.

        Returns:
            List of skill names in installation order (dependencies first)

        Raises:
            CircularDependencyError: If a cycle is detected
        """
        # Check for cycles first
        cycle = self.detect_cycles()
        if cycle:
            raise CircularDependencyError(
                "Circular dependency detected",
                cycle=cycle,
            )

        # Kahn's algorithm for topological sort
        in_degree = {name: 0 for name in self.nodes}
        for neighbors in self.edges.values():
            for neighbor in neighbors:
                if neighbor in in_degree:
                    in_degree[neighbor] += 1

        # Start with nodes that have no dependencies
        queue = [name for name, degree in in_degree.items() if degree == 0]
        result: List[str] = []

        while queue:
            # Sort for deterministic output
            queue.sort()
            node = queue.pop(0)
            result.append(node)

            for neighbor in sorted(self.edges.get(node, set())):
                if neighbor in in_degree:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)

        return result

    def get_installation_order(self) -> List[ResolvedDependency]:
        """Get the installation order with resolved dependencies.

        Returns:
            List of ResolvedDependency in installation order
        """
        order = self.topological_sort()
        return [self._resolved[name] for name in order if name in self._resolved]

    def to_dict(self) -> Dict[str, Any]:
        """Convert graph to dictionary representation."""
        return {
            "nodes": {
                name: {
                    "version_constraint": node.version_constraint,
                    "resolved_version": node.resolved_version,
                }
                for name, node in self.nodes.items()
            },
            "edges": {name: list(deps) for name, deps in self.edges.items()},
            "resolved": {
                name: dep.to_dict() for name, dep in self._resolved.items()
            },
        }


class DependencyResolver:
    """Resolves dependencies from skill manifests.

    This class handles:
    - Resolving direct and transitive dependencies
    - Semver version range matching
    - Circular dependency detection
    - Version conflict detection
    - Lock file generation
    """

    def __init__(
        self,
        registry_url: Optional[str] = None,
        cache_dir: Optional[Path] = None,
    ) -> None:
        """Initialize the dependency resolver.

        Args:
            registry_url: URL of the skill registry
            cache_dir: Directory for caching resolution results
        """
        self.registry_url = registry_url
        self.cache_dir = cache_dir or KURULTAI_HOME / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._graph = DependencyGraph()
        self._registry_cache: Dict[str, List[Dict[str, Any]]] = {}

    def resolve(
        self,
        manifest: SkillManifest,
        include_optional: bool = False,
    ) -> DependencyGraph:
        """Resolve all dependencies for a skill manifest.

        Args:
            manifest: The skill manifest to resolve dependencies for
            include_optional: Whether to include optional dependencies

        Returns:
            DependencyGraph with all resolved dependencies

        Raises:
            CircularDependencyError: If a circular dependency is detected
            DependencyConflictError: If version conflicts cannot be resolved
            ResolutionError: If a dependency cannot be resolved
        """
        self._graph = DependencyGraph()

        # Get dependencies to resolve
        dependencies = manifest.parsed_dependencies
        if not include_optional:
            dependencies = manifest.get_required_dependencies()

        # Resolve each dependency recursively
        for dep in dependencies:
            self._resolve_dependency(
                dep=dep,
                parent=None,
                resolution_path=[manifest.name],
            )

        # Check for conflicts
        conflicts = self._graph.get_conflicts()
        if conflicts:
            for skill_name, conflict_list in conflicts.items():
                versions = [c[0] for c in conflict_list]
                paths = [c[1] for c in conflict_list]
                raise DependencyConflictError(
                    f"Version conflict for skill '{skill_name}'",
                    skill_name=skill_name,
                    required_versions=versions,
                    resolution_path=paths[0] if paths else None,
                )

        # Check for cycles
        cycle = self._graph.detect_cycles()
        if cycle:
            raise CircularDependencyError(
                "Circular dependency detected",
                cycle=cycle,
            )

        return self._graph

    def _resolve_dependency(
        self,
        dep: Dependency,
        parent: Optional[DependencyNode],
        resolution_path: List[str],
    ) -> ResolvedDependency:
        """Resolve a single dependency recursively.

        Args:
            dep: The dependency to resolve
            parent: Parent node that required this dependency
            resolution_path: Current resolution path for error reporting

        Returns:
            ResolvedDependency with full resolution information

        Raises:
            ResolutionError: If the dependency cannot be resolved
            SkillNotFoundError: If the skill is not found in the registry
        """
        # Add to graph
        node = self._graph.add_node(
            name=dep.name,
            version_constraint=dep.version_constraint,
            parent=parent,
        )

        # Check if already resolved
        existing = self._graph.get_resolved(dep.name)
        if existing:
            # Verify version compatibility
            if not satisfies_constraint(existing.version, dep.version_constraint):
                raise DependencyConflictError(
                    f"Version conflict for '{dep.name}'",
                    skill_name=dep.name,
                    required_versions=[dep.version_constraint, f"={existing.version}"],
                    resolution_path=resolution_path,
                )
            return existing

        # Resolve from registry
        resolved = self.resolve_from_registry(dep.name, dep.version_constraint)

        # Add to graph
        self._graph.set_resolved(dep.name, resolved)
        node.resolved_version = resolved.version

        # Resolve transitive dependencies
        for transitive_dep in self._get_transitive_dependencies(resolved):
            self._resolve_dependency(
                dep=transitive_dep,
                parent=node,
                resolution_path=resolution_path + [dep.name],
            )

        return resolved

    def _get_transitive_dependencies(
        self,
        resolved: ResolvedDependency,
    ) -> List[Dependency]:
        """Get transitive dependencies for a resolved skill.

        Args:
            resolved: The resolved dependency

        Returns:
            List of transitive dependencies
        """
        # In a real implementation, this would fetch the skill manifest
        # from the registry or cache and parse its dependencies
        # For now, return empty list - this would be populated from manifest
        return []

    def resolve_from_registry(
        self,
        skill_name: str,
        version_constraint: str,
    ) -> ResolvedDependency:
        """Resolve a skill from the registry.

        Args:
            skill_name: Name of the skill
            version_constraint: Version constraint to satisfy

        Returns:
            ResolvedDependency with exact version and URL

        Raises:
            SkillNotFoundError: If skill not found in registry
            ResolutionError: If no version satisfies the constraint
        """
        # Fetch available versions from registry
        versions = self._fetch_registry_versions(skill_name)

        if not versions:
            raise SkillNotFoundError(
                f"Skill '{skill_name}' not found in registry",
                skill_name=skill_name,
                version_constraint=version_constraint,
                registry_url=self.registry_url,
            )

        # Find best matching version
        matching_versions = [
            v for v in versions
            if satisfies_constraint(v["version"], version_constraint)
        ]

        if not matching_versions:
            available = [v["version"] for v in versions]
            raise ResolutionError(
                f"No version satisfies constraint '{version_constraint}'",
                skill_name=skill_name,
                version_constraint=version_constraint,
                details={"available_versions": available},
            )

        # Sort by version and pick the highest
        matching_versions.sort(
            key=lambda v: self._version_sort_key(v["version"]),
            reverse=True,
        )
        best_match = matching_versions[0]

        return ResolvedDependency(
            name=skill_name,
            version=best_match["version"],
            source=DependencySource.REGISTRY,
            resolved_url=best_match.get("url", f"{self.registry_url}/skills/{skill_name}"),
            checksum=best_match.get("checksum"),
        )

    def resolve_from_git(
        self,
        repo_url: str,
        ref: Optional[str] = None,
    ) -> ResolvedDependency:
        """Resolve a skill from a Git repository.

        Args:
            repo_url: Git repository URL
            ref: Git reference (branch, tag, or commit)

        Returns:
            ResolvedDependency with version information
        """
        # Extract skill name from URL
        name = self._extract_name_from_git_url(repo_url)

        # Determine version from ref or use a placeholder
        version = ref or "0.0.0-git"

        # Calculate checksum from URL and ref
        checksum_input = f"{repo_url}@{ref or 'HEAD'}"
        checksum = hashlib.sha256(checksum_input.encode()).hexdigest()[:16]

        return ResolvedDependency(
            name=name,
            version=version,
            source=DependencySource.GIT,
            resolved_url=repo_url,
            checksum=checksum,
        )

    def _fetch_registry_versions(self, skill_name: str) -> List[Dict[str, Any]]:
        """Fetch available versions from the registry.

        Args:
            skill_name: Name of the skill

        Returns:
            List of version information dictionaries
        """
        # Check cache first
        if skill_name in self._registry_cache:
            return self._registry_cache[skill_name]

        # In a real implementation, this would make an HTTP request
        # to the registry API. For now, return empty list.
        # This should be overridden or implemented with actual registry client
        return []

    def _extract_name_from_git_url(self, url: str) -> str:
        """Extract skill name from a Git URL.

        Args:
            url: Git repository URL

        Returns:
            Extracted skill name
        """
        # Remove .git suffix if present
        url = url.rstrip("/").removesuffix(".git")

        # Extract last path component
        if "/" in url:
            return url.split("/")[-1]

        return url

    def _version_sort_key(self, version: str) -> Tuple[int, int, int, str]:
        """Create a sort key for version strings.

        Args:
            version: Semantic version string

        Returns:
            Tuple for sorting (major, minor, patch, prerelease)
        """
        # Parse version components
        match = re.match(
            r"^(\d+)\.(\d+)\.(\d+)(?:-(.+))?$",
            version,
        )
        if match:
            major, minor, patch, prerelease = match.groups()
            # Prerelease versions sort before release versions
            prerelease_key = prerelease or "~"  # ~ sorts after any string
            return (int(major), int(minor), int(patch), prerelease_key)

        return (0, 0, 0, version)

    def write_lock_file(
        self,
        resolved_deps: List[ResolvedDependency],
        path: Optional[Path] = None,
    ) -> Path:
        """Write a lock file with resolved dependencies.

        Args:
            resolved_deps: List of resolved dependencies
            path: Path to write lock file (default: kurultai.lock in current directory)

        Returns:
            Path to the written lock file

        Raises:
            LockFileError: If writing fails
        """
        if path is None:
            path = Path("kurultai.lock")

        try:
            lock_data = {
                "version": "1.0.0",
                "generated_at": self._get_timestamp(),
                "dependencies": [dep.to_dict() for dep in resolved_deps],
            }

            with open(path, "w") as f:
                json.dump(lock_data, f, indent=2)

            return path
        except Exception as e:
            raise LockFileError(
                f"Failed to write lock file: {e}",
                lock_file_path=str(path),
            ) from e

    def read_lock_file(self, path: Optional[Path] = None) -> List[ResolvedDependency]:
        """Read a lock file and return resolved dependencies.

        Args:
            path: Path to lock file (default: kurultai.lock in current directory)

        Returns:
            List of ResolvedDependency objects

        Raises:
            LockFileError: If reading or parsing fails
        """
        if path is None:
            path = Path("kurultai.lock")

        if not path.exists():
            raise LockFileError(
                f"Lock file not found: {path}",
                lock_file_path=str(path),
            )

        try:
            with open(path, "r") as f:
                lock_data = json.load(f)

            # Validate version
            version = lock_data.get("version", "1.0.0")
            if version != "1.0.0":
                raise LockFileError(
                    f"Unsupported lock file version: {version}",
                    lock_file_path=str(path),
                )

            return [
                ResolvedDependency.from_dict(dep)
                for dep in lock_data.get("dependencies", [])
            ]
        except json.JSONDecodeError as e:
            raise LockFileError(
                f"Invalid JSON in lock file: {e}",
                lock_file_path=str(path),
            ) from e
        except Exception as e:
            raise LockFileError(
                f"Failed to read lock file: {e}",
                lock_file_path=str(path),
            ) from e

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()

    def check_lock_file_consistency(
        self,
        manifest: SkillManifest,
        lock_file_path: Optional[Path] = None,
    ) -> bool:
        """Check if lock file is consistent with manifest.

        Args:
            manifest: Skill manifest to check against
            lock_file_path: Path to lock file

        Returns:
            True if consistent, False otherwise
        """
        try:
            locked_deps = self.read_lock_file(lock_file_path)
            locked_names = {dep.name for dep in locked_deps}

            # Check that all manifest dependencies are in lock file
            manifest_deps = set(manifest.dependencies.keys())
            if not manifest_deps.issubset(locked_names):
                return False

            # Check that versions still satisfy constraints
            for dep_name, constraint in manifest.dependencies.items():
                locked_dep = next(
                    (d for d in locked_deps if d.name == dep_name),
                    None,
                )
                if locked_dep is None:
                    return False

                if not satisfies_constraint(locked_dep.version, constraint):
                    return False

            return True
        except LockFileError:
            return False


def resolve_dependencies(
    manifest: SkillManifest,
    registry_url: Optional[str] = None,
    include_optional: bool = False,
) -> DependencyGraph:
    """Convenience function to resolve dependencies.

    Args:
        manifest: Skill manifest to resolve
        registry_url: Optional registry URL
        include_optional: Whether to include optional dependencies

    Returns:
        DependencyGraph with resolved dependencies
    """
    resolver = DependencyResolver(registry_url=registry_url)
    return resolver.resolve(manifest, include_optional=include_optional)


def generate_lock_file(
    manifest: SkillManifest,
    path: Optional[Path] = None,
    registry_url: Optional[str] = None,
) -> Path:
    """Generate a lock file for a skill manifest.

    Args:
        manifest: Skill manifest to generate lock file for
        path: Path to write lock file
        registry_url: Optional registry URL

    Returns:
        Path to the written lock file
    """
    resolver = DependencyResolver(registry_url=registry_url)
    graph = resolver.resolve(manifest)
    resolved = graph.get_installation_order()
    return resolver.write_lock_file(resolved, path)
