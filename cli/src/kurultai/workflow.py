"""Workflow runner for Kurultai CLI.

This module provides the WorkflowRunner class for loading, validating,
and executing workflow files. It supports variable substitution, output
chaining, parallel execution, and dependency management.
"""

from __future__ import annotations

import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

import yaml

from kurultai.exceptions import KurultaiError


class WorkflowError(KurultaiError):
    """Error raised during workflow execution."""

    pass


class WorkflowValidationError(KurultaiError):
    """Error raised when workflow validation fails."""

    pass


@dataclass
class WorkflowVariable:
    """Definition of a workflow variable."""

    name: str
    description: str = ""
    required: bool = False
    default: Optional[str] = None

    def validate(self, value: Optional[str] = None) -> str:
        """Validate and return the variable value.

        Args:
            value: The provided value, or None to use default.

        Returns:
            The validated value.

        Raises:
            WorkflowValidationError: If required variable is missing.
        """
        if value is not None:
            return value
        if self.default is not None:
            return self.default
        if self.required:
            raise WorkflowValidationError(
                f"Required variable '{self.name}' not provided"
            )
        return ""


@dataclass
class WorkflowStep:
    """A single step in a workflow."""

    id: str
    name: str
    skill: str
    description: str = ""
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: List[str] = field(default_factory=list)
    depends_on: List[str] = field(default_factory=list)
    parallel_group: Optional[str] = None

    def __post_init__(self):
        """Validate step configuration."""
        if not self.id:
            raise WorkflowValidationError("Step must have an id")
        if not self.skill:
            raise WorkflowValidationError(f"Step '{self.id}' must have a skill")


@dataclass
class WorkflowContext:
    """Context for workflow execution, storing variables and step outputs."""

    variables: Dict[str, str] = field(default_factory=dict)
    step_outputs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    execution_log: List[Dict[str, Any]] = field(default_factory=list)

    def set_variable(self, name: str, value: str) -> None:
        """Set a workflow variable."""
        self.variables[name] = value

    def get_variable(self, name: str) -> Optional[str]:
        """Get a workflow variable."""
        return self.variables.get(name)

    def set_step_output(self, step_id: str, outputs: Dict[str, Any]) -> None:
        """Store outputs from a completed step."""
        self.step_outputs[step_id] = outputs

    def get_step_output(self, step_id: str, output_name: str) -> Optional[Any]:
        """Get a specific output from a step."""
        step_data = self.step_outputs.get(step_id, {})
        return step_data.get(output_name)

    def log_execution(
        self, step_id: str, status: str, duration: float, error: Optional[str] = None
    ) -> None:
        """Log step execution."""
        self.execution_log.append(
            {
                "step_id": step_id,
                "status": status,
                "duration": duration,
                "error": error,
                "timestamp": time.time(),
            }
        )


@dataclass
class WorkflowConfig:
    """Configuration for workflow execution."""

    continue_on_error: bool = False
    step_timeout: int = 300
    max_retries: int = 2
    parallel_enabled: bool = False
    parallel_max_workers: int = 4
    parallel_groups: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class Workflow:
    """A complete workflow definition."""

    name: str
    version: str
    description: str = ""
    variables: Dict[str, WorkflowVariable] = field(default_factory=dict)
    steps: List[WorkflowStep] = field(default_factory=list)
    outputs: Dict[str, Any] = field(default_factory=dict)
    config: WorkflowConfig = field(default_factory=WorkflowConfig)

    def get_step(self, step_id: str) -> Optional[WorkflowStep]:
        """Get a step by ID."""
        for step in self.steps:
            if step.id == step_id:
                return step
        return None

    def get_step_dependencies(self, step: WorkflowStep) -> Set[str]:
        """Get all dependencies for a step (transitive)."""
        deps = set(step.depends_on)
        for dep_id in list(deps):
            dep_step = self.get_step(dep_id)
            if dep_step:
                deps.update(self.get_step_dependencies(dep_step))
        return deps

    def get_execution_order(self) -> List[Union[str, List[str]]]:
        """Get steps in execution order, with parallel groups.

        Returns:
            List of step IDs or lists of step IDs (for parallel execution).
        """
        # Build dependency graph
        in_degree: Dict[str, int] = {}
        dependents: Dict[str, Set[str]] = {step.id: set() for step in self.steps}

        for step in self.steps:
            in_degree[step.id] = len(step.depends_on)
            for dep in step.depends_on:
                dependents[dep].add(step.id)

        # Topological sort
        ready = [step.id for step in self.steps if in_degree[step.id] == 0]
        executed: Set[str] = set()
        order: List[Union[str, List[str]]] = []

        while ready:
            # Group parallel steps
            if self.config.parallel_enabled:
                parallel_groups: Dict[str, List[str]] = {}
                independent = []

                for step_id in ready:
                    step = self.get_step(step_id)
                    if step and step.parallel_group:
                        parallel_groups.setdefault(step.parallel_group, []).append(step_id)
                    else:
                        independent.append(step_id)

                # Add independent steps
                for step_id in independent:
                    order.append(step_id)
                    executed.add(step_id)
                    ready.remove(step_id)

                # Add parallel groups
                for group_name, group_steps in parallel_groups.items():
                    if all(s in ready for s in group_steps):
                        order.append(group_steps)
                        for step_id in group_steps:
                            executed.add(step_id)
                            ready.remove(step_id)
            else:
                step_id = ready.pop(0)
                order.append(step_id)
                executed.add(step_id)

            # Update ready list
            for step_id in list(executed):
                for dependent in dependents[step_id]:
                    if dependent not in executed:
                        in_degree[dependent] -= 1
                        if in_degree[dependent] == 0:
                            ready.append(dependent)

        return order


