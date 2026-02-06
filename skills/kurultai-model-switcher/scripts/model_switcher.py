#!/usr/bin/env python3
"""
Model Switcher for Kurultai Multi-Agent System

Handles switching LLM models and providers for the 6-agent system:
- Kublai (main): Squad lead/router
- Möngke (researcher): Research tasks
- Chagatai (writer): Content writing
- Temüjin (developer): Development/security
- Jochi (analyst): Analysis tasks
- Ögedei (ops): Operations/emergency router
"""

import fcntl
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

__all__ = ['ModelSwitcher']

# Default file permissions for sensitive files
_SENSITIVE_FILE_MODE = 0o600


class ModelSwitcher:
    """Handles model switching operations with validation and rollback support."""

    AGENT_IDS = ["main", "researcher", "writer", "developer", "analyst", "ops"]
    AGENT_NAMES = {
        "main": "Kublai",
        "researcher": "Möngke",
        "writer": "Chagatai",
        "developer": "Temüjin",
        "analyst": "Jochi",
        "ops": "Ögedei"
    }

    def __init__(
        self,
        moltbot_path: Optional[str] = None,
        openclaw_path: Optional[str] = None,
        history_path: Optional[str] = None,
        allowed_base_dir: Optional[str] = None
    ):
        """
        Initialize ModelSwitcher with configuration paths.

        Args:
            moltbot_path: Path to moltbot.json (default: from MOLTBOT_CONFIG env or "moltbot.json")
            openclaw_path: Path to openclaw.json (default: from OPENCLAW_CONFIG env or "/data/.clawdbot/openclaw.json")
            history_path: Path to history file (default: ".model-switch-history.json")
            allowed_base_dir: Base directory for path validation (default: current working directory)
        """
        # Use environment variables for paths with sensible defaults
        moltbot_default = os.environ.get("MOLTBOT_CONFIG", "moltbot.json")
        openclaw_default = os.environ.get("OPENCLAW_CONFIG", "/data/.clawdbot/openclaw.json")

        self.moltbot_path = Path(moltbot_path or moltbot_default)
        self.openclaw_path = Path(openclaw_path or openclaw_default)
        self.history_path = Path(history_path or ".model-switch-history.json")

        # Set and validate allowed base directory for path traversal protection
        self.allowed_base_dir = Path(allowed_base_dir or os.getcwd()).resolve()

        # Validate paths are within allowed directory
        self._validate_path(self.moltbot_path, "moltbot_path")
        self._validate_path(self.openclaw_path, "openclaw_path")
        self._validate_path(self.history_path, "history_path")

        # File lock for concurrent modification protection
        self._lock_fd = None

    def _validate_path(self, path: Path, path_name: str) -> None:
        """
        Validate that a path is safe for file operations.

        Args:
            path: Path to validate
            path_name: Name of the path parameter for error messages

        Raises:
            ValueError: If path contains directory traversal or is outside allowed directory
        """
        try:
            resolved = path.resolve()
        except OSError as e:
            # Path resolution failed - this could be a traversal attempt
            raise ValueError(f"Invalid {path_name}: path resolution failed") from e

        # Check for path traversal indicators in the original path string
        if ".." in str(path):
            raise ValueError(f"Invalid {path_name}: directory traversal (..) not allowed")

        # For absolute paths, ensure they're within allowed base directory
        if path.is_absolute():
            try:
                resolved.relative_to(self.allowed_base_dir)
            except ValueError:
                # Path is outside allowed directory - this is OK for production paths like /data/.clawdbot
                # but we should log a warning in production
                if not str(resolved).startswith("/data/.clawdbot"):
                    # Only allow paths outside base dir if they're in the production data directory
                    raise ValueError(f"Invalid {path_name}: path outside allowed directory")

    def _get_lock(self):
        """Acquire file lock for concurrent modification protection."""
        if self._lock_fd is None:
            lock_path = self.moltbot_path.with_suffix(".lock")
            self._lock_fd = open(lock_path, 'w')
            try:
                fcntl.flock(self._lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except (IOError, OSError):
                # Lock is held by another process
                self._lock_fd.close()
                self._lock_fd = None
                raise RuntimeError("Cannot acquire lock - another operation is in progress")

    def _release_lock(self):
        """Release the file lock."""
        if self._lock_fd is not None:
            fcntl.flock(self._lock_fd.fileno(), fcntl.LOCK_UN)
            self._lock_fd.close()
            self._lock_fd = None

    def _get_agent_list_str(self) -> str:
        """Get formatted string of valid agents with names."""
        return ", ".join(f"{aid} ({self.AGENT_NAMES.get(aid, aid)})" for aid in self.AGENT_IDS)

    def switch_model(
        self,
        agent_id: str,
        model: str,
        provider: Optional[str] = None,
        reason: Optional[str] = None,
        dry_run: bool = False
    ) -> dict:
        """
        Switch an agent to a new model.

        Args:
            agent_id: Agent ID ('main', 'researcher', 'writer', 'developer', 'analyst', 'ops') or 'all'
            model: Target model identifier (e.g., 'claude-sonnet-4', 'zai/glm-4.7')
            provider: Optional provider hint for validation
            reason: Optional reason for the switch (logged to Neo4j)
            dry_run: If True, validate but don't apply changes

        Returns:
            Result dict with status, message, and details
        """
        # Validate agent
        if agent_id != "all" and agent_id not in self.AGENT_IDS:
            return {
                "status": "error",
                "message": f"Invalid agent '{agent_id}'. Valid agents: {self._get_agent_list_str()}"
            }

        # Validate model exists in provider config
        validation = self._validate_model(model, provider)
        if not validation["valid"]:
            return {
                "status": "error",
                "message": validation["error"]
            }

        # Load current config
        try:
            config = self._load_moltbot_config()
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to load moltbot.json: {e}"
            }

        # Determine which agents to update
        agents_to_update = self.AGENT_IDS if agent_id == "all" else [agent_id]

        # Build change list
        changes = []
        for aid in agents_to_update:
            agent_config = self._get_agent_config(config, aid)
            if agent_config:
                old_model = agent_config.get("model", config.get("agents", {}).get("defaults", {}).get("model", {}).get("primary", "unknown"))
                changes.append({
                    "agent_id": aid,
                    "agent_name": self.AGENT_NAMES.get(aid, aid),
                    "old_model": old_model,
                    "new_model": model
                })

        if dry_run:
            return {
                "status": "dry_run",
                "message": f"Would switch {len(changes)} agent(s) to {model}",
                "changes": changes,
                "provider": validation.get("provider")
            }

        # Acquire lock for atomic operation
        try:
            self._get_lock()
        except RuntimeError as e:
            return {
                "status": "error",
                "message": str(e)
            }

        try:
            # Backup current state (before any changes)
            self._backup_state_from_file()

            # Apply changes
            for change in changes:
                self._update_agent_model(config, change["agent_id"], model)

            self._save_moltbot_config(config)

            # Log to history
            self._log_switch(changes, reason)

            return {
                "status": "success",
                "message": f"Successfully switched {len(changes)} agent(s) to {model}",
                "changes": changes,
                "provider": validation.get("provider"),
                "deploy_commands": self._get_deploy_commands()
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to apply changes: {e}"
            }
        finally:
            self._release_lock()

    def rollback(self, agent_id: str) -> dict:
        """
        Rollback an agent to its previous model.

        Args:
            agent_id: Agent ID to rollback (must not be 'all')

        Returns:
            Result dict with status and message
        """
        if agent_id == "all":
            return {
                "status": "error",
                "message": "Rollback for 'all' agents is not supported. Please specify a single agent."
            }

        if agent_id not in self.AGENT_IDS:
            return {
                "status": "error",
                "message": f"Invalid agent '{agent_id}'. Valid agents: {self._get_agent_list_str()}"
            }

        history = self._load_history()
        agent_history = history.get(agent_id, [])

        if len(agent_history) < 2:
            agent_name = self.AGENT_NAMES.get(agent_id, agent_id)
            return {
                "status": "error",
                "message": f"No rollback history available for {agent_name} ({agent_id}). At least 2 states are required. Run 'history --agent {agent_id}' to check available history."
            }

        # Get previous model (index 1, since 0 is current)
        previous = agent_history[1]
        previous_model = previous["model"]

        # Validate that the previous model still exists
        model_validation = self._validate_model(previous_model, None)
        if not model_validation["valid"]:
            agent_name = self.AGENT_NAMES.get(agent_id, agent_id)
            return {
                "status": "error",
                "message": f"Cannot rollback {agent_name} ({agent_id}) to model '{previous_model}': {model_validation.get('error', 'model no longer available')}. Please choose a different model manually."
            }

        return self.switch_model(agent_id, previous_model, reason="Rollback to previous model")

    def get_status(self) -> dict:
        """Get current model assignments for all agents."""
        try:
            config = self._load_moltbot_config()
        except Exception as e:
            return {"status": "error", "message": str(e)}

        defaults = config.get("agents", {}).get("defaults", {}).get("model", {}).get("primary", "unknown")
        agents = config.get("agents", {}).get("list", [])

        status = {}
        for agent in agents:
            aid = agent.get("id")
            model = agent.get("model", defaults)
            status[aid] = {
                "name": self.AGENT_NAMES.get(aid, aid),
                "model": model,
                "is_default": "model" not in agent
            }

        return {"status": "success", "agents": status, "default_model": defaults}

    def get_history(self, agent_id: Optional[str] = None, limit: int = 10) -> dict:
        """
        Get switch history for an agent or all agents.

        Args:
            agent_id: Optional agent ID to filter history
            limit: Maximum number of history entries to return (must be non-negative)

        Returns:
            Dict with status and history data
        """
        # Validate limit parameter
        limit = max(0, limit)

        history = self._load_history()

        if agent_id:
            if agent_id not in self.AGENT_IDS:
                return {"status": "error", "message": f"Invalid agent '{agent_id}'. Valid agents: {self._get_agent_list_str()}"}
            return {
                "status": "success",
                "agent": agent_id,
                "history": history.get(agent_id, [])[:limit]
            }

        # Return all agents
        return {
            "status": "success",
            "history": {aid: history.get(aid, [])[:limit] for aid in self.AGENT_IDS}
        }

    def validate_config(self) -> dict:
        """Validate moltbot.json and openclaw.json configuration."""
        errors = []
        warnings = []

        # Check moltbot.json exists and is valid JSON
        if not self.moltbot_path.exists():
            errors.append(f"moltbot.json not found at {self.moltbot_path}")
        else:
            try:
                with open(self.moltbot_path, encoding='utf-8') as f:
                    config = json.load(f)

                # Validate agent structure
                agents = config.get("agents", {})
                if not agents.get("list"):
                    errors.append("No agents defined in moltbot.json")

                agent_ids = [a.get("id") for a in agents.get("list", [])]
                for aid in self.AGENT_IDS:
                    if aid not in agent_ids:
                        warnings.append(f"Standard agent '{aid}' ({self.AGENT_NAMES.get(aid, aid)}) not found in configuration")

            except json.JSONDecodeError as e:
                errors.append(f"moltbot.json is invalid JSON: {e}")

        # Check openclaw.json
        if not self.openclaw_path.exists():
            warnings.append(f"openclaw.json not found at {self.openclaw_path}")
        else:
            try:
                with open(self.openclaw_path, encoding='utf-8') as f:
                    openclaw = json.load(f)

                models = openclaw.get("models", {}).get("providers", {})
                if not models:
                    warnings.append("No model providers configured in openclaw.json")

            except json.JSONDecodeError as e:
                errors.append(f"openclaw.json is invalid JSON: {e}")

        # Check environment variables
        required_env = ["ANTHROPIC_API_KEY", "OPENCLAW_GATEWAY_TOKEN"]
        for env in required_env:
            if not os.environ.get(env):
                warnings.append(f"Environment variable {env} not set")

        if errors:
            return {"status": "error", "errors": errors, "warnings": warnings}

        return {"status": "valid", "warnings": warnings}

    def _load_moltbot_config(self) -> dict:
        """Load and cache moltbot.json."""
        with open(self.moltbot_path, encoding='utf-8') as f:
            return json.load(f)

    def _save_moltbot_config(self, config: dict):
        """Save moltbot.json atomically."""
        temp_path = self.moltbot_path.with_suffix(".tmp")
        with open(temp_path, "w", encoding='utf-8') as f:
            json.dump(config, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        # Use os.replace for atomic operation on same filesystem
        os.replace(temp_path, self.moltbot_path)

    def _get_agent_config(self, config: dict, agent_id: str) -> Optional[dict]:
        """Get configuration for a specific agent."""
        agents = config.get("agents", {}).get("list", [])
        for agent in agents:
            if agent.get("id") == agent_id:
                return agent
        return None

    def _update_agent_model(self, config: dict, agent_id: str, model: str):
        """Update model for an agent in the config."""
        agents = config.get("agents", {}).get("list", [])
        for agent in agents:
            if agent.get("id") == agent_id:
                agent["model"] = model
                return

    def _validate_model(self, model: str, provider_hint: Optional[str] = None) -> dict:
        """Validate that a model exists in the configuration."""
        if not self.openclaw_path.exists():
            return {"valid": True, "warning": "openclaw.json not found, skipping model validation"}

        try:
            with open(self.openclaw_path, encoding='utf-8') as f:
                config = json.load(f)

            providers = config.get("models", {}).get("providers", {})

            for provider_name, provider_config in providers.items():
                if provider_hint and provider_name != provider_hint:
                    continue

                models = provider_config.get("models", [])
                for m in models:
                    if m.get("id") == model:
                        return {"valid": True, "provider": provider_name}

            # Check if it looks like a provider/model path (only if no provider hint)
            if "/" in model and not provider_hint:
                parts = model.split("/")
                if len(parts) == 2 and parts[0] in providers:
                    return {"valid": True, "provider": parts[0]}

            # Build list of available models for error message
            available = []
            for provider_name, provider_config in providers.items():
                models = provider_config.get("models", [])
                available.extend([m.get("id") for m in models[:3]])  # Sample

            return {
                "valid": False,
                "error": f"Model '{model}' not found in openclaw.json. Available models include: {', '.join(available[:5])}... Run 'validate' to see all configured models."
            }

        except (json.JSONDecodeError, IOError, OSError) as e:
            return {"valid": False, "error": f"Failed to validate model: {e}"}

    def _backup_state_from_file(self):
        """
        Backup current configuration to history by reading directly from file.

        This ensures we capture the exact state being modified, not an in-memory
        copy that may be stale.
        """
        try:
            with open(self.moltbot_path, encoding='utf-8') as f:
                config = json.load(f)
        except (json.JSONDecodeError, IOError, OSError):
            # If we can't read the file, skip backup
            return

        history = self._load_history()

        defaults = config.get("agents", {}).get("defaults", {}).get("model", {}).get("primary", "unknown")
        agents = config.get("agents", {}).get("list", [])

        for agent in agents:
            aid = agent.get("id")
            if aid not in self.AGENT_IDS:
                continue

            model = agent.get("model", defaults)
            if aid not in history:
                history[aid] = []

            history[aid].insert(0, {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "model": model
            })

            # Keep only last 10
            history[aid] = history[aid][:10]

        self._save_history(history)

    def _load_history(self) -> dict:
        """Load switch history."""
        if not self.history_path.exists():
            return {}
        try:
            with open(self.history_path, encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # File is corrupt - preserve for manual recovery
            backup_path = self.history_path.with_suffix(".corrupt." + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"))
            try:
                shutil.copy(self.history_path, backup_path)
            except (IOError, OSError):
                pass
            return {}
        except (IOError, OSError):
            return {}

    def _save_history(self, history: dict):
        """Save switch history atomically."""
        temp_path = self.history_path.with_suffix(".tmp")
        with open(temp_path, "w", encoding='utf-8') as f:
            json.dump(history, f, indent=2)
            f.flush()
            os.fsync(f.fileno())

        # Set restrictive permissions before moving
        os.chmod(temp_path, _SENSITIVE_FILE_MODE)

        # Use os.replace for atomic operation
        os.replace(temp_path, self.history_path)

    def _log_switch(self, changes: list, reason: Optional[str]):
        """Log switch to audit file."""
        # Sanitize reason field to prevent log injection
        if reason:
            reason = reason.replace("\n", " ").replace("\r", " ").replace("\t", " ")

        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "changes": changes,
            "reason": reason
        }

        log_path = Path("model-switch.log")

        # Append to log file
        with open(log_path, "a", encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + "\n")

        # Set restrictive permissions on log file
        try:
            current_mode = log_path.stat().st_mode
            if current_mode & 0o777 != _SENSITIVE_FILE_MODE:
                log_path.chmod(_SENSITIVE_FILE_MODE)
        except (IOError, OSError):
            pass

    def _get_deploy_commands(self) -> list:
        """Get deployment commands for Railway."""
        project_name = os.environ.get("RAILWAY_PROJECT_NAME", "kublai")
        return [
            "git add moltbot.json",
            'git commit -m "switch-model: Update agent model assignments"',
            "railway login",
            f"railway link --project {project_name}",
            "railway up",
            "railway logs --follow"
        ]


def main():
    """CLI interface for model switching."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Kurultai Model Switcher",
        epilog="""
Examples:
  %(prog)s switch --agent main --model claude-sonnet-4
  %(prog)s switch --agent all --model zai/glm-4.7 --provider zai
  %(prog)s switch --agent developer --model claude-sonnet-4 --dry-run
  %(prog)s rollback --agent main
  %(prog)s status
  %(prog)s history --agent main
  %(prog)s validate
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("command", choices=["switch", "rollback", "status", "history", "validate"])
    parser.add_argument("--agent", "-a", help="Agent ID or 'all'")
    parser.add_argument("--model", "-m", help="Target model")
    parser.add_argument("--provider", "-p", help="Provider hint")
    parser.add_argument("--reason", "-r", help="Reason for switch")
    parser.add_argument("--dry-run", action="store_true", help="Validate without applying changes")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="Output format (default: json)")

    args = parser.parse_args()

    # Validate required arguments per command
    if args.command == "switch":
        if not args.agent:
            print("Error: --agent is required for switch command", file=sys.stderr)
            return 1
        if not args.model:
            print("Error: --model is required for switch command", file=sys.stderr)
            return 1

    if args.command in ["rollback", "history"]:
        if not args.agent:
            print(f"Error: --agent is required for {args.command} command", file=sys.stderr)
            return 1

    switcher = ModelSwitcher()

    if args.command == "switch":
        result = switcher.switch_model(
            args.agent, args.model, args.provider, args.reason, args.dry_run
        )
    elif args.command == "rollback":
        result = switcher.rollback(args.agent)
    elif args.command == "status":
        result = switcher.get_status()
    elif args.command == "history":
        result = switcher.get_history(args.agent)
    elif args.command == "validate":
        result = switcher.validate_config()
    else:
        result = {"status": "error", "message": f"Unknown command: {args.command}"}

    # Format output based on requested format
    if args.format == "text":
        print(_format_result_text(result))
    else:
        print(json.dumps(result, indent=2))

    # Determine exit code
    if result.get("status") in ("success", "valid", "dry_run"):
        return 0
    return 1


def _format_result_text(result: dict) -> str:
    """Format result dict as human-readable text."""
    lines = []

    status = result.get("status", "unknown")
    status_symbol = {
        "success": "✓",
        "valid": "✓",
        "dry_run": "→",
        "error": "✗",
        "unknown": "?"
    }.get(status, "?")

    lines.append(f"{status_symbol} {result.get('message', status.title())}")

    if status == "success" and "changes" in result:
        lines.append("\nChanges applied:")
        for change in result["changes"]:
            lines.append(f"  - {change['agent_name']} ({change['agent_id']}): {change['old_model']} → {change['new_model']}")

    if status == "success" and "deploy_commands" in result:
        lines.append("\nDeploy commands:")
        for cmd in result["deploy_commands"]:
            lines.append(f"  {cmd}")

    if status == "success" and "agents" in result:
        lines.append("\nCurrent model assignments:")
        for aid, info in result["agents"].items():
            default_marker = " (default)" if info.get("is_default") else ""
            lines.append(f"  - {info['name']} ({aid}): {info['model']}{default_marker}")

    if "warnings" in result and result["warnings"]:
        lines.append("\nWarnings:")
        for warning in result["warnings"]:
            lines.append(f"  ⚠ {warning}")

    if "errors" in result and result["errors"]:
        lines.append("\nErrors:")
        for error in result["errors"]:
            lines.append(f"  ✗ {error}")

    return "\n".join(lines)


if __name__ == "__main__":
    sys = __import__("sys")
    sys.exit(main())
