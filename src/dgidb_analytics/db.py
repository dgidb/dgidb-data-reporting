"""Store data"""

import sqlite3
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
        notes TEXT
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
    conn: sqlite3.Connection,
    name: str,
    status: SnapshotStatus,
    notes: str | None = None,
) -> int:
    """Create a new snapshot metadata object"""
    cursor = conn.execute(
        """
        INSERT INTO snapshots (name, status, notes)
        VALUES (?, ?, ?)
        """,
        (name, status.value, notes),
    )
    conn.commit()

    lastrow_id = cursor.lastrowid
    if lastrow_id is None:
        raise ValueError
    return lastrow_id


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
