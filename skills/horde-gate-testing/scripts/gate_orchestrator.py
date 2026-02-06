#!/usr/bin/env python3
"""
Gate Orchestrator for Phase-Gate Testing Workflow.

This script coordinates the full phase-gate-testing workflow, serving as the main
entry point that runs integration surface detection, generates tests, executes them,
and makes PASS/WARN/FAIL decisions.

Usage:
    python3 gate_orchestrator.py \
        --plan-path "docs/plans/neo4j.md" \
        --current-phase "Phase 1" \
        --next-phase "Phase 2" \
        --phase-paths "src/agent/" "src/config/" \
        --output "gate_report.md"

Exit Codes:
    0 - PASS: Safe to proceed to next phase
    1 - WARN: Proceed with caution, address warnings
    2 - FAIL: Do not proceed, fix issues first
"""

import argparse
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# Exit codes
EXIT_PASS = 0
EXIT_WARN = 1
EXIT_FAIL = 2


@dataclass
class Risk:
    """Represents a risk identified during assessment."""

    level: str
    issue: str

    def to_dict(self) -> dict[str, str]:
        return {"level": self.level, "issue": self.issue}


@dataclass
class GateDecision:
    """Represents the final gate decision."""

    status: str  # PASS, WARN, or FAIL
    exit_code: int
    risks: list[Risk] = field(default_factory=list)
    reasoning: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "exit_code": self.exit_code,
            "risks": [r.to_dict() for r in self.risks],
            "reasoning": self.reasoning,
        }


@dataclass
class TestResults:
    """Represents the results of test execution."""

    passed: list[dict[str, Any]] = field(default_factory=list)
    failed: list[dict[str, Any]] = field(default_factory=list)
    skipped: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)
    total: int = 0
    duration_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "errors": self.errors,
            "total": self.total,
            "duration_ms": self.duration_ms,
        }


@dataclass
class IntegrationSurface:
    """Represents the integration surface analysis."""

    exports: dict[str, Any] = field(default_factory=dict)
    dependencies: dict[str, Any] = field(default_factory=dict)
    contracts: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "exports": self.exports,
            "dependencies": self.dependencies,
            "contracts": self.contracts,
            "metadata": self.metadata,
        }


