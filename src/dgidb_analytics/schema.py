"""Data models for analytics snapshots and metrics."""

from datetime import datetime  # noqa: TC003
from enum import StrEnum

from pydantic import BaseModel


class SnapshotStatus(StrEnum):
    """Lifecycle status of a snapshot."""

    PROVISIONAL = "provisional"
    RELEASED = "released"


class SnapshotMetadata(BaseModel):
    """Metadata describing a snapshot."""

    id: int | None = None
    name: str
    created_at: datetime | None = None
    status: SnapshotStatus
    notes: str | None = None


class SourceMetric(StrEnum):
    """Metric collected for a specific source."""

    DRUG_CLAIMS = "drug_claims"
    DRUG_CLAIM_ALIASES = "drug_claim_aliases"
    DRUG_CLAIM_ATTRIBUTES = "drug_claim_attributes"
    GENE_CLAIMS = "gene_claims"
    GENE_CLAIM_ALIASES = "gene_claim_aliases"
    GENE_CLAIM_ATTRIBUTES = "gene_claim_attributes"
    INTERACTION_CLAIMS = "interaction_claims"
    INTERACTION_CLAIM_ATTRIBUTES = "interaction_claim_attributes"
    INTERACTION_CLAIM_TYPES_INTERACTION_CLAIMS = (
        "interaction_claim_types_interaction_claims"
    )
    INTERACTION_CLAIMS_PUBLICATIONS = "interaction_claims_publications"
    GENE_CATEGORY_CLAIMS = "gene_category_claims"


class SourceMetricCount(BaseModel):
    """Count for a source-specific metric."""

    source_name: str
    metric_name: SourceMetric
    count: int


class GlobalMetric(StrEnum):
    """Metric collected across the entire DGIdb dataset."""

    DRUG_CLAIMS = "drug_claims"
    GENE_CLAIMS = "gene_claims"
    INTERACTION_CLAIMS = "interaction_claims"
    GENE_CATEGORY_CLAIMS = "gene_category_claims"
    GENES = "genes"
    DRUGS = "drugs"
    INTERACTIONS = "interactions"
    SOURCES = "sources"
    GENE_CATEGORIZATIONS = "gene_categorizations"
    DRUG_APPROVAL_RATINGS = "drug_approval_ratings"
    DRUG_APPLICATIONS = "drug_applications"
    PUBLICATIONS = "publications"


class GlobalMetricCount(BaseModel):
    """Count for a global metric."""

    metric_name: GlobalMetric
    count: int
