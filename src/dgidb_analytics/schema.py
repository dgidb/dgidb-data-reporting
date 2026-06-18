from enum import StrEnum

from pydantic import BaseModel


class SnapshotStatus(StrEnum):
    PROVISIONAL = "provisional"
    RELEASED = "released"


class SourceMetric(StrEnum):
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
    source_name: str
    metric_name: SourceMetric
    count: int


class GlobalMetric(StrEnum):
    GENES = "genes"
    DRUGS = "drugs"
    INTERACTIONS = "interactions"
    SOURCES = "sources"
    GENE_CATEGORIZATIONS = "gene_categorizations"
    DRUG_APPROVAL_RATINGS = "drug_approval_ratings"
    DRUG_APPLICATIONS = "drug_applications"
    PUBLICATIONS = "publications"


class GlobalMetricCount(BaseModel):
    metric_name: GlobalMetric
    count: int
