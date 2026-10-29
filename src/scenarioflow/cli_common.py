"""Shared Click options and CLI setup.

Logging is configured only at CLI entry points, never in library code. See
``.github/docs/CLI_GUIDE.md``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import click

from scenarioflow.logging_config import configure_logging, resolve_loglevel

__all__ = ["logging_options", "setup_logging"]


def logging_options(func: Callable) -> Callable:
    """Add ``--logdir``, ``--debug``, ``-v/--verbose`` and ``-q/--quiet``."""
    func = click.option("-q", "--quiet", is_flag=True,
                        help="Suppress console logging (file logging via --logdir continues).")(func)
    func = click.option("-v", "--verbose", count=True, help="Increase verbosity; -vv is debug.")(func)
    func = click.option("--debug", is_flag=True, help="Debug-level logging.")(func)
    func = click.option("--logdir", type=click.Path(path_type=Path), default=None,
                        help="Directory for a timestamped log file.")(func)
    return func


def setup_logging(*, logdir: Path | None, debug: bool, verbose: int, quiet: bool,
                  prefix: str) -> Path | None:
    """Configure the ``scenarioflow`` logger tree from common CLI flags.

    Returns
    -------
    pathlib.Path or None
        Log file path when ``logdir`` is given.

    Raises
    ------
    click.UsageError
        If both ``--quiet`` and ``--verbose`` are given.
    """
    if quiet and verbose:
        raise click.UsageError("--quiet and --verbose are mutually exclusive")
    level, console = resolve_loglevel(debug=debug, quiet=quiet, verbose=verbose)
    return configure_logging(package_name="scenarioflow", level=level, console=console,
                             logdir=logdir, logfile_prefix=prefix)
