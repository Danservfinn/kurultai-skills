"""Tests for dependency resolution.

This module tests:
- Dependency resolution
- Circular dependency detection
- Version constraint parsing (^, ~, >=, etc.)
- Lock file creation/reading
- Conflict detection
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest

from kurultai.dependencies import (
    DependencyGraph,
    DependencyNode,
    DependencyResolver,
    DependencySource,
    ResolvedDependency,
    generate_lock_file,
    resolve_dependencies,
)
from kurultai.exceptions import (
    CircularDependencyError,
    DependencyConflictError,
    LockFileError,
    ResolutionError,
    SkillNotFoundError,
)
from kurultai.models.skill import Dependency, SkillManifest, SkillType, satisfies_constraint


class TestDependencyGraph:
    """Tests for DependencyGraph class."""

    def test_empty_graph(self):
        """Test creating an empty dependency graph."""
        graph = DependencyGraph()
        assert graph.nodes == {}
        assert graph.detect_cycles() is None
        assert graph.topological_sort() == []

    def test_add_node(self):
        """Test adding nodes to the graph."""
        graph = DependencyGraph()
        node = graph.add_node("skill-a", "^1.0.0")

        assert "skill-a" in graph.nodes
        assert node.name == "skill-a"
        assert node.version_constraint == "^1.0.0"

    def test_add_edge(self):
        """Test adding edges between nodes."""
        graph = DependencyGraph()
        graph.add_node("skill-a", "^1.0.0")
        graph.add_node("skill-b", "^2.0.0")
        graph.add_edge("skill-a", "skill-b")

        assert "skill-b" in graph.edges["skill-a"]

    def test_set_resolved(self):
        """Test setting resolved dependency."""
        graph = DependencyGraph()
        graph.add_node("skill-a", "^1.0.0")
        resolved = ResolvedDependency(
            name="skill-a",
            version="1.2.0",
            source=DependencySource.REGISTRY,
            resolved_url="url",
        )

        graph.set_resolved("skill-a", resolved)

        assert graph.get_resolved("skill-a") == resolved
        assert graph.nodes["skill-a"].resolved_version == "1.2.0"

    def test_detect_no_cycles(self):
        """Test detecting no cycles in a DAG."""
        graph = DependencyGraph()

        # a -> b -> c
        graph.add_node("skill-a", "^1.0.0")
        graph.add_node("skill-b", "^1.0.0")
        graph.add_node("skill-c", "^1.0.0")
        graph.add_edge("skill-a", "skill-b")
        graph.add_edge("skill-b", "skill-c")

        assert graph.detect_cycles() is None

    def test_detect_cycle(self):
        """Test detecting a cycle."""
        graph = DependencyGraph()

        # a -> b -> c -> a
        graph.add_node("skill-a", "^1.0.0")
        graph.add_node("skill-b", "^1.0.0")
        graph.add_node("skill-c", "^1.0.0")
        graph.add_edge("skill-a", "skill-b")
        graph.add_edge("skill-b", "skill-c")
        graph.add_edge("skill-c", "skill-a")

        cycle = graph.detect_cycles()
        assert cycle is not None
        assert "skill-a" in cycle
        assert "skill-b" in cycle
        assert "skill-c" in cycle

    def test_topological_sort_linear(self):
        """Test topological sort on linear dependency chain."""
        graph = DependencyGraph()

        # a -> b -> c (c depends on b, b depends on a)
        graph.add_node("skill-a", "^1.0.0")
        graph.add_node("skill-b", "^1.0.0")
        graph.add_node("skill-c", "^1.0.0")
        graph.add_edge("skill-a", "skill-b")
        graph.add_edge("skill-b", "skill-c")

        order = graph.topological_sort()

        # Dependencies should come first
        assert order.index("skill-a") < order.index("skill-b")
        assert order.index("skill-b") < order.index("skill-c")

    def test_topological_sort_diamond(self):
        """Test topological sort on diamond dependency pattern."""
        graph = DependencyGraph()

        #   a
        #  / \
        # b   c
        #  \ /
        #   d
        graph.add_node("skill-a", "^1.0.0")
        graph.add_node("skill-b", "^1.0.0")
        graph.add_node("skill-c", "^1.0.0")
        graph.add_node("skill-d", "^1.0.0")
        graph.add_edge("skill-a", "skill-b")
        graph.add_edge("skill-a", "skill-c")
        graph.add_edge("skill-b", "skill-d")
        graph.add_edge("skill-c", "skill-d")

        order = graph.topological_sort()

        # a should be first, d should be last
        assert order[0] == "skill-a"
        assert order[-1] == "skill-d"

    def test_topological_sort_raises_on_cycle(self):
        """Test that topological sort raises on cycle detection."""
        graph = DependencyGraph()

        graph.add_node("skill-a", "^1.0.0")
        graph.add_node("skill-b", "^1.0.0")
        graph.add_edge("skill-a", "skill-b")
        graph.add_edge("skill-b", "skill-a")

        with pytest.raises(CircularDependencyError) as exc_info:
            graph.topological_sort()

        assert "skill-a" in exc_info.value.cycle
        assert "skill-b" in exc_info.value.cycle

    def test_version_conflict_detection(self):
        """Test detecting version conflicts."""
        graph = DependencyGraph()

        # Add same skill with different constraints
        graph.add_node("skill-a", "^1.0.0")
        graph.add_node("skill-a", "^2.0.0")  # Conflict

        assert graph.has_conflict("skill-a")
        conflicts = graph.get_conflicts()
        assert "skill-a" in conflicts

    def test_get_installation_order(self):
        """Test getting installation order with resolved dependencies."""
        graph = DependencyGraph()

        graph.add_node("skill-a", "^1.0.0")
        graph.add_node("skill-b", "^1.0.0")
        graph.add_edge("skill-a", "skill-b")

        resolved_a = ResolvedDependency(
            name="skill-a",
            version="1.0.0",
            source=DependencySource.REGISTRY,
            resolved_url="url-a",
        )
        resolved_b = ResolvedDependency(
            name="skill-b",
            version="1.0.0",
            source=DependencySource.REGISTRY,
            resolved_url="url-b",
        )

        graph.set_resolved("skill-a", resolved_a)
        graph.set_resolved("skill-b", resolved_b)

        order = graph.get_installation_order()

        assert len(order) == 2
        assert order[0].name == "skill-a"
        assert order[1].name == "skill-b"


class TestDependencyResolver:
    """Tests for DependencyResolver class."""

    def test_create_resolver(self):
        """Test creating a dependency resolver."""
        resolver = DependencyResolver(registry_url="https://example.com")
        assert resolver.registry_url == "https://example.com"

    def test_resolve_from_git(self):
        """Test resolving a skill from git."""
        resolver = DependencyResolver()

        resolved = resolver.resolve_from_git(
            "https://github.com/user/my-skill.git",
            ref="v1.0.0",
        )

        assert resolved.name == "my-skill"
        assert resolved.version == "v1.0.0"
        assert resolved.source == DependencySource.GIT
        assert resolved.resolved_url == "https://github.com/user/my-skill.git"
        assert resolved.checksum is not None

    def test_resolve_from_git_no_ref(self):
        """Test resolving from git without ref."""
        resolver = DependencyResolver()

        resolved = resolver.resolve_from_git("https://github.com/user/skill.git")

        assert resolved.version == "0.0.0-git"

    def test_extract_name_from_git_url(self):
        """Test extracting skill name from git URL."""
        resolver = DependencyResolver()

        assert resolver._extract_name_from_git_url(
            "https://github.com/user/my-skill.git"
        ) == "my-skill"
        assert resolver._extract_name_from_git_url(
            "https://github.com/user/my-skill"
        ) == "my-skill"
        assert resolver._extract_name_from_git_url(
            "git@github.com:user/my-skill.git"
        ) == "my-skill"

    def test_version_sort_key(self):
        """Test version sorting."""
        resolver = DependencyResolver()

        # Test basic versions
        assert resolver._version_sort_key("1.0.0") == (1, 0, 0, "~")
        assert resolver._version_sort_key("2.1.3") == (2, 1, 3, "~")

        # Test prerelease versions
        key = resolver._version_sort_key("1.0.0-alpha")
        assert key[3] == "alpha"


class TestLockFileOperations:
    """Tests for lock file operations."""

    def test_write_and_read_lock_file(self, temp_dir: Path):
        """Test writing and reading lock file."""
        lock_path = temp_dir / "kurultai.lock"
        resolver = DependencyResolver()

        deps = [
            ResolvedDependency(
                name="skill-a",
                version="1.0.0",
                source=DependencySource.REGISTRY,
                resolved_url="url-a",
                checksum="abc123",
            ),
            ResolvedDependency(
                name="skill-b",
                version="2.0.0",
                source=DependencySource.GIT,
                resolved_url="https://github.com/user/skill-b.git",
            ),
        ]

        # Write lock file
        written_path = resolver.write_lock_file(deps, lock_path)
        assert written_path == lock_path
        assert lock_path.exists()

        # Read lock file
        read_deps = resolver.read_lock_file(lock_path)
        assert len(read_deps) == 2
        assert read_deps[0].name == "skill-a"
        assert read_deps[0].version == "1.0.0"
        assert read_deps[1].name == "skill-b"
        assert read_deps[1].source == DependencySource.GIT

    def test_read_lock_file_not_found(self):
        """Test reading non-existent lock file."""
        resolver = DependencyResolver()

        with pytest.raises(LockFileError) as exc_info:
            resolver.read_lock_file(Path("/nonexistent/lock.file"))

        assert "not found" in str(exc_info.value).lower()

    def test_read_lock_file_invalid_json(self, temp_dir: Path):
        """Test reading invalid JSON lock file."""
        lock_path = temp_dir / "kurultai.lock"
        lock_path.write_text("not valid json")

        resolver = DependencyResolver()

        with pytest.raises(LockFileError) as exc_info:
            resolver.read_lock_file(lock_path)

        assert "invalid json" in str(exc_info.value).lower()

    def test_lock_file_format(self, temp_dir: Path):
        """Test the lock file JSON format."""
        lock_path = temp_dir / "kurultai.lock"
        resolver = DependencyResolver()

        deps = [
            ResolvedDependency(
                name="skill-a",
                version="1.0.0",
                source=DependencySource.REGISTRY,
                resolved_url="https://registry.kurultai.ai/skills/skill-a",
                checksum="sha256:abc123",
                dependencies=["skill-b"],
            ),
        ]

        resolver.write_lock_file(deps, lock_path)

        # Read and verify JSON structure
        with open(lock_path) as f:
            data = json.load(f)

        assert "version" in data
        assert "generated_at" in data
        assert "dependencies" in data
        assert len(data["dependencies"]) == 1

        dep = data["dependencies"][0]
        assert dep["name"] == "skill-a"
        assert dep["version"] == "1.0.0"
        assert dep["source"] == "registry"
        assert dep["resolved_url"] == "https://registry.kurultai.ai/skills/skill-a"
        assert dep["checksum"] == "sha256:abc123"
        assert dep["dependencies"] == ["skill-b"]

    def test_check_lock_file_consistency_no_lock(self):
        """Test consistency check with no lock file."""
        resolver = DependencyResolver()

        manifest = SkillManifest(
            name="test-skill",
            version="1.0.0",
            description="A test skill for testing",
            author="test",
            type=SkillType.SKILL,
            dependencies={"dep1": "^1.0.0"},
        )

        assert not resolver.check_lock_file_consistency(manifest, Path("/nonexistent"))


class TestCircularDependencyDetection:
    """Tests for circular dependency detection."""

    def test_simple_cycle(self):
        """Test detecting a simple cycle."""
        graph = DependencyGraph()

        # a -> b -> a
        graph.add_node("skill-a", "^1.0.0")
        graph.add_node("skill-b", "^1.0.0")
        graph.add_edge("skill-a", "skill-b")
        graph.add_edge("skill-b", "skill-a")

        cycle = graph.detect_cycles()
        assert cycle is not None
        assert len(cycle) >= 2

    def test_self_dependency(self):
        """Test detecting self-dependency."""
        graph = DependencyGraph()

        graph.add_node("skill-a", "^1.0.0")
        graph.add_edge("skill-a", "skill-a")

        cycle = graph.detect_cycles()
        assert cycle is not None
        assert "skill-a" in cycle

    def test_complex_cycle(self):
        """Test detecting a complex cycle."""
        graph = DependencyGraph()

        # a -> b -> c -> d -> b
        graph.add_node("skill-a", "^1.0.0")
        graph.add_node("skill-b", "^1.0.0")
        graph.add_node("skill-c", "^1.0.0")
        graph.add_node("skill-d", "^1.0.0")
        graph.add_edge("skill-a", "skill-b")
        graph.add_edge("skill-b", "skill-c")
        graph.add_edge("skill-c", "skill-d")
        graph.add_edge("skill-d", "skill-b")

        cycle = graph.detect_cycles()
        assert cycle is not None
        assert "skill-b" in cycle
        assert "skill-c" in cycle
        assert "skill-d" in cycle

    def test_no_cycle_dag(self):
        """Test that DAG has no cycles."""
        graph = DependencyGraph()

        # a -> b -> c
        #  \-> d
        graph.add_node("skill-a", "^1.0.0")
        graph.add_node("skill-b", "^1.0.0")
        graph.add_node("skill-c", "^1.0.0")
        graph.add_node("skill-d", "^1.0.0")
        graph.add_edge("skill-a", "skill-b")
        graph.add_edge("skill-b", "skill-c")
        graph.add_edge("skill-a", "skill-d")

        cycle = graph.detect_cycles()
        assert cycle is None


class TestVersionConstraintParsing:
    """Tests for version constraint parsing."""

    def test_caret_constraint(self):
        """Test caret (^) constraint matching."""
        # ^1.0.0 allows 1.x.x but not 2.0.0
        assert satisfies_constraint("1.0.0", "^1.0.0")
        assert satisfies_constraint("1.2.0", "^1.0.0")
        assert satisfies_constraint("1.2.3", "^1.0.0")
        assert not satisfies_constraint("2.0.0", "^1.0.0")
        assert not satisfies_constraint("0.9.0", "^1.0.0")

        # ^0.1.0 allows 0.1.x but not 0.2.0
        assert satisfies_constraint("0.1.0", "^0.1.0")
        assert satisfies_constraint("0.1.5", "^0.1.0")
        assert not satisfies_constraint("0.2.0", "^0.1.0")

    def test_tilde_constraint(self):
        """Test tilde (~) constraint matching."""
        # ~1.0.0 allows 1.0.x but not 1.1.0
        assert satisfies_constraint("1.0.0", "~1.0.0")
        assert satisfies_constraint("1.0.5", "~1.0.0")
        assert not satisfies_constraint("1.1.0", "~1.0.0")

        # ~1.2.0 allows 1.2.x but not 1.3.0
        assert satisfies_constraint("1.2.0", "~1.2.0")
        assert satisfies_constraint("1.2.9", "~1.2.0")
        assert not satisfies_constraint("1.3.0", "~1.2.0")

    def test_greater_than_constraint(self):
        """Test greater than (>) constraint."""
        assert satisfies_constraint("2.0.0", ">1.0.0")
        assert satisfies_constraint("1.1.0", ">1.0.0")
        assert not satisfies_constraint("1.0.0", ">1.0.0")
        assert not satisfies_constraint("0.9.0", ">1.0.0")

    def test_greater_than_or_equal_constraint(self):
        """Test greater than or equal (>=) constraint."""
        assert satisfies_constraint("1.0.0", ">=1.0.0")
        assert satisfies_constraint("1.1.0", ">=1.0.0")
        assert satisfies_constraint("2.0.0", ">=1.0.0")
        assert not satisfies_constraint("0.9.0", ">=1.0.0")

    def test_less_than_constraint(self):
        """Test less than (<) constraint."""
        assert satisfies_constraint("0.9.0", "<1.0.0")
        assert satisfies_constraint("0.9.9", "<1.0.0")
        assert not satisfies_constraint("1.0.0", "<1.0.0")
        assert not satisfies_constraint("1.1.0", "<1.0.0")

    def test_less_than_or_equal_constraint(self):
        """Test less than or equal (<=) constraint."""
        assert satisfies_constraint("1.0.0", "<=1.0.0")
        assert satisfies_constraint("0.9.0", "<=1.0.0")
        assert not satisfies_constraint("1.1.0", "<=1.0.0")

    def test_exact_constraint(self):
        """Test exact (=) constraint."""
        assert satisfies_constraint("1.0.0", "=1.0.0")
        assert not satisfies_constraint("1.0.1", "=1.0.0")
        assert not satisfies_constraint("1.1.0", "=1.0.0")

    def test_exact_version_no_prefix(self):
        """Test exact version without prefix."""
        assert satisfies_constraint("1.0.0", "1.0.0")
        assert not satisfies_constraint("1.0.1", "1.0.0")


class TestConflictDetection:
    """Tests for version conflict detection."""

    def test_same_skill_different_constraints(self):
        """Test detecting same skill with different constraints."""
        graph = DependencyGraph()

        graph.add_node("skill-a", "^1.0.0", parent=None)
        graph.add_node("skill-a", "^2.0.0", parent=None)

        assert graph.has_conflict("skill-a")

    def test_no_conflict_same_constraint(self):
        """Test that same constraint is not a conflict."""
        graph = DependencyGraph()

        graph.add_node("skill-a", "^1.0.0", parent=None)
        graph.add_node("skill-a", "^1.0.0", parent=None)

        # Same constraint should not be a conflict
        assert not graph.has_conflict("skill-a")

    def test_get_conflicts(self):
        """Test getting all conflicts."""
        graph = DependencyGraph()

        graph.add_node("skill-a", "^1.0.0")
        graph.add_node("skill-a", "^2.0.0")
        graph.add_node("skill-b", "~1.0.0")
        graph.add_node("skill-b", "~2.0.0")

        conflicts = graph.get_conflicts()
        assert "skill-a" in conflicts
        assert "skill-b" in conflicts


class TestResolvedDependency:
    """Tests for ResolvedDependency dataclass."""

    def test_create_resolved_dependency(self):
        """Test creating a resolved dependency."""
        dep = ResolvedDependency(
            name="test-skill",
            version="1.0.0",
            source=DependencySource.REGISTRY,
            resolved_url="https://registry.kurultai.ai/v1/skills/test-skill",
            checksum="abc123",
            dependencies=["dep1", "dep2"],
        )

        assert dep.name == "test-skill"
        assert dep.version == "1.0.0"
        assert dep.source == DependencySource.REGISTRY
        assert dep.resolved_url == "https://registry.kurultai.ai/v1/skills/test-skill"
        assert dep.checksum == "abc123"
        assert dep.dependencies == ["dep1", "dep2"]

    def test_resolved_dependency_to_dict(self):
        """Test converting ResolvedDependency to dict."""
        dep = ResolvedDependency(
            name="test-skill",
            version="1.0.0",
            source=DependencySource.REGISTRY,
            resolved_url="https://example.com/skill",
        )

        data = dep.to_dict()

        assert data["name"] == "test-skill"
        assert data["version"] == "1.0.0"
        assert data["source"] == "registry"
        assert data["resolved_url"] == "https://example.com/skill"
        assert data["checksum"] is None
        assert data["dependencies"] == []

    def test_resolved_dependency_from_dict(self):
        """Test creating ResolvedDependency from dict."""
        data = {
            "name": "test-skill",
            "version": "2.0.0",
            "source": "git",
            "resolved_url": "https://github.com/user/skill.git",
            "checksum": "def456",
            "dependencies": ["other-skill"],
        }

        dep = ResolvedDependency.from_dict(data)

        assert dep.name == "test-skill"
        assert dep.version == "2.0.0"
        assert dep.source == DependencySource.GIT
        assert dep.resolved_url == "https://github.com/user/skill.git"
        assert dep.checksum == "def456"
        assert dep.dependencies == ["other-skill"]

    def test_resolved_dependency_hash(self):
        """Test that ResolvedDependency is hashable."""
        dep1 = ResolvedDependency(
            name="skill1",
            version="1.0.0",
            source=DependencySource.REGISTRY,
            resolved_url="url1",
        )
        dep2 = ResolvedDependency(
            name="skill1",
            version="1.0.0",
            source=DependencySource.REGISTRY,
            resolved_url="url1",
        )
        dep3 = ResolvedDependency(
            name="skill2",
            version="1.0.0",
            source=DependencySource.REGISTRY,
            resolved_url="url2",
        )

        # Same values should have same hash
        assert hash(dep1) == hash(dep2)
        # Different values should have different hash
        assert hash(dep1) != hash(dep3)

        # Can be used in set
        dep_set = {dep1, dep2, dep3}
        assert len(dep_set) == 2


class TestExceptions:
    """Tests for custom exceptions."""

    def test_circular_dependency_error(self):
        """Test CircularDependencyError formatting."""
        error = CircularDependencyError(
            message="Circular dependency detected",
            cycle=["a", "b", "c"],
        )

        assert "a" in str(error)
        assert "b" in str(error)
        assert "c" in str(error)
        assert error.cycle == ["a", "b", "c"]

    def test_dependency_conflict_error(self):
        """Test DependencyConflictError formatting."""
        error = DependencyConflictError(
            message="Version conflict",
            skill_name="my-skill",
            required_versions=["^1.0.0", "^2.0.0"],
            resolution_path=["root", "intermediate"],
        )

        assert "my-skill" in str(error)
        assert "^1.0.0" in str(error)
        assert "^2.0.0" in str(error)
        assert error.skill_name == "my-skill"

    def test_resolution_error(self):
        """Test ResolutionError formatting."""
        error = ResolutionError(
            message="Failed to resolve",
            skill_name="missing-skill",
            version_constraint=">=1.0.0",
        )

        assert "missing-skill" in str(error)
        assert ">=1.0.0" in str(error)

    def test_skill_not_found_error(self):
        """Test SkillNotFoundError formatting."""
        error = SkillNotFoundError(
            message="Skill not found",
            skill_name="unknown-skill",
            version_constraint="^1.0.0",
            registry_url="https://registry.example.com",
        )

        assert "unknown-skill" in str(error)
        assert "registry.example.com" in str(error)


class TestIntegration:
    """Integration tests for dependency resolution."""

    def test_resolve_dependencies_function(self):
        """Test the resolve_dependencies convenience function."""
        manifest = SkillManifest(
            name="test-skill",
            version="1.0.0",
            description="A test skill",
            author="test",
            type=SkillType.SKILL,
            dependencies={},
        )

        graph = resolve_dependencies(manifest)
        assert isinstance(graph, DependencyGraph)

    def test_generate_lock_file(self, temp_dir: Path):
        """Test the generate_lock_file convenience function."""
        lock_path = temp_dir / "kurultai.lock"

        manifest = SkillManifest(
            name="test-skill",
            version="1.0.0",
            description="A test skill",
            author="test",
            type=SkillType.SKILL,
            dependencies={},
        )

        # This will create an empty lock file since there are no dependencies
        result_path = generate_lock_file(manifest, lock_path)
        assert result_path == lock_path
