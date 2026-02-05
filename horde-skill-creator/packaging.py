"""
Skill Packaging System with Quality Gates

Provides comprehensive packaging, validation, and quality assessment for skills
created by the Supercharged Skill Creator. Implements quality gates that determine
whether a skill is ready for Production, Beta, Alpha, or has Failed quality levels.

Quality Levels:
    - Production: 0 critical, <=2 high severity issues, >=70% test coverage
    - Beta: <=1 critical, <=5 high, >=50% coverage
    - Alpha: <=3 critical, <=10 high, >=30% coverage
    - Failed: Exceeds Alpha thresholds

Exit Codes:
    - 0: Success (skill packaged)
    - 1: Validation failed (skill failed quality gates)
    - 2: Structure error (SKILL.md missing or invalid)
    - 3: Dependency error (required files or capabilities missing)
    - 4: Test failure (tests failed to run or all failed)
    - 5: Secret detection (hardcoded secrets found)
    - 6: Permission error (cannot read/write files)

Example:
    ```python
    from packaging import SkillPackager, PackageResult

    packager = SkillPackager()
    result = packager.package_skill("/path/to/skill")

    if result.quality_level == QualityLevel.PRODUCTION:
        print(f"Skill ready for production: {result.package_path}")
    elif result.quality_level == QualityLevel.FAILED:
        print(f"Packaging failed: {result.failure_reason}")
    ```
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union


# =============================================================================
# Exit Codes
# =============================================================================

class ExitCode(Enum):
    """Exit codes for different failure scenarios."""

    SUCCESS = 0
    VALIDATION_FAILED = 1
    STRUCTURE_ERROR = 2
    DEPENDENCY_ERROR = 3
    TEST_FAILURE = 4
    SECRET_DETECTED = 5
    PERMISSION_ERROR = 6


# =============================================================================
# Quality Level Definitions
# =============================================================================

class QualityLevel(Enum):
    """Quality levels for packaged skills."""

    PRODUCTION = auto()
    BETA = auto()
    ALPHA = auto()
    FAILED = auto()

    @classmethod
    def from_metrics(cls, metrics: "QualityMetrics") -> "QualityLevel":
        """Determine quality level from metrics."""
        # Production: No critical issues, low high-severity, good coverage
        if (
            metrics.critical_count == 0
            and metrics.high_count <= 2
            and metrics.coverage_percent >= 70
        ):
            return cls.PRODUCTION

        # Beta: Allow some issues
        if (
            metrics.critical_count <= 1
            and metrics.high_count <= 5
            and metrics.coverage_percent >= 50
        ):
            return cls.BETA

        # Alpha: More lenient but still functional
        if (
            metrics.critical_count <= 3
            and metrics.high_count <= 10
            and metrics.coverage_percent >= 30
        ):
            return cls.ALPHA

        return cls.FAILED

    def __str__(self) -> str:
        return self.name

    def get_badge_color(self) -> str:
        """Get hex color for badges."""
        return {
            self.PRODUCTION: "#00c853",  # Green
            self.BETA: "#ffc107",       # Amber
            self.ALPHA: "#ff9800",      # Orange
            self.FAILED: "#f44336",     # Red
        }[self]

    def get_description(self) -> str:
        """Get human-readable description."""
        return {
            self.PRODUCTION: "Ready for production use",
            self.BETA: "Ready for beta testing",
            self.ALPHA: "Early development, use with caution",
            self.FAILED: "Does not meet minimum quality standards",
        }[self]


# =============================================================================
# Quality Metrics
# =============================================================================

@dataclass
class QualityMetrics:
    """Metrics collected during quality evaluation."""

    # Issue counts by severity
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    info_count: int = 0

    # Test coverage
    coverage_percent: float = 0.0
    tests_total: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    tests_skipped: int = 0

    # Code metrics
    lines_of_code: int = 0
    files_count: int = 0
    python_files: int = 0
    docstring_percent: float = 0.0

    # Security metrics
    secrets_found: int = 0
    dependencies_count: int = 0

    @property
    def total_issues(self) -> int:
        """Total number of issues."""
        return (
            self.critical_count
            + self.high_count
            + self.medium_count
            + self.low_count
            + self.info_count
        )

    @property
    def test_success_rate(self) -> float:
        """Test success rate as percentage."""
        if self.tests_total == 0:
            return 0.0
        return (self.tests_passed / self.tests_total) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "issues": {
                "critical": self.critical_count,
                "high": self.high_count,
                "medium": self.medium_count,
                "low": self.low_count,
                "info": self.info_count,
                "total": self.total_issues,
            },
            "coverage": {
                "percent": round(self.coverage_percent, 2),
                "tests": {
                    "total": self.tests_total,
                    "passed": self.tests_passed,
                    "failed": self.tests_failed,
                    "skipped": self.tests_skipped,
                    "success_rate": round(self.test_success_rate, 2),
                },
            },
            "code": {
                "lines_of_code": self.lines_of_code,
                "files_count": self.files_count,
                "python_files": self.python_files,
                "docstring_percent": round(self.docstring_percent, 2),
            },
            "security": {
                "secrets_found": self.secrets_found,
                "dependencies_count": self.dependencies_count,
            },
        }


# =============================================================================
# Validation Issues
# =============================================================================

@dataclass
class StructureIssue:
    """Issue found during structure validation."""

    path: str
    issue_type: str
    message: str
    severity: str = "error"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "type": self.issue_type,
            "message": self.message,
            "severity": self.severity,
        }


@dataclass
class SecurityIssue:
    """Issue found during security scan."""

    file_path: str
    line_number: int
    issue_type: str
    description: str
    severity: str = "high"
    matched_pattern: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file": str(self.file_path),
            "line": self.line_number,
            "type": self.issue_type,
            "description": self.description,
            "severity": self.severity,
            "pattern": self.matched_pattern,
        }


# =============================================================================
# Validation Results
# =============================================================================

@dataclass
class StructureValidationResult:
    """Result of structure validation."""

    is_valid: bool
    skill_name: Optional[str] = None
    skill_version: Optional[str] = None
    issues: List[StructureIssue] = field(default_factory=list)
    missing_files: List[Path] = field(default_factory=list)
    invalid_sections: List[str] = field(default_factory=list)
    yaml_errors: List[str] = field(default_factory=list)
    non_executable_scripts: List[Path] = field(default_factory=list)
    has_secrets: bool = False
    secret_locations: List[str] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "valid": self.is_valid,
            "skill_name": self.skill_name,
            "skill_version": self.skill_version,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "issues": [i.to_dict() for i in self.issues],
            "missing_files": [str(f) for f in self.missing_files],
            "invalid_sections": self.invalid_sections,
            "yaml_errors": self.yaml_errors,
            "non_executable_scripts": [str(s) for s in self.non_executable_scripts],
            "has_secrets": self.has_secrets,
            "secret_locations": self.secret_locations,
        }


@dataclass
class TestResult:
    """Result of running tests."""

    success: bool
    exit_code: int
    output: str = ""
    error_output: str = ""
    coverage_percent: float = 0.0
    tests_run: int = 0
    tests_passed: int = 0
    tests_failed: int = 0
    tests_skipped: int = 0
    duration_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "exit_code": self.exit_code,
            "coverage_percent": round(self.coverage_percent, 2),
            "tests": {
                "run": self.tests_run,
                "passed": self.tests_passed,
                "failed": self.tests_failed,
                "skipped": self.tests_skipped,
            },
            "duration_seconds": round(self.duration_seconds, 2),
            "output": self.output[:1000] if self.output else "",  # Truncate
            "error": self.error_output[:1000] if self.error_output else "",
        }


@dataclass
class PackageResult:
    """Result of packaging a skill."""

    success: bool
    quality_level: QualityLevel
    skill_path: Path
    package_path: Optional[Path] = None
    checksum: Optional[str] = None
    metrics: Optional[QualityMetrics] = None
    structure_result: Optional[StructureValidationResult] = None
    test_result: Optional[TestResult] = None
    security_issues: List[SecurityIssue] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    failure_reason: Optional[str] = None
    exit_code: int = ExitCode.SUCCESS.value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "quality_level": str(self.quality_level),
            "quality_description": self.quality_level.get_description(),
            "badge_color": self.quality_level.get_badge_color(),
            "skill_path": str(self.skill_path),
            "package_path": str(self.package_path) if self.package_path else None,
            "checksum": self.checksum,
            "metrics": self.metrics.to_dict() if self.metrics else None,
            "structure": self.structure_result.to_dict() if self.structure_result else None,
            "tests": self.test_result.to_dict() if self.test_result else None,
            "security": [i.to_dict() for i in self.security_issues],
            "warnings": self.warnings,
            "failure_reason": self.failure_reason,
            "exit_code": self.exit_code,
        }

    def to_report(self) -> str:
        """Generate a human-readable report."""
        lines = [
            "=" * 60,
            f"Skill Packaging Report: {self.skill_path.name}",
            "=" * 60,
            "",
        ]

        if self.success:
            lines.append(f"Status: SUCCESS")
            lines.append(f"Quality Level: {self.quality_level}")
            lines.append(f"Description: {self.quality_level.get_description()}")
            lines.append(f"Package: {self.package_path}")
            lines.append(f"Checksum: {self.checksum}")
        else:
            lines.append(f"Status: FAILED")
            lines.append(f"Reason: {self.failure_reason}")
            lines.append(f"Exit Code: {self.exit_code}")

        lines.append("")

        if self.metrics:
            lines.append("-" * 40)
            lines.append("Metrics:")
            lines.append(f"  Issues: {self.metrics.total_issues} "
                        f"(C:{self.metrics.critical_count}, "
                        f"H:{self.metrics.high_count}, "
                        f"M:{self.metrics.medium_count})")
            lines.append(f"  Coverage: {self.metrics.coverage_percent:.1f}%")
            lines.append(f"  Tests: {self.metrics.tests_passed}/{self.metrics.tests_total} passed")

        if self.warnings:
            lines.append("")
            lines.append("Warnings:")
            for w in self.warnings:
                lines.append(f"  - {w}")

        if self.security_issues:
            lines.append("")
            lines.append("Security Issues:")
            for i in self.security_issues:
                lines.append(f"  - {i.file_path}:{i.line_number} - {i.description}")

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)


# =============================================================================
# Quality Gate Thresholds
# =============================================================================

@dataclass
class QualityThreshold:
    """Thresholds for a quality level."""

    name: str
    max_critical: int
    max_high: int
    min_coverage: float
    description: str


class QualityGateEvaluator:
    """Evaluates quality metrics against gate thresholds."""

    # Define quality thresholds
    THRESHOLDS = {
        QualityLevel.PRODUCTION: QualityThreshold(
            name="Production",
            max_critical=0,
            max_high=2,
            min_coverage=70.0,
            description="Ready for production deployment",
        ),
        QualityLevel.BETA: QualityThreshold(
            name="Beta",
            max_critical=1,
            max_high=5,
            min_coverage=50.0,
            description="Ready for beta testing",
        ),
        QualityLevel.ALPHA: QualityThreshold(
            name="Alpha",
            max_critical=3,
            max_high=10,
            min_coverage=30.0,
            description="Early development stage",
        ),
    }

    @classmethod
    def evaluate(cls, metrics: QualityMetrics) -> Tuple[QualityLevel, List[str]]:
        """Evaluate metrics against all quality gates.

        Returns:
            Tuple of (quality_level, list of reasons for not meeting higher levels)
        """
        reasons = []

        # Check production first
        prod = cls.THRESHOLDS[QualityLevel.PRODUCTION]
        if (
            metrics.critical_count <= prod.max_critical
            and metrics.high_count <= prod.max_high
            and metrics.coverage_percent >= prod.min_coverage
        ):
            return QualityLevel.PRODUCTION, []

        # Add reasons for not meeting production
        if metrics.critical_count > prod.max_critical:
            reasons.append(
                f"Too many critical issues for production: {metrics.critical_count} > {prod.max_critical}"
            )
        if metrics.high_count > prod.max_high:
            reasons.append(
                f"Too many high-severity issues for production: {metrics.high_count} > {prod.max_high}"
            )
        if metrics.coverage_percent < prod.min_coverage:
            reasons.append(
                f"Coverage too low for production: {metrics.coverage_percent:.1f}% < {prod.min_coverage}%"
            )

        # Check beta
        beta = cls.THRESHOLDS[QualityLevel.BETA]
        if (
            metrics.critical_count <= beta.max_critical
            and metrics.high_count <= beta.max_high
            and metrics.coverage_percent >= beta.min_coverage
        ):
            return QualityLevel.BETA, reasons

        # Add reasons for not meeting beta
        if metrics.critical_count > beta.max_critical:
            reasons.append(
                f"Too many critical issues for beta: {metrics.critical_count} > {beta.max_critical}"
            )
        if metrics.high_count > beta.max_high:
            reasons.append(
                f"Too many high-severity issues for beta: {metrics.high_count} > {beta.max_high}"
            )
        if metrics.coverage_percent < beta.min_coverage:
            reasons.append(
                f"Coverage too low for beta: {metrics.coverage_percent:.1f}% < {beta.min_coverage}%"
            )

        # Check alpha
        alpha = cls.THRESHOLDS[QualityLevel.ALPHA]
        if (
            metrics.critical_count <= alpha.max_critical
            and metrics.high_count <= alpha.max_high
            and metrics.coverage_percent >= alpha.min_coverage
        ):
            return QualityLevel.ALPHA, reasons

        return QualityLevel.FAILED, reasons

    @classmethod
    def get_report(cls, metrics: QualityMetrics, level: QualityLevel) -> str:
        """Generate a quality gate report."""
        lines = [
            "Quality Gate Evaluation",
            "-" * 40,
            f"Determined Level: {level}",
            f"Description: {level.get_description()}",
            "",
            "Metrics:",
            f"  Critical Issues: {metrics.critical_count}",
            f"  High Issues: {metrics.high_count}",
            f"  Medium Issues: {metrics.medium_count}",
            f"  Low Issues: {metrics.low_count}",
            f"  Coverage: {metrics.coverage_percent:.1f}%",
            f"  Tests Passed: {metrics.tests_passed}/{metrics.tests_total}",
            "",
        ]

        if level != QualityLevel.PRODUCTION:
            lines.extend([
                "Threshold Requirements:",
                "",
                "Production:",
                "  Critical: <= 0",
                "  High: <= 2",
                "  Coverage: >= 70%",
                "",
                "Beta:",
                "  Critical: <= 1",
                "  High: <= 5",
                "  Coverage: >= 50%",
                "",
                "Alpha:",
                "  Critical: <= 3",
                "  High: <= 10",
                "  Coverage: >= 30%",
                "",
            ])

        return "\n".join(lines)


# =============================================================================
# Secret Detection
# =============================================================================

class SecretDetector:
    """Detects hardcoded secrets and sensitive information."""

    # Patterns for detecting secrets
    PATTERNS = [
        # API Keys
        (r"(?i)(api[_-]?key|apikey|api[_-]?secret)['\"]?\s*[:=]\s*['\"]([a-zA-Z0-9_\-]{20,})['\"]", "api_key"),
        (r"(?i)(openai[_-]?api[_-]?key|anthropic[_-]?api[_-]?key)['\"]?\s*[:=]\s*['\"]([a-zA-Z0-9_\-]{20,})['\"]", "llm_api_key"),

        # Tokens
        (r"(?i)(bearer[_-]?token|access[_-]?token|auth[_-]?token)['\"]?\s*[:=]\s*['\"]([a-zA-Z0-9_\-\.]{20,})['\"]", "auth_token"),
        (r"(?i)github[_-]?token['\"]?\s*[:=]\s*['\"]([a-zA-Z0-9_\-]{36,})['\"]", "github_token"),
        (r"(?i)(slack[_-]?token|discord[_-]?token)['\"]?\s*[:=]\s*['\"]([a-zA-Z0-9_\-]{20,})['\"]", "chat_token"),

        # Passwords
        (r"(?i)(password|passwd|pwd)['\"]?\s*[:=]\s*['\"]([^'\"]{8,})['\"]", "password"),

        # URLs with credentials
        (r"(?i)(mongodb|postgresql|mysql|redis)://[^:\s]+:[^@\s]+@", "database_url_creds"),

        # SSH keys
        (r"-----BEGIN\s+(RSA\s+PRIVATE|PRIVATE|EC\s+PRIVATE)\s+KEY-----", "private_key"),

        # JWT tokens
        (r"ey[A-Za-z0-9_\-]{20,}\.ey[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}", "jwt_token"),

        # AWS keys
        (r"(?i)aws[_-]?(access[_-]?key[_-]?id|secret[_-]?access[_-]?key)['\"]?\s*[:=]\s*['\"]([A-Z0-9]{16,})['\"]", "aws_credentials"),

        # Generic base64 strings that might be secrets
        (r"(?i)(secret|token|key|password)['\"]?\s*[:=]\s*['\"]([A-Za-z0-9+/]{32,}={0,2})['\"]", "base64_secret"),

        # Email addresses (may be sensitive)
        (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "email"),

        # IP addresses (internal infrastructure)
        (r"\b(10\.|172\.(1[6-9]|2[0-9]|3[01])\.|192\.168\.)\d{1,3}\.\d{1,3}\b", "private_ip"),
    ]

    # Common false positives to exclude
    FALSE_POSITIVES = [
        "your-api-key",
        "your-token-here",
        "your-secret-key",
        "replace-with-your-key",
        "example-key",
        "test-api-key",
        "demo-token",
        "xxx",
        "placeholder",
        "<your-key>",
    ]

    @classmethod
    def scan_file(cls, file_path: Path) -> List[SecurityIssue]:
        """Scan a single file for secrets."""
        issues = []

        try:
            content = file_path.read_text()
            lines = content.splitlines()

            for line_num, line in enumerate(lines, 1):
                for pattern, issue_type in cls.PATTERNS:
                    matches = re.finditer(pattern, line)

                    for match in matches:
                        # Extract the matched value
                        matched_value = match.group(0) if len(match.groups()) == 0 else match.group(0)

                        # Check for false positives
                        if any(fp in matched_value.lower() for fp in cls.FALSE_POSITIVES):
                            continue

                        # Skip comments (but be careful with multi-line strings)
                        stripped = line.strip()
                        if stripped.startswith("#") or stripped.startswith("//"):
                            continue

                        issues.append(
                            SecurityIssue(
                                file_path=file_path,
                                line_number=line_num,
                                issue_type=issue_type,
                                description=f"Potential {issue_type.replace('_', ' ')} detected",
                                severity="high",
                                matched_pattern=matched_value[:50] + "..." if len(matched_value) > 50 else matched_value,
                            )
                        )
        except (UnicodeDecodeError, PermissionError):
            # Skip binary files or files we can't read
            pass

        return issues

    @classmethod
    def scan_directory(cls, directory: Path, exclude_dirs: Optional[Set[str]] = None) -> List[SecurityIssue]:
        """Scan all files in a directory for secrets."""
        if exclude_dirs is None:
            exclude_dirs = {
                "__pycache__",
                ".git",
                ".pytest_cache",
                "node_modules",
                ".venv",
                "venv",
                "dist",
                "build",
                ".eggs",
            }

        issues = []

        for file_path in directory.rglob("*"):
            # Skip directories
            if file_path.is_dir():
                continue

            # Skip excluded directories
            if any(part in exclude_dirs for part in file_path.parts):
                continue

            # Only scan text files
            if not cls.is_text_file(file_path):
                continue

            issues.extend(cls.scan_file(file_path))

        return issues

    @classmethod
    def is_text_file(cls, file_path: Path) -> bool:
        """Check if a file is likely a text file."""
        # By extension
        text_extensions = {
            ".py", ".txt", ".md", ".rst", ".yml", ".yaml",
            ".json", ".toml", ".ini", ".cfg", ".conf",
            ".sh", ".bash", ".zsh", ".env", ".example",
            ".js", ".ts", ".jsx", ".tsx", ".css", ".scss",
            ".html", ".xml", ".sql",
        }

        if file_path.suffix.lower() in text_extensions:
            return True

        # Check for common text file names
        if file_path.name in {"Dockerfile", "Makefile", "README", "LICENSE"}:
            return True

        # Check file type
        try:
            with open(file_path, "rb") as f:
                chunk = f.read(1024)
                if b"\x00" in chunk:
                    return False
        except Exception:
            return False

        return True


# =============================================================================
# Structure Validator
# =============================================================================

class SkillStructureValidator:
    """Validates the structure of a skill directory."""

    # Required sections in SKILL.md
    REQUIRED_SECTIONS = {
        "name",
        "description",
        "version",
        "author",
        "entry_point",
    }

    # Optional but recommended sections
    RECOMMENDED_SECTIONS = {
        "requirements",
        "dependencies",
        "examples",
        "parameters",
        "outputs",
    }

    def __init__(self, skill_path: Path):
        self.skill_path = Path(skill_path).resolve()
        self.skill_md_path = self.skill_path / "SKILL.md"

    def validate(self) -> StructureValidationResult:
        """Run full structure validation."""
        issues = []
        missing_files = []
        invalid_sections = []
        yaml_errors = []
        non_executable_scripts = []
        has_secrets = False
        secret_locations = []

        # Check SKILL.md exists
        if not self.skill_md_path.exists():
            issues.append(
                StructureIssue(
                    path="SKILL.md",
                    issue_type="missing_file",
                    message="SKILL.md not found",
                    severity="error",
                )
            )
            return StructureValidationResult(
                is_valid=False,
                issues=issues,
                missing_files=[self.skill_md_path],
            )

        # Parse SKILL.md
        skill_metadata = self._parse_skill_md()
        if skill_metadata is None:
            issues.append(
                StructureIssue(
                    path="SKILL.md",
                    issue_type="parse_error",
                    message="Failed to parse SKILL.md",
                    severity="error",
                )
            )
            return StructureValidationResult(is_valid=False, issues=issues)

        skill_name = skill_metadata.get("name")
        skill_version = skill_metadata.get("version")

        # Validate required sections
        for section in self.REQUIRED_SECTIONS:
            if section not in skill_metadata:
                invalid_sections.append(section)
                issues.append(
                    StructureIssue(
                        path=f"SKILL.md#{section}",
                        issue_type="missing_section",
                        message=f"Required section '{section}' not found",
                        severity="error",
                    )
                )

        # Check entry point file exists
        entry_point = skill_metadata.get("entry_point")
        if entry_point:
            entry_path = self.skill_path / entry_point
            if not entry_path.exists():
                missing_files.append(entry_path)
                issues.append(
                    StructureIssue(
                        path=entry_point,
                        issue_type="missing_file",
                        message=f"Entry point file not found: {entry_point}",
                        severity="error",
                    )
                )

        # Check referenced files
        referenced_files = self._extract_referenced_files(skill_metadata)
        for ref_file in referenced_files:
            ref_path = self.skill_path / ref_file
            if not ref_path.exists():
                missing_files.append(ref_path)
                issues.append(
                    StructureIssue(
                        path=str(ref_file),
                        issue_type="missing_referenced_file",
                        message=f"Referenced file not found: {ref_file}",
                        severity="error",
                    )
                )

        # Check scripts are executable
        scripts = self._find_scripts()
        for script in scripts:
            if not os.access(script, os.X_OK):
                non_executable_scripts.append(script)
                issues.append(
                    StructureIssue(
                        path=str(script.relative_to(self.skill_path)),
                        issue_type="not_executable",
                        message="Script file is not executable",
                        severity="warning",
                    )
                )

        # Check for secrets
        security_issues = SecretDetector.scan_directory(self.skill_path)
        if security_issues:
            has_secrets = True
            secret_locations = [f"{i.file_path}:{i.line_number}" for i in security_issues]
            for issue in security_issues:
                issues.append(
                    StructureIssue(
                        path=str(issue.file_path.relative_to(self.skill_path)),
                        issue_type="secret_detected",
                        message=issue.description,
                        severity="error",
                    )
                )

        is_valid = (
            not any(i.severity == "error" for i in issues)
            and not invalid_sections
            and not missing_files
            and not has_secrets
        )

        return StructureValidationResult(
            is_valid=is_valid,
            skill_name=skill_name,
            skill_version=skill_version,
            issues=issues,
            missing_files=missing_files,
            invalid_sections=invalid_sections,
            yaml_errors=yaml_errors,
            non_executable_scripts=non_executable_scripts,
            has_secrets=has_secrets,
            secret_locations=secret_locations,
        )

    def _parse_skill_md(self) -> Optional[Dict[str, Any]]:
        """Parse SKILL.md and extract YAML frontmatter and metadata."""
        try:
            content = self.skill_md_path.read_text()
        except (PermissionError, UnicodeDecodeError):
            return None

        # Check for YAML frontmatter
        if content.startswith("---"):
            try:
                # Extract YAML frontmatter
                parts = content.split("---", 2)
                if len(parts) >= 3:
                    yaml_content = parts[1]
                    try:
                        import yaml
                        return yaml.safe_load(yaml_content) or {}
                    except ImportError:
                        # Fallback: simple key-value parsing
                        return self._parse_simple_yaml(yaml_content)
            except Exception:
                pass

        # Fallback: Parse as simple markdown with headers
        return self._parse_markdown_headers(content)

    def _parse_simple_yaml(self, yaml_content: str) -> Dict[str, Any]:
        """Simple YAML parser for basic key-value pairs."""
        result = {}
        for line in yaml_content.strip().split("\n"):
            if ":" in line and not line.strip().startswith("#"):
                key, value = line.split(":", 1)
                result[key.strip()] = value.strip()
        return result

    def _parse_markdown_headers(self, content: str) -> Dict[str, Any]:
        """Parse markdown headers to extract metadata."""
        result = {}
        current_key = None

        for line in content.split("\n"):
            # Headers
            if line.startswith("#"):
                header = line.lstrip("#").strip()
                if header.lower() in {"name", "description", "version", "author"}:
                    current_key = header.lower()
                else:
                    current_key = header.lower().replace(" ", "_")

            # Code blocks with values
            elif current_key and line.strip().startswith("```"):
                continue

            # Key-value lines
            elif ":" in line and not line.strip().startswith("#"):
                key, value = line.split(":", 1)
                result[key.strip().lower()] = value.strip()

            # Lists under headers
            elif current_key and line.strip().startswith("-"):
                if current_key not in result:
                    result[current_key] = []
                result[current_key].append(line.strip()[1:].strip())

        return result

    def _extract_referenced_files(self, metadata: Dict[str, Any]) -> List[Path]:
        """Extract file paths referenced in metadata."""
        referenced = []

        # Entry point
        entry_point = metadata.get("entry_point")
        if entry_point:
            referenced.append(Path(entry_point))

        # Requirements files
        for req_key in ["requirements", "requirements_file", "dependencies"]:
            req_value = metadata.get(req_key)
            if isinstance(req_value, str):
                referenced.append(Path(req_value))
            elif isinstance(req_value, list):
                for item in req_value:
                    if isinstance(item, str):
                        referenced.append(Path(item))

        # Documentation files
        for doc_key in ["readme", "docs", "documentation"]:
            doc_value = metadata.get(doc_key)
            if isinstance(doc_value, str):
                referenced.append(Path(doc_value))

        return referenced

    def _find_scripts(self) -> List[Path]:
        """Find all script files that should be executable."""
        scripts = []
        script_extensions = {".py", ".sh", ".bash"}
        script_names = {"run", "start", "install", "setup", "build"}

        for file_path in self.skill_path.rglob("*"):
            if file_path.is_file():
                if file_path.suffix in script_extensions or file_path.stem in script_names:
                    scripts.append(file_path)

        return scripts


# =============================================================================
# Test Runner
# =============================================================================

class SkillTestRunner:
    """Runs tests for a skill and collects metrics."""

    def __init__(self, skill_path: Path):
        self.skill_path = Path(skill_path).resolve()

    def run(self) -> TestResult:
        """Run the test suite."""
        # Find test directory
        test_dirs = [
            self.skill_path / "tests",
            self.skill_path / "test",
            self.skill_path,
        ]

        test_dir = None
        for d in test_dirs:
            if d.exists() and d.is_dir():
                # Check if it has test files
                if any(f.name.startswith("test_") for f in d.glob("*.py")):
                    test_dir = d
                    break

        if test_dir is None:
            return TestResult(
                success=False,
                exit_code=-1,
                output="No test directory found",
            )

        # Run pytest
        return self._run_pytest(test_dir)

    def _run_pytest(self, test_dir: Path) -> TestResult:
        """Run pytest and collect results."""
        import time

        start_time = time.time()

        # Build pytest command
        cmd = [
            sys.executable, "-m", "pytest",
            str(test_dir),
            "-v",
            "--tb=short",
            "--no-header",
        ]

        # Try to add coverage
        try:
            import pytest_cov
            cmd.extend(["--cov=", str(self.skill_path), "--cov-report=term-missing"])
            coverage_available = True
        except ImportError:
            coverage_available = False

        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.skill_path),
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            output = result.stdout + result.stderr
            duration = time.time() - start_time

            # Parse output for metrics
            metrics = self._parse_pytest_output(output, coverage_available)

            return TestResult(
                success=result.returncode == 0 or result.returncode == 5,  # 5 = no tests collected
                exit_code=result.returncode,
                output=result.stdout,
                error_output=result.stderr,
                coverage_percent=metrics.get("coverage", 0.0),
                tests_run=metrics.get("run", 0),
                tests_passed=metrics.get("passed", 0),
                tests_failed=metrics.get("failed", 0),
                tests_skipped=metrics.get("skipped", 0),
                duration_seconds=duration,
            )

        except subprocess.TimeoutExpired:
            return TestResult(
                success=False,
                exit_code=-1,
                output="Tests timed out after 5 minutes",
            )
        except FileNotFoundError:
            return TestResult(
                success=False,
                exit_code=-1,
                output="pytest not found. Install with: pip install pytest pytest-cov",
            )
        except Exception as e:
            return TestResult(
                success=False,
                exit_code=-1,
                output=f"Error running tests: {e}",
            )

    def _parse_pytest_output(self, output: str, has_coverage: bool) -> Dict[str, Any]:
        """Parse pytest output to extract metrics."""
        metrics = {
            "run": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "coverage": 0.0,
        }

        # Parse test summary line
        # Examples:
        # "5 passed in 1.2s"
        # "5 passed, 1 failed, 2 skipped in 1.2s"
        summary_pattern = r"(\d+)\s+passed(?:,\s+(\d+)\s+failed)?(?:,\s+(\d+)\s+skipped)?"
        match = re.search(summary_pattern, output)
        if match:
            metrics["passed"] = int(match.group(1))
            if match.group(2):
                metrics["failed"] = int(match.group(2))
            if match.group(3):
                metrics["skipped"] = int(match.group(3))
            metrics["run"] = (
                metrics["passed"] + metrics["failed"] + metrics["skipped"]
            )

        # Parse coverage if available
        if has_coverage:
            # Look for coverage percentage
            coverage_pattern = r"(\d+\.?\d*)%"
            coverage_matches = re.findall(coverage_pattern, output)
            if coverage_matches:
                try:
                    # Usually the last percentage is the total coverage
                    metrics["coverage"] = float(coverage_matches[-1])
                except ValueError:
                    pass

        return metrics


# =============================================================================
# Code Analyzer
# =============================================================================

class CodeAnalyzer:
    """Analyzes Python code for quality metrics."""

    def __init__(self, skill_path: Path):
        self.skill_path = Path(skill_path).resolve()

    def analyze(self) -> QualityMetrics:
        """Analyze all Python files in the skill."""
        metrics = QualityMetrics()

        for py_file in self.skill_path.rglob("*.py"):
            # Skip test files
            if "test" in py_file.parts or py_file.name.startswith("test_"):
                continue

            # Skip __pycache__
            if "__pycache__" in py_file.parts:
                continue

            metrics.python_files += 1

            try:
                content = py_file.read_text()
                tree = ast.parse(content, filename=str(py_file))

                # Count lines of code
                lines = content.splitlines()
                metrics.lines_of_code += len([
                    l for l in lines
                    if l.strip() and not l.strip().startswith("#")
                ])

                # Check for docstrings
                has_docstring = False
                if tree.body and isinstance(tree.body[0], ast.Expr):
                    if isinstance(tree.body[0].value, ast.Constant):
                        has_docstring = isinstance(tree.body[0].value.value, str)

                # Count function docstrings
                docstring_functions = 0
                total_functions = 0
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        total_functions += 1
                        if (
                            node.body
                            and isinstance(node.body[0], ast.Expr)
                            and isinstance(node.body[0].value, ast.Constant)
                            and isinstance(node.body[0].value.value, str)
                        ):
                            docstring_functions += 1

                # Class docstrings
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        total_functions += 1
                        if (
                            node.body
                            and isinstance(node.body[0], ast.Expr)
                            and isinstance(node.body[0].value, ast.Constant)
                            and isinstance(node.body[0].value.value, str)
                        ):
                            docstring_functions += 1

                if total_functions > 0:
                    module_doc_percent = (docstring_functions / total_functions) * 100
                    # Weight module docstring more
                    if has_docstring:
                        module_doc_percent = min(100, module_doc_percent + 20)
                    metrics.docstring_percent = (
                        (metrics.docstring_percent * (metrics.python_files - 1) + module_doc_percent)
                        / metrics.python_files
                    )

            except (SyntaxError, UnicodeDecodeError):
                # Skip files with syntax errors
                pass

        # Count total files
        metrics.files_count = sum(1 for f in self.skill_path.rglob("*") if f.is_file())

        return metrics


# =============================================================================
# Main Packager
# =============================================================================

class SkillPackager:
    """Main packaging class for skills."""

    def __init__(
        self,
        output_dir: Optional[Path] = None,
        include_tests: bool = True,
        include_docs: bool = True,
    ):
        """
        Initialize the packager.

        Args:
            output_dir: Directory to write packages to. Defaults to temp directory.
            include_tests: Whether to include test files in the package.
            include_docs: Whether to include documentation files in the package.
        """
        self.output_dir = Path(output_dir) if output_dir else Path(tempfile.gettempdir()) / "skill-packages"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.include_tests = include_tests
        self.include_docs = include_docs

    def package_skill(self, skill_path: str | Path) -> PackageResult:
        """Package a skill and evaluate its quality.

        This is the main entry point for packaging a skill. It runs the full
        validation pipeline and creates a distributable package.

        Args:
            skill_path: Path to the skill directory.

        Returns:
            PackageResult with the outcome of packaging.
        """
        skill_path = Path(skill_path).resolve()

        # Step 1: Validate structure
        structure_result = self.validate_structure(skill_path)
        if not structure_result.is_valid:
            return PackageResult(
                success=False,
                quality_level=QualityLevel.FAILED,
                skill_path=skill_path,
                structure_result=structure_result,
                failure_reason=self._get_failure_reason(structure_result),
                exit_code=self._get_exit_code(structure_result),
            )

        # Step 2: Run tests
        test_result = self.run_tests(skill_path)
        if not test_result.success and test_result.exit_code == -1:
            # Tests failed to run, not just test failures
            return PackageResult(
                success=False,
                quality_level=QualityLevel.FAILED,
                skill_path=skill_path,
                test_result=test_result,
                failure_reason="Tests failed to run",
                exit_code=ExitCode.TEST_FAILURE.value,
            )

        # Step 3: Analyze code
        code_metrics = self._analyze_code(skill_path)

        # Step 4: Check for security issues
        security_issues = SecretDetector.scan_directory(skill_path)

        # Step 5: Evaluate quality
        metrics = self._build_metrics(
            code_metrics=code_metrics,
            test_result=test_result,
            security_issues=security_issues,
            structure_result=structure_result,
        )

        quality_level, reasons = QualityGateEvaluator.evaluate(metrics)

        # Step 6: Create package (even if quality is low, as long as structure is valid)
        package_path, checksum = self.create_zip(
            skill_path,
            structure_result.skill_name or "skill",
            structure_result.skill_version or "0.1.0",
        )

        # Build warnings
        warnings = []
        warnings.extend([f"{i.path}: {i.message}" for i in structure_result.issues if i.severity == "warning"])
        warnings.extend(reasons)

        if quality_level == QualityLevel.FAILED:
            return PackageResult(
                success=False,
                quality_level=quality_level,
                skill_path=skill_path,
                package_path=package_path,
                checksum=checksum,
                metrics=metrics,
                structure_result=structure_result,
                test_result=test_result,
                security_issues=security_issues,
                warnings=warnings,
                failure_reason="Does not meet minimum quality standards (Alpha)",
                exit_code=ExitCode.VALIDATION_FAILED.value,
            )

        return PackageResult(
            success=True,
            quality_level=quality_level,
            skill_path=skill_path,
            package_path=package_path,
            checksum=checksum,
            metrics=metrics,
            structure_result=structure_result,
            test_result=test_result,
            security_issues=security_issues,
            warnings=warnings,
            exit_code=ExitCode.SUCCESS.value,
        )

    def validate_structure(self, skill_path: str | Path) -> StructureValidationResult:
        """Validate the structure of a skill before packaging.

        Args:
            skill_path: Path to the skill directory.

        Returns:
            StructureValidationResult with validation outcome.
        """
        validator = SkillStructureValidator(skill_path)
        return validator.validate()

    def run_tests(self, skill_path: str | Path) -> TestResult:
        """Run the test suite for a skill.

        Args:
            skill_path: Path to the skill directory.

        Returns:
            TestResult with test outcomes.
        """
        runner = SkillTestRunner(skill_path)
        return runner.run()

    def evaluate_quality(
        self,
        structure_result: StructureValidationResult,
        test_result: TestResult,
    ) -> Tuple[QualityLevel, QualityMetrics]:
        """Evaluate the quality of a skill based on validation results.

        Args:
            structure_result: Result from structure validation.
            test_result: Result from test execution.

        Returns:
            Tuple of (QualityLevel, QualityMetrics).
        """
        # Build metrics from results
        metrics = QualityMetrics()

        # Issue counts from structure validation
        for issue in structure_result.issues:
            severity = issue.severity
            if severity == "critical":
                metrics.critical_count += 1
            elif severity == "error" or severity == "high":
                metrics.high_count += 1
            elif severity == "warning" or severity == "medium":
                metrics.medium_count += 1
            elif severity == "low":
                metrics.low_count += 1
            else:
                metrics.info_count += 1

        # Test metrics
        metrics.tests_total = test_result.tests_run
        metrics.tests_passed = test_result.tests_passed
        metrics.tests_failed = test_result.tests_failed
        metrics.tests_skipped = test_result.tests_skipped
        metrics.coverage_percent = test_result.coverage_percent

        # Security issues
        metrics.secrets_found = len(structure_result.secret_locations)
        if metrics.secrets_found > 0:
            metrics.critical_count += metrics.secrets_found

        quality_level, _ = QualityGateEvaluator.evaluate(metrics)

        return quality_level, metrics

    def create_zip(
        self,
        skill_path: str | Path,
        skill_name: str,
        version: str,
    ) -> Tuple[Path, str]:
        """Create a distributable zip package for a skill.

        Args:
            skill_path: Path to the skill directory.
            skill_name: Name of the skill.
            version: Version of the skill.

        Returns:
            Tuple of (package_path, sha256_checksum).
        """
        skill_path = Path(skill_path).resolve()
        package_name = f"{skill_name}-{version}.zip"
        package_path = self.output_dir / package_name

        # Files to exclude
        exclude_dirs = {
            "__pycache__",
            ".git",
            ".pytest_cache",
            ".ruff_cache",
            ".mypy_cache",
            "node_modules",
            ".venv",
            "venv",
            ".eggs",
            "*.egg-info",
            "dist",
            "build",
        }

        exclude_files = {
            ".DS_Store",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".gitignore",
            ".env",
            ".env.local",
            "*.log",
        }

        with zipfile.ZipFile(package_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in skill_path.rglob("*"):
                if file_path.is_dir():
                    continue

                # Check exclusions
                if any(part in exclude_dirs for part in file_path.parts):
                    continue
                if file_path.name in exclude_files or file_path.suffix in {".pyc", ".pyo", ".pyd"}:
                    continue

                # Skip tests if not including them
                if not self.include_tests and "test" in file_path.parts:
                    continue

                # Add to zip with relative path
                arcname = file_path.relative_to(skill_path)
                zf.write(file_path, arcname)

        # Calculate checksum
        checksum = self._calculate_checksum(package_path)

        return package_path, checksum

    def _analyze_code(self, skill_path: Path) -> QualityMetrics:
        """Analyze code for quality metrics."""
        analyzer = CodeAnalyzer(skill_path)
        return analyzer.analyze()

    def _build_metrics(
        self,
        code_metrics: QualityMetrics,
        test_result: TestResult,
        security_issues: List[SecurityIssue],
        structure_result: StructureValidationResult,
    ) -> QualityMetrics:
        """Build complete metrics from all sources."""
        metrics = code_metrics

        # Add test results
        metrics.tests_total = test_result.tests_run
        metrics.tests_passed = test_result.tests_passed
        metrics.tests_failed = test_result.tests_failed
        metrics.tests_skipped = test_result.tests_skipped
        metrics.coverage_percent = test_result.coverage_percent

        # Add security issues
        metrics.secrets_found = len(security_issues)

        # Count issues from structure validation
        for issue in structure_result.issues:
            if issue.issue_type == "secret_detected":
                metrics.critical_count += 1
            elif issue.severity == "error":
                metrics.high_count += 1
            elif issue.severity == "warning":
                metrics.medium_count += 1

        # Count dependencies
        requirements_file = structure_result.skill_path.parent / "requirements.txt"
        if requirements_file.exists():
            metrics.dependencies_count = len([
                line for line in requirements_file.read_text().splitlines()
                if line.strip() and not line.startswith("#")
            ])

        return metrics

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _get_failure_reason(self, structure_result: StructureValidationResult) -> str:
        """Get a human-readable failure reason."""
        if structure_result.has_secrets:
            return f"Secrets detected in: {', '.join(structure_result.secret_locations[:3])}"

        if structure_result.missing_files:
            return f"Missing files: {', '.join(str(f) for f in structure_result.missing_files[:3])}"

        if structure_result.invalid_sections:
            return f"Missing required sections: {', '.join(structure_result.invalid_sections)}"

        if structure_result.yaml_errors:
            return f"YAML parsing errors: {structure_result.yaml_errors[0]}"

        return "Structure validation failed"

    def _get_exit_code(self, structure_result: StructureValidationResult) -> int:
        """Map structure validation failures to exit codes."""
        if structure_result.has_secrets:
            return ExitCode.SECRET_DETECTED.value
        if structure_result.missing_files:
            return ExitCode.DEPENDENCY_ERROR.value
        if structure_result.yaml_errors:
            return ExitCode.STRUCTURE_ERROR.value
        return ExitCode.STRUCTURE_ERROR.value


# =============================================================================
# CLI Interface
# =============================================================================

def main() -> int:
    """Command-line interface for the packager."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Package a skill with quality gate validation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exit Codes:
    0  Success (skill packaged)
    1  Validation failed (skill failed quality gates)
    2  Structure error (SKILL.md missing or invalid)
    3  Dependency error (required files or capabilities missing)
    4  Test failure (tests failed to run or all failed)
    5  Secret detection (hardcoded secrets found)
    6  Permission error (cannot read/write files)

