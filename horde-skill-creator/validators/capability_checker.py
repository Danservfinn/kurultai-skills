"""
Capability Checker

Checks the availability of required MCP servers, agents, environment variables,
and system resources before skill execution. Returns capability status with
degradation levels for planning fallback behavior.

Example:
    ```python
    from capability_checker import (
        CapabilityChecker,
        CapabilityStatus,
        check_mcp_server,
        check_env_vars,
    )

    checker = CapabilityChecker()

    # Check a single MCP server
    status = check_mcp_server("filesystem")
    if status == CapabilityStatus.AVAILABLE:
        print("Filesystem operations available")

    # Check multiple dependencies
    result = checker.check_all(
        mcp_servers=["filesystem", "memory"],
        env_vars=["OPENAI_API_KEY", "DATABASE_URL"],
    )

    if result.can_proceed:
        execute_skill()
    elif result.degradation_level == DegradationLevel.DEGRADED:
        execute_with_fallbacks()
    else:
        raise Exception("Required capabilities unavailable")
    ```

Capability Status Levels:
    - AVAILABLE: Full capability, no issues
    - UNAVAILABLE: Capability missing, operation impossible
    - DEGRADED: Partially available, reduced functionality
"""

from __future__ import annotations

import asyncio
import os
import subprocess
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any


class CapabilityStatus(Enum):
    """Status of a capability check."""

    AVAILABLE = auto()      # Fully available, ready to use
    UNAVAILABLE = auto()    # Not available, cannot proceed
    DEGRADED = auto()       # Partially available, limited functionality
    UNKNOWN = auto()        # Status cannot be determined


class DegradationLevel(Enum):
    """Overall system degradation level."""

    FULL = auto()           # All capabilities available
    DEGRADED = auto()       # Some capabilities degraded or missing
    MINIMAL = auto()        # Only core capabilities available
    OFFLINE = auto()        # Critical capabilities missing


class ResourceType(Enum):
    """Types of resources that can be checked."""

    MCP_SERVER = auto()
    AGENT = auto()
    ENV_VAR = auto()
    FILE = auto()
    DIRECTORY = auto()
    COMMAND = auto()
    NETWORK = auto()
    PYTHON_PACKAGE = auto()
    API_ENDPOINT = auto()


@dataclass
class CapabilityResult:
    """Result of a single capability check.

    Attributes:
        resource_type: Type of resource checked
        resource_name: Name/identifier of the resource
        status: The capability status
        message: Human-readable status message
        details: Additional details about the capability
        degradation_info: Information about degradation if applicable
    """

    resource_type: ResourceType
    resource_name: str
    status: CapabilityStatus
    message: str
    details: dict[str, Any] = field(default_factory=dict)
    degradation_info: str | None = None

    @property
    def is_available(self) -> bool:
        """Check if capability is available (including degraded)."""
        return self.status in (CapabilityStatus.AVAILABLE, CapabilityStatus.DEGRADED)

    @property
    def is_fully_available(self) -> bool:
        """Check if capability is fully available."""
        return self.status == CapabilityStatus.AVAILABLE

    def to_dict(self) -> dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "resource_type": self.resource_type.name,
            "resource_name": self.resource_name,
            "status": self.status.name,
            "message": self.message,
            "details": self.details,
            "degradation_info": self.degradation_info,
        }


