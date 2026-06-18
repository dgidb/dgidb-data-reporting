"""Create data entries for a DGIdb snapshot."""

from typing import TYPE_CHECKING, Literal

import psycopg

from dgidb_analytics.db import (
    add_snapshot_global_count,
    add_snapshot_source_count,
    connect,
    create_snapshot,
)
from dgidb_analytics.schema import (
    GlobalMetric,
    GlobalMetricCount,
    SnapshotStatus,
    SourceMetric,
    SourceMetricCount,
)

if TYPE_CHECKING:
    import sqlite3
    from pathlib import Path


def collect_source_counts(pg_conn: psycopg.Connection) -> list[SourceMetricCount]:
    """Run queries to get source-based counts"""
    counts = []
    queries = {
        SourceMetric.DRUG_CLAIMS: t"SELECT s.source_db_name, COUNT(*) FROM drug_claims dc LEFT JOIN sources s on s.id = dc.source_id group by s.source_db_name;",
        SourceMetric.DRUG_CLAIM_ALIASES: t"SELECT s.source_db_name, COUNT(*) FROM drug_claim_aliases dca LEFT JOIN drug_claims dc ON dca.drug_claim_id = dc.id LEFT JOIN sources s ON s.id = dc.source_id GROUP BY s.source_db_name",
        SourceMetric.DRUG_CLAIM_ATTRIBUTES: t"SELECT s.source_db_name, COUNT(*) FROM drug_claim_attributes dca LEFT JOIN drug_claims dc ON dca.drug_claim_id = dc.id LEFT JOIN sources s ON s.id = dc.source_id GROUP BY s.source_db_name",
        SourceMetric.GENE_CLAIMS: t"SELECT s.source_db_name, COUNT(*) FROM gene_claims gc LEFT JOIN sources s on s.id = gc.source_id group by s.source_db_name;",
        SourceMetric.GENE_CLAIM_ALIASES: t"SELECT s.source_db_name, COUNT(*) FROM gene_claim_aliases gca LEFT JOIN gene_claims gc ON gca.gene_claim_id = gc.id LEFT JOIN sources s ON s.id = gc.source_id GROUP BY s.source_db_name",
        SourceMetric.GENE_CLAIM_ATTRIBUTES: t"SELECT s.source_db_name, COUNT(*) FROM gene_claim_attributes gca LEFT JOIN gene_claims gc ON gca.gene_claim_id = gc.id LEFT JOIN sources s ON s.id = gc.source_id GROUP BY s.source_db_name",
        SourceMetric.INTERACTION_CLAIMS: t"SELECT s.source_db_name, COUNT(*) FROM interaction_claims ic LEFT JOIN sources s on s.id = ic.source_id group by s.source_db_name;",
        SourceMetric.INTERACTION_CLAIM_ATTRIBUTES: t"SELECT s.source_db_name, COUNT(*) FROM interaction_claim_attributes ica LEFT JOIN interaction_claims ic ON ica.interaction_claim_id = ic.id LEFT JOIN sources s ON s.id = ic.source_id GROUP BY s.source_db_name",
        SourceMetric.INTERACTION_CLAIMS_PUBLICATIONS: t"SELECT s.source_db_name, COUNT(*) FROM interaction_claims_publications icp LEFT JOIN interaction_claims ic ON ic.id = icp.interaction_claim_id LEFT JOIN sources s ON s.id = ic.source_id GROUP BY s.source_db_name;",
        SourceMetric.INTERACTION_CLAIM_TYPES_INTERACTION_CLAIMS: t"SELECT s.source_db_name, COUNT(*) FROM interaction_claim_types_interaction_claims ictic LEFT JOIN interaction_claims ic ON ictic.interaction_claim_id = ic.id LEFT JOIN sources s ON ic.source_id = s.id GROUP BY s.source_db_name",
        SourceMetric.GENE_CATEGORY_CLAIMS: t"SELECT s.source_db_name, COUNT(*) FROM gene_claim_categories_gene_claims gccgc LEFT JOIN gene_claims gc ON gccgc.gene_claim_id = gc.id LEFT JOIN sources s ON gc.source_id = s.id GROUP BY s.source_db_name;",
    }
    for metric, query in queries.items():
        with pg_conn.cursor() as cursor:
            cursor.execute(query)
            counts.extend(
                SourceMetricCount(
                    source_name=result[0], metric_name=metric, count=result[1]
                )
                for result in cursor.fetchall()
            )
    return counts


def collect_global_counts(pg_conn: psycopg.Connection) -> list:
    """Run queries to get global counts"""
    queries = {
        GlobalMetric.SOURCES: t"SELECT COUNT(*) FROM sources;",
        GlobalMetric.GENES: t"SELECT COUNT(*) FROM genes;",
        GlobalMetric.DRUGS: t"SELECT COUNT(*) FROM drugs;",
        GlobalMetric.INTERACTIONS: t"SELECT COUNT(*) FROM interactions;",
        GlobalMetric.GENE_CATEGORIZATIONS: t"SELECT COUNT(*) FROM gene_categories_genes;",
        GlobalMetric.DRUG_APPROVAL_RATINGS: t"SELECT COUNT(*) FROM drug_approval_ratings;",
        GlobalMetric.DRUG_APPLICATIONS: t"SELECT COUNT(*) FROM drug_applications;",
        GlobalMetric.PUBLICATIONS: t"SELECT COUNT(*) FROM publications;",
    }
    counts = []
    for metric, query in queries.items():
        with pg_conn.cursor() as cursor:
            cursor.execute(query)
            counts.extend(
                GlobalMetricCount(metric_name=metric, count=result[0])
                for result in cursor.fetchall()
            )
    return counts


def save_analytics(
    analytics_conn: sqlite3.Connection,
    snapshot_id: int,
    global_counts: list[GlobalMetricCount],
    source_counts: list[SourceMetricCount],
) -> None:
    """Save collected analytics to SQLite."""
    for count in global_counts:
        add_snapshot_global_count(
            analytics_conn,
            snapshot_id=snapshot_id,
            metric_name=count.metric_name,
            count=count.count,
        )

    for count in source_counts:
        add_snapshot_source_count(
            analytics_conn,
            snapshot_id=snapshot_id,
            source_name=count.source_name,
            metric_name=count.metric_name,
            count=count.count,
        )


def create_analytics_snapshot(
    analytics_db_path: Path,
    postgres_dsn: str,
    snapshot_name: str,
    snapshot_status: SnapshotStatus = SnapshotStatus.PROVISIONAL,
    notes: str | None = None,
) -> int:
    """Collect analytics from Postgres and save them as a new snapshot."""
    with connect(analytics_db_path) as analytics_conn:
        snapshot_id = create_snapshot(
            analytics_conn,
            name=snapshot_name,
            status=snapshot_status,
            notes=notes,
        )

        with psycopg.connect(postgres_dsn) as pg_conn:
            global_counts = collect_global_counts(pg_conn)
            source_counts = collect_source_counts(pg_conn)

        save_analytics(
            analytics_conn,
            snapshot_id=snapshot_id,
            global_counts=global_counts,
            source_counts=source_counts,
        )

    return snapshot_id
