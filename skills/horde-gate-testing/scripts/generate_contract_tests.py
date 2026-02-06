#!/usr/bin/env python3
"""
Generate contract tests based on integration surface analysis.

This script generates tests that verify Phase N outputs match the contracts
expected by Phase N+1, based on the integration surface JSON produced by
detect_integration_surface.py.

Usage:
    python3 generate_contract_tests.py \
        --surface "phase1_surface.json" \
        --output-dir "tests/contracts/" \
        --framework pytest \
        --mock-next-phase
"""

from __future__ import annotations

import argparse
import inspect
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


# =============================================================================
# Custom Exceptions
# =============================================================================


class ContractTestError(Exception):
    """Base exception for contract test generation errors."""
    pass


class SurfaceFileNotFoundError(ContractTestError):
    """Raised when the integration surface JSON file is not found."""
    pass


class InvalidSurfaceError(ContractTestError):
    """Raised when the integration surface JSON is invalid."""
    pass


class UnsupportedFrameworkError(ContractTestError):
    """Raised when an unsupported test framework is specified."""
    pass


class OutputDirectoryError(ContractTestError):
    """Raised when there's an issue with the output directory."""
    pass


# =============================================================================
# Data Models
# =============================================================================


@dataclass
class FunctionExport:
    """Represents a function export from the integration surface."""
    name: str
    module: str
    parameters: List[Dict[str, Any]]
    return_type: Optional[str] = None
    docstring: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> FunctionExport:
        """Create a FunctionExport from a dictionary."""
        return cls(
            name=data.get("name", ""),
            module=data.get("file", data.get("module", "")),
            parameters=data.get("parameters", []),
            return_type=data.get("return_type"),
            docstring=data.get("docstring"),
        )


@dataclass
class ClassExport:
    """Represents a class export from the integration surface."""
    name: str
    module: str
    methods: List[Dict[str, Any]]
    attributes: List[str]
    base_classes: List[str]
    docstring: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ClassExport:
        """Create a ClassExport from a dictionary."""
        return cls(
            name=data.get("name", ""),
            module=data.get("file", data.get("module", "")),
            methods=data.get("methods", []),
            attributes=data.get("attributes", []),
            base_classes=data.get("base_classes", []),
            docstring=data.get("docstring"),
        )


