"""Provide CLI for application."""

from pathlib import Path

import click

from dgidb_analytics import __version__
from dgidb_analytics.snapshot import create_analytics_snapshot


@click.group()
@click.version_option(__version__)
def cli() -> None:
    """Short description of CLI.

    \b
        $ echo "provide a multiline description with a leading \\b"
        $ echo "more commands here"
        $ echo "otherwise, a single indent will pick up proper formatting"

    Conclude by summarizing additional commands
    """  # noqa: D301


@cli.command()
@click.argument(
    "analytics_db_path",
    type=click.Path(
        path_type=Path,
        dir_okay=False,
        file_okay=True,
        exists=False,
    ),
)
@click.argument("postgres_dsn")
@click.argument("snapshot_name", type=str | None)
def ingest(
    analytics_db_path: Path, postgres_dsn: str, snapshot_name: str | None
) -> None:
    """Ingest DGIdb snapshot into tracking database"""
    if not snapshot_name:
        snapshot_name = postgres_dsn.rsplit("/", 1)[0]
    create_analytics_snapshot(analytics_db_path, postgres_dsn, snapshot_name)