@dataclass
class CapabilityReport:
    """Aggregated report of multiple capability checks.

    Attributes:
        results: Individual capability check results
        degradation_level: Overall system degradation level
        can_proceed: Whether execution can proceed
        missing_required: List of required but missing capabilities
        available_capabilities: List of available capabilities
    """

    results: list[CapabilityResult] = field(default_factory=list)
    degradation_level: DegradationLevel = DegradationLevel.FULL
    can_proceed: bool = True
    missing_required: list[str] = field(default_factory=list)
    available_capabilities: list[str] = field(default_factory=list)

    def add_result(self, result: CapabilityResult) -> None:
        """Add a capability check result and update overall status."""
        self.results.append(result)

        if result.is_available:
            self.available_capabilities.append(result.resource_name)
        else:
            self.missing_required.append(result.resource_name)

        self._recalculate_status()

    def _recalculate_status(self) -> None:
        """Recalculate overall degradation level and proceed status."""
        unavailable = [r for r in self.results if r.status == CapabilityStatus.UNAVAILABLE]
        degraded = [r for r in self.results if r.status == CapabilityStatus.DEGRADED]

        total = len(self.results)
        unavailable_count = len(unavailable)
        degraded_count = len(degraded)

        if total == 0:
            self.degradation_level = DegradationLevel.FULL
            self.can_proceed = True
            return

        # Calculate degradation level
        if unavailable_count == 0:
            if degraded_count == 0:
                self.degradation_level = DegradationLevel.FULL
            else:
                self.degradation_level = DegradationLevel.DEGRADED
        elif unavailable_count <= total * 0.3:
            self.degradation_level = DegradationLevel.DEGRADED
        elif unavailable_count <= total * 0.7:
            self.degradation_level = DegradationLevel.MINIMAL
        else:
            self.degradation_level = DegradationLevel.OFFLINE

        # Can proceed if not offline and no critical failures
        self.can_proceed = self.degradation_level != DegradationLevel.OFFLINE

    def get_by_type(self, resource_type: ResourceType) -> list[CapabilityResult]:
        """Get all results for a specific resource type."""
        return [r for r in self.results if r.resource_type == resource_type]

    def get_unavailable(self) -> list[CapabilityResult]:
        """Get all unavailable capabilities."""
        return [r for r in self.results if r.status == CapabilityStatus.UNAVAILABLE]

    def get_degraded(self) -> list[CapabilityResult]:
        """Get all degraded capabilities."""
        return [r for r in self.results if r.status == CapabilityStatus.DEGRADED]

    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "degradation_level": self.degradation_level.name,
            "can_proceed": self.can_proceed,
            "missing_required": self.missing_required,
            "available_capabilities": self.available_capabilities,
            "results": [r.to_dict() for r in self.results],
            "summary": {
                "total": len(self.results),
                "available": len(self.available_capabilities),
                "unavailable": len(self.missing_required),
                "degraded": len(self.get_degraded()),
            },
        }

    def format_report(self) -> str:
        """Format the report as a readable string."""
        lines = [
            f"Capability Report",
            f"=================",
            f"Overall Status: {self.degradation_level.name}",
            f"Can Proceed: {self.can_proceed}",
            f"",
            f"Summary:",
            f"  Total Checks: {len(self.results)}",
            f"  Available: {len(self.available_capabilities)}",
            f"  Unavailable: {len(self.missing_required)}",
            f"  Degraded: {len(self.get_degraded())}",
        ]

        if self.get_unavailable():
            lines.append("")
            lines.append("Unavailable:")
            for r in self.get_unavailable():
                lines.append(f"  - {r.resource_name}: {r.message}")

        if self.get_degraded():
            lines.append("")
            lines.append("Degraded:")
            for r in self.get_degraded():
                lines.append(f"  - {r.resource_name}: {r.message}")
                if r.degradation_info:
                    lines.append(f"    {r.degradation_info}")

        return "\n".join(lines)


