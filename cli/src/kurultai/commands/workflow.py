"""Workflow command for Kurultai CLI.

Handles workflow execution, validation, and listing.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import click
import yaml

from kurultai.workflow import (
    WorkflowError,
    WorkflowRunner,
    WorkflowValidationError,
)


@click.group(name="workflow")
def workflow_command():
    """Run and manage workflows.

    Workflows are YAML files that define multi-step processes using
    the Kurultai skill system. They support variable substitution,
    output chaining, and parallel execution.

    \b
    Examples:
        kurultai workflow list
        kurultai workflow validate examples/feature-development.yaml
        kurultai workflow run examples/feature-development.yaml
        kurultai workflow run workflow.yaml --var feature_name="my-feature"
    """
    pass


@workflow_command.command(name="run")
@click.argument("workflow_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--var",
    "variables",
    multiple=True,
    help="Set workflow variable (KEY=VALUE). Can be used multiple times.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be executed without running.",
)
@click.option(
    "--output",
    "output_format",
    type=click.Choice(["json", "yaml", "table"]),
    default="yaml",
    help="Output format for results.",
)
@click.option(
    "--output-file",
    "-o",
    type=click.Path(path_type=Path),
    help="Write results to file instead of stdout.",
)
def workflow_run(
    workflow_file: Path,
    variables: tuple,
    dry_run: bool,
    output_format: str,
    output_file: Optional[Path],
):
    """Execute a workflow file.

    WORKFLOW_FILE is the path to the workflow YAML file to execute.

    \b
    Examples:
        kurultai workflow run examples/feature-development.yaml
        kurultai workflow run workflow.yaml --var name="my-project"
        kurultai workflow run workflow.yaml --var a=1 --var b=2
        kurultai workflow run workflow.yaml --dry-run
    """
    try:
        # Parse variables
        var_dict = {}
        for var in variables:
            if "=" not in var:
                raise click.BadParameter(
                    f"Variable must be in KEY=VALUE format: {var}"
                )
            key, value = var.split("=", 1)
            var_dict[key] = value

        # Create runner and load workflow
        runner = WorkflowRunner(workflow_file)
        runner.load()

        # Set variables
        runner.set_variables(**var_dict)

        if dry_run:
            # Show execution plan
            plan = runner.dry_run()
            _output_results(plan, output_format, output_file)
            return

        # Execute workflow
        results = runner.run()
        _output_results(results, output_format, output_file)

    except WorkflowValidationError as e:
        raise click.ClickException(f"Workflow validation failed: {e}")
    except WorkflowError as e:
        raise click.ClickException(str(e))
    except Exception as e:
        raise click.ClickException(f"Unexpected error: {e}")


@workflow_command.command(name="validate")
@click.argument("workflow_file", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Show detailed validation information.",
)
def workflow_validate(workflow_file: Path, verbose: bool):
    """Validate a workflow file.

    WORKFLOW_FILE is the path to the workflow YAML file to validate.

    Checks:
    - YAML syntax is valid
    - All required fields are present
    - Step dependencies are valid
    - No circular dependencies
    - Variable references are valid

    \b
    Examples:
        kurultai workflow validate examples/feature-development.yaml
        kurultai workflow validate workflow.yaml --verbose
    """
    try:
        runner = WorkflowRunner(workflow_file)
        workflow = runner.load()

        click.echo(f"Validating workflow: {workflow.name} v{workflow.version}")
        click.echo()

        errors = runner.validate()

        if errors:
            click.echo(click.style("Validation failed:", fg="red", bold=True))
            for error in errors:
                click.echo(f"  - {error}")
            raise click.Exit(1)
        else:
            click.echo(click.style("Validation passed!", fg="green", bold=True))

        if verbose:
            click.echo()
            click.echo("Workflow details:")
            click.echo(f"  Steps: {len(workflow.steps)}")
            click.echo(f"  Variables: {len(workflow.variables)}")
            click.echo(f"  Outputs: {len(workflow.outputs)}")

            if workflow.steps:
                click.echo()
                click.echo("Steps:")
                for step in workflow.steps:
                    deps = f" (depends on: {', '.join(step.depends_on)})" if step.depends_on else ""
                    parallel = f" [parallel: {step.parallel_group}]" if step.parallel_group else ""
                    click.echo(f"  - {step.id}: {step.name}{deps}{parallel}")

    except WorkflowError as e:
        raise click.ClickException(str(e))
    except Exception as e:
        raise click.ClickException(f"Unexpected error: {e}")


@workflow_command.command(name="list")
@click.option(
    "--path",
    "-p",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path("examples"),
    help="Directory to search for workflows.",
)
@click.option(
    "--recursive",
    "-r",
    is_flag=True,
    help="Search recursively in subdirectories.",
)
def workflow_list(path: Path, recursive: bool):
    """List available workflows.

    Searches for workflow YAML files in the specified directory
    and displays information about each workflow.

    \b
    Examples:
        kurultai workflow list
        kurultai workflow list --path ./workflows
        kurultai workflow list --path ./workflows --recursive
    """
    try:
        pattern = "**/*.yaml" if recursive else "*.yaml"
        workflow_files = list(path.glob(pattern))

        if not workflow_files:
            click.echo(f"No workflow files found in {path}")
            return

        click.echo(f"Found {len(workflow_files)} workflow file(s) in {path}:")
        click.echo()

        for wf_file in sorted(workflow_files):
            try:
                runner = WorkflowRunner(wf_file)
                workflow = runner.load()

                # Check if it's actually a workflow file
                with open(wf_file, "r") as f:
                    data = yaml.safe_load(f)
                if not data or "workflow" not in data:
                    continue

                rel_path = wf_file.relative_to(Path.cwd()) if wf_file.is_absolute() else wf_file

                click.echo(click.style(f"  {rel_path}", fg="blue", bold=True))
                click.echo(f"    Name: {workflow.name}")
                click.echo(f"    Version: {workflow.version}")
                if workflow.description:
                    desc = workflow.description.strip().split("\n")[0][:60]
                    click.echo(f"    Description: {desc}...")
                click.echo(f"    Steps: {len(workflow.steps)}")
                click.echo()

            except Exception as e:
                click.echo(click.style(f"  {wf_file}", fg="yellow"))
                click.echo(f"    Error loading: {e}")
                click.echo()

    except Exception as e:
        raise click.ClickException(f"Error listing workflows: {e}")


def _output_results(
    results: dict, output_format: str, output_file: Optional[Path]
) -> None:
    """Output results in the specified format.

    Args:
        results: The results dictionary.
        output_format: Format to output (json, yaml, table).
        output_file: Optional file to write to.
    """
    if output_format == "json":
        output = json.dumps(results, indent=2, default=str)
    elif output_format == "yaml":
        output = yaml.dump(results, default_flow_style=False, sort_keys=False)
    else:  # table
        output = _format_as_table(results)

    if output_file:
        output_file.write_text(output)
        click.echo(f"Results written to {output_file}")
    else:
        click.echo(output)


def _format_as_table(results: dict) -> str:
    """Format results as a simple table.

    Args:
        results: The results dictionary.

    Returns:
        Formatted table string.
    """
    lines = []

    if "workflow" in results:
        lines.append(f"Workflow: {results['workflow']}")
        lines.append(f"Version: {results['version']}")
        lines.append("")

    if "execution_log" in results:
        lines.append("Execution Log:")
        lines.append("-" * 60)
        for entry in results["execution_log"]:
            status_color = "green" if entry["status"] == "success" else "red"
            lines.append(
                f"  {entry['step_id']}: {click.style(entry['status'], fg=status_color)} "
                f"({entry['duration']:.2f}s)"
            )
        lines.append("")

    if "outputs" in results:
        lines.append("Outputs:")
        lines.append("-" * 60)
        for key, value in results["outputs"].items():
            if isinstance(value, str) and len(value) > 100:
                value = value[:100] + "..."
            lines.append(f"  {key}: {value}")

    if "execution_plan" in results:
        lines.append("Execution Plan:")
        lines.append("-" * 60)
        for item in results["execution_plan"]:
            if item["type"] == "parallel":
                lines.append("  [Parallel]")
                for step in item["steps"]:
                    lines.append(f"    - {step['id']}: {step['name']} ({step['skill']})")
            else:
                step = item["step"]
                lines.append(f"  - {step['id']}: {step['name']} ({step['skill']})")

    return "\n".join(lines)
