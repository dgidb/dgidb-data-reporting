"""Provide CLI for application."""

from pathlib import Path
from sqlite3 import connect

import click
from tabulate import tabulate

from dgidb_analytics import __version__, db
from dgidb_analytics.analytics import create_analytics_snapshot
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
        snapshot_name = postgres_dsn.rsplit("/", 1)[-1]
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
        db.update_snapshot_status(conn, snapshot_name, SnapshotStatus.RELEASED)


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
def show_snapshots(analytics_db_path: Path) -> None:
    """List all snapshots"""
    with connect(analytics_db_path) as conn:
        snapshots = db.get_all_snapshot_metadata(conn)
    click.echo(
        tabulate(
            [
                [
                    s.id,
                    s.name,
                    s.status,
                    s.created_at,
                    s.notes,
                ]
                for s in snapshots
            ],
            headers=["ID", "Name", "Status", "Created", "Notes"],
        )
    )


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
def delete_snapshot(analytics_db_path: Path, snapshot_name: str) -> None:
    """Delete a snapshot"""
    with connect(analytics_db_path) as conn:
        snapshot = db.get_snapshot_by_name(conn, snapshot_name)
        db.delete_snapshot(conn, snapshot.id)


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
@click.option("--show-unchanged", is_flag=True)
def report(analytics_db_path: Path, snapshot_name: str, show_unchanged: bool) -> None:
    """Run a report on a provisional snapshot against the most recent release snapshot."""
    with connect(analytics_db_path) as conn:
        previous_snapshot = db.get_latest_released_snapshot(conn)
    click.echo(f"Latest release snapshot: {previous_snapshot.name}")
    comparisons = check_provisional_snapshot(analytics_db_path, snapshot_name)

    rows = []

    for comparison in comparisons:
        if comparison.previous_count is None:
            status = "NEW"
            delta = "-"
            pct_change = "-"
        elif comparison.provisional_count is None:
            status = "LOST"
            delta = -comparison.previous_count
            pct_change = "-100.0%"
        else:
            delta = comparison.provisional_count - comparison.previous_count

            if delta < 0:
                status = "DROP"
            elif delta > 0:
                status = "GAIN"
            elif show_unchanged:
                status = "SAME"
            else:
                continue

            pct_change = (
                f"{100 * delta / comparison.previous_count:.1f}%"
                if comparison.previous_count
                else "-"
            )

        rows.append(
            [
                status,
                comparison.scope,
                comparison.source_name or "-",
                comparison.metric_name,
                comparison.previous_count,
                comparison.provisional_count,
                delta,
                pct_change,
            ]
        )

    print(
        tabulate(
            rows,
            headers=[
                "Status",
                "Scope",
                "Source",
                "Metric",
                "Previous",
                "Current",
                "Delta",
                "% Change",
            ],
            tablefmt="simple",
        )
    )