class CapabilityChecker:
    """Main capability checking coordinator.

    Provides methods to check various types of capabilities and
    generates aggregated reports.

    Example:
        ```python
        checker = CapabilityChecker()

        report = checker.check_all(
            mcp_servers=["filesystem", "memory"],
            env_vars=["API_KEY"],
            files=["/path/to/config.yaml"],
        )

        if not report.can_proceed:
            print(report.format_report())
        ```
    """

    def __init__(self, timeout: float = 5.0) -> None:
        """Initialize the capability checker.

        Args:
            timeout: Default timeout for capability checks
        """
        self.timeout = timeout
        self._cache: dict[str, CapabilityResult] = {}

    def check_mcp_server(self, server_name: str) -> CapabilityResult:
        """Check if an MCP server is available.

        Args:
            server_name: Name of the MCP server to check

        Returns:
            CapabilityResult with availability status
        """
        cache_key = f"mcp:{server_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Check via Claude's MCP server list
        try:
            from ListMcpResourcesTool import list_mcp_resources
            # Try to list resources from the server
            resources = list_mcp_resources(server=server_name)
            status = CapabilityStatus.AVAILABLE
            message = f"MCP server '{server_name}' is available"
            details = {"resource_count": len(resources) if resources else 0}
        except ImportError:
            # Running outside Claude environment
            status = CapabilityStatus.UNKNOWN
            message = f"Cannot check MCP server '{server_name}' - no Claude environment"
            details = {"reason": "no_mcp_module"}
        except Exception as e:
            status = CapabilityStatus.UNAVAILABLE
            message = f"MCP server '{server_name}' is not available"
            details = {"error": str(e)}

        result = CapabilityResult(
            resource_type=ResourceType.MCP_SERVER,
            resource_name=server_name,
            status=status,
            message=message,
            details=details,
        )
        self._cache[cache_key] = result
        return result

    def check_env_var(
        self,
        var_name: str,
        required: bool = True,
        allow_empty: bool = False,
    ) -> CapabilityResult:
        """Check if an environment variable is set.

        Args:
            var_name: Name of the environment variable
            required: Whether the variable is required
            allow_empty: Whether empty string values are acceptable

        Returns:
            CapabilityResult with availability status
        """
        cache_key = f"env:{var_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        value = os.environ.get(var_name)

        if value is None:
            if required:
                status = CapabilityStatus.UNAVAILABLE
                message = f"Required environment variable '{var_name}' is not set"
            else:
                status = CapabilityStatus.DEGRADED
                message = f"Optional environment variable '{var_name}' is not set"
        elif not value and not allow_empty:
            status = CapabilityStatus.DEGRADED
            message = f"Environment variable '{var_name}' is empty"
        else:
            status = CapabilityStatus.AVAILABLE
            message = f"Environment variable '{var_name}' is set"
            # Don't include the actual value in details for security
            value = value[:4] + "..." if len(value) > 8 else "..." if value else ""

        result = CapabilityResult(
            resource_type=ResourceType.ENV_VAR,
            resource_name=var_name,
            status=status,
            message=message,
            details={"value_preview": value if value else None},
        )
        self._cache[cache_key] = result
        return result

    def check_env_vars(
        self,
        var_names: list[str],
        required: bool = True,
        allow_empty: bool = False,
    ) -> list[CapabilityResult]:
        """Check multiple environment variables.

        Args:
            var_names: List of environment variable names
            required: Whether variables are required
            allow_empty: Whether empty values are acceptable

        Returns:
            List of CapabilityResults
        """
        return [
            self.check_env_var(name, required, allow_empty)
            for name in var_names
        ]

    def check_file(
        self,
        file_path: str | Path,
        required: bool = True,
    ) -> CapabilityResult:
        """Check if a file exists and is readable.

        Args:
            file_path: Path to the file
            required: Whether the file is required

        Returns:
            CapabilityResult with availability status
        """
        path = Path(file_path)
        cache_key = f"file:{path}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if path.exists():
            if path.is_file():
                if os.access(path, os.R_OK):
                    status = CapabilityStatus.AVAILABLE
                    message = f"File '{file_path}' exists and is readable"
                    details = {"size": path.stat().st_size}
                else:
                    status = CapabilityStatus.DEGRADED
                    message = f"File '{file_path}' exists but is not readable"
                    details = {}
            else:
                status = CapabilityStatus.DEGRADED
                message = f"Path '{file_path}' exists but is not a file"
                details = {}
        else:
            if required:
                status = CapabilityStatus.UNAVAILABLE
                message = f"Required file '{file_path}' does not exist"
            else:
                status = CapabilityStatus.DEGRADED
                message = f"Optional file '{file_path}' does not exist"
            details = {}

        result = CapabilityResult(
            resource_type=ResourceType.FILE,
            resource_name=str(file_path),
            status=status,
            message=message,
            details=details,
        )
        self._cache[cache_key] = result
        return result

    def check_directory(
        self,
        dir_path: str | Path,
        writable: bool = False,
        required: bool = True,
    ) -> CapabilityResult:
        """Check if a directory exists and is accessible.

        Args:
            dir_path: Path to the directory
            writable: Whether write access is required
            required: Whether the directory is required

        Returns:
            CapabilityResult with availability status
        """
        path = Path(dir_path)
        cache_key = f"dir:{path}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if path.exists():
            if path.is_dir():
                readable = os.access(path, os.R_OK)
                can_write = os.access(path, os.W_OK)

                if readable and (not writable or can_write):
                    status = CapabilityStatus.AVAILABLE
                    message = f"Directory '{dir_path}' is accessible"
                    details = {"writable": can_write}
                elif readable:
                    status = CapabilityStatus.DEGRADED
                    message = f"Directory '{dir_path}' is read-only"
                    details = {"writable": False}
                else:
                    status = CapabilityStatus.UNAVAILABLE
                    message = f"Directory '{dir_path}' is not accessible"
                    details = {}
            else:
                status = CapabilityStatus.DEGRADED
                message = f"Path '{dir_path}' exists but is not a directory"
                details = {}
        else:
            # Try to create the directory
            try:
                path.mkdir(parents=True, exist_ok=True)
                status = CapabilityStatus.AVAILABLE
                message = f"Directory '{dir_path}' created"
                details = {"created": True}
            except Exception:
                if required:
                    status = CapabilityStatus.UNAVAILABLE
                    message = f"Required directory '{dir_path}' does not exist"
                else:
                    status = CapabilityStatus.DEGRADED
                    message = f"Optional directory '{dir_path}' does not exist"
                details = {}

        result = CapabilityResult(
            resource_type=ResourceType.DIRECTORY,
            resource_name=str(dir_path),
            status=status,
            message=message,
            details=details,
        )
        self._cache[cache_key] = result
        return result

    def check_command(self, command: str) -> CapabilityResult:
        """Check if a command is available on the system.

        Args:
            command: Command name to check

        Returns:
            CapabilityResult with availability status
        """
        cache_key = f"cmd:{command}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            result = subprocess.run(
                ["which", command],
                capture_output=True,
                timeout=1.0,
            )
            if result.returncode == 0:
                status = CapabilityStatus.AVAILABLE
                message = f"Command '{command}' is available"
                details = {"path": result.stdout.decode().strip()}
            else:
                status = CapabilityStatus.UNAVAILABLE
                message = f"Command '{command}' not found"
                details = {}
        except subprocess.TimeoutExpired:
            status = CapabilityStatus.UNKNOWN
            message = f"Command check for '{command}' timed out"
            details = {}
        except Exception as e:
            status = CapabilityStatus.UNKNOWN
            message = f"Could not check command '{command}': {e}"
            details = {}

        return CapabilityResult(
            resource_type=ResourceType.COMMAND,
            resource_name=command,
            status=status,
            message=message,
            details=details,
        )

    def check_python_package(self, package_name: str) -> CapabilityResult:
        """Check if a Python package is installed.

        Args:
            package_name: Name of the package (import name)

        Returns:
            CapabilityResult with availability status
        """
        cache_key = f"pkg:{package_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            __import__(package_name)
            status = CapabilityStatus.AVAILABLE
            message = f"Python package '{package_name}' is installed"
            details = {}
        except ImportError:
            status = CapabilityStatus.UNAVAILABLE
            message = f"Python package '{package_name}' is not installed"
            details = {}
        except Exception as e:
            status = CapabilityStatus.DEGRADED
            message = f"Error checking package '{package_name}': {e}"
            details = {}

        result = CapabilityResult(
            resource_type=ResourceType.PYTHON_PACKAGE,
            resource_name=package_name,
            status=status,
            message=message,
            details=details,
        )
        self._cache[cache_key] = result
        return result

    def check_network(
        self,
        host: str,
        port: int,
        timeout: float | None = None,
    ) -> CapabilityResult:
        """Check if a network endpoint is reachable.

        Args:
            host: Hostname or IP address
            port: Port number
            timeout: Connection timeout in seconds

        Returns:
            CapabilityResult with availability status
        """
        import socket

        timeout = timeout or self.timeout
        cache_key = f"net:{host}:{port}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()

            if result == 0:
                status = CapabilityStatus.AVAILABLE
                message = f"Network endpoint '{host}:{port}' is reachable"
            else:
                status = CapabilityStatus.UNAVAILABLE
                message = f"Network endpoint '{host}:{port}' is not reachable"
            details = {}
        except socket.gaierror:
            status = CapabilityStatus.UNAVAILABLE
            message = f"Cannot resolve host '{host}'"
            details = {}
        except Exception as e:
            status = CapabilityStatus.UNKNOWN
            message = f"Error checking network '{host}:{port}': {e}"
            details = {}

        return CapabilityResult(
            resource_type=ResourceType.NETWORK,
            resource_name=f"{host}:{port}",
            status=status,
            message=message,
            details=details,
        )

    def check_all(
        self,
        mcp_servers: list[str] | None = None,
        env_vars: list[str] | None = None,
        files: list[str] | None = None,
        directories: list[str] | None = None,
        commands: list[str] | None = None,
        packages: list[str] | None = None,
    ) -> CapabilityReport:
        """Check multiple capabilities and generate aggregated report.

        Args:
            mcp_servers: List of MCP server names to check
            env_vars: List of environment variable names to check
            files: List of file paths to check
            directories: List of directory paths to check
            commands: List of commands to check
            packages: List of Python packages to check

        Returns:
            CapabilityReport with aggregated results
        """
        report = CapabilityReport()

        if mcp_servers:
            for server in mcp_servers:
                report.add_result(self.check_mcp_server(server))

        if env_vars:
            for var in env_vars:
                report.add_result(self.check_env_var(var))

        if files:
            for file_path in files:
                report.add_result(self.check_file(file_path))

        if directories:
            for dir_path in directories:
                report.add_result(self.check_directory(dir_path))

        if commands:
            for cmd in commands:
                report.add_result(self.check_command(cmd))

        if packages:
            for pkg in packages:
                report.add_result(self.check_python_package(pkg))

        return report

    def clear_cache(self) -> None:
        """Clear the capability check cache."""
        self._cache.clear()


# Convenience functions
def check_mcp_server(server_name: str) -> CapabilityStatus:
    """Quick check for MCP server availability."""
    checker = CapabilityChecker()
    result = checker.check_mcp_server(server_name)
    return result.status


def check_env_var(var_name: str, required: bool = True) -> CapabilityStatus:
    """Quick check for environment variable availability."""
    checker = CapabilityChecker()
    result = checker.check_env_var(var_name, required)
    return result.status


def check_file_exists(file_path: str) -> CapabilityStatus:
    """Quick check for file existence."""
    checker = CapabilityChecker()
    result = checker.check_file(file_path)
    return result.status


def check_package_installed(package_name: str) -> CapabilityStatus:
    """Quick check for Python package installation."""
    checker = CapabilityChecker()
    result = checker.check_python_package(package_name)
    return result.status


__all__ = [
    "CapabilityStatus",
    "DegradationLevel",
    "ResourceType",
    "CapabilityResult",
    "CapabilityReport",
    "CapabilityChecker",
    # Convenience functions
    "check_mcp_server",
    "check_env_var",
    "check_file_exists",
    "check_package_installed",
]
