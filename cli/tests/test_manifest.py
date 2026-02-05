"""Tests for manifest parsing and validation.

This module tests manifest parsing, semantic version validation,
dependency parsing, and all skill types (engine, skill, workflow).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from unittest.mock import patch

import pytest
import yaml

from kurultai.models.skill import (
    Dependency,
    SkillManifest,
    SkillType,
    compare_versions,
    parse_semver,
    satisfies_constraint,
    validate_semver,
)
from kurultai.validators import (
    ManifestValidationError,
    validate_dependencies,
    validate_entry_point,
    validate_manifest,
    validate_manifest_file,
    validate_manifest_structure,
    validate_skill_name,
    validate_skill_type,
    validate_tags,
    validate_url,
)


class TestValidManifestParsing:
    """Tests for parsing valid manifests."""

    def test_parse_minimal_manifest(self, valid_skill_manifest: Dict[str, Any]):
        """Test parsing a minimal valid manifest."""
        manifest = validate_manifest(valid_skill_manifest)
        assert isinstance(manifest, SkillManifest)
        assert manifest.name == "test-skill"
        assert manifest.version == "1.0.0"
        assert manifest.type == SkillType.SKILL

    def test_parse_engine_manifest(self, valid_engine_manifest: Dict[str, Any]):
        """Test parsing an engine manifest."""
        manifest = validate_manifest(valid_engine_manifest)
        assert isinstance(manifest, SkillManifest)
        assert manifest.type == SkillType.ENGINE
        assert manifest.entry_point == "src/engine.py"

    def test_parse_workflow_manifest(self, valid_workflow_manifest: Dict[str, Any]):
        """Test parsing a workflow manifest."""
        manifest = validate_manifest(valid_workflow_manifest)
        assert isinstance(manifest, SkillManifest)
        assert manifest.type == SkillType.WORKFLOW
        assert manifest.entry_point == "workflow.yaml"

    def test_parse_manifest_with_all_fields(self):
        """Test parsing a manifest with all optional fields."""
        data = {
            "name": "complete-skill",
            "version": "2.1.0-beta.1",
            "description": "A complete skill with all fields defined",
            "author": "Kurultai Team",
            "type": "skill",
            "dependencies": {
                "dep1": ">=1.0.0",
                "dep2": "optional:^2.0.0",
            },
            "entry_point": "src/main.py",
            "prompts_dir": "custom-prompts",
            "tags": ["ai", "nlp", "test"],
            "homepage": "https://example.com",
            "repository": "https://github.com/example/skill",
        }
        manifest = validate_manifest(data)
        assert manifest.name == "complete-skill"
        assert len(manifest.tags) == 3
        assert manifest.prompts_dir == "custom-prompts"
        assert manifest.homepage == "https://example.com"
        assert manifest.repository == "https://github.com/example/skill"

    def test_parse_manifest_from_yaml_string(self):
        """Test parsing a manifest from YAML string."""
        yaml_content = """
name: yaml-skill
version: 1.0.0
description: A skill defined in YAML format
author: YAML Author
type: engine
dependencies:
  other-skill: ">=1.0.0"
tags:
  - ai
  - test
