"""``sflow`` command group."""

import click

from scenarioflow import __version__
from scenarioflow.plot_scenario import plot_scenario_cli


@click.group()
@click.version_option(__version__, "-V", "--version")
@click.help_option("-h", "--help")
def cli():
    """scenarioflow command-line tools."""


cli.add_command(plot_scenario_cli, "plot")


if __name__ == "__main__":
    cli()