class GateOrchestrator:
    """
    Orchestrates the phase-gate testing workflow.

    This class coordinates the execution of integration surface detection,
    contract test generation, test execution, and risk assessment to make
    informed PASS/WARN/FAIL decisions for phase transitions.
    """

    def __init__(
        self,
        plan_path: str,
        current_phase: str,
        next_phase: str,
        phase_paths: list[str],
        output_path: str,
        scripts_dir: str | None = None,
        verbose: bool = False,
    ):
        """
        Initialize the gate orchestrator.

        Args:
            plan_path: Path to the phase plan document (e.g., docs/plans/neo4j.md)
            current_phase: Name of the current phase (e.g., "Phase 1")
            next_phase: Name of the next phase (e.g., "Phase 2")
            phase_paths: List of paths to code directories for the current phase
            output_path: Path where the gate report will be written
            scripts_dir: Directory containing helper scripts (default: same as this script)
            verbose: Enable verbose logging
        """
        # Validate plan_path first (without project root check since it's the anchor)
        self.plan_path = Path(plan_path).resolve()
        if not self.plan_path.exists():
            raise ValueError(f"Plan path does not exist: {self.plan_path}")

        self.current_phase = current_phase
        self.next_phase = next_phase
        self.phase_paths = [self._validate_path(Path(p), self.plan_path) for p in phase_paths]
        self.output_path = self._validate_path(Path(output_path), self.plan_path)
        self.scripts_dir = Path(scripts_dir) if scripts_dir else Path(__file__).parent
        self.verbose = verbose

        if verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        self.surface_analysis: IntegrationSurface | None = None
        self.test_results: TestResults | None = None
        self.generated_test_file: Path | None = None
        self.decision: GateDecision | None = None

        self.has_json_report = self._check_pytest_json_report()
        if not self.has_json_report:
            logger.warning("pytest-json-report not installed. JSON parsing will be limited.")

    def _check_pytest_json_report(self) -> bool:
        """Check if pytest-json-report plugin is available."""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "--help"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return "--json-report" in result.stdout
        except Exception:
            return False

    def _validate_path(self, path: Path, plan_path: Path | None = None, allow_absolute: bool = False) -> Path:
        """Validate that a path is within the project directory."""
        # Find project root: if plan_path is provided, find the project root by looking
        # for common markers (.git, pyproject.toml, etc.), otherwise use CWD
        if plan_path and plan_path.exists():
            # Start from plan's parent and walk up to find project root
            check_dir = plan_path.parent
            project_root = check_dir  # Default to plan's directory
            root_markers = ['.git', 'pyproject.toml', 'setup.py', 'docs', 'src']
            while check_dir != check_dir.parent:  # Stop at filesystem root
                if any((check_dir / marker).exists() for marker in root_markers):
                    project_root = check_dir
                    break
                check_dir = check_dir.parent
        else:
            project_root = Path.cwd().resolve()

        # Resolve path: if relative, resolve against project root
        if not path.is_absolute():
            resolved = (project_root / path).resolve()
        else:
            resolved = path.resolve()

        if not allow_absolute and not str(resolved).startswith(str(project_root)):
            raise ValueError(f"Path {path} is outside project directory {project_root}")

        return resolved

    def run(self) -> int:
        """
        Execute the full gate orchestration workflow.

        Returns:
            Exit code: 0 (PASS), 1 (WARN), or 2 (FAIL)
        """
        logger.info(f"Starting gate orchestration for {self.current_phase} -> {self.next_phase}")
        logger.debug(f"Plan path: {self.plan_path}")
        logger.debug(f"Phase paths: {self.phase_paths}")
        logger.debug(f"Output path: {self.output_path}")

        # Validate all paths at runtime to fail fast on path traversal attempts
        self._validate_path(self.plan_path, self.plan_path)
        for path in self.phase_paths:
            self._validate_path(path, self.plan_path)
        self._validate_path(self.output_path, self.plan_path)

        try:
            # Step 1: Run integration surface detection
            self._run_surface_detection()

            # Step 2: Generate contract tests
            self._generate_contract_tests()

            # Step 3: Execute generated tests
            self._execute_tests()

            # Step 4: Assess risks
            risks = self._assess_risks()

            # Step 5: Make decision
            self._make_decision(risks)

            # Step 6: Generate gate report
            self._generate_report()

            logger.info(f"Gate decision: {self.decision.status}")
            return self.decision.exit_code

        except Exception as e:
            logger.exception("Gate orchestration failed")
            self._handle_failure(str(e))
            return EXIT_FAIL

    def _run_surface_detection(self) -> None:
        """Run the integration surface detection script."""
        logger.info("Step 1: Detecting integration surface...")

        detector_script = self.scripts_dir / "detect_integration_surface.py"
        if not detector_script.exists():
            raise FileNotFoundError(f"Surface detector script not found: {detector_script}")

        # Use TemporaryDirectory context manager for automatic cleanup
        with tempfile.TemporaryDirectory() as tmpdir:
            surface_output = Path(tmpdir) / "surface.json"

            cmd = [
                sys.executable,
                str(detector_script),
                "--phase", self.current_phase,
                "--output", str(surface_output),
            ]

            # Surface detection expects --paths followed by all paths
            cmd.append("--paths")
            for path in self.phase_paths:
                cmd.append(str(path))

            logger.debug(f"Running: {' '.join(cmd)}")

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=300,  # 5 minutes for surface detection
                )
            except subprocess.TimeoutExpired:
                logger.error("Surface detection timed out after 300s")
                raise RuntimeError("Gate step timed out: surface detection exceeded 300 seconds")

            if self.verbose and result.stdout:
                logger.debug(f"Surface detector output:\n{result.stdout}")

            # Parse surface analysis results
            with open(surface_output, "r") as f:
                surface_data = json.load(f)

            self.surface_analysis = IntegrationSurface(
                exports=surface_data.get("exports", {}),
                dependencies=surface_data.get("dependencies", {}),
                contracts=surface_data.get("contracts", {}),
                metadata=surface_data.get("metadata", {}),
            )

            logger.info(
                f"Surface detection complete: "
                f"{len(self.surface_analysis.exports.get('functions', []))} functions, "
                f"{len(self.surface_analysis.exports.get('classes', []))} classes"
            )
        # Cleanup is automatic when exiting the context manager

    def _generate_contract_tests(self) -> None:
        """Run the contract test generation script."""
        logger.info("Step 2: Generating contract tests...")

        generator_script = self.scripts_dir / "generate_contract_tests.py"
        if not generator_script.exists():
            raise FileNotFoundError(f"Test generator script not found: {generator_script}")

        # Use TemporaryDirectory context manager for automatic cleanup
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            test_file = tmpdir_path / "contract_tests.py"
            surface_file = tmpdir_path / "surface.json"

            # Write surface analysis to temp file
            with open(surface_file, "w") as f:
                json.dump(self.surface_analysis.to_dict(), f, indent=2)

            cmd = [
                sys.executable,
                str(generator_script),
                "--surface", str(surface_file),
                "--output-dir", str(test_file.parent),
                "--framework", "pytest",
            ]

            if self.verbose:
                cmd.append("--verbose")

            logger.debug(f"Running: {' '.join(cmd)}")

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=60,  # 1 minute for test generation
                )
            except subprocess.TimeoutExpired:
                logger.error("Test generation timed out after 60s")
                raise RuntimeError("Gate step timed out: test generation exceeded 60 seconds")

            if self.verbose and result.stdout:
                logger.debug(f"Test generator output:\n{result.stdout}")

            # Find generated test files in the output directory
            generated_files = list(tmpdir_path.glob("test_*.py"))
            if not generated_files:
                raise RuntimeError("Test generation failed: no test files found in output directory")

            # For now, use the first (main) test file for execution
            # The generator creates test_{phase}_exports.py and test_{phase}_contracts.py
            test_file = generated_files[0]

            # Copy generated test file to a persistent location
            safe_phase_name = self.current_phase.replace(' ', '_').replace(':', '_')
            persistent_test_file = Path(tempfile.gettempdir()) / f"test_{safe_phase_name}_contract_tests.py"
            shutil.copy2(test_file, persistent_test_file)
            self.generated_test_file = persistent_test_file

            logger.info(f"Contract tests generated: {self.generated_test_file} (from {len(generated_files)} files)")
        # Cleanup of temp directory is automatic, but generated test file persists

    def _execute_tests(self) -> None:
        """Execute the generated contract tests."""
        logger.info("Step 3: Executing contract tests...")

        if not self.generated_test_file or not self.generated_test_file.exists():
            raise RuntimeError("Generated test file not found")

        # Use TemporaryDirectory context manager for automatic cleanup
        with tempfile.TemporaryDirectory() as tmpdir:
            results_output = Path(tmpdir) / "test_results.json"

            # Build pytest command based on json-report availability
            cmd = [
                sys.executable,
                "-m", "pytest",
                str(self.generated_test_file),
                "-v",
                "--tb=short",
            ]

            # Only add JSON report options if plugin is available
            if self.has_json_report:
                cmd.extend(["--json-report", "--json-report-file", str(results_output)])

            if self.verbose:
                cmd.append("-vv")

            logger.debug(f"Running: {' '.join(cmd)}")

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 minutes for test execution
                )
            except subprocess.TimeoutExpired:
                logger.error("Test execution timed out after 600s")
                raise RuntimeError("Gate step timed out: test execution exceeded 600 seconds")

            # pytest returns non-zero on test failures, which is expected
            if result.returncode != 0 and "passed" not in result.stdout and "failed" not in result.stdout:
                # Real error, not just test failures
                raise RuntimeError(f"Test execution failed: {result.stderr}")

            if self.verbose:
                logger.debug(f"Test output:\n{result.stdout}")

            # Parse test results
            if self.has_json_report:
                self._parse_test_results(str(results_output))
            else:
                self._parse_test_results_from_stdout(result.stdout)

            logger.info(
                f"Test execution complete: "
                f"{len(self.test_results.passed)} passed, "
                f"{len(self.test_results.failed)} failed, "
                f"{len(self.test_results.skipped)} skipped"
            )
        # Cleanup is automatic when exiting the context manager

    def _parse_test_results(self, results_file: str) -> None:
        """Parse pytest JSON report into TestResults."""
        try:
            with open(results_file, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # Fallback: parse from stdout if JSON report failed
            self._parse_test_results_from_stdout("")
            return

        tests = data.get("tests", [])
        summary = data.get("summary", {})

        passed = []
        failed = []
        skipped = []
        errors = []

        for test in tests:
            outcome = test.get("outcome", "")
            nodeid = test.get("nodeid", "")
            # Extract function name from nodeid
            func_name = nodeid.split("::")[-1] if "::" in nodeid else nodeid

            test_info = {
                "function": func_name,
                "nodeid": nodeid,
                "duration": test.get("call", {}).get("duration", 0),
            }

            if outcome == "passed":
                passed.append(test_info)
            elif outcome == "failed":
                test_info["error"] = test.get("call", {}).get("longrepr", "Unknown error")
                failed.append(test_info)
            elif outcome == "skipped":
                test_info["reason"] = test.get("setup", {}).get("longrepr", "Unknown reason")
                skipped.append(test_info)
            elif outcome == "error":
                test_info["error"] = test.get("setup", {}).get("longrepr", "Unknown error")
                errors.append(test_info)

        self.test_results = TestResults(
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            total=summary.get("total", len(tests)),
            duration_ms=summary.get("duration", 0) * 1000,
        )

    def _parse_test_results_from_stdout(self, stdout: str) -> None:
        """Fallback parser for test results from pytest stdout."""
        passed = []
        failed = []
        skipped = []
        errors = []

        # Parse summary line like "5 passed, 2 failed, 1 skipped"
        summary_pattern = r'(\d+)\s+passed(?:,\s+(\d+)\s+failed)?(?:,\s+(\d+)\s+skipped)?(?:,\s+(\d+)\s+error)?'
        summary_match = re.search(summary_pattern, stdout)

        passed_count = int(summary_match.group(1)) if summary_match and summary_match.group(1) else 0
        failed_count = int(summary_match.group(2)) if summary_match and summary_match.group(2) else 0
        skipped_count = int(summary_match.group(3)) if summary_match and summary_match.group(3) else 0
        error_count = int(summary_match.group(4)) if summary_match and summary_match.group(4) else 0

        # Parse individual test results from verbose output
        # Look for lines like "test_file.py::test_name PASSED" or "test_file.py::test_name FAILED"
        test_pattern = r'(\S+)::(\S+)\s+(PASSED|FAILED|SKIPPED|ERROR)'
        for match in re.finditer(test_pattern, stdout):
            nodeid = f"{match.group(1)}::{match.group(2)}"
            func_name = match.group(2)
            outcome = match.group(3).lower()

            test_info = {
                "function": func_name,
                "nodeid": nodeid,
                "duration": 0,
            }

            if outcome == "passed":
                passed.append(test_info)
            elif outcome == "failed":
                test_info["error"] = "Test failed (details unavailable without pytest-json-report)"
                failed.append(test_info)
            elif outcome == "skipped":
                test_info["reason"] = "Test skipped"
                skipped.append(test_info)
            elif outcome == "error":
                test_info["error"] = "Test error (details unavailable without pytest-json-report)"
                errors.append(test_info)

        # If we couldn't parse individual tests but have counts, create placeholder entries
        if not passed and passed_count > 0:
            for i in range(passed_count):
                passed.append({
                    "function": f"test_{i+1}",
                    "nodeid": f"unknown::test_{i+1}",
                    "duration": 0,
                })

        if not failed and failed_count > 0:
            for i in range(failed_count):
                failed.append({
                    "function": f"test_{i+1}",
                    "nodeid": f"unknown::test_{i+1}",
                    "duration": 0,
                    "error": "Test failed (details unavailable without pytest-json-report)",
                })

        if not skipped and skipped_count > 0:
            for i in range(skipped_count):
                skipped.append({
                    "function": f"test_{i+1}",
                    "nodeid": f"unknown::test_{i+1}",
                    "duration": 0,
                    "reason": "Test skipped",
                })

        if not errors and error_count > 0:
            for i in range(error_count):
                errors.append({
                    "function": f"test_{i+1}",
                    "nodeid": f"unknown::test_{i+1}",
                    "duration": 0,
                    "error": "Test error (details unavailable without pytest-json-report)",
                })

        total = passed_count + failed_count + skipped_count + error_count

        self.test_results = TestResults(
            passed=passed,
            failed=failed,
            skipped=skipped,
            errors=errors,
            total=total,
            duration_ms=0.0,
        )

        if not self.has_json_report:
            logger.info(f"Parsed test results from stdout: {passed_count} passed, {failed_count} failed, {skipped_count} skipped")

    def _assess_risks(self) -> list[Risk]:
        """
        Assess risks based on test results and surface analysis.

        Returns:
            List of identified risks
        """
        logger.info("Step 4: Assessing risks...")

        risks: list[Risk] = []

        if not self.surface_analysis or not self.test_results:
            risks.append(Risk("HIGH", "Incomplete analysis - missing surface or test data"))
            return risks

        # High risk: Missing critical exports
        functions = self.surface_analysis.exports.get("functions", [])
        if not functions:
            risks.append(Risk("HIGH", "No functions exported from current phase"))

        classes = self.surface_analysis.exports.get("classes", [])
        if not functions and not classes:
            risks.append(Risk("HIGH", "No exports (functions or classes) found"))

        # Medium risk: Untested exports
        tested = set(r["function"] for r in self.test_results.passed)
        exported = set(f.get("name", "") for f in functions)
        exported.update(c.get("name", "") for c in classes)

        untested = exported - tested
        if untested:
            risks.append(
                Risk("MEDIUM", f"Untested exports: {', '.join(sorted(untested))}")
            )

        # High risk: Test failures
        if self.test_results.failed:
            count = len(self.test_results.failed)
            risks.append(Risk("HIGH", f"{count} contract test(s) failed"))

        # High risk: Test errors (setup/teardown issues)
        if self.test_results.errors:
            count = len(self.test_results.errors)
            risks.append(Risk("HIGH", f"{count} test error(s) occurred"))

        # Medium risk: Low test coverage
        if exported:
            coverage = len(tested) / len(exported) * 100
            if coverage < 50:
                risks.append(
                    Risk("MEDIUM", f"Low test coverage: {coverage:.1f}% ({len(tested)}/{len(exported)})")
                )

        # Low risk: Missing documentation
        if not self.surface_analysis.metadata.get("has_documentation", True):
            risks.append(Risk("LOW", "Missing or incomplete documentation"))

        logger.info(f"Risk assessment complete: {len(risks)} risk(s) identified")
        for risk in risks:
            logger.debug(f"  [{risk.level}] {risk.issue}")

        return risks

    def _make_decision(self, risks: list[Risk]) -> None:
        """
        Make the final PASS/WARN/FAIL decision based on risks.

        Args:
            risks: List of identified risks
        """
        logger.info("Step 5: Making gate decision...")

        high_risks = [r for r in risks if r.level == "HIGH"]
        medium_risks = [r for r in risks if r.level == "MEDIUM"]

        if high_risks:
            status = "FAIL"
            exit_code = EXIT_FAIL
            reasoning = (
                f"Gate FAILED due to {len(high_risks)} high-risk issue(s). "
                "Resolve these issues before proceeding to the next phase."
            )
        elif medium_risks:
            status = "WARN"
            exit_code = EXIT_WARN
            reasoning = (
                f"Gate PASSED with WARNINGS: {len(medium_risks)} medium-risk issue(s) found. "
                "Review and address these issues before or during the next phase."
            )
        else:
            status = "PASS"
            exit_code = EXIT_PASS
            reasoning = (
                "Gate PASSED. All contract tests passed with no significant risks identified. "
                "Safe to proceed to the next phase."
            )

        self.decision = GateDecision(
            status=status,
            exit_code=exit_code,
            risks=risks,
            reasoning=reasoning,
        )

        logger.info(f"Decision: {status} (exit code {exit_code})")

    def _generate_report(self) -> None:
        """Generate the gate report in Markdown format."""
        logger.info("Step 6: Generating gate report...")

        report = self._build_markdown_report()

        # Ensure output directory exists
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.output_path, "w") as f:
            f.write(report)

        logger.info(f"Gate report written to: {self.output_path}")

    def _build_markdown_report(self) -> str:
        """Build the Markdown gate report."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines = [
            "# Phase Gate Report",
            "",
            "## Summary",
            "",
            f"| Field | Value |",
            f"|-------|-------|",
            f"| **Current Phase** | {self.current_phase} |",
            f"| **Next Phase** | {self.next_phase} |",
            f"| **Decision** | {'✅' if self.decision.status == 'PASS' else '⚠️' if self.decision.status == 'WARN' else '❌'} {self.decision.status} |",
            f"| **Generated** | {timestamp} |",
            f"| **Plan Document** | `{self.plan_path}` |",
            "",
            f"### Decision Reasoning",
            "",
            f"{self.decision.reasoning}",
            "",
            "---",
            "",
            "## Integration Surface",
            "",
        ]

        # Integration Surface Section
        if self.surface_analysis:
            lines.extend([
                "### Exported Functions",
                "",
            ])

            functions = self.surface_analysis.exports.get("functions", [])
            if functions:
                lines.extend([
                    "| Function | Signature | Description |",
                    "|----------|-----------|-------------|",
                ])
                for func in functions:
                    name = func.get("name", "unknown")
                    sig = func.get("signature", "N/A")
                    desc = func.get("description", "No description")
                    lines.append(f"| `{name}` | `{sig}` | {desc} |")
                lines.append("")
            else:
                lines.append("*No functions exported*\n")

            lines.extend([
                "### Exported Classes",
                "",
            ])

            classes = self.surface_analysis.exports.get("classes", [])
            if classes:
                lines.extend([
                    "| Class | Methods | Description |",
                    "|-------|---------|-------------|",
                ])
                for cls in classes:
                    name = cls.get("name", "unknown")
                    methods = ", ".join(cls.get("methods", [])) or "N/A"
                    desc = cls.get("description", "No description")
                    lines.append(f"| `{name}` | {methods} | {desc} |")
                lines.append("")
            else:
                lines.append("*No classes exported*\n")

            # Dependencies
            deps = self.surface_analysis.dependencies.get("external", [])
            if deps:
                lines.extend([
                    "### External Dependencies",
                    "",
                    "| Dependency | Version |",
                    "|------------|---------|",
                ])
                for dep in deps:
                    name = dep.get("name", "unknown")
                    version = dep.get("version", "*")
                    lines.append(f"| `{name}` | {version} |")
                lines.append("")
        else:
            lines.append("*Integration surface analysis not available*\n")

        lines.append("---\n")

        # Test Results Section
        lines.extend([
            "## Test Results",
            "",
        ])

        if self.test_results:
            lines.extend([
                "### Summary",
                "",
                f"| Metric | Value |",
                f"|--------|-------|",
                f"| **Total Tests** | {self.test_results.total} |",
                f"| **Passed** | {len(self.test_results.passed)} ✅ |",
                f"| **Failed** | {len(self.test_results.failed)} {'❌' if self.test_results.failed else ''} |",
                f"| **Skipped** | {len(self.test_results.skipped)} |",
                f"| **Errors** | {len(self.test_results.errors)} |",
                f"| **Duration** | {self.test_results.duration_ms:.2f} ms |",
                "",
            ])

            if self.test_results.passed:
                lines.extend([
                    "### Passed Tests",
                    "",
                ])
                for test in self.test_results.passed:
                    lines.append(f"- ✅ `{test['function']}` ({test.get('duration', 0):.3f}s)")
                lines.append("")

            if self.test_results.failed:
                lines.extend([
                    "### Failed Tests",
                    "",
                ])
                for test in self.test_results.failed:
                    lines.append(f"- ❌ `{test['function']}`")
                    error = test.get("error", "Unknown error")
                    lines.append(f"  - Error: `{error[:200]}{'...' if len(error) > 200 else ''}`")
                lines.append("")

            if self.test_results.skipped:
                lines.extend([
                    "### Skipped Tests",
                    "",
                ])
                for test in self.test_results.skipped:
                    reason = test.get("reason", "Unknown reason")
                    lines.append(f"- ⏭️ `{test['function']}` - {reason}")
                lines.append("")
        else:
            lines.append("*Test results not available*\n")

        lines.append("---\n")

        # Risk Assessment Section
        lines.extend([
            "## Risk Assessment",
            "",
        ])

        if self.decision.risks:
            lines.extend([
                "| Level | Issue |",
                "|-------|-------|",
            ])
            for risk in self.decision.risks:
                icon = "🔴" if risk.level == "HIGH" else "🟡" if risk.level == "MEDIUM" else "🟢"
                lines.append(f"| {icon} {risk.level} | {risk.issue} |")
            lines.append("")
        else:
            lines.append("*No risks identified*\n")

        lines.append("---\n")

        # Recommendations Section
        lines.extend([
            "## Recommendations",
            "",
        ])

        if self.decision.status == "PASS":
            lines.extend([
                "- ✅ All checks passed - safe to proceed to the next phase",
                "- 📋 Review the integration surface for any undocumented features",
                "- 🔄 Continue monitoring test coverage as the project evolves",
            ])
        elif self.decision.status == "WARN":
            lines.extend([
                "- ⚠️ Address medium-risk issues before or during the next phase",
                "- 📝 Consider adding tests for untested exports",
                "- 📊 Review test coverage and add tests for critical paths",
            ])
        else:  # FAIL
            lines.extend([
                "- ❌ **DO NOT PROCEED** to the next phase until high-risk issues are resolved",
                "- 🔧 Fix all failing tests before continuing",
                "- 📚 Ensure all critical exports are properly tested",
                "- 🏗️ Review the integration surface for missing exports",
            ])

        lines.extend([
            "",
            "---",
            "",
            "## Next Steps",
            "",
        ])

        if self.decision.status == "PASS":
            lines.extend([
                f"1. Proceed with {self.next_phase} implementation",
                "2. Update documentation with new integration surface",
                "3. Schedule next gate review",
            ])
        elif self.decision.status == "WARN":
            lines.extend([
                f"1. Review warnings above",
                f"2. Optionally proceed to {self.next_phase} with caution",
                "3. Create tickets to address warnings",
                "4. Monitor these issues during next phase",
            ])
        else:
            lines.extend([
                "1. **STOP** - Do not proceed to next phase",
                "2. Address all HIGH risk issues listed above",
                "3. Re-run gate orchestration after fixes",
                "4. Obtain approval before proceeding",
            ])

        lines.extend([
            "",
            "---",
            "",
            "*Generated by Phase Gate Testing Framework*",
        ])

        return "\n".join(lines)

    def _handle_failure(self, error_message: str) -> None:
        """Handle orchestration failure by generating a failure report."""
        logger.error(f"Orchestration failed: {error_message}")

        self.decision = GateDecision(
            status="FAIL",
            exit_code=EXIT_FAIL,
            risks=[Risk("HIGH", f"Orchestration failure: {error_message}")],
            reasoning=f"Gate FAILED due to orchestration error: {error_message}",
        )

        # Still try to generate a report
        try:
            self._generate_report()
        except Exception as e:
            logger.error(f"Could not generate failure report: {e}")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Gate Orchestrator for Phase-Gate Testing Workflow",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Basic usage
    python3 gate_orchestrator.py \
        --plan-path "docs/plans/neo4j.md" \
        --current-phase "Phase 1" \
        --next-phase "Phase 2" \
        --phase-paths "src/agent/" "src/config/"

    # With custom output and verbose logging
    python3 gate_orchestrator.py \
        --plan-path "docs/plans/api.md" \
        --current-phase "Phase 3" \
        --next-phase "Phase 4" \
        --phase-paths "src/api/" "src/models/" \
        --output "reports/gate_report.md" \
        --verbose

Exit Codes:
    0 - PASS: Safe to proceed to next phase
    1 - WARN: Proceed with caution, address warnings
    2 - FAIL: Do not proceed, fix issues first
        """,
    )

    parser.add_argument(
        "--plan-path",
        required=True,
        help="Path to the phase plan document (e.g., docs/plans/neo4j.md)",
    )

    parser.add_argument(
        "--current-phase",
        required=True,
        help="Name of the current phase (e.g., 'Phase 1')",
    )

    parser.add_argument(
        "--next-phase",
        required=True,
        help="Name of the next phase (e.g., 'Phase 2')",
    )

    parser.add_argument(
        "--phase-paths",
        nargs="+",
        required=True,
        help="Paths to code directories for the current phase",
    )

    parser.add_argument(
        "--output",
        default="gate_report.md",
        help="Path where the gate report will be written (default: gate_report.md)",
    )

    parser.add_argument(
        "--scripts-dir",
        help="Directory containing helper scripts (default: same as this script)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_args()

    orchestrator = GateOrchestrator(
        plan_path=args.plan_path,
        current_phase=args.current_phase,
        next_phase=args.next_phase,
        phase_paths=args.phase_paths,
        output_path=args.output,
        scripts_dir=args.scripts_dir,
        verbose=args.verbose,
    )

    return orchestrator.run()


if __name__ == "__main__":
    sys.exit(main())