"""
        manifest = validate_manifest(yaml_content)
        assert manifest.name == "yaml-skill"
        assert manifest.type == SkillType.ENGINE

    def test_parse_manifest_from_file(self, temp_dir: Path):
        """Test parsing a manifest from file."""
        data = {
            "name": "file-skill",
            "version": "1.0.0",
            "description": "A skill loaded from file",
            "author": "File Author",
            "type": "workflow",
        }
        manifest_path = temp_dir / "skill.yaml"
        with open(manifest_path, "w") as f:
            yaml.dump(data, f)

        manifest = validate_manifest_file(manifest_path)
        assert manifest.name == "file-skill"
        assert manifest.type == SkillType.WORKFLOW


class TestInvalidManifestErrors:
    """Tests for invalid manifest error handling."""

    def test_missing_required_field(self, invalid_manifests: Dict[str, Dict[str, Any]]):
        """Test that missing required fields raise errors."""
        for field_name, data in invalid_manifests.items():
            if field_name.startswith("missing_"):
                with pytest.raises(ManifestValidationError) as exc_info:
                    validate_manifest(data)
                assert "missing" in str(exc_info.value).lower() or "required" in str(exc_info.value).lower()

    def test_invalid_name(self, invalid_manifests: Dict[str, Dict[str, Any]]):
        """Test that invalid names raise errors."""
        with pytest.raises(ManifestValidationError) as exc_info:
            validate_manifest(invalid_manifests["invalid_name"])
        assert "Invalid" in str(exc_info.value) or "name" in str(exc_info.value).lower()

    def test_invalid_version(self, invalid_manifests: Dict[str, Dict[str, Any]]):
        """Test that invalid versions raise errors."""
        with pytest.raises(ManifestValidationError) as exc_info:
            validate_manifest(invalid_manifests["invalid_version"])
        assert "version" in str(exc_info.value).lower()

    def test_short_description(self, invalid_manifests: Dict[str, Dict[str, Any]]):
        """Test that short descriptions raise errors."""
        with pytest.raises(ManifestValidationError) as exc_info:
            validate_manifest(invalid_manifests["short_description"])
        assert "10 characters" in str(exc_info.value) or "description" in str(exc_info.value).lower()

    def test_invalid_type(self, invalid_manifests: Dict[str, Dict[str, Any]]):
        """Test that invalid types raise errors."""
        with pytest.raises(ManifestValidationError) as exc_info:
            validate_manifest(invalid_manifests["invalid_type"])
        assert "type" in str(exc_info.value).lower()

    def test_non_dict_manifest(self):
        """Test that non-dict manifest raises error."""
        errors = validate_manifest_structure(["not", "a", "dict"])
        assert not errors.is_valid()

    def test_null_required_fields(self):
        """Test that null required fields raise errors."""
        data = {
            "name": None,
            "version": "1.0.0",
            "description": "A test skill",
            "author": "Test",
            "type": "skill",
        }
        errors = validate_manifest_structure(data)
        assert not errors.is_valid()

    def test_empty_required_fields(self):
        """Test that empty required fields raise errors."""
        data = {
            "name": "test-skill",
            "version": "",
            "description": "A test skill",
            "author": "Test",
            "type": "skill",
        }
        errors = validate_manifest_structure(data)
        assert not errors.is_valid()

    def test_invalid_yaml(self):
        """Test that invalid YAML raises error."""
        invalid_yaml = "name: test\nversion: [unclosed bracket"
        with pytest.raises(ManifestValidationError) as exc_info:
            validate_manifest(invalid_yaml)
        assert "yaml" in str(exc_info.value).lower() or "parse" in str(exc_info.value).lower()

    def test_file_not_found(self):
        """Test that missing file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            validate_manifest_file("/nonexistent/path/skill.yaml")


class TestSemanticVersionValidation:
    """Tests for semantic version validation."""

    def test_valid_semver_versions(self):
        """Test that valid semver strings are accepted."""
        valid_versions = [
            "1.0.0",
            "0.0.1",
            "10.20.30",
            "1.0.0-alpha",
            "1.0.0-alpha.1",
            "1.0.0-0.3.7",
            "1.0.0-x.7.z.92",
            "1.0.0+build",
            "1.0.0+build.1",
            "1.0.0-alpha+build",
            "1.0.0-beta.11",
            "1.0.0-rc.1",
        ]
        for version in valid_versions:
            assert validate_semver(version), f"Expected {version} to be valid"

    def test_invalid_semver_versions(self):
        """Test that invalid semver strings are rejected."""
        invalid_versions = [
            "",
            "1",
            "1.0",
            "1.0.0.0",
            "01.0.0",
            "1.01.0",
            "v1.0.0",
            "1.0.0-",
            "1.0.0+",
            "not-a-version",
        ]
        for version in invalid_versions:
            assert not validate_semver(version), f"Expected {version} to be invalid"

    def test_parse_semver_valid(self):
        """Test parsing valid semver strings."""
        result = parse_semver("1.2.3-alpha+build")
        assert result is not None
        assert result["major"] == 1
        assert result["minor"] == 2
        assert result["patch"] == 3
        assert result["prerelease"] == "alpha"
        assert result["build"] == "build"

    def test_parse_semver_invalid(self):
        """Test parsing invalid semver strings returns None."""
        assert parse_semver("invalid") is None
        assert parse_semver("") is None

    def test_compare_versions_equal(self):
        """Test comparing equal versions."""
        assert compare_versions("1.0.0", "1.0.0") == 0
        assert compare_versions("1.2.3", "1.2.3") == 0

    def test_compare_versions_less_than(self):
        """Test version less than comparison."""
        assert compare_versions("1.0.0", "2.0.0") == -1
        assert compare_versions("1.0.0", "1.1.0") == -1
        assert compare_versions("1.0.0", "1.0.1") == -1

    def test_compare_versions_greater_than(self):
        """Test version greater than comparison."""
        assert compare_versions("2.0.0", "1.0.0") == 1
        assert compare_versions("1.1.0", "1.0.0") == 1
        assert compare_versions("1.0.1", "1.0.0") == 1

    def test_compare_versions_prerelease(self):
        """Test version comparison with prerelease identifiers."""
        assert compare_versions("1.0.0-alpha", "1.0.0") == -1
        assert compare_versions("1.0.0", "1.0.0-alpha") == 1
        assert compare_versions("1.0.0-alpha", "1.0.0-beta") == -1
        assert compare_versions("1.0.0-beta", "1.0.0-alpha") == 1

    def test_compare_versions_invalid(self):
        """Test that comparing invalid versions raises ValueError."""
        with pytest.raises(ValueError, match="Invalid semantic version"):
            compare_versions("invalid", "1.0.0")
        with pytest.raises(ValueError, match="Invalid semantic version"):
            compare_versions("1.0.0", "invalid")


