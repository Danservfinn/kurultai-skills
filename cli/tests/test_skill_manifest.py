"""
Tests for skill manifest parsing and validation.
"""

import pytest
from pathlib import Path
import tempfile
import yaml

from kurultai.models.skill import (
    Dependency,
    SkillManifest,
    SkillType,
    validate_semver,
    parse_semver,
    compare_versions,
    satisfies_constraint,
)
from kurultai.validators import (
    ManifestValidationError,
    ValidationError,
    ValidationErrorCollection,
    validate_skill_name,
    validate_skill_type,
    validate_dependencies,
    validate_manifest,
    validate_manifest_file,
    validate_manifest_structure,
)


class TestSemanticVersioning:
    """Tests for semantic version parsing and validation."""

    def test_validate_semver_valid_versions(self):
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

    def test_validate_semver_invalid_versions(self):
        """Test that invalid semver strings are rejected."""
        invalid_versions = [
            "",
            "1",
            "1.0",
            "1.0.0.0",
            "01.0.0",  # Leading zeros not allowed
            "1.01.0",
            "v1.0.0",  # 'v' prefix not part of semver spec
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
        # Prerelease versions have lower precedence
        assert compare_versions("1.0.0-alpha", "1.0.0") == -1
        assert compare_versions("1.0.0", "1.0.0-alpha") == 1
        # Compare prerelease identifiers
        assert compare_versions("1.0.0-alpha", "1.0.0-beta") == -1
        assert compare_versions("1.0.0-beta", "1.0.0-alpha") == 1

    def test_compare_versions_invalid(self):
        """Test that comparing invalid versions raises ValueError."""
        with pytest.raises(ValueError, match="Invalid semantic version"):
            compare_versions("invalid", "1.0.0")
        with pytest.raises(ValueError, match="Invalid semantic version"):
            compare_versions("1.0.0", "invalid")

    def test_satisfies_constraint_exact(self):
        """Test exact version constraint."""
        assert satisfies_constraint("1.0.0", "1.0.0") is True
        assert satisfies_constraint("1.0.0", "1.0.1") is False

    def test_satisfies_constraint_greater_than(self):
        """Test greater than constraint."""
        assert satisfies_constraint("2.0.0", ">1.0.0") is True
        assert satisfies_constraint("1.0.0", ">1.0.0") is False
        assert satisfies_constraint("0.9.0", ">1.0.0") is False

    def test_satisfies_constraint_greater_than_equal(self):
        """Test greater than or equal constraint."""
        assert satisfies_constraint("1.0.0", ">=1.0.0") is True
        assert satisfies_constraint("1.0.1", ">=1.0.0") is True
        assert satisfies_constraint("0.9.0", ">=1.0.0") is False

    def test_satisfies_constraint_less_than(self):
        """Test less than constraint."""
        assert satisfies_constraint("0.9.0", "<1.0.0") is True
        assert satisfies_constraint("1.0.0", "<1.0.0") is False
        assert satisfies_constraint("1.1.0", "<1.0.0") is False

    def test_satisfies_constraint_caret(self):
        """Test caret (compatible) constraint."""
        # ^1.0.0 allows 1.x.x but not 2.0.0
        assert satisfies_constraint("1.0.0", "^1.0.0") is True
        assert satisfies_constraint("1.5.0", "^1.0.0") is True
        assert satisfies_constraint("1.0.5", "^1.0.0") is True
        assert satisfies_constraint("2.0.0", "^1.0.0") is False
        # ^0.1.0 allows 0.1.x but not 0.2.0
        assert satisfies_constraint("0.1.5", "^0.1.0") is True
        assert satisfies_constraint("0.2.0", "^0.1.0") is False

    def test_satisfies_constraint_tilde(self):
        """Test tilde (approximately) constraint."""
        # ~1.0.0 allows 1.0.x but not 1.1.0
        assert satisfies_constraint("1.0.0", "~1.0.0") is True
        assert satisfies_constraint("1.0.5", "~1.0.0") is True
        assert satisfies_constraint("1.1.0", "~1.0.0") is False

    def test_satisfies_constraint_invalid_version(self):
        """Test that invalid version raises ValueError."""
        with pytest.raises(ValueError, match="Invalid version"):
            satisfies_constraint("invalid", ">=1.0.0")

    def test_satisfies_constraint_invalid_constraint(self):
        """Test that invalid constraint raises ValueError."""
        with pytest.raises(ValueError, match="Invalid constraint format"):
            satisfies_constraint("1.0.0", "invalid-constraint")


class TestSkillNameValidation:
    """Tests for skill name validation."""

    def test_valid_names(self):
        """Test valid skill names."""
        valid_names = [
            "my-skill",
            "my_skill",
            "skill123",
            "a",
            "valid-name-here",
        ]
        for name in valid_names:
            assert validate_skill_name(name), f"Expected {name} to be valid"

    def test_invalid_names(self):
        """Test invalid skill names."""
        invalid_names = [
            "",
            "123skill",  # Must start with letter
            "MySkill",   # No uppercase
            "my skill",  # No spaces
            "my.skill",  # No dots
            "my/skill",  # No slashes
            "-skill",    # Must start with letter
            "_skill",    # Must start with letter
        ]
        for name in invalid_names:
            assert not validate_skill_name(name), f"Expected {name} to be invalid"


class TestSkillTypeValidation:
    """Tests for skill type validation."""

    def test_valid_types(self):
        """Test valid skill types."""
        assert validate_skill_type("engine") is True
        assert validate_skill_type("skill") is True
        assert validate_skill_type("workflow") is True

    def test_invalid_types(self):
        """Test invalid skill types."""
        assert validate_skill_type("invalid") is False
        assert validate_skill_type("") is False
        assert validate_skill_type("ENGINE") is False  # Case sensitive


class TestDependencyValidation:
    """Tests for dependency validation."""

    def test_valid_dependencies(self):
        """Test valid dependency specifications."""
        deps = {
            "other-skill": ">=1.0.0",
            "another-skill": "^2.0.0",
            "optional-skill": "optional:>=1.0.0",
        }
        errors = validate_dependencies(deps)
        assert errors.is_valid()

    def test_invalid_dependency_name(self):
        """Test invalid dependency names are caught."""
        deps = {"Invalid-Name": ">=1.0.0"}
        errors = validate_dependencies(deps)
        assert not errors.is_valid()
        assert any("Invalid-Name" in str(e) for e in errors.errors)

    def test_invalid_version_constraint(self):
        """Test invalid version constraints are caught."""
        deps = {"valid-skill": "invalid-version"}
        errors = validate_dependencies(deps)
        assert not errors.is_valid()

    def test_non_dict_dependencies(self):
        """Test that non-dict dependencies raise error."""
        errors = validate_dependencies(["not", "a", "dict"])
        assert not errors.is_valid()


class TestSkillManifestModel:
    """Tests for the SkillManifest Pydantic model."""

    def test_create_valid_manifest(self):
        """Test creating a valid skill manifest."""
        manifest = SkillManifest(
            name="test-skill",
            version="1.0.0",
            description="A test skill for validation",
            author="Test Author",
            type=SkillType.SKILL,
        )
        assert manifest.name == "test-skill"
        assert manifest.version == "1.0.0"
        assert manifest.type == SkillType.SKILL

    def test_create_manifest_with_all_fields(self):
        """Test creating a manifest with all optional fields."""
        manifest = SkillManifest(
            name="full-skill",
            version="2.1.0-beta.1",
            description="A complete skill manifest with all fields",
            author="Kurultai Team",
            type=SkillType.ENGINE,
            dependencies={"other-skill": ">=1.0.0", "optional-dep": "optional:^2.0.0"},
            entry_point="src/main.py",
            prompts_dir="custom-prompts",
            tags=["ai", "nlp", "test"],
            homepage="https://example.com",
            repository="https://github.com/example/skill",
        )
        assert len(manifest.tags) == 3
        assert manifest.prompts_dir == "custom-prompts"

    def test_invalid_name_raises_error(self):
        """Test that invalid names raise validation error."""
        with pytest.raises(Exception) as exc_info:
            SkillManifest(
                name="InvalidName",
                version="1.0.0",
                description="Test description",
                author="Test",
                type=SkillType.SKILL,
            )
        assert "InvalidName" in str(exc_info.value)

    def test_invalid_version_raises_error(self):
        """Test that invalid versions raise validation error."""
        with pytest.raises(Exception) as exc_info:
            SkillManifest(
                name="valid-skill",
                version="not-a-version",
                description="Test description",
                author="Test",
                type=SkillType.SKILL,
            )
        assert "not-a-version" in str(exc_info.value)

    def test_short_description_raises_error(self):
        """Test that short descriptions raise validation error."""
        with pytest.raises(Exception) as exc_info:
            SkillManifest(
                name="valid-skill",
                version="1.0.0",
                description="Too short",
                author="Test",
                type=SkillType.SKILL,
            )
        assert "10 characters" in str(exc_info.value)

    def test_invalid_tag_format(self):
        """Test that invalid tag formats raise validation error."""
        with pytest.raises(Exception) as exc_info:
            SkillManifest(
                name="valid-skill",
                version="1.0.0",
                description="A valid description that is long enough",
                author="Test",
                type=SkillType.SKILL,
                tags=["Invalid Tag"],
            )
        assert "Invalid Tag" in str(exc_info.value) or "invalid tag" in str(exc_info.value).lower()

    def test_invalid_url(self):
        """Test that invalid URLs raise validation error."""
        with pytest.raises(Exception) as exc_info:
            SkillManifest(
                name="valid-skill",
                version="1.0.0",
                description="A valid description that is long enough",
                author="Test",
                type=SkillType.SKILL,
                homepage="not-a-valid-url",
            )
        assert "Invalid URL" in str(exc_info.value)

    def test_parsed_dependencies(self):
        """Test that dependencies are correctly parsed."""
        manifest = SkillManifest(
            name="test-skill",
            version="1.0.0",
            description="A test skill for validation",
            author="Test",
            type=SkillType.SKILL,
            dependencies={
                "required-skill": ">=1.0.0",
                "optional-skill": "optional:^2.0.0",
            },
        )
        deps = manifest.parsed_dependencies
        assert len(deps) == 2

        required = manifest.get_required_dependencies()
        assert len(required) == 1
        assert required[0].name == "required-skill"

        optional = manifest.get_optional_dependencies()
        assert len(optional) == 1
        assert optional[0].name == "optional-skill"
        assert optional[0].is_optional is True

    def test_has_dependency(self):
        """Test checking for dependency existence."""
        manifest = SkillManifest(
            name="test-skill",
            version="1.0.0",
            description="A test skill for validation",
            author="Test",
            type=SkillType.SKILL,
            dependencies={"other-skill": ">=1.0.0"},
        )
        assert manifest.has_dependency("other-skill") is True
        assert manifest.has_dependency("missing-skill") is False

    def test_get_dependency(self):
        """Test getting a specific dependency."""
        manifest = SkillManifest(
            name="test-skill",
            version="1.0.0",
            description="A test skill for validation",
            author="Test",
            type=SkillType.SKILL,
            dependencies={"other-skill": ">=1.0.0"},
        )
        dep = manifest.get_dependency("other-skill")
        assert dep is not None
        assert dep.name == "other-skill"
        assert dep.version_constraint == ">=1.0.0"

        assert manifest.get_dependency("missing") is None

    def test_to_yaml_dict(self):
        """Test converting manifest to YAML dictionary."""
        manifest = SkillManifest(
            name="test-skill",
            version="1.0.0",
            description="A test skill",
            author="Test",
            type=SkillType.SKILL,
            tags=["test"],
        )
        data = manifest.to_yaml_dict()
        assert data["name"] == "test-skill"
        assert data["type"] == "skill"
        assert "tags" in data

    def test_string_representation(self):
        """Test string representation of manifest."""
        manifest = SkillManifest(
            name="test-skill",
            version="1.0.0",
            description="A test skill",
            author="Test",
            type=SkillType.SKILL,
        )
        assert str(manifest) == "test-skill@1.0.0 (skill)"
        assert "test-skill" in repr(manifest)


class TestDependencyModel:
    """Tests for the Dependency model."""

    def test_create_dependency(self):
        """Test creating a dependency."""
        dep = Dependency(name="test-dep", version_constraint=">=1.0.0")
        assert dep.name == "test-dep"
        assert dep.version_constraint == ">=1.0.0"
        assert dep.is_optional is False

    def test_create_optional_dependency(self):
        """Test creating an optional dependency."""
        dep = Dependency(name="test-dep", version_constraint=">=1.0.0", is_optional=True)
        assert dep.is_optional is True

    def test_invalid_dependency_name(self):
        """Test that invalid dependency names raise error."""
        with pytest.raises(Exception):
            Dependency(name="Invalid", version_constraint=">=1.0.0")

    def test_invalid_version_constraint(self):
        """Test that invalid version constraints raise error."""
        with pytest.raises(Exception):
            Dependency(name="valid", version_constraint="invalid")

    def test_dependency_string_representation(self):
        """Test string representation of dependency."""
        dep = Dependency(name="test", version_constraint=">=1.0.0")
        assert str(dep) == "test@>=1.0.0"

        opt_dep = Dependency(name="test", version_constraint=">=1.0.0", is_optional=True)
        assert str(opt_dep) == "optional:test@>=1.0.0"

    def test_dependency_hash_and_equality(self):
        """Test that dependencies are hashable and comparable."""
        dep1 = Dependency(name="test", version_constraint=">=1.0.0")
        dep2 = Dependency(name="test", version_constraint=">=1.0.0")
        dep3 = Dependency(name="other", version_constraint=">=1.0.0")

        assert dep1 == dep2
        assert dep1 != dep3
        assert hash(dep1) == hash(dep2)


class TestManifestValidation:
    """Tests for the main validate_manifest function."""

    def test_validate_manifest_from_dict(self):
        """Test validating a manifest from dictionary."""
        data = {
            "name": "test-skill",
            "version": "1.0.0",
            "description": "A test skill for validation purposes",
            "author": "Test Author",
            "type": "skill",
        }
        manifest = validate_manifest(data)
        assert isinstance(manifest, SkillManifest)
        assert manifest.name == "test-skill"

    def test_validate_manifest_missing_required_fields(self):
        """Test that missing required fields raise error."""
        data = {
            "name": "test-skill",
            # Missing version, description, author, type
        }
        with pytest.raises(ManifestValidationError) as exc_info:
            validate_manifest(data)
        assert "missing" in str(exc_info.value).lower() or "required" in str(exc_info.value).lower()

    def test_validate_manifest_invalid_field_values(self):
        """Test that invalid field values raise error."""
        data = {
            "name": "InvalidName",
            "version": "not-a-version",
            "description": "Short",
            "author": "",
            "type": "invalid-type",
        }
        with pytest.raises(ManifestValidationError):
            validate_manifest(data)

    def test_validate_manifest_from_yaml_string(self):
        """Test validating a manifest from YAML string."""
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

    def test_validate_manifest_from_file(self):
        """Test validating a manifest from file."""
        data = {
            "name": "file-skill",
            "version": "1.0.0",
            "description": "A skill loaded from file",
            "author": "File Author",
            "type": "workflow",
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(data, f)
            temp_path = f.name

        try:
            manifest = validate_manifest_file(temp_path)
            assert manifest.name == "file-skill"
            assert manifest.type == SkillType.WORKFLOW
        finally:
            Path(temp_path).unlink()

    def test_validate_manifest_file_not_found(self):
        """Test that missing file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            validate_manifest_file("/nonexistent/path/skill.yaml")

    def test_validate_manifest_invalid_yaml(self):
        """Test that invalid YAML raises ManifestValidationError."""
        invalid_yaml = "name: test\nversion: [unclosed bracket"
        with pytest.raises(ManifestValidationError) as exc_info:
            validate_manifest(invalid_yaml)
        assert "yaml" in str(exc_info.value).lower() or "parse" in str(exc_info.value).lower()

    def test_validate_manifest_structure_non_dict(self):
        """Test that non-dict data raises appropriate error."""
        errors = validate_manifest_structure(["not", "a", "dict"])
        assert not errors.is_valid()
        assert any("dictionary" in str(e).lower() or "object" in str(e).lower() for e in errors.errors)


class TestValidationErrorCollection:
    """Tests for ValidationErrorCollection."""

    def test_empty_collection_is_valid(self):
        """Test that empty collection is valid."""
        errors = ValidationErrorCollection()
        assert errors.is_valid()
        assert not errors.has_errors()
        assert bool(errors) is True

    def test_add_error(self):
        """Test adding errors to collection."""
        errors = ValidationErrorCollection()
        errors.add("Test error", field="test_field")
        assert not errors.is_valid()
        assert errors.has_errors()
        assert len(errors) == 1

    def test_get_errors_for_field(self):
        """Test getting errors for specific field."""
        errors = ValidationErrorCollection()
        errors.add("Error 1", field="field1")
        errors.add("Error 2", field="field1")
        errors.add("Error 3", field="field2")

        field1_errors = errors.get_errors_for_field("field1")
        assert len(field1_errors) == 2

    def test_get_field_names(self):
        """Test getting all field names with errors."""
        errors = ValidationErrorCollection()
        errors.add("Error 1", field="field1")
        errors.add("Error 2", field="field2")
        errors.add("Error 3")  # No field

        field_names = errors.get_field_names()
        assert "field1" in field_names
        assert "field2" in field_names
        assert len(field_names) == 2

    def test_raise_if_invalid(self):
        """Test that raise_if_invalid raises when errors exist."""
        errors = ValidationErrorCollection()
        errors.add("Test error")

        with pytest.raises(ManifestValidationError):
            errors.raise_if_invalid()

    def test_raise_if_invalid_no_errors(self):
        """Test that raise_if_invalid doesn't raise when no errors."""
        errors = ValidationErrorCollection()
        errors.raise_if_invalid()  # Should not raise

    def test_format_errors(self):
        """Test error formatting."""
        errors = ValidationErrorCollection()
        errors.add("Error message", field="field1")

        formatted = errors.format_errors()
        assert "Validation failed" in formatted
        assert "field1" in formatted
        assert "Error message" in formatted

    def test_iteration(self):
        """Test iterating over errors."""
        errors = ValidationErrorCollection()
        errors.add("Error 1")
        errors.add("Error 2")

        error_messages = [e.message for e in errors]
        assert "Error 1" in error_messages
        assert "Error 2" in error_messages


class TestManifestValidationError:
    """Tests for ManifestValidationError exception."""

    def test_basic_error(self):
        """Test basic error creation."""
        error = ManifestValidationError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.field is None

    def test_error_with_field(self):
        """Test error with field specification."""
        error = ManifestValidationError("Invalid value", field="name")
        assert "name" in str(error)
        assert error.field == "name"

    def test_error_with_errors_list(self):
        """Test error with detailed errors list."""
        errors = [{"field": "name", "message": "Invalid"}]
        error = ManifestValidationError("Validation failed", errors=errors)
        assert error.errors == errors

    def test_to_dict(self):
        """Test converting error to dictionary."""
        error = ManifestValidationError("Test", field="name", errors=[{"msg": "error"}])
        data = error.to_dict()
        assert data["message"] == "Test"
        assert data["field"] == "name"
        assert data["errors"] == [{"msg": "error"}]


class TestIntegrationExamples:
    """Integration tests with example manifest data."""

    def test_engine_manifest(self):
        """Test a complete engine manifest."""
        data = {
            "name": "nlp-engine",
            "version": "2.1.0",
            "description": "Natural language processing engine for text analysis and entity extraction",
            "author": "Kurultai NLP Team",
            "type": "engine",
            "entry_point": "src/engine.py",
            "dependencies": {
                "transformers": ">=4.20.0",
                "torch": "^2.0.0",
            },
            "tags": ["nlp", "ai", "ml"],
            "homepage": "https://kurultai.ai/nlp-engine",
            "repository": "https://github.com/kurultai/nlp-engine",
        }
        manifest = validate_manifest(data)
        assert manifest.type == SkillType.ENGINE
        assert manifest.entry_point == "src/engine.py"

    def test_skill_manifest(self):
        """Test a complete skill manifest."""
        data = {
            "name": "sentiment-analyzer",
            "version": "1.5.0-beta.2",
            "description": "Analyze sentiment in text using pre-trained models",
            "author": "Jane Doe",
            "type": "skill",
            "prompts_dir": "prompts",
            "dependencies": {
                "nlp-engine": ">=2.0.0",
                "data-utils": "optional:^1.0.0",
            },
            "tags": ["sentiment", "analysis"],
        }
        manifest = validate_manifest(data)
        assert manifest.type == SkillType.SKILL
        assert len(manifest.get_optional_dependencies()) == 1

    def test_workflow_manifest(self):
        """Test a complete workflow manifest."""
        data = {
            "name": "document-processing",
            "version": "3.0.0",
            "description": "Complete document processing workflow from ingestion to analysis",
            "author": "Kurultai Workflows Team",
            "type": "workflow",
            "entry_point": "workflow.yaml",
            "dependencies": {
                "ingestion-skill": ">=1.0.0",
                "ocr-skill": ">=2.0.0",
                "nlp-engine": "^2.0.0",
            },
            "tags": ["document", "processing", "pipeline"],
        }
        manifest = validate_manifest(data)
        assert manifest.type == SkillType.WORKFLOW
        assert len(manifest.parsed_dependencies) == 3