class WorkflowRunner:
    """Runner for executing workflows."""

    def __init__(self, workflow_path: Union[str, Path]):
        """Initialize the workflow runner.

        Args:
            workflow_path: Path to the workflow YAML file.
        """
        self.workflow_path = Path(workflow_path)
        self.workflow: Optional[Workflow] = None
        self.context = WorkflowContext()

    def load(self) -> Workflow:
        """Load workflow from YAML file.

        Returns:
            The loaded Workflow object.

        Raises:
            WorkflowError: If the file cannot be loaded.
        """
        if not self.workflow_path.exists():
            raise WorkflowError(f"Workflow file not found: {self.workflow_path}")

        try:
            with open(self.workflow_path, "r") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise WorkflowError(f"Invalid YAML in workflow file: {e}")

        if not data or "workflow" not in data:
            raise WorkflowError("Workflow file must have a 'workflow' root key")

        workflow_data = data["workflow"]
        self.workflow = self._parse_workflow(workflow_data)
        return self.workflow

    def _parse_workflow(self, data: Dict[str, Any]) -> Workflow:
        """Parse workflow data into Workflow object."""
        # Parse variables
        variables = {}
        for var_name, var_data in data.get("variables", {}).items():
            variables[var_name] = WorkflowVariable(
                name=var_name,
                description=var_data.get("description", ""),
                required=var_data.get("required", False),
                default=var_data.get("default"),
            )

        # Parse steps
        steps = []
        for step_data in data.get("steps", []):
            steps.append(
                WorkflowStep(
                    id=step_data["id"],
                    name=step_data.get("name", step_data["id"]),
                    skill=step_data["skill"],
                    description=step_data.get("description", ""),
                    inputs=step_data.get("inputs", {}),
                    outputs=step_data.get("outputs", []),
                    depends_on=step_data.get("depends_on", []),
                    parallel_group=step_data.get("parallel_group"),
                )
            )

        # Parse config
        config_data = data.get("config", {})
        parallel_config = config_data.get("parallel", {})
        config = WorkflowConfig(
            continue_on_error=config_data.get("continue_on_error", False),
            step_timeout=config_data.get("step_timeout", 300),
            max_retries=config_data.get("max_retries", 2),
            parallel_enabled=parallel_config.get("enabled", False),
            parallel_max_workers=parallel_config.get("max_workers", 4),
            parallel_groups=parallel_config.get("groups", {}),
        )

        return Workflow(
            name=data["name"],
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            variables=variables,
            steps=steps,
            outputs=data.get("outputs", {}),
            config=config,
        )

    def validate(self) -> List[str]:
        """Validate the workflow structure.

        Returns:
            List of validation errors (empty if valid).
        """
        if not self.workflow:
            self.load()

        errors = []

        # Check for duplicate step IDs
        step_ids = [step.id for step in self.workflow.steps]
        if len(step_ids) != len(set(step_ids)):
            duplicates = set(x for x in step_ids if step_ids.count(x) > 1)
            errors.append(f"Duplicate step IDs: {duplicates}")

        # Check dependencies exist
        for step in self.workflow.steps:
            for dep in step.depends_on:
                if dep not in step_ids:
                    errors.append(f"Step '{step.id}' depends on unknown step '{dep}'")

        # Check for circular dependencies
        try:
            self.workflow.get_execution_order()
        except Exception as e:
            errors.append(f"Dependency error: {e}")

        # Validate output references
        for step in self.workflow.steps:
            for key, value in step.inputs.items():
                if isinstance(value, str):
                    refs = self._extract_references(value)
                    for ref in refs:
                        if not self._validate_reference(ref):
                            errors.append(f"Step '{step.id}' has invalid reference: {ref}")

        return errors

    def _extract_references(self, value: str) -> List[str]:
        """Extract variable references from a string."""
        pattern = r"\{\{\s*([^}]+)\s*\}\}"
        return re.findall(pattern, value)

    def _validate_reference(self, ref: str) -> bool:
        """Validate a variable reference."""
        parts = ref.strip().split(".")

        if len(parts) == 1:
            # Simple variable
            return parts[0] in self.workflow.variables

        if len(parts) >= 3 and parts[0] == "steps":
            # Step output reference: steps.step_id.outputs.output_name
            step_id = parts[1]
            step = self.workflow.get_step(step_id)
            if not step:
                return False
            if len(parts) >= 4 and parts[2] == "outputs":
                output_name = parts[3]
                return output_name in step.outputs
            return True

        return True  # Allow unknown references (may be template filters)

    def set_variables(self, **variables: str) -> None:
        """Set workflow variables.

        Args:
            **variables: Variable name-value pairs.

        Raises:
            WorkflowValidationError: If a required variable is missing.
        """
        if not self.workflow:
            self.load()

        # Validate and set variables
        for var_name, var_def in self.workflow.variables.items():
            value = variables.get(var_name)
            validated_value = var_def.validate(value)
            self.context.set_variable(var_name, validated_value)

        # Set extra variables
        for name, value in variables.items():
            if name not in self.workflow.variables:
                self.context.set_variable(name, value)

    def _substitute_variables(self, value: Any) -> Any:
        """Substitute variables in a value.

        Args:
            value: The value to process (string, dict, list).

        Returns:
            The value with variables substituted.
        """
        if isinstance(value, str):
            return self._substitute_string(value)
        elif isinstance(value, dict):
            return {k: self._substitute_variables(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [self._substitute_variables(item) for item in value]
        return value

    def _substitute_string(self, value: str) -> str:
        """Substitute variables in a string."""
        pattern = r"\{\{\s*([^}]+)\s*\}\}"

        def replace(match):
            ref = match.group(1).strip()
            parts = ref.split(".")

            if len(parts) == 1:
                # Simple variable
                var_value = self.context.get_variable(parts[0])
                return var_value if var_value is not None else match.group(0)

            if len(parts) >= 3 and parts[0] == "steps":
                # Step output reference
                step_id = parts[1]
                if len(parts) >= 4 and parts[2] == "outputs":
                    output_name = parts[3]
                    output_value = self.context.get_step_output(step_id, output_name)
                    if output_value is not None:
                        return str(output_value)
                return match.group(0)

            return match.group(0)

        return re.sub(pattern, replace, value)

    def execute_step(self, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a single workflow step.

        Args:
            step: The step to execute.

        Returns:
            Dictionary of step outputs.

        Raises:
            WorkflowError: If step execution fails.
        """
        start_time = time.time()

        try:
            # Substitute variables in inputs
            inputs = self._substitute_variables(step.inputs)

            # Log step start
            print(f"  Executing step: {step.name} (skill: {step.skill})")

            # TODO: Integrate with actual skill execution system
            # For now, simulate step execution
            outputs = self._simulate_step_execution(step, inputs)

            duration = time.time() - start_time
            self.context.log_execution(step.id, "success", duration)
            print(f"    Completed in {duration:.2f}s")

            return outputs

        except Exception as e:
            duration = time.time() - start_time
            self.context.log_execution(step.id, "failed", duration, str(e))
            raise WorkflowError(f"Step '{step.id}' failed: {e}")

    def _simulate_step_execution(
        self, step: WorkflowStep, inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulate step execution (placeholder for actual skill integration).

        In production, this would call the actual skill system.
        """
        # Generate mock outputs based on step configuration
        outputs = {}
        for output_name in step.outputs:
            outputs[output_name] = f"[Output from {step.skill}: {output_name}]"
        return outputs

    def run(self) -> Dict[str, Any]:
        """Execute the workflow.

        Returns:
            Dictionary containing workflow outputs and execution results.

        Raises:
            WorkflowError: If workflow execution fails.
        """
        if not self.workflow:
            self.load()

        # Validate before execution
        errors = self.validate()
        if errors:
            raise WorkflowValidationError(f"Workflow validation failed: {errors}")

        print(f"Running workflow: {self.workflow.name} v{self.workflow.version}")
        print(f"Description: {self.workflow.description.strip()}")
        print()

        # Get execution order
        execution_order = self.workflow.get_execution_order()

        # Execute steps
        completed_steps: Set[str] = set()
        failed_steps: Set[str] = set()

        for item in execution_order:
            if isinstance(item, list):
                # Parallel execution
                self._execute_parallel(item, completed_steps, failed_steps)
            else:
                # Sequential execution
                step = self.workflow.get_step(item)
                if step:
                    self._execute_single(step, completed_steps, failed_steps)

        # Check for failures
        if failed_steps and not self.workflow.config.continue_on_error:
            raise WorkflowError(f"Workflow failed. Failed steps: {failed_steps}")

        # Generate outputs
        results = self._generate_outputs()

        print()
        print(f"Workflow completed. Steps: {len(completed_steps)} succeeded")
        if failed_steps:
            print(f"  Failed steps: {failed_steps}")

        return results

    def _execute_single(
        self, step: WorkflowStep, completed_steps: Set[str], failed_steps: Set[str]
    ) -> None:
        """Execute a single step."""
        if step.id in completed_steps or step.id in failed_steps:
            return

        try:
            outputs = self.execute_step(step)
            self.context.set_step_output(step.id, outputs)
            completed_steps.add(step.id)
        except WorkflowError as e:
            failed_steps.add(step.id)
            if not self.workflow.config.continue_on_error:
                raise

    def _execute_parallel(
        self,
        step_ids: List[str],
        completed_steps: Set[str],
        failed_steps: Set[str],
    ) -> None:
        """Execute multiple steps in parallel."""
        steps = [self.workflow.get_step(sid) for sid in step_ids]
        steps = [s for s in steps if s and s.id not in completed_steps]

        if not steps:
            return

        print(f"  Executing {len(steps)} steps in parallel...")

        with ThreadPoolExecutor(
            max_workers=self.workflow.config.parallel_max_workers
        ) as executor:
            future_to_step = {
                executor.submit(self.execute_step, step): step for step in steps
            }

            for future in as_completed(future_to_step):
                step = future_to_step[future]
                try:
                    outputs = future.result(
                        timeout=self.workflow.config.step_timeout
                    )
                    self.context.set_step_output(step.id, outputs)
                    completed_steps.add(step.id)
                except Exception as e:
                    failed_steps.add(step.id)
                    if not self.workflow.config.continue_on_error:
                        raise WorkflowError(
                            f"Parallel step '{step.id}' failed: {e}"
                        )

    def _generate_outputs(self) -> Dict[str, Any]:
        """Generate final workflow outputs."""
        results = {
            "workflow": self.workflow.name,
            "version": self.workflow.version,
            "execution_log": self.context.execution_log,
            "outputs": {},
        }

        for output_name, output_def in self.workflow.outputs.items():
            if isinstance(output_def, dict) and "value" in output_def:
                results["outputs"][output_name] = self._substitute_variables(
                    output_def["value"]
                )
            else:
                results["outputs"][output_name] = self._substitute_variables(
                    output_def
                )

        return results

    def dry_run(self) -> Dict[str, Any]:
        """Show what would be executed without running.

        Returns:
            Dictionary describing the execution plan.
        """
        if not self.workflow:
            self.load()

        execution_order = self.workflow.get_execution_order()

        plan = {
            "workflow": self.workflow.name,
            "version": self.workflow.version,
            "variables": self.context.variables,
            "execution_plan": [],
        }

        for item in execution_order:
            if isinstance(item, list):
                plan["execution_plan"].append(
                    {
                        "type": "parallel",
                        "steps": [
                            {
                                "id": self.workflow.get_step(sid).id,
                                "name": self.workflow.get_step(sid).name,
                                "skill": self.workflow.get_step(sid).skill,
                            }
                            for sid in item
                        ],
                    }
                )
            else:
                step = self.workflow.get_step(item)
                plan["execution_plan"].append(
                    {
                        "type": "sequential",
                        "step": {
                            "id": step.id,
                            "name": step.name,
                            "skill": step.skill,
                            "inputs": step.inputs,
                        },
                    }
                )

        return plan


def load_workflow(path: Union[str, Path]) -> Workflow:
    """Load a workflow from a file.

    Args:
        path: Path to the workflow YAML file.

    Returns:
        The loaded Workflow object.
    """
    runner = WorkflowRunner(path)
    return runner.load()


def validate_workflow(path: Union[str, Path]) -> List[str]:
    """Validate a workflow file.

    Args:
        path: Path to the workflow YAML file.

    Returns:
        List of validation errors (empty if valid).
    """
    runner = WorkflowRunner(path)
    return runner.validate()


def run_workflow(
    path: Union[str, Path], **variables: str
) -> Dict[str, Any]:
    """Run a workflow with the given variables.

    Args:
        path: Path to the workflow YAML file.
        **variables: Variable name-value pairs.

    Returns:
        Workflow execution results.
    """
    runner = WorkflowRunner(path)
    runner.load()
    runner.set_variables(**variables)
    return runner.run()