class TestVersionConstraintParsing:
    """Tests for version constraint parsing."""

    def test_caret_constraint(self, version_constraints: Dict[str, Dict[str, Any]]):
        """Test caret (^) constraint matching."""
        caret = version_constraints["caret"]
        for version in caret["matching"]:
            assert satisfies_constraint(version, caret["constraint"])
        for version in caret["non_matching"]:
            assert not satisfies_constraint(version, caret["constraint"])

    def test_tilde_constraint(self, version_constraints: Dict[str, Dict[str, Any]]):
        """Test tilde (~) constraint matching."""
        tilde = version_constraints["tilde"]
        for version in tilde["matching"]:
            assert satisfies_constraint(version, tilde["constraint"])
        for version in tilde["non_matching"]:
            assert not satisfies_constraint(version, tilde["constraint"])

    def test_gte_constraint(self, version_constraints: Dict[str, Dict[str, Any]]):
        """Test greater than or equal (>=) constraint."""
        gte = version_constraints["gte"]
        for version in gte["matching"]:
            assert satisfies_constraint(version, gte["constraint"])
        for version in gte["non_matching"]:
            assert not satisfies_constraint(version, gte["constraint"])

    def test_gt_constraint(self, version_constraints: Dict[str, Dict[str, Any]]):
        """Test greater than (>) constraint."""
        gt = version_constraints["gt"]
        for version in gt["matching"]:
            assert satisfies_constraint(version, gt["constraint"])
        for version in gt["non_matching"]:
            assert not satisfies_constraint(version, gt["constraint"])

    def test_lte_constraint(self, version_constraints: Dict[str, Dict[str, Any]]):
        """Test less than or equal (<=) constraint."""
        lte = version_constraints["lte"]
        for version in lte["matching"]:
            assert satisfies_constraint(version, lte["constraint"])
        for version in lte["non_matching"]:
            assert not satisfies_constraint(version, lte["constraint"])

    def test_lt_constraint(self, version_constraints: Dict[str, Dict[str, Any]]):
        """Test less than (<) constraint."""
        lt = version_constraints["lt"]
        for version in lt["matching"]:
            assert satisfies_constraint(version, lt["constraint"])
        for version in lt["non_matching"]:
            assert not satisfies_constraint(version, lt["constraint"])

    def test_exact_constraint(self, version_constraints: Dict[str, Dict[str, Any]]):
        """Test exact version constraint."""
        exact = version_constraints["exact"]
        for version in exact["matching"]:
            assert satisfies_constraint(version, exact["constraint"])
        for version in exact["non_matching"]:
            assert not satisfies_constraint(version, exact["constraint"])

    def test_invalid_version_raises(self):
        """Test that invalid version raises ValueError."""
        with pytest.raises(ValueError, match="Invalid version"):
            satisfies_constraint("invalid", ">=1.0.0")

    def test_invalid_constraint_raises(self):
        """Test that invalid constraint raises ValueError."""
        with pytest.raises(ValueError, match="Invalid constraint format"):
            satisfies_constraint("1.0.0", "invalid-constraint")


