"""Main CLI entry point for Kurultai."""

import click

from kurultai import __version__
from kurultai.commands.info import info_command
from kurultai.commands.install import install_command
from kurultai.commands.list import list_command
from kurultai.commands.publish import publish_command
from kurultai.commands.remove import remove_command
from kurultai.commands.workflow import workflow_command


@click.group()
@click.version_option(version=__version__, prog_name="kurultai")
@click.help_option("--help", "-h")
def cli():
    """Kurultai CLI - AI Skill Registry and Management Tool.

    Manage AI skills and agents through a unified command-line interface.

    \b
    Common Commands:
        install     Install a skill from the registry
        list        List installed or available skills
        remove      Remove an installed skill
        info        Display detailed information about a skill
        publish     Publish a skill to the registry
        workflow    Run and manage workflows

    \b
    Examples:
        kurultai install web-scraper
        kurultai list
        kurultai list --available
        kurultai remove web-scraper
        kurultai info web-scraper
        kurultai publish ./my-skill
        kurultai workflow run examples/feature-development.yaml

    \b
    For more help on a specific command:
        kurultai COMMAND --help
    """
    pass


# Register commands
cli.add_command(install_command)
cli.add_command(list_command)
cli.add_command(remove_command)
cli.add_command(info_command)
cli.add_command(publish_command)
cli.add_command(workflow_command)


def main():
    """Entry point for the Kurultai CLI."""
    cli()


if __name__ == "__main__":
    main()
