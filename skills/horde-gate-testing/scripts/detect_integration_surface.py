#!/usr/bin/env python3
"""
Detect Integration Surface

Analyzes completed phase code to identify the integration surface - what APIs,
functions, classes, and contracts it exports for the next phase to consume.

Usage:
    python3 detect_integration_surface.py \
        --phase "Phase 1: Agent Setup" \
        --paths "src/agent/" "src/config/" \
        --output "phase1_surface.json"
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TextIO


# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class FunctionExport:
    """Represents a function export."""
    name: str
    file: str
    signature: str
    docstring: str | None = None
    is_async: bool = False
    decorators: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "file": self.file,
            "signature": self.signature,
            "docstring": self.docstring,
            "is_async": self.is_async,
            "decorators": self.decorators,
        }


@dataclass
class ClassExport:
    """Represents a class export."""
    name: str
    file: str
    methods: list[str] = field(default_factory=list)
    properties: list[str] = field(default_factory=list)
    base_classes: list[str] = field(default_factory=list)
    docstring: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "file": self.file,
            "methods": self.methods,
            "properties": self.properties,
            "base_classes": self.base_classes,
            "docstring": self.docstring,
        }


@dataclass
class ConstantExport:
    """Represents a constant export."""
    name: str
    file: str
    type: str | None = None
    value: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "file": self.file,
            "type": self.type,
            "value": self.value,
        }


@dataclass
class DataStructureContract:
    """Represents a data structure contract."""
    name: str
    schema: dict[str, Any] | None = None
    file: str | None = None
    type: str = "unknown"  # dataclass, TypedDict, Pydantic, interface, etc.

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "schema": self.schema,
            "file": self.file,
            "type": self.type,
        }


@dataclass
class IntegrationSurface:
    """Complete integration surface for a phase."""
    phase: str
    analyzed_at: str
    exports: dict[str, list] = field(default_factory=dict)
    contracts: dict[str, list] = field(default_factory=dict)
    dependencies: dict[str, list[str]] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.exports:
            self.exports = {
                "functions": [],
                "classes": [],
                "constants": [],
            }
        if not self.contracts:
            self.contracts = {
                "data_structures": [],
            }
        if not self.dependencies:
            self.dependencies = {
                "external": [],
                "internal": [],
            }

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase,
            "analyzed_at": self.analyzed_at,
            "exports": {
                "functions": [f.to_dict() for f in self.exports.get("functions", [])],
                "classes": [c.to_dict() for c in self.exports.get("classes", [])],
                "constants": [c.to_dict() for c in self.exports.get("constants", [])],
            },
            "contracts": {
                "data_structures": [d.to_dict() for d in self.contracts.get("data_structures", [])],
            },
            "dependencies": self.dependencies,
            "errors": self.errors,
        }


# =============================================================================
# Python Parser
# =============================================================================

class PythonSurfaceExtractor(ast.NodeVisitor):
    """Extracts integration surface from Python source files."""

    def __init__(self, file_path: str, source: str):
        self.file_path = file_path
        self.source = source
        self.functions: list[FunctionExport] = []
        self.classes: list[ClassExport] = []
        self.constants: list[ConstantExport] = []
        self.data_structures: list[DataStructureContract] = []
        self.dependencies: dict[str, set[str]] = {
            "external": set(),
            "internal": set(),
        }

    def extract(self) -> tuple[list, list, list, list, dict]:
        """Extract all surface elements from the source."""
        try:
            tree = ast.parse(self.source)
            self.visit(tree)
        except SyntaxError as e:
            raise ParseError(f"Syntax error in {self.file_path}: {e}") from e

        return (
            self.functions,
            self.classes,
            self.constants,
            self.data_structures,
            self.dependencies,
        )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._process_function(node, is_async=False)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._process_function(node, is_async=True)
        self.generic_visit(node)

    def _process_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef, is_async: bool) -> None:
        """Process a function definition."""
        # Skip private functions (single underscore prefix)
        if node.name.startswith("_") and not node.name.startswith("__"):
            return

        # Skip dunder methods
        if node.name.startswith("__") and node.name.endswith("__"):
            return

        signature = self._get_function_signature(node, is_async)
        docstring = ast.get_docstring(node)
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]

        func_export = FunctionExport(
            name=node.name,
            file=self.file_path,
            signature=signature,
            docstring=docstring,
            is_async=is_async,
            decorators=decorators,
        )
        self.functions.append(func_export)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Process a class definition."""
        # Skip private classes
        if node.name.startswith("_") and not node.name.startswith("__"):
            self.generic_visit(node)
            return

        methods = []
        properties = []

        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Skip private methods
                if not item.name.startswith("_") or item.name.startswith("__"):
                    methods.append(item.name)
            elif isinstance(item, ast.AnnAssign):
                # Class-level annotated attributes (often properties)
                if isinstance(item.target, ast.Name):
                    properties.append(item.target.id)

        base_classes = [
            self._get_base_class_name(base)
            for base in node.bases
        ]

        docstring = ast.get_docstring(node)

        class_export = ClassExport(
            name=node.name,
            file=self.file_path,
            methods=methods,
            properties=properties,
            base_classes=base_classes,
            docstring=docstring,
        )
        self.classes.append(class_export)

        # Check if this is a data structure (dataclass, TypedDict, Pydantic, etc.)
        self._check_data_structure(node, base_classes)

        self.generic_visit(node)

    def _check_data_structure(self, node: ast.ClassDef, base_classes: list[str]) -> None:
        """Check if a class is a data structure and extract its schema."""
        is_dataclass = any("dataclass" in base for base in base_classes)
        is_typeddict = any("TypedDict" in base for base in base_classes)
        is_pydantic = any("BaseModel" in base or "pydantic" in base.lower() for base in base_classes)

        schema = {}
        for item in node.body:
            if isinstance(item, ast.AnnAssign):
                if isinstance(item.target, ast.Name):
                    schema[item.target.id] = self._get_annotation_type(item.annotation)
            elif isinstance(item, ast.FunctionDef):
                if item.name == "__init__":
                    # Extract from __init__ annotations
                    for stmt in item.body:
                        if isinstance(stmt, ast.AnnAssign):
                            if isinstance(stmt.target, ast.Attribute):
                                attr_name = stmt.target.attr
                                schema[attr_name] = self._get_annotation_type(stmt.annotation)

        if is_dataclass or is_typeddict or is_pydantic or schema:
            ds_type = "dataclass" if is_dataclass else "TypedDict" if is_typeddict else "pydantic" if is_pydantic else "class"
            data_structure = DataStructureContract(
                name=node.name,
                schema=schema if schema else None,
                file=self.file_path,
                type=ds_type,
            )
            self.data_structures.append(data_structure)

    def visit_Import(self, node: ast.Import) -> None:
        """Process import statements."""
        for alias in node.names:
            self._categorize_import(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Process from-import statements."""
        if node.module:
            self._categorize_import(node.module)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Process annotated assignments (module-level constants)."""
        if isinstance(node.target, ast.Name):
            name = node.target.id
            # Check if it's a constant (ALL_CAPS convention)
            if name.isupper():
                type_hint = self._get_annotation_type(node.annotation)
                value = None
                if node.value:
                    value = self._get_value_repr(node.value)

                constant = ConstantExport(
                    name=name,
                    file=self.file_path,
                    type=type_hint,
                    value=value,
                )
                self.constants.append(constant)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Process assignments (module-level constants)."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                name = target.id
                # Check if it's a constant (ALL_CAPS convention)
                if name.isupper():
                    value = self._get_value_repr(node.value)
                    constant = ConstantExport(
                        name=name,
                        file=self.file_path,
                        value=value,
                    )
                    self.constants.append(constant)
        self.generic_visit(node)

    def _get_function_signature(self, node: ast.FunctionDef | ast.AsyncFunctionDef, is_async: bool) -> str:
        """Reconstruct function signature from AST."""
        args_parts = []

        # Process arguments
        args = node.args

        # Positional-only args (Python 3.8+)
        if hasattr(args, 'posonlyargs'):
            for arg in args.posonlyargs:
                args_parts.append(self._format_arg(arg))
            if args.posonlyargs:
                args_parts.append("/")

        # Regular args
        for arg in args.args:
            args_parts.append(self._format_arg(arg))

        # Vararg (*args)
        if args.vararg:
            args_parts.append(f"*{args.vararg.arg}")

        # Keyword-only args
        if args.kwonlyargs:
            if not args.vararg:
                args_parts.append("*")
            for arg in args.kwonlyargs:
                args_parts.append(self._format_arg(arg))

        # Kwarg (**kwargs)
        if args.kwarg:
            args_parts.append(f"**{args.kwarg.arg}")

        # Return annotation
        return_annotation = ""
        if node.returns:
            return_annotation = f" -> {self._get_annotation_type(node.returns)}"

        async_prefix = "async " if is_async else ""
        return f"{async_prefix}def {node.name}({', '.join(args_parts)}){return_annotation}"

    def _format_arg(self, arg: ast.arg) -> str:
        """Format a single argument."""
        result = arg.arg
        if arg.annotation:
            result += f": {self._get_annotation_type(arg.annotation)}"
        return result

    def _get_annotation_type(self, annotation: ast.AST | None) -> str:
        """Get string representation of a type annotation."""
        if annotation is None:
            return "Any"

        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return repr(annotation.value)
        elif isinstance(annotation, ast.Subscript):
            value = self._get_annotation_type(annotation.value)
            slice_val = self._get_annotation_type(annotation.slice)
            return f"{value}[{slice_val}]"
        elif isinstance(annotation, ast.Attribute):
            return f"{self._get_annotation_type(annotation.value)}.{annotation.attr}"
        elif isinstance(annotation, ast.List):
            elements = [self._get_annotation_type(e) for e in annotation.elts]
            return f"[{', '.join(elements)}]"
        elif isinstance(annotation, ast.Tuple):
            elements = [self._get_annotation_type(e) for e in annotation.elts]
            return f"({', '.join(elements)})"
        elif isinstance(annotation, ast.BinOp):
            if isinstance(annotation.op, ast.BitOr):
                left = self._get_annotation_type(annotation.left)
                right = self._get_annotation_type(annotation.right)
                return f"{left} | {right}"
        elif isinstance(annotation, ast.NameConstant):  # Python < 3.8
            return str(annotation.value)

        return "Any"

    def _get_decorator_name(self, decorator: ast.AST) -> str:
        """Get string representation of a decorator."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{self._get_annotation_type(decorator.value)}.{decorator.attr}"
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                return f"{self._get_annotation_type(decorator.func.value)}.{decorator.func.attr}"
        return "unknown"

    def _get_base_class_name(self, base: ast.AST) -> str:
        """Get string representation of a base class."""
        return self._get_annotation_type(base)

    def _get_value_repr(self, value: ast.AST) -> str:
        """Get string representation of a value."""
        if isinstance(value, ast.Constant):
            return repr(value.value)
        elif isinstance(value, ast.Name):
            return value.id
        elif isinstance(value, ast.List):
            return "[...]"
        elif isinstance(value, ast.Dict):
            return "{...}"
        elif isinstance(value, ast.Tuple):
            return "(...)"
        elif isinstance(value, ast.Call):
            if isinstance(value.func, ast.Name):
                return f"{value.func.id}(...)"
        return "..."

    def _categorize_import(self, module: str) -> None:
        """Categorize an import as external or internal."""
        # Standard library modules
        stdlib_modules = {
            "abc", "argparse", "ast", "asyncio", "base64", "collections",
            "contextlib", "copy", "csv", "dataclasses", "datetime", "decimal",
            "enum", "functools", "hashlib", "importlib", "inspect", "io",
            "itertools", "json", "logging", "math", "os", "pathlib",
            "pickle", "random", "re", "shutil", "socket", "sqlite3",
            "string", "subprocess", "sys", "tempfile", "textwrap", "threading",
            "time", "traceback", "typing", "unittest", "urllib", "uuid",
            "warnings", "xml", "zipfile",
        }

        top_level = module.split(".")[0]

        if top_level in stdlib_modules:
            return  # Skip standard library

        # Check if it's a local/internal import
        if top_level.startswith(".") or top_level.startswith("src"):
            self.dependencies["internal"].add(module)
        else:
            self.dependencies["external"].add(top_level)


class ParseError(Exception):
    """Raised when parsing fails."""
    pass


# =============================================================================
# TypeScript Parser
# =============================================================================

class TypeScriptSurfaceExtractor:
    """Extracts integration surface from TypeScript source files."""

    # Regex patterns for TypeScript
    EXPORT_FUNCTION_PATTERN = re.compile(
        r'export\s+(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)(?:\s*:\s*([^\{;]+))?',
        re.MULTILINE
    )
    EXPORT_CONST_PATTERN = re.compile(
        r'export\s+const\s+(\w+)\s*:\s*([^=]+)=\s*([^;]+);?',
        re.MULTILINE
    )
    EXPORT_CLASS_PATTERN = re.compile(
        r'export\s+(?:abstract\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([^{]+))?',
        re.MULTILINE
    )
    EXPORT_INTERFACE_PATTERN = re.compile(
        r'export\s+interface\s+(\w+)(?:\s+extends\s+([^{]+))?\s*\{([^}]+)\}',
        re.MULTILINE
    )
    EXPORT_TYPE_PATTERN = re.compile(
        r'export\s+type\s+(\w+)\s*=\s*([^;]+);?',
        re.MULTILINE
    )
    METHOD_PATTERN = re.compile(
        r'(?:public|private|protected)?\s*(?:async\s+)?(\w+)\s*\(([^)]*)\)(?:\s*:\s*([^\{;]+))?',
        re.MULTILINE
    )
    IMPORT_PATTERN = re.compile(
        r'import\s+(?:(?:\{[^}]*\}|\*\s+as\s+\w+|\w+)\s+from\s+)?["\']([^"\']+)["\'];?',
        re.MULTILINE
    )

    def __init__(self, file_path: str, source: str):
        self.file_path = file_path
        self.source = source
        self.functions: list[FunctionExport] = []
        self.classes: list[ClassExport] = []
        self.constants: list[ConstantExport] = []
        self.data_structures: list[DataStructureContract] = []
        self.dependencies: dict[str, set[str]] = {
            "external": set(),
            "internal": set(),
        }

    def extract(self) -> tuple[list, list, list, list, dict]:
        """Extract all surface elements from the source."""
        self._extract_functions()
        self._extract_classes()
        self._extract_constants()
        self._extract_interfaces()
        self._extract_types()
        self._extract_imports()

        return (
            self.functions,
            self.classes,
            self.constants,
            self.data_structures,
            self.dependencies,
        )

    def _extract_functions(self) -> None:
        """Extract exported functions."""
        for match in self.EXPORT_FUNCTION_PATTERN.finditer(self.source):
            name = match.group(1)
            params = match.group(2).strip()
            return_type = match.group(3).strip() if match.group(3) else None

            is_async = "async" in match.group(0)
            signature = f"{'async ' if is_async else ''}function {name}({params})"
            if return_type:
                signature += f": {return_type}"

            func = FunctionExport(
                name=name,
                file=self.file_path,
                signature=signature,
                is_async=is_async,
            )
            self.functions.append(func)

    def _extract_classes(self) -> None:
        """Extract exported classes."""
        for match in self.EXPORT_CLASS_PATTERN.finditer(self.source):
            name = match.group(1)
            base_class = match.group(2)
            implements = match.group(3)

            # Find the class body
            start = match.end()
            brace_count = 1
            end = start
            for i, char in enumerate(self.source[start:], start):
                if char == "{":
                    brace_count += 1
                elif char == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        end = i
                        break

            class_body = self.source[start:end]

            # Extract methods
            methods = []
            for method_match in self.METHOD_PATTERN.finditer(class_body):
                method_name = method_match.group(1)
                if not method_name.startswith("_"):
                    methods.append(method_name)

            base_classes = []
            if base_class:
                base_classes.append(base_class.strip())
            if implements:
                base_classes.extend([i.strip() for i in implements.split(",")])

            class_export = ClassExport(
                name=name,
                file=self.file_path,
                methods=methods,
                base_classes=base_classes,
            )
            self.classes.append(class_export)

    def _extract_constants(self) -> None:
        """Extract exported constants."""
        for match in self.EXPORT_CONST_PATTERN.finditer(self.source):
            name = match.group(1)
            type_hint = match.group(2).strip()
            value = match.group(3).strip()

            constant = ConstantExport(
                name=name,
                file=self.file_path,
                type=type_hint,
                value=value,
            )
            self.constants.append(constant)

    def _extract_interfaces(self) -> None:
        """Extract exported interfaces."""
        for match in self.EXPORT_INTERFACE_PATTERN.finditer(self.source):
            name = match.group(1)
            extends = match.group(2)
            body = match.group(3)

            schema = {}
            for line in body.split(";"):
                line = line.strip()
                if ":" in line:
                    parts = line.split(":", 1)
                    field_name = parts[0].strip()
                    field_type = parts[1].strip()
                    schema[field_name] = field_type

            ds = DataStructureContract(
                name=name,
                schema=schema if schema else None,
                file=self.file_path,
                type="interface",
            )
            self.data_structures.append(ds)

    def _extract_types(self) -> None:
        """Extract exported type aliases."""
        for match in self.EXPORT_TYPE_PATTERN.finditer(self.source):
            name = match.group(1)
            definition = match.group(2).strip()

            ds = DataStructureContract(
                name=name,
                schema={"definition": definition},
                file=self.file_path,
                type="type_alias",
            )
            self.data_structures.append(ds)

    def _extract_imports(self) -> None:
        """Extract and categorize imports."""
        for match in self.IMPORT_PATTERN.finditer(self.source):
            module = match.group(1)

            if module.startswith("."):
                self.dependencies["internal"].add(module)
            elif not module.startswith("node:"):
                # External package
                top_level = module.split("/")[0]
                self.dependencies["external"].add(top_level)


# =============================================================================
# Generic Parser
# =============================================================================

class GenericSurfaceExtractor:
    """Generic extractor for unsupported file types - does basic pattern matching."""

    FUNCTION_PATTERN = re.compile(
        r'(?:function|def|func)\s+(\w+)\s*\(([^)]*)\)',
        re.MULTILINE
    )
    CLASS_PATTERN = re.compile(
        r'(?:class|struct|interface)\s+(\w+)',
        re.MULTILINE
    )
    CONSTANT_PATTERN = re.compile(
        r'(?:const|let|var|final)\s+([A-Z_][A-Z_0-9]*)\s*=',
        re.MULTILINE
    )

    def __init__(self, file_path: str, source: str):
        self.file_path = file_path
        self.source = source
        self.functions: list[FunctionExport] = []
        self.classes: list[ClassExport] = []
        self.constants: list[ConstantExport] = []
        self.data_structures: list[DataStructureContract] = []
        self.dependencies: dict[str, set[str]] = {
            "external": set(),
            "internal": set(),
        }

    def extract(self) -> tuple[list, list, list, list, dict]:
        """Extract basic surface elements using regex."""
        self._extract_functions()
        self._extract_classes()
        self._extract_constants()

        return (
            self.functions,
            self.classes,
            self.constants,
            self.data_structures,
            self.dependencies,
        )

    def _extract_functions(self) -> None:
        """Extract function definitions."""
        for match in self.FUNCTION_PATTERN.finditer(self.source):
            name = match.group(1)
            params = match.group(2).strip()

            func = FunctionExport(
                name=name,
                file=self.file_path,
                signature=f"function {name}({params})",
            )
            self.functions.append(func)

    def _extract_classes(self) -> None:
        """Extract class definitions."""
        for match in self.CLASS_PATTERN.finditer(self.source):
            name = match.group(1)

            class_export = ClassExport(
                name=name,
                file=self.file_path,
            )
            self.classes.append(class_export)

    def _extract_constants(self) -> None:
        """Extract constant definitions."""
        for match in self.CONSTANT_PATTERN.finditer(self.source):
            name = match.group(1)

            constant = ConstantExport(
                name=name,
                file=self.file_path,
            )
            self.constants.append(constant)


# =============================================================================
# Main Analyzer
# =============================================================================

def get_extractor(file_path: str, source: str) -> PythonSurfaceExtractor | TypeScriptSurfaceExtractor | GenericSurfaceExtractor:
    """Get the appropriate extractor for a file."""
    ext = Path(file_path).suffix.lower()

    if ext == ".py":
        return PythonSurfaceExtractor(file_path, source)
    elif ext in (".ts", ".tsx", ".js", ".jsx"):
        return TypeScriptSurfaceExtractor(file_path, source)
    else:
        return GenericSurfaceExtractor(file_path, source)


def analyze_file(file_path: str) -> tuple[list, list, list, list, dict, list[str]]:
    """Analyze a single file and return its surface elements."""
    errors: list[str] = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
    except UnicodeDecodeError:
        # Try with different encoding
        try:
            with open(file_path, "r", encoding="latin-1") as f:
                source = f.read()
        except Exception as e:
            errors.append(f"Failed to read {file_path}: {e}")
            return [], [], [], [], {"external": set(), "internal": set()}, errors
    except Exception as e:
        errors.append(f"Failed to read {file_path}: {e}")
        return [], [], [], [], {"external": set(), "internal": set()}, errors

    if not source.strip():
        return [], [], [], [], {"external": set(), "internal": set()}, errors

    try:
        extractor = get_extractor(file_path, source)
        functions, classes, constants, data_structures, dependencies = extractor.extract()
        return functions, classes, constants, data_structures, dependencies, errors
    except ParseError as e:
        errors.append(str(e))
        return [], [], [], [], {"external": set(), "internal": set()}, errors
    except Exception as e:
        errors.append(f"Error analyzing {file_path}: {e}")
        return [], [], [], [], {"external": set(), "internal": set()}, errors


def collect_files(paths: list[str]) -> list[str]:
    """Collect all files from the given paths."""
    files = []

    for path in paths:
        p = Path(path)

        if not p.exists():
            continue

        if p.is_file():
            files.append(str(p))
        elif p.is_dir():
            # Recursively find all code files
            for ext in ("*.py", "*.ts", "*.tsx", "*.js", "*.jsx", "*.go", "*.rs", "*.java"):
                files.extend(str(f) for f in p.rglob(ext))

    return sorted(set(files))


def analyze_phase(phase: str, paths: list[str]) -> IntegrationSurface:
    """Analyze a phase and return its integration surface."""
    surface = IntegrationSurface(
        phase=phase,
        analyzed_at=datetime.now(timezone.utc).isoformat(),
    )

    files = collect_files(paths)

    if not files:
        surface.errors.append("No files found to analyze")
        return surface

    all_external_deps: set[str] = set()
    all_internal_deps: set[str] = set()

    for file_path in files:
        functions, classes, constants, data_structures, dependencies, errors = analyze_file(file_path)

        surface.exports["functions"].extend(functions)
        surface.exports["classes"].extend(classes)
        surface.exports["constants"].extend(constants)
        surface.contracts["data_structures"].extend(data_structures)
        surface.errors.extend(errors)

        all_external_deps.update(dependencies["external"])
        all_internal_deps.update(dependencies["internal"])

    surface.dependencies["external"] = sorted(all_external_deps)
    surface.dependencies["internal"] = sorted(all_internal_deps)

    # Remove duplicates while preserving order
    surface.exports["functions"] = list({f.name: f for f in surface.exports["functions"]}.values())
    surface.exports["classes"] = list({c.name: c for c in surface.exports["classes"]}.values())
    surface.exports["constants"] = list({c.name: c for c in surface.exports["constants"]}.values())
    surface.contracts["data_structures"] = list({d.name: d for d in surface.contracts["data_structures"]}.values())

    return surface


def write_output(surface: IntegrationSurface, output: TextIO | None = None) -> str:
    """Write the integration surface to output."""
    result = json.dumps(surface.to_dict(), indent=2, default=str)

    if output:
        output.write(result)
        output.write("\n")

    return result


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Detect integration surface of a completed phase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s --phase "Phase 1" --paths src/agent/ --output phase1.json
    %(prog)s --phase "API Layer" --paths api/ models/ --output api_surface.json
    %(prog)s --phase "Utils" --paths src/utils.py --output -
        """,
    )

    parser.add_argument(
        "--phase",
        required=True,
        help="Name of the phase to analyze",
    )
    parser.add_argument(
        "--paths",
        nargs="+",
        required=True,
        help="Files or directories to analyze",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="-",
        help="Output file path (use - for stdout, default: -)",
    )
    parser.add_argument(
        "--config",
        help="Path to configuration file (JSON)",
    )

    args = parser.parse_args()

    # Load configuration if provided
    config: dict[str, Any] = {}
    if args.config:
        try:
            with open(args.config, "r") as f:
                config = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load config: {e}", file=sys.stderr)

    # Analyze the phase
    surface = analyze_phase(args.phase, args.paths)

    # Write output
    if args.output == "-":
        write_output(surface, sys.stdout)
    else:
        try:
            with open(args.output, "w") as f:
                write_output(surface, f)
            print(f"Integration surface written to {args.output}", file=sys.stderr)
        except Exception as e:
            print(f"Error writing output: {e}", file=sys.stderr)
            return 1

    # Return non-zero if there were errors
    return 1 if surface.errors else 0


if __name__ == "__main__":
    sys.exit(main())