class TestDependencyParsing:
    """Tests for dependency parsing."""

    def test_parse_required_dependency(self):
        """Test parsing a required dependency."""
        dep = Dependency(name="test-dep", version_constraint=">=1.0.0")
        assert dep.name == "test-dep"
        assert dep.version_constraint == ">=1.0.0"
        assert dep.is_optional is False

    def test_parse_optional_dependency(self):
        """Test parsing an optional dependency."""
        dep = Dependency(name="test-dep", version_constraint=">=1.0.0", is_optional=True)
        assert dep.is_optional is True

    def test_dependency_from_manifest(self):
        """Test parsing dependencies from manifest."""
        data = {
            "name": "test-skill",
            "version": "1.0.0",
            "description": "A test skill",
            "author": "Test",
            "type": "skill",
            "dependencies": {
                "required-dep": ">=1.0.0",
                "optional-dep": "optional:^2.0.0",
            },
        }
        manifest = validate_manifest(data)
        deps = manifest.parsed_dependencies

        required = [d for d in deps if not d.is_optional]
        optional = [d for d in deps if d.is_optional]

        assert len(required) == 1
        assert len(optional) == 1
        assert required[0].name == "required-dep"
        assert optional[0].name == "optional-dep"

    def test_invalid_dependency_name(self):
        """Test that invalid dependency names raise errors."""
        with pytest.raises(Exception):
            Dependency(name="Invalid Name", version_constraint=">=1.0.0")

    def test_invalid_version_constraint(self):
        """Test that invalid version constraints raise errors."""
        with pytest.raises(Exception):
            Dependency(name="valid-name", version_constraint="invalid")

    def test_dependency_hash_and_equality(self):
        """Test that dependencies are hashable and comparable."""
        dep1 = Dependency(name="test", version_constraint=">=1.0.0")
        dep2 = Dependency(name="test", version_constraint=">=1.0.0")
        dep3 = Dependency(name="other", version_constraint=">=1.0.0")

        assert dep1 == dep2
        assert dep1 != dep3
        assert hash(dep1) == hash(dep2)

        # Can be used in set
        dep_set = {dep1, dep2, dep3}
        assert len(dep_set) == 2


class TestSkillTypes:
    """Tests for all skill types."""

    def test_engine_type(self):
        """Test engine skill type."""
        data = {
            "name": "test-engine",
            "version": "1.0.0",
            "description": "A test engine for processing",
            "author": "Test",
            "type": "engine",
            "entry_point": "src/engine.py",
        }
        manifest = validate_manifest(data)
        assert manifest.type == SkillType.ENGINE

    def test_skill_type(self):
        """Test regular skill type."""
        data = {
            "name": "test-skill",
            "version": "1.0.0",
            "description": "A test skill",
            "author": "Test",
            "type": "skill",
        }
        manifest = validate_manifest(data)
        assert manifest.type == SkillType.SKILL

    def test_workflow_type(self):
        """Test workflow skill type."""
        data = {
            "name": "test-workflow",
            "version": "1.0.0",
            "description": "A test workflow",
            "author": "Test",
            "type": "workflow",
            "entry_point": "workflow.yaml",
        }
        manifest = validate_manifest(data)
        assert manifest.type == SkillType.WORKFLOW

    def test_skill_type_enum_values(self):
        """Test skill type enum values."""
        assert SkillType.ENGINE.value == "engine"
        assert SkillType.SKILL.value == "skill"
        assert SkillType.WORKFLOW.value == "workflow"

    def test_skill_type_from_string(self):
        """Test creating skill type from string."""
        assert SkillType("engine") == SkillType.ENGINE
        assert SkillType("skill") == SkillType.SKILL
        assert SkillType("workflow") == SkillType.WORKFLOW


