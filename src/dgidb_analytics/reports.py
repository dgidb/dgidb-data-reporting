"""Create user-facing reports about analytics results"""

import sqlite3
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel

from dgidb_analytics.db import (
    get_latest_released_snapshot,
    get_snapshot_by_name,
    get_snapshot_metrics,
)

if TYPE_CHECKING:
    from pathlib import Path

    from dgidb_analytics.schema import (
        GlobalMetric,
        GlobalMetricCount,
        SourceMetric,
        SourceMetricCount,
    )


class MetricComparison(BaseModel):
    """Comparison between prior and provisional counts for a given metric"""

    scope: Literal["global"] | Literal["source"]
    metric_name: GlobalMetric | SourceMetric
    provisional_count: int | None
    previous_count: int | None
    source_name: str | None = None


def _compare_source_metrics(
    provisional_counts: list[SourceMetricCount],
    previous_counts: list[SourceMetricCount],
) -> list[MetricComparison]:
    provisional_map = {
        (m.source_name, m.metric_name): m.count for m in provisional_counts
    }
    previous_map = {(m.source_name, m.metric_name): m.count for m in previous_counts}

    results = []

    for (source_name, metric_name), provisional_count in provisional_map.items():
        results.append(
            MetricComparison(
                scope="source",
                source_name=source_name,
                metric_name=metric_name,
                provisional_count=provisional_count,
                previous_count=previous_map.get((source_name, metric_name)),
            )
        )

    for source_name, metric_name in previous_map.keys() - provisional_map.keys():
        results.append(
            MetricComparison(
                scope="source",
                source_name=source_name,
                metric_name=metric_name,
                provisional_count=None,
                previous_count=previous_map[(source_name, metric_name)],
            )
        )

    return results


def _compare_global_metrics(
    provisional_counts: list[GlobalMetricCount],
    previous_counts: list[GlobalMetricCount],
) -> list[MetricComparison]:
    provisional_map = {m.metric_name: m.count for m in provisional_counts}
    previous_map = {m.metric_name: m.count for m in previous_counts}
    results = []
    for metric_name, provisional_count in provisional_map.items():
        results.append(
            MetricComparison(
                scope="global",
                metric_name=metric_name,
                provisional_count=provisional_count,
                previous_count=previous_map.get(metric_name),
            )
        )
    for metric_name in previous_map.keys() - provisional_map.keys():
        results.append(  # noqa: PERF401
            MetricComparison(
                scope="global",
                metric_name=metric_name,
                provisional_count=None,
                previous_count=previous_map[metric_name],
            )
        )

    return results


def check_provisional_snapshot(
    analytics_db_path: Path, snapshot_name: str
) -> list[MetricComparison]:
    """Compare a provisional snapshot against the most recent official release"""
    with sqlite3.connect(analytics_db_path) as connect:
        provisional_snapshot = get_snapshot_by_name(connect, snapshot_name)
        provisional_counts = get_snapshot_metrics(connect, provisional_snapshot.id)
        previous_snapshot = get_latest_released_snapshot(connect)
        previous_counts = get_snapshot_metrics(connect, previous_snapshot.id)
    return _compare_global_metrics(
        provisional_counts[1], previous_counts[1]
    ) + _compare_source_metrics(provisional_counts[0], previous_counts[0])
