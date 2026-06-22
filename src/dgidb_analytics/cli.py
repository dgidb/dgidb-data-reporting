"""Provide CLI for application."""

from pathlib import Path
from sqlite3 import connect

import click

from dgidb_analytics import __version__
from dgidb_analytics.analytics import create_analytics_snapshot
from dgidb_analytics.db import update_snapshot_status
from dgidb_analytics.reports import check_provisional_snapshot
from dgidb_analytics.schema import SnapshotStatus


@click.group()
@click.version_option(__version__)
def cli() -> None:
    """Track and compare DGIdb snapshot metrics."""


@cli.command()
@click.argument(
    "analytics-db-path",
    type=click.Path(
        path_type=Path,
        dir_okay=False,
        file_okay=True,
        exists=False,
    ),
)
@click.option(
    "--postgres-dsn", type=str, default="postgresql://postgres@localhost:5432/dgidb"
)
@click.option("--snapshot-name")
def ingest(
    analytics_db_path: Path, postgres_dsn: str, snapshot_name: str | None
) -> None:
    """Create a provisional snapshot from a DGIdb database."""
    if not snapshot_name:
        snapshot_name = postgres_dsn.rsplit("/", 1)[0]
    create_analytics_snapshot(analytics_db_path, postgres_dsn, snapshot_name)


@cli.command()
@click.argument(
    "analytics-db-path",
    type=click.Path(
        path_type=Path,
        dir_okay=False,
        file_okay=True,
        exists=False,
    ),
)
@click.argument("snapshot-name")
def save_snapshot(analytics_db_path: Path, snapshot_name: str) -> None:
    """Mark a provisional snapshot as released."""
    with connect(analytics_db_path) as conn:
        update_snapshot_status(conn, snapshot_name, SnapshotStatus.RELEASED)


@cli.command()
@click.argument(
    "analytics-db-path",
    type=click.Path(
        path_type=Path,
        dir_okay=False,
        file_okay=True,
        exists=False,
    ),
)
@click.argument("snapshot-name", type=str)
def report(analytics_db_path: Path, snapshot_name: str) -> None:
    """Run a report on a provisional snapshot against the most recent release snapshot"""
    comparisons = check_provisional_snapshot(analytics_db_path, snapshot_name)
    for comparison in comparisons:
        if comparison.previous_count is None:
            click.echo(
                f"New item: {comparison.metric_name} ({comparison.source_name or ''}); count: {comparison.provisional_count}"
            )
        elif comparison.provisional_count is None:
            click.echo(
                f"Item lost: {comparison.metric_name} ({comparison.source_name or ''}); previously: {comparison.previous_count}"
            )
        elif comparison.provisional_count < comparison.previous_count:
            reduction = comparison.provisional_count / comparison.previous_count
            click.echo(
                f"Item dropped: {comparison.metric_name} ({comparison.source_name or ''}); {reduction}%; {comparison.previous_count} -> {comparison.provisional_count}"
            )