class TestManifestHelpers:
    """Tests for manifest helper methods."""

    def test_has_dependency(self):
        """Test checking for dependency existence."""
        data = {
            "name": "test-skill",
            "version": "1.0.0",
            "description": "A test skill",
            "author": "Test",
            "type": "skill",
            "dependencies": {"other-skill": ">=1.0.0"},
        }
        manifest = validate_manifest(data)
        assert manifest.has_dependency("other-skill") is True
        assert manifest.has_dependency("missing-skill") is False

    def test_get_dependency(self):
        """Test getting a specific dependency."""
        data = {
            "name": "test-skill",
            "version": "1.0.0",
            "description": "A test skill",
            "author": "Test",
            "type": "skill",
            "dependencies": {"other-skill": ">=1.0.0"},
        }
        manifest = validate_manifest(data)
        dep = manifest.get_dependency("other-skill")
        assert dep is not None
        assert dep.name == "other-skill"
        assert dep.version_constraint == ">=1.0.0"
        assert manifest.get_dependency("missing") is None

    def test_to_yaml_dict(self):
        """Test converting manifest to YAML dictionary."""
        data = {
            "name": "test-skill",
            "version": "1.0.0",
            "description": "A test skill",
            "author": "Test",
            "type": "skill",
            "tags": ["test"],
        }
        manifest = validate_manifest(data)
        yaml_dict = manifest.to_yaml_dict()
        assert yaml_dict["name"] == "test-skill"
        assert yaml_dict["type"] == "skill"
        assert "tags" in yaml_dict

    def test_string_representation(self):
        """Test string representation of manifest."""
        data = {
            "name": "test-skill",
            "version": "1.0.0",
            "description": "A test skill",
            "author": "Test",
            "type": "skill",
        }
        manifest = validate_manifest(data)
        assert str(manifest) == "test-skill@1.0.0 (skill)"
        assert "test-skill" in repr(manifest)


class TestValidationHelpers:
    """Tests for validation helper functions."""

    def test_validate_skill_name_valid(self):
        """Test valid skill names."""
        valid_names = ["my-skill", "my_skill", "skill123", "a", "valid-name-here"]
        for name in valid_names:
            assert validate_skill_name(name), f"Expected {name} to be valid"

    def test_validate_skill_name_invalid(self):
        """Test invalid skill names."""
        invalid_names = ["", "123skill", "MySkill", "my skill", "my.skill", "-skill", "_skill"]
        for name in invalid_names:
            assert not validate_skill_name(name), f"Expected {name} to be invalid"

    def test_validate_skill_type_valid(self):
        """Test valid skill types."""
        assert validate_skill_type("engine") is True
        assert validate_skill_type("skill") is True
        assert validate_skill_type("workflow") is True

    def test_validate_skill_type_invalid(self):
        """Test invalid skill types."""
        assert validate_skill_type("invalid") is False
        assert validate_skill_type("") is False
        assert validate_skill_type("ENGINE") is False

    def test_validate_dependencies_valid(self):
        """Test valid dependency specifications."""
        deps = {
            "other-skill": ">=1.0.0",
            "another-skill": "^2.0.0",
            "optional-skill": "optional:>=1.0.0",
        }
        errors = validate_dependencies(deps)
        assert errors.is_valid()

    def test_validate_dependencies_invalid_name(self):
        """Test invalid dependency names are caught."""
        deps = {"Invalid-Name": ">=1.0.0"}
        errors = validate_dependencies(deps)
        assert not errors.is_valid()

    def test_validate_dependencies_non_dict(self):
        """Test that non-dict dependencies raise error."""
        errors = validate_dependencies(["not", "a", "dict"])
        assert not errors.is_valid()

    def test_validate_tags_valid(self):
        """Test valid tags."""
        errors = validate_tags(["ai", "nlp", "test-tag"])
        assert errors.is_valid()

    def test_validate_tags_invalid(self):
        """Test invalid tags."""
        errors = validate_tags(["Invalid Tag"])
        assert not errors.is_valid()

    def test_validate_url_valid(self):
        """Test valid URLs."""
        errors = validate_url("https://example.com")
        assert errors.is_valid()

    def test_validate_url_invalid(self):
        """Test invalid URLs."""
        errors = validate_url("not-a-url")
        assert not errors.is_valid()

    def test_validate_entry_point_valid(self):
        """Test valid entry points."""
        errors = validate_entry_point("src/main.py")
        assert errors.is_valid()

    def test_validate_entry_point_dangerous(self):
        """Test dangerous entry point patterns."""
        errors = validate_entry_point("../dangerous.py")
        assert not errors.is_valid()
