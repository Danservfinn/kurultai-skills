#!/usr/bin/env python3
"""
Audit script for checking implementation phase completion.
Called by audit subagents to verify phase status.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def check_files_exist(files: List[str]) -> Dict[str, bool]:
    """Check if required files exist."""
    return {f: Path(f).exists() for f in files}


def check_file_contains(filepath: str, markers: List[str]) -> Dict[str, bool]:
    """Check if file contains expected implementation markers."""
    path = Path(filepath)
    if not path.exists():
        return {m: False for m in markers}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return {m: m in content for m in markers}
    except (OSError, IOError):
        return {m: False for m in markers}


def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate the phase configuration structure.

    Args:
        config: Configuration dict to validate

    Raises:
        ValueError: If config structure is invalid
    """
    if not isinstance(config, dict):
        raise ValueError("Config must be a dictionary")

    if "name" not in config:
        raise ValueError("Config must contain 'name' key")

    if "requirements" not in config:
        raise ValueError("Config must contain 'requirements' key")

    requirements = config["requirements"]
    if not isinstance(requirements, dict):
        raise ValueError("'requirements' must be a dictionary")

    # Validate optional keys have correct types if present
    if "files" in requirements and not isinstance(requirements["files"], list):
        raise ValueError("'requirements.files' must be a list")

    if "markers" in requirements and not isinstance(requirements["markers"], dict):
        raise ValueError("'requirements.markers' must be a dictionary")

    if "tests" in requirements and not isinstance(requirements["tests"], list):
        raise ValueError("'requirements.tests' must be a list")


def audit_phase(phase_name: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
    """
    Audit a single phase for completion.

    Args:
        phase_name: Name of the phase (e.g., "Phase 1: Agent Setup")
        requirements: Dict with 'files', 'markers', 'tests' keys

    Returns:
        Dict with status, implemented, missing, issues
    """
    results: Dict[str, Any] = {
        "phase": phase_name,
        "status": "unknown",
        "implemented": [],
        "missing": [],
        "issues": []
    }

    files_list = requirements.get("files", [])
    markers_dict = requirements.get("markers", {})

    # Handle empty requirements case
    if not files_list and not markers_dict:
        results["status"] = "empty"
        results["issues"].append("No requirements specified (empty files and markers)")
        return results

    # Check files exist
    files_status = check_files_exist(files_list)
    for f, exists in files_status.items():
        if exists:
            results["implemented"].append(f)
        else:
            results["missing"].append(f)

    # Check implementation markers
    for filepath, markers in markers_dict.items():
        if not isinstance(markers, list):
            results["issues"].append(f"{filepath}: markers must be a list")
            continue
        marker_status = check_file_contains(filepath, markers)
        missing_markers = [m for m, found in marker_status.items() if not found]
        if missing_markers:
            results["issues"].append(f"{filepath} missing: {missing_markers}")

    # Determine overall status
    if not results["missing"] and not results["issues"]:
        results["status"] = "complete"
    elif results["implemented"] and (results["missing"] or results["issues"]):
        results["status"] = "partial"
    else:
        results["status"] = "missing"

    return results


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="audit_phase.py",
        description="Audit script for checking implementation phase completion.",
        epilog="Example: audit_phase.py '{\"name\": \"Phase 1\", \"requirements\": {\"files\": [\"main.py\"]}}'"
    )
    parser.add_argument(
        "config",
        help="Phase configuration as JSON string"
    )
    return parser.parse_args()


def main() -> int:
    """CLI entry point for audit script."""
    args = parse_args()

    try:
        config = json.loads(args.config)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON - {e}", file=sys.stderr)
        return 1

    try:
        validate_config(config)
    except ValueError as e:
        print(f"Error: Invalid config - {e}", file=sys.stderr)
        return 1

    results = audit_phase(config["name"], config["requirements"])
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
