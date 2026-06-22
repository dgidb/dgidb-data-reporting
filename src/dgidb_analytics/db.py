"""Store data"""

import sqlite3
from typing import TYPE_CHECKING

from dgidb_analytics.schema import (
    GlobalMetricCount,
    SnapshotMetadata,
    SourceMetricCount,
)

if TYPE_CHECKING:
    from pathlib import Path

    from dgidb_analytics.schema import SnapshotStatus

VALID_SNAPSHOT_STATUSES = ("provisional", "released")


def connect(db_path: str | Path) -> sqlite3.Connection:
    """Connect to the analytics database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    """Create database tables and indexes."""
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        status TEXT NOT NULL CHECK (status IN ('provisional', 'released')),
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        notes TEXT,

        UNIQUE (name)
    );

    CREATE TABLE IF NOT EXISTS snapshot_source_counts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        snapshot_id INTEGER NOT NULL,
        source_name TEXT NOT NULL,
        metric_name TEXT NOT NULL,
        count INTEGER NOT NULL CHECK (count >= 0),

        FOREIGN KEY (snapshot_id)
            REFERENCES snapshots (id)
            ON DELETE CASCADE,

        UNIQUE (snapshot_id, source_name, metric_name)
    );

    CREATE TABLE IF NOT EXISTS snapshot_global_counts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        snapshot_id INTEGER NOT NULL,
        metric_name TEXT NOT NULL,
        count INTEGER NOT NULL CHECK (count >= 0),

        FOREIGN KEY (snapshot_id)
            REFERENCES snapshots (id)
            ON DELETE CASCADE,

        UNIQUE (snapshot_id, metric_name)
    );
    """)
    conn.commit()


def initialize_database(db_path: str | Path) -> None:
    """Initialize the analytics database."""
    with connect(db_path) as conn:
        create_schema(conn)


def create_snapshot(
    conn: sqlite3.Connection, snapshot_metadata: SnapshotMetadata
) -> int:
    """Create a new snapshot metadata object"""
    cursor = conn.execute(
        """
        INSERT INTO snapshots (name, status, notes)
        VALUES (?, ?, ?)
        """,
        (
            snapshot_metadata.name,
            snapshot_metadata.status.value,
            snapshot_metadata.notes,
        ),
    )
    conn.commit()

    lastrow_id = cursor.lastrowid
    if lastrow_id is None:
        raise ValueError
    return lastrow_id


def get_snapshot_by_name(conn: sqlite3.Connection, name: str) -> SnapshotMetadata:
    """Get a snapshot ID"""
    row = conn.execute(
        "SELECT id, name, status, notes FROM snapshots WHERE name = ?", (name,)
    ).fetchone()
    if row is None:
        msg = f"No snapshots named '{name}' found"
        raise ValueError(msg)
    return SnapshotMetadata(id=row[0], name=row[1], status=row[2], notes=row[3] or None)


def get_latest_released_snapshot(conn: sqlite3.Connection) -> SnapshotMetadata:
    """Get ID for latest released snapshot.

    We can order by ID because the DB has an autoincrementing ID policy

    :raise ValueError: if no official release snapshot is available
    """
    row = conn.execute(
        """
        SELECT id
        FROM snapshots
        WHERE status = 'released'
        ORDER BY id DESC
        LIMIT 1
        """
    ).fetchone()

    if row is None:
        msg = "No released snapshots found"
        raise ValueError(msg)

    return row["id"]


def update_snapshot_status(
    conn: sqlite3.Connection, name: str, status: SnapshotStatus
) -> None:
    """Update status of a snapshot"""
    cursor = conn.execute(
        "UPDATE snapshots SET status = ? WHERE name = ?",
        (status, name),
    )

    if cursor.rowcount == 0:
        msg = f"Snapshot '{name}' not found"
        raise ValueError(msg)

    conn.commit()


def add_snapshot_source_count(
    conn: sqlite3.Connection,
    snapshot_id: int,
    source_name: str,
    metric_name: str,
    count: int,
) -> None:
    """Add an instance of a source metric count to a snapshot"""
    conn.execute(
        """
        INSERT INTO snapshot_source_counts (
            snapshot_id,
            source_name,
            metric_name,
            count
        )
        VALUES (?, ?, ?, ?)
        """,
        (snapshot_id, source_name, metric_name, count),
    )
    conn.commit()


def add_snapshot_global_count(
    conn: sqlite3.Connection,
    snapshot_id: int,
    metric_name: str,
    count: int,
) -> None:
    """Add a global metric count to a snapshot."""
    conn.execute(
        """
        INSERT INTO snapshot_global_counts (
            snapshot_id,
            metric_name,
            count
        )
        VALUES (?, ?, ?)
        """,
        (snapshot_id, metric_name, count),
    )
    conn.commit()


def get_snapshot_metrics(
    conn: sqlite3.Connection, snapshot_id: int
) -> tuple[list[SourceMetricCount], list[GlobalMetricCount]]:
    """Get counts for a snapshot"""
    cursor = conn.execute(
        "SELECT source_name, metric_name, count FROM snapshot_source_counts WHERE snapshot_id = ?",
        (snapshot_id,),
    )
    source_counts = [
        SourceMetricCount(source_name=s[0], metric_name=s[1], count=s[2])
        for s in cursor.fetchall()
    ]

    cursor = conn.execute(
        "SELECT metric_name, count FROM snapshot_global_counts WHERE snapshot_id = ?",
        (snapshot_id,),
    )
    global_counts = [
        GlobalMetricCount(metric_name=s[1], count=s[2]) for s in cursor.fetchall()
    ]
    return source_counts, global_counts