Quality Levels:
    Production  0 critical, <=2 high, >=70% coverage
    Beta        <=1 critical, <=5 high, >=50% coverage
    Alpha       <=3 critical, <=10 high, >=30% coverage
    Failed      Exceeds Alpha thresholds

Examples:
    # Package a skill
    python packaging.py /path/to/skill

    # Specify output directory
    python packaging.py /path/to/skill -o ./dist

    # Generate JSON report
    python packaging.py /path/to/skill --json > report.json

    # Run without creating package (validation only)
    python packaging.py /path/to/skill --dry-run
        """,
    )

    parser.add_argument(
        "skill_path",
        type=str,
        help="Path to the skill directory",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Output directory for packages (default: /tmp/skill-packages)",
    )
    parser.add_argument(
        "--no-tests",
        action="store_true",
        help="Skip test execution",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate without creating package",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output",
    )

    args = parser.parse_args()

    # Configure logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Create packager
    packager = SkillPackager(output_dir=args.output)

    # Validate skill exists
    skill_path = Path(args.skill_path).resolve()
    if not skill_path.exists():
        print(f"Error: Skill path does not exist: {skill_path}", file=sys.stderr)
        return ExitCode.STRUCTURE_ERROR.value

    if not skill_path.is_dir():
        print(f"Error: Skill path is not a directory: {skill_path}", file=sys.stderr)
        return ExitCode.STRUCTURE_ERROR.value

    # Package the skill
    result = packager.package_skill(skill_path)

    # Output results
    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(result.to_report())

    return result.exit_code


if __name__ == "__main__":
    import logging
    sys.exit(main())