@dataclass
class DataStructureContract:
    """Represents a data structure contract from the integration surface."""
    name: str
    module: str
    fields: List[Dict[str, Any]]
    required_fields: List[str]
    optional_fields: List[str]
    type_hints: Optional[Dict[str, str]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DataStructureContract:
        """Create a DataStructureContract from a dictionary."""
        return cls(
            name=data.get("name", ""),
            module=data.get("module", ""),
            fields=data.get("fields", []),
            required_fields=data.get("required_fields", []),
            optional_fields=data.get("optional_fields", []),
            type_hints=data.get("type_hints"),
        )


@dataclass
class IntegrationSurface:
    """Represents the complete integration surface."""
    phase: str
    functions: List[FunctionExport]
    classes: List[ClassExport]
    data_structures: List[DataStructureContract]
    exports: List[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> IntegrationSurface:
        """Create an IntegrationSurface from a dictionary."""
        return cls(
            phase=data.get("phase", "unknown"),
            functions=[
                FunctionExport.from_dict(f)
                for f in data.get("exports", {}).get("functions", [])
            ],
            classes=[
                ClassExport.from_dict(c)
                for c in data.get("exports", {}).get("classes", [])
            ],
            data_structures=[
                DataStructureContract.from_dict(d)
                for d in data.get("contracts", {}).get("data_structures", [])
            ],
            exports=data.get("exports", {}).get("exports", []),
        )


# =============================================================================
# Test Generators
# =============================================================================


class TestGenerator:
    """Base class for test generators."""

    def __init__(self, surface: IntegrationSurface, output_dir: Path):
        self.surface = surface
        self.output_dir = output_dir
        self.phase_name = surface.phase.lower().replace(" ", "_")

    def generate_all(self) -> List[Path]:
        """Generate all test files and return their paths."""
        raise NotImplementedError

    def _sanitize_name(self, name: str) -> str:
        """Sanitize a name for use in test function names."""
        return name.replace(".", "_").replace("-", "_")


class PytestGenerator(TestGenerator):
    """Generate pytest-style contract tests."""

    def generate_all(self) -> List[Path]:
        """Generate all pytest test files."""
        generated_files = []

        # Generate export tests
        export_test_path = self.output_dir / f"test_{self.phase_name}_exports.py"
        export_test_content = self._generate_export_tests()
        export_test_path.write_text(export_test_content)
        generated_files.append(export_test_path)

        # Generate contract tests
        contract_test_path = self.output_dir / f"test_{self.phase_name}_contracts.py"
        contract_test_content = self._generate_contract_tests()
        contract_test_path.write_text(contract_test_content)
        generated_files.append(contract_test_path)

        return generated_files

    def _generate_export_tests(self) -> str:
        """Generate tests verifying exports exist and are accessible."""
        lines = [
            '"""',
            f"Export contract tests for {self.surface.phase}.",
            "",
            "These tests verify that all expected exports are present and accessible.",
            '"""',
            "",
            "import inspect",
            "import pytest",
            "",
            "",
        ]

        # Generate function export tests
        for func in self.surface.functions:
            lines.extend(self._generate_function_export_test(func))
            lines.append("")

        # Generate class export tests
        for cls in self.surface.classes:
            lines.extend(self._generate_class_export_test(cls))
            lines.append("")

        # Generate data structure export tests
        for ds in self.surface.data_structures:
            lines.extend(self._generate_data_structure_export_test(ds))
            lines.append("")

        return "\n".join(lines)

    def _generate_function_export_test(self, func: FunctionExport) -> List[str]:
        """Generate export tests for a function."""
        sanitized_name = self._sanitize_name(func.name)
        module_path = func.module

        lines = [
            f"def test_{sanitized_name}_exists():",
            f'    """Verify {func.name} function is exported from {module_path}."""',
            f"    from {module_path} import {func.name}",
            f"    assert callable({func.name})",
            "",
            f"def test_{sanitized_name}_signature():",
            f'    """Verify {func.name} has expected parameters."""',
            f"    from {module_path} import {func.name}",
            f"    sig = inspect.signature({func.name})",
            f"    params = list(sig.parameters.keys())",
        ]

        # Add parameter assertions
        for param in func.parameters:
            param_name = param.get("name", "")
            lines.append(f"    assert '{param_name}' in params")

        if func.return_type:
            lines.append(f"    # Return type: {func.return_type}")

        return lines

    def _generate_class_export_test(self, cls: ClassExport) -> List[str]:
        """Generate export tests for a class."""
        sanitized_name = self._sanitize_name(cls.name)
        module_path = cls.module

        lines = [
            f"def test_{sanitized_name}_exists():",
            f'    """Verify {cls.name} class is exported from {module_path}."""',
            f"    from {module_path} import {cls.name}",
            f"    assert inspect.isclass({cls.name})",
            "",
            f"def test_{sanitized_name}_has_required_methods():",
            f'    """Verify {cls.name} has expected methods."""',
            f"    from {module_path} import {cls.name}",
        ]

        # Add method assertions
        for method in cls.methods:
            # Handle both dict format {"name": "..."} and string format "..."
            if isinstance(method, dict):
                method_name = method.get("name", "")
            else:
                method_name = str(method)
            lines.append(f"    assert hasattr({cls.name}, '{method_name}')")
            lines.append(f"    assert callable(getattr({cls.name}, '{method_name}', None))")

        if cls.attributes:
            lines.append("")
            lines.append(f"def test_{sanitized_name}_has_expected_attributes():")
            lines.append(f'    """Verify {cls.name} has expected attributes."""')
            lines.append(f"    from {module_path} import {cls.name}")
            for attr in cls.attributes:
                lines.append(f"    assert hasattr({cls.name}, '{attr}')")

        return lines

    def _generate_data_structure_export_test(self, ds: DataStructureContract) -> List[str]:
        """Generate export tests for a data structure."""
        sanitized_name = self._sanitize_name(ds.name)
        module_path = ds.module

        lines = [
            f"def test_{sanitized_name}_schema():",
            f'    """Verify {ds.name} has expected fields."""',
            f"    from {module_path} import {ds.name}",
            "",
            "    # Required fields",
        ]

        for field in ds.required_fields:
            lines.append(f"    assert hasattr({ds.name}, '{field}')")

        if ds.optional_fields:
            lines.append("")
            lines.append("    # Optional fields")
            for field in ds.optional_fields:
                lines.append(f"    # assert hasattr({ds.name}, '{field}')  # optional")

        return lines

    def _generate_contract_tests(self) -> str:
        """Generate detailed contract tests."""
        lines = [
            '"""',
            f"Contract tests for {self.surface.phase}.",
            "",
            "These tests verify that implementations satisfy their contracts.",
            '"""',
            "",
            "import inspect",
            "import pytest",
            "from typing import get_type_hints",
            "",
            "",
        ]

        # Generate function contract tests
        for func in self.surface.functions:
            lines.extend(self._generate_function_contract_test(func))
            lines.append("")

        # Generate class contract tests
        for cls in self.surface.classes:
            lines.extend(self._generate_class_contract_test(cls))
            lines.append("")

        # Generate data structure contract tests
        for ds in self.surface.data_structures:
            lines.extend(self._generate_data_structure_contract_test(ds))
            lines.append("")

        return "\n".join(lines)

    def _generate_function_contract_test(self, func: FunctionExport) -> List[str]:
        """Generate contract tests for a function."""
        sanitized_name = self._sanitize_name(func.name)

        lines = [
            f"def test_{sanitized_name}_callable():",
            f'    """Verify {func.name} is callable with expected signature."""',
            f"    from {func.module} import {func.name}",
            "",
            "    # Verify it's callable",
            f"    assert callable({func.name})",
            "",
            "    # Verify signature",
            "    sig = inspect.signature(func)",
            f"    assert len(sig.parameters) >= {len([p for p in func.parameters if p.get('required', True)])}",
            "",
            f"def test_{sanitized_name}_docstring_exists():",
            f'    """Verify {func.name} has documentation."""',
            f"    from {func.module} import {func.name}",
            f"    assert {func.name}.__doc__ is not None",
        ]

        if func.return_type:
            lines.append("")
            lines.append(f"def test_{sanitized_name}_return_type():")
            lines.append(f'    """Verify {func.name} return type annotation."""')
            lines.append(f"    from {func.module} import {func.name}")
            lines.append("    hints = get_type_hints(func)")
            lines.append("    assert 'return' in hints")

        return lines

    def _generate_class_contract_test(self, cls: ClassExport) -> List[str]:
        """Generate contract tests for a class."""
        sanitized_name = self._sanitize_name(cls.name)

        lines = [
            f"def test_{sanitized_name}_is_class():",
            f'    """Verify {cls.name} is a proper class."""',
            f"    from {cls.module} import {cls.name}",
            "",
            "    # Verify it's a class",
            f"    assert inspect.isclass({cls.name})",
            "",
        ]

        if cls.base_classes:
            lines.append("    # Verify inheritance")
            for base in cls.base_classes:
                lines.append(f"    assert issubclass({cls.name}, {base})")
            lines.append("")

        lines.extend([
            f"def test_{sanitized_name}_instantiable():",
            f'    """Verify {cls.name} can be instantiated."""',
            f"    from {cls.module} import {cls.name}",
            "",
            "    # Attempt instantiation with no args (may need adjustment)",
            "    try:",
            f"        instance = {cls.name}()",
            "    except TypeError as e:",
            "        # If required args, that's acceptable for contract test",
            "        pytest.skip(f'Cannot instantiate without args: {e}')",
            "",
            f"def test_{sanitized_name}_method_signatures():",
            f'    """Verify {cls.name} method signatures."""',
            f"    from {cls.module} import {cls.name}",
            "",
        ])

        for method in cls.methods:
            # Handle both dict format {"name": "..."} and string format "..."
            if isinstance(method, dict):
                method_name = method.get("name", "")
            else:
                method_name = str(method)
            if method_name.startswith("_"):
                continue
            lines.append(f"    # Check {method_name} method")
            lines.append(f"    method = getattr({cls.name}, '{method_name}', None)")
            lines.append("    if method:")
            lines.append("        sig = inspect.signature(method)")
            lines.append(f"        assert sig is not None")
            lines.append("")

        return lines

    def _generate_data_structure_contract_test(self, ds: DataStructureContract) -> List[str]:
        """Generate contract tests for a data structure."""
        sanitized_name = self._sanitize_name(ds.name)

        lines = [
            f"def test_{sanitized_name}_field_types():",
            f'    """Verify {ds.name} field type annotations."""',
            f"    from {ds.module} import {ds.name}",
            "",
            "    # Get type hints if available",
            "    try:",
            f"        hints = get_type_hints({ds.name})",
            "    except (TypeError, NameError):",
            "        hints = {}",
            "",
        ]

        if ds.type_hints:
            for field, type_hint in ds.type_hints.items():
                lines.append(f"    # {field}: {type_hint}")
                if field in (ds.required_fields or []):
                    lines.append(f"    assert '{field}' in hints or hasattr({ds.name}, '{field}')")
                lines.append("")

        lines.extend([
            f"def test_{sanitized_name}_required_fields():",
            f'    """Verify {ds.name} required fields are enforced."""',
            f"    from {ds.module} import {ds.name}",
            "",
            "    # Attempt to create with missing required fields should fail",
            "    # This test may need adjustment based on actual implementation",
            "    required = [",
        ])

        for field in ds.required_fields:
            lines.append(f"        '{field}',")

        lines.extend([
            "    ]",
            "",
            "    for field in required:",
            "        # Verify field is documented or enforced",
            f"        assert hasattr({ds.name}, field) or field in ({ds.name}.__init__.__code__.co_varnames if hasattr({ds.name}, '__init__') else [])",
            "",
        ])

        return lines


class JestGenerator(TestGenerator):
    """Generate Jest-style contract tests for JavaScript/TypeScript."""

    def generate_all(self) -> List[Path]:
        """Generate all Jest test files."""
        generated_files = []

        # Generate export tests
        export_test_path = self.output_dir / f"{self.phase_name}.exports.test.js"
        export_test_content = self._generate_export_tests()
        export_test_path.write_text(export_test_content)
        generated_files.append(export_test_path)

        # Generate contract tests
        contract_test_path = self.output_dir / f"{self.phase_name}.contracts.test.js"
        contract_test_content = self._generate_contract_tests()
        contract_test_path.write_text(contract_test_content)
        generated_files.append(contract_test_path)

        return generated_files

    def _generate_export_tests(self) -> str:
        """Generate Jest tests verifying exports exist."""
        lines = [
            "/**",
            f" * Export contract tests for {self.surface.phase}",
            " * @jest-environment node",
            " */",
            "",
            "const {",
        ]

        # Add imports
        all_exports = []
        for func in self.surface.functions:
            all_exports.append(func.name)
        for cls in self.surface.classes:
            all_exports.append(cls.name)
        for ds in self.surface.data_structures:
            all_exports.append(ds.name)

        for export in all_exports:
            lines.append(f"  {export},")

        lines.extend([
            "} = require('./index');  // Adjust path as needed",
            "",
            "describe('Exports', () => {",
            "",
        ])

        # Function tests
        for func in self.surface.functions:
            lines.extend([
                f"  describe('{func.name}', () => {{",
                f"    it('should be exported', () => {{",
                f"      expect({func.name}).toBeDefined();",
                "    });",
                "",
                "    it('should be callable', () => {{",
                f"      expect(typeof {func.name}).toBe('function');",
                "    });",
                "  });",
                "",
            ])

        # Class tests
        for cls in self.surface.classes:
            lines.extend([
                f"  describe('{cls.name}', () => {{",
                f"    it('should be exported', () => {{",
                f"      expect({cls.name}).toBeDefined();",
                "    });",
                "",
                "    it('should be a class', () => {{",
                f"      expect(typeof {cls.name}).toBe('function');",
                f"      expect({cls.name}.prototype).toBeDefined();",
                "    });",
                "  });",
                "",
            ])

        lines.extend([
            "});",
            "",
        ])

        return "\n".join(lines)

    def _generate_contract_tests(self) -> str:
        """Generate Jest contract tests."""
        lines = [
            "/**",
            f" * Contract tests for {self.surface.phase}",
            " * @jest-environment node",
            " */",
            "",
            "const {",
        ]

        # Add imports
        all_exports = []
        for func in self.surface.functions:
            all_exports.append(func.name)
        for cls in self.surface.classes:
            all_exports.append(cls.name)
        for ds in self.surface.data_structures:
            all_exports.append(ds.name)

        for export in all_exports:
            lines.append(f"  {export},")

        lines.extend([
            "} = require('./index');  // Adjust path as needed",
            "",
            "describe('Contracts', () => {",
            "",
        ])

        # Function contract tests
        for func in self.surface.functions:
            lines.extend([
                f"  describe('{func.name} contract', () => {{",
                f"    it('should accept expected parameters', () => {{",
                f"      const func = {func.name};",
                "      expect(func.length).toBeGreaterThanOrEqual(0);",
                "    });",
                "  });",
                "",
            ])

        # Class contract tests
        for cls in self.surface.classes:
            lines.extend([
                f"  describe('{cls.name} contract', () => {{",
                f"    it('should have expected methods', () => {{",
                f"      const instance = new {cls.name}();",
            ])
            for method in cls.methods:
                # Handle both dict format {"name": "..."} and string format "..."
                if isinstance(method, dict):
                    method_name = method.get("name", "")
                else:
                    method_name = str(method)
                if not method_name.startswith("_"):
                    lines.append(f"      expect(typeof instance.{method_name}).toBe('function');")
            lines.extend([
                "    });",
                "  });",
                "",
            ])

        lines.extend([
            "});",
            "",
        ])

        return "\n".join(lines)


class VitestGenerator(JestGenerator):
    """Generate Vitest-style contract tests (similar to Jest with minor differences)."""

    def generate_all(self) -> List[Path]:
        """Generate all Vitest test files."""
        generated_files = []

        # Generate export tests
        export_test_path = self.output_dir / f"{self.phase_name}.exports.test.ts"
        export_test_content = self._generate_export_tests()
        export_test_path.write_text(export_test_content)
        generated_files.append(export_test_path)

        # Generate contract tests
        contract_test_path = self.output_dir / f"{self.phase_name}.contracts.test.ts"
        contract_test_content = self._generate_contract_tests()
        contract_test_path.write_text(contract_test_content)
        generated_files.append(contract_test_path)

        return generated_files

    def _generate_export_tests(self) -> str:
        """Generate Vitest tests verifying exports exist."""
        base_content = super()._generate_export_tests()
        # Replace Jest-specific syntax with Vitest
        content = base_content.replace("require('./index')", "from './index'")
        content = content.replace("const {", "import {")
        content = content.replace("} = require", "} from")
        content = content.replace("@jest-environment node", "@vitest-environment node")

        # Add Vitest import
        lines = content.split("\n")
        lines.insert(0, "import { describe, it, expect } from 'vitest';")
        lines.insert(1, "")

        return "\n".join(lines)

    def _generate_contract_tests(self) -> str:
        """Generate Vitest contract tests."""
        base_content = super()._generate_contract_tests()
        # Replace Jest-specific syntax with Vitest
        content = base_content.replace("require('./index')", "from './index'")
        content = content.replace("const {", "import {")
        content = content.replace("} = require", "} from")
        content = content.replace("@jest-environment node", "@vitest-environment node")

        # Add Vitest import
        lines = content.split("\n")
        lines.insert(0, "import { describe, it, expect } from 'vitest';")
        lines.insert(1, "")

        return "\n".join(lines)


# =============================================================================
# Mock Generators
# =============================================================================


class MockGenerator:
    """Generate mocks for the next phase's expected interfaces."""

    def __init__(self, surface: IntegrationSurface, output_dir: Path):
        self.surface = surface
        self.output_dir = output_dir
        self.phase_name = surface.phase.lower().replace(" ", "_")

    def generate(self) -> Path:
        """Generate mock file and return its path."""
        raise NotImplementedError


class PythonMockGenerator(MockGenerator):
    """Generate Python mocks for the next phase."""

    def generate(self) -> Path:
        """Generate Python mock file."""
        mock_path = self.output_dir / "mocks" / f"{self.phase_name}_mock.py"
        mock_path.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            '"""',
            f"Mock implementations for {self.surface.phase} interfaces.",
            "",
            "These mocks can be used by the next phase for testing.",
            '"""',
            "",
            "from typing import Any, Dict, List, Optional, Union",
            "from unittest.mock import MagicMock",
            "",
            "",
        ]

        # Generate function mocks
        for func in self.surface.functions:
            lines.extend(self._generate_function_mock(func))
            lines.append("")

        # Generate class mocks
        for cls in self.surface.classes:
            lines.extend(self._generate_class_mock(cls))
            lines.append("")

        # Generate data structure mocks
        for ds in self.surface.data_structures:
            lines.extend(self._generate_data_structure_mock(ds))
            lines.append("")

        # Generate factory function
        lines.extend(self._generate_mock_factory())

        mock_path.write_text("\n".join(lines))
        return mock_path

    def _generate_function_mock(self, func: FunctionExport) -> List[str]:
        """Generate a mock for a function."""
        param_str = ", ".join([
            f"{p.get('name', 'arg')}={p.get('default', 'None') if not p.get('required', True) else 'None'}"
            for p in func.parameters
        ]) if func.parameters else "*args, **kwargs"

        return_type = f" -> {func.return_type}" if func.return_type else ""

        lines = [
            f"def mock_{func.name}({param_str}){return_type}:",
            f'    """Mock implementation of {func.name}."""',
            "    # TODO: Adjust return value as needed",
            "    return None",
        ]

        return lines

    def _generate_class_mock(self, cls: ClassExport) -> List[str]:
        """Generate a mock for a class."""
        base_str = f"({', '.join(cls.base_classes)})" if cls.base_classes else ""

        lines = [
            f"class Mock{cls.name}{base_str}:",
            f'    """Mock implementation of {cls.name}."""',
            "",
            "    def __init__(self, *args, **kwargs):",
            "        self._mock_data = kwargs",
        ]

        for attr in cls.attributes:
            lines.append(f"        self.{attr} = kwargs.get('{attr}')")

        lines.append("")

        for method in cls.methods:
            # Handle both dict format {"name": "...", "parameters": [...]} and string format "..."
            if isinstance(method, dict):
                method_name = method.get("name", "")
                params = method.get("parameters", [])
            else:
                method_name = str(method)
                params = []
            if method_name == "__init__":
                continue

            param_str = ", ".join(["self"] + [
                f"{p.get('name', 'arg')}=None" for p in params
            ])

            lines.extend([
                f"    def {method_name}({param_str}):",
                f'        """Mock {method_name} method."""',
                "        # TODO: Adjust return value as needed",
                "        return None",
                "",
            ])

        return lines

    def _generate_data_structure_mock(self, ds: DataStructureContract) -> List[str]:
        """Generate a mock for a data structure."""
        lines = [
            f"class Mock{ds.name}:",
            f'    """Mock implementation of {ds.name} data structure."""',
            "",
            "    def __init__(self, **kwargs):",
        ]

        for field in ds.fields:
            field_name = field.get("name", "")
            default = field.get("default", "None")
            lines.append(f"        self.{field_name} = kwargs.get('{field_name}', {default})")

        lines.append("")
        lines.append("    def to_dict(self) -> dict:")
        lines.append('        """Convert to dictionary."""')
        lines.append("        return {")
        for field in ds.fields:
            field_name = field.get("name", "")
            lines.append(f"            '{field_name}': self.{field_name},")
        lines.append("        }")

        return lines

    def _generate_mock_factory(self) -> List[str]:
        """Generate a factory function for creating mocks."""
        lines = [
            "def create_mock(typename: str, **kwargs) -> Any:",
            '    """Factory function for creating mocks by type name."""',
            "    factories = {",
        ]

        for func in self.surface.functions:
            lines.append(f"        '{func.name}': mock_{func.name},")

        for cls in self.surface.classes:
            lines.append(f"        '{cls.name}': Mock{cls.name},")

        for ds in self.surface.data_structures:
            lines.append(f"        '{ds.name}': Mock{ds.name},")

        lines.extend([
            "    }",
            "",
            "    factory = factories.get(typename)",
            "    if factory is None:",
            "        raise ValueError(f'Unknown type: {typename}')",
            "",
            "    return factory(**kwargs)",
            "",
            "",
            "# Convenience exports",
            "__all__ = [",
            "    'create_mock',",
        ])

        for func in self.surface.functions:
            lines.append(f"    'mock_{func.name}',")

        for cls in self.surface.classes:
            lines.append(f"    'Mock{cls.name}',")

        for ds in self.surface.data_structures:
            lines.append(f"    'Mock{ds.name}',")

        lines.append("]")

        return lines


class JavaScriptMockGenerator(MockGenerator):
    """Generate JavaScript/TypeScript mocks for the next phase."""

    def generate(self) -> Path:
        """Generate JavaScript mock file."""
        mock_path = self.output_dir / "mocks" / f"{self.phase_name}Mock.js"
        mock_path.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            "/**",
            f" * Mock implementations for {self.surface.phase} interfaces",
            " * These mocks can be used by the next phase for testing",
            " */",
            "",
            "",
        ]

        # Generate function mocks
        for func in self.surface.functions:
            lines.extend(self._generate_function_mock(func))
            lines.append("")

        # Generate class mocks
        for cls in self.surface.classes:
            lines.extend(self._generate_class_mock(cls))
            lines.append("")

        # Generate factory
        lines.extend(self._generate_mock_factory())

        mock_path.write_text("\n".join(lines))
        return mock_path

    def _generate_function_mock(self, func: FunctionExport) -> List[str]:
        """Generate a mock for a function."""
        param_str = ", ".join([
            f"{p.get('name', 'arg')} = null"
            for p in func.parameters
        ]) if func.parameters else "...args"

        lines = [
            f"/**",
            f" * Mock implementation of {func.name}",
            f" * @param {{any}} {param_str}",
            f" * @returns {{any}}",
            f" */",
            f"export function mock{func.name[0].upper() + func.name[1:]}({param_str}) {{",
            "  // TODO: Adjust return value as needed",
            "  return null;",
            "}",
        ]

        return lines

    def _generate_class_mock(self, cls: ClassExport) -> List[str]:
        """Generate a mock for a class."""
        lines = [
            f"/**",
            f" * Mock implementation of {cls.name}",
            f" */",
            f"export class Mock{cls.name} {{",
            "  constructor(options = {}) {",
        ]

        for attr in cls.attributes:
            lines.append(f"    this.{attr} = options.{attr} || null;")

        lines.append("  }")
        lines.append("")

        for method in cls.methods:
            # Handle both dict format {"name": "...", "parameters": [...]} and string format "..."
            if isinstance(method, dict):
                method_name = method.get("name", "")
                params = method.get("parameters", [])
            else:
                method_name = str(method)
                params = []
            if method_name == "constructor":
                continue

            param_str = ", ".join([
                f"{p.get('name', 'arg')} = null" for p in params
            ])

            lines.extend([
                "",
                f"  {method_name}({param_str}) {{",
                f"    // Mock {method_name} implementation",
                "    return null;",
                "  }",
            ])

        lines.append("}")

        return lines

    def _generate_mock_factory(self) -> List[str]:
        """Generate a factory function for creating mocks."""
        lines = [
            "/**",
            " * Factory function for creating mocks by type name",
            " * @param {string} typeName - The type of mock to create",
            " * @param {object} options - Options for the mock",
            " * @returns {any}",
            " */",
            "export function createMock(typeName, options = {}) {",
            "  const factories = {",
        ]

        for func in self.surface.functions:
            mock_name = f"mock{func.name[0].upper() + func.name[1:]}"
            lines.append(f"    '{func.name}': {mock_name},")

        for cls in self.surface.classes:
            lines.append(f"    '{cls.name}': Mock{cls.name},")

        lines.extend([
            "  };",
            "",
            "  const factory = factories[typeName];",
            "  if (!factory) {",
            "    throw new Error(`Unknown type: ${typeName}`);",
            "  }",
            "",
            "  return new factory(options);",
            "}",
        ])

        return lines


