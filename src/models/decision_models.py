"""
DecisionDNA AI — Domain Models

Pydantic models for Decision Genomes, Gene structures, Mutation results,
and Audit reports.  These are the shared data contracts that every agent,
tool, and service speaks.

Design note:  We use Pydantic v2 `model_validate` everywhere so that raw
dicts coming from JSON files or MCP tools are validated consistently.
"""

from __future__ import annotations

import hashlib
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class DecisionStatus(str, Enum):
    """Possible decision outcomes across PA, claims, and network domains."""
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    PAID = "PAID"
    REJECTED = "REJECTED"
    ACTIVE = "ACTIVE"
    TERMINATED = "TERMINATED"
    PENDING = "PENDING"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SecuritySeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


# ---------------------------------------------------------------------------
# Gene Models — the "chromosomes" of a Decision Genome
# ---------------------------------------------------------------------------

class PolicyGene(BaseModel):
    """Captures which policy version governs a decision."""
    version: str
    status: str = "matched"
    policy_name: str = ""


class ContractGene(BaseModel):
    """Captures provider contract / network enrollment state."""
    version: str
    network_status: str = "IN_NETWORK"
    provider_status: str = "ACTIVE"


class RuleGene(BaseModel):
    """Captures the business-rule version and its validation results."""
    version: str
    validations_passed: list[str] = Field(default_factory=list)
    validations_failed: list[str] = Field(default_factory=list)


class DocumentationGene(BaseModel):
    """Required vs. submitted evidence — the gap drives denials."""
    required: list[str] = Field(default_factory=list)
    submitted: list[str] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)


class NetworkGene(BaseModel):
    """Provider network participation snapshot."""
    status: str = "IN_NETWORK"
    network: str = ""


class EvidenceGene(BaseModel):
    """Supporting and contradicting clinical / administrative evidence."""
    supporting: list[str] = Field(default_factory=list)
    contradicting: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Decision Genome — the full "DNA fingerprint" of a decision at a point in time
# ---------------------------------------------------------------------------

class DecisionGenes(BaseModel):
    """Bundle of all six gene types that define a decision's DNA."""
    policy_gene: PolicyGene
    contract_gene: ContractGene
    rule_gene: RuleGene
    documentation_gene: DocumentationGene
    network_gene: NetworkGene
    evidence_gene: EvidenceGene = Field(default_factory=lambda: EvidenceGene())


class DecisionGenome(BaseModel):
    """
    A complete Decision Genome — a snapshot of every factor that
    influenced a healthcare decision on a specific date.
    """
    case_id: str
    snapshot_date: str
    decision: str
    decision_type: str = ""
    member_id: Optional[str] = None
    provider_id: Optional[str] = None
    provider_name: Optional[str] = None
    procedure: Optional[str] = None
    cpt_code: Optional[str] = None
    genes: DecisionGenes


# ---------------------------------------------------------------------------
# Gene Mutation — what changed in a single gene between two snapshots
# ---------------------------------------------------------------------------

class GeneMutation(BaseModel):
    """Describes how a single gene mutated between two decision snapshots."""
    gene_name: str
    mutated: bool = False
    severity: str = "none"  # none | low | medium | high | critical
    before: dict[str, Any] = Field(default_factory=dict)
    after: dict[str, Any] = Field(default_factory=dict)
    details: str = ""


# ---------------------------------------------------------------------------
# Mutation Report — aggregated result of the MutationDetectionAgent
# ---------------------------------------------------------------------------

class MutationReport(BaseModel):
    """
    The output of temporal decision forensics: which genes mutated,
    what the root cause is, and whether a human must review.
    """
    case_id: str
    old_decision: str
    new_decision: str
    old_snapshot_date: str
    new_snapshot_date: str
    primary_mutation: str
    secondary_mutations: list[str] = Field(default_factory=list)
    gene_mutations: list[GeneMutation] = Field(default_factory=list)
    mutation_score: int = 0
    confidence: float = 0.0
    root_cause: str = ""
    human_review_required: bool = False
    recommendation: str = ""

    # --- Originality metadata ---
    scenario_fingerprint: str = ""
    genome_hash: str = ""

    def compute_genome_hash(self) -> str:
        """Deterministic SHA-256 over the mutation-relevant fields."""
        payload = (
            f"{self.case_id}|{self.old_decision}|{self.new_decision}|"
            f"{self.primary_mutation}|{','.join(self.secondary_mutations)}|"
            f"{self.mutation_score}"
        )
        self.genome_hash = hashlib.sha256(payload.encode()).hexdigest()[:16]
        return self.genome_hash

    def compute_scenario_fingerprint(self) -> str:
        """Human-readable fingerprint for screenshots / video."""
        parts = [
            "DDNA",
            self.case_id,
            str(self.mutation_score),
            self.primary_mutation.replace(" ", "").upper()[:6],
        ]
        if self.secondary_mutations:
            parts.append(
                "-".join(m.replace(" ", "").upper()[:3] for m in self.secondary_mutations[:2])
            )
        parts.append(self.new_snapshot_date[:4])
        self.scenario_fingerprint = "-".join(parts)
        return self.scenario_fingerprint


# ---------------------------------------------------------------------------
# Impact Assessment
# ---------------------------------------------------------------------------

class ImpactAssessment(BaseModel):
    """Business-impact estimate produced by the ImpactAgent."""
    case_id: str
    affected_decision_type: str
    affected_population_estimate: int = 0
    affected_systems: list[str] = Field(default_factory=list)
    operational_impact: str = ""
    risk_level: str = "MEDIUM"
    financial_estimate: str = ""
    compliance_note: str = ""


# ---------------------------------------------------------------------------
# Security Finding
# ---------------------------------------------------------------------------

class SecurityFinding(BaseModel):
    """One finding from the SecurityAgent."""
    finding_type: str  # prompt_injection | pii_detected | unsafe_instruction
    severity: SecuritySeverity = SecuritySeverity.WARNING
    detail: str = ""
    matched_pattern: str = ""


class SecurityReport(BaseModel):
    """Full output of the SecurityAgent."""
    input_text: str
    sanitized_text: str = ""
    allowed: bool = True
    findings: list[SecurityFinding] = Field(default_factory=list)
    scan_timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )


# ---------------------------------------------------------------------------
# Audit Report — the executive-level deliverable
# ---------------------------------------------------------------------------

class AuditReport(BaseModel):
    """
    Final executive audit report combining mutation analysis,
    impact assessment, security review, and recommendations.
    """
    report_id: str = ""
    case_id: str
    generated_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )
    executive_summary: str = ""
    decision_lineage: str = ""
    root_cause: str = ""
    supporting_evidence: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    recommendation: str = ""
    human_review_flag: bool = False
    risk_level: str = "MEDIUM"
    impact: Optional[ImpactAssessment] = None
    security_status: str = "PASSED"

    # --- Originality metadata ---
    project_name: str = "DecisionDNA AI"
    author: str = "Sharath Chandra"
    build_mode: str = "PUBLIC"
    scenario_fingerprint: str = ""
    genome_hash: str = ""


# ---------------------------------------------------------------------------
# Timeline Event (for the temporal view)
# ---------------------------------------------------------------------------

class TimelineEvent(BaseModel):
    """A single event on the decision's temporal timeline."""
    date: str
    event: str
    category: str = "general"  # policy | contract | rule | documentation | network | decision