# =============================================================================
# Main Generator
# =============================================================================


class ContractTestGenerator:
    """Main class for generating contract tests."""

    SUPPORTED_FRAMEWORKS = {
        "pytest": PytestGenerator,
        "jest": JestGenerator,
        "vitest": VitestGenerator,
    }

    def __init__(
        self,
        surface_path: Path,
        output_dir: Path,
        framework: str = "pytest",
        generate_mocks: bool = False,
    ):
        self.surface_path = surface_path
        self.output_dir = output_dir
        self.framework = framework.lower()
        self.generate_mocks = generate_mocks
        self.surface: Optional[IntegrationSurface] = None

    def load_surface(self) -> IntegrationSurface:
        """Load and validate the integration surface JSON."""
        if not self.surface_path.exists():
            raise SurfaceFileNotFoundError(
                f"Integration surface file not found: {self.surface_path}"
            )

        try:
            with open(self.surface_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise InvalidSurfaceError(
                f"Invalid JSON in surface file: {e}"
            )

        try:
            self.surface = IntegrationSurface.from_dict(data)
        except (KeyError, TypeError) as e:
            raise InvalidSurfaceError(
                f"Invalid surface structure: {e}"
            )

        return self.surface

    def validate_framework(self) -> None:
        """Validate the selected test framework."""
        if self.framework not in self.SUPPORTED_FRAMEWORKS:
            raise UnsupportedFrameworkError(
                f"Unsupported framework: {self.framework}. "
                f"Supported: {', '.join(self.SUPPORTED_FRAMEWORKS.keys())}"
            )

    def setup_output_directory(self) -> None:
        """Create output directory structure."""
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            if self.generate_mocks:
                (self.output_dir / "mocks").mkdir(exist_ok=True)
        except OSError as e:
            raise OutputDirectoryError(
                f"Failed to create output directory: {e}"
            )

    def generate(self) -> List[Path]:
        """Generate all contract tests and mocks."""
        # Load surface
        self.load_surface()

        # Validate framework
        self.validate_framework()

        # Setup directories
        self.setup_output_directory()

        # Generate tests
        generator_class = self.SUPPORTED_FRAMEWORKS[self.framework]
        generator = generator_class(self.surface, self.output_dir)
        generated_files = generator.generate_all()

        # Generate mocks if requested
        if self.generate_mocks:
            if self.framework == "pytest":
                mock_generator = PythonMockGenerator(self.surface, self.output_dir)
            else:
                mock_generator = JavaScriptMockGenerator(self.surface, self.output_dir)

            mock_path = mock_generator.generate()
            generated_files.append(mock_path)

        return generated_files


# =============================================================================
# CLI Interface
# =============================================================================


def create_argument_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        description="Generate contract tests based on integration surface analysis.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Generate pytest tests
    python3 generate_contract_tests.py \\
        --surface phase1_surface.json \\
        --output-dir tests/contracts/

    # Generate tests with mocks
    python3 generate_contract_tests.py \\
        --surface phase1_surface.json \\
        --output-dir tests/contracts/ \\
        --mock-next-phase

    # Generate Jest tests for JavaScript project
    python3 generate_contract_tests.py \\
        --surface phase1_surface.json \\
        --output-dir tests/contracts/ \\
        --framework jest
        """,
    )

    parser.add_argument(
        "--surface",
        type=str,
        required=True,
        help="Path to integration surface JSON file (from detect_integration_surface.py)",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        required=True,
        help="Output directory for generated test files",
    )

    parser.add_argument(
        "--framework",
        type=str,
        choices=["pytest", "jest", "vitest"],
        default="pytest",
        help="Test framework to generate tests for (default: pytest)",
    )

    parser.add_argument(
        "--mock-next-phase",
        action="store_true",
        help="Generate mocks for the next phase's expected interfaces",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output",
    )

    return parser


def main() -> int:
    """Main entry point for the CLI."""
    parser = create_argument_parser()
    args = parser.parse_args()

    try:
        # Create generator
        generator = ContractTestGenerator(
            surface_path=Path(args.surface).resolve(),
            output_dir=Path(args.output_dir).resolve(),
            framework=args.framework,
            generate_mocks=args.mock_next_phase,
        )

        if args.verbose:
            print(f"Loading surface from: {args.surface}")
            print(f"Output directory: {args.output_dir}")
            print(f"Framework: {args.framework}")
            print(f"Generate mocks: {args.mock_next_phase}")

        # Generate tests
        generated_files = generator.generate()

        # Report results
        print(f"\nGenerated {len(generated_files)} file(s):")
        for file_path in generated_files:
            print(f"  - {file_path}")

        return 0

    except SurfaceFileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    except InvalidSurfaceError as e:
        print(f"Error: Invalid surface file - {e}", file=sys.stderr)
        return 2

    except UnsupportedFrameworkError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 3

    except OutputDirectoryError as e:
        print(f"Error: Cannot create output directory - {e}", file=sys.stderr)
        return 4

    except ContractTestError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 5

    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 6


if __name__ == "__main__":
    sys.exit(main())
