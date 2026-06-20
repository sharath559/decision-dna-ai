"""
DecisionDNA AI — Mutation Engine Service

Orchestrates the multi-agent analysis pipeline:
  1. Load genome pair
  2. Run each genome agent in parallel
  3. Aggregate via MutationDetectionAgent
  4. Compute impact via ImpactAgent
  5. Run security scan
  6. Generate audit report

Provides the top-level ``run_full_analysis`` function.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from src.agents.audit_agent import AuditAgent
from src.agents.contract_genome_agent import ContractGenomeAgent
from src.agents.documentation_genome_agent import DocumentationGenomeAgent
from src.agents.impact_agent import ImpactAgent
from src.agents.mutation_detection_agent import MutationDetectionAgent
from src.agents.network_genome_agent import NetworkGenomeAgent
from src.agents.policy_genome_agent import PolicyGenomeAgent
from src.agents.rule_genome_agent import RuleGenomeAgent
from src.agents.security_agent import SecurityAgent
from src.models.decision_models import (
    AuditReport,
    DecisionGenome,
    GeneMutation,
    ImpactAssessment,
    MutationReport,
    SecurityReport,
)
from src.services.genome_builder import get_genome_pair

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_sample_cases() -> list[dict[str, Any]]:
    with open(_DATA_DIR / "sample_cases.json") as f:
        return json.load(f).get("cases", [])


def _find_case_meta(case_id: str) -> dict[str, Any]:
    for c in _load_sample_cases():
        if c["case_id"] == case_id:
            return c
    return {}


# ── Agent singletons ──────────────────────────────────────────────────────

_policy_agent = PolicyGenomeAgent()
_contract_agent = ContractGenomeAgent()
_rule_agent = RuleGenomeAgent()
_doc_agent = DocumentationGenomeAgent()
_network_agent = NetworkGenomeAgent()
_mutation_agent = MutationDetectionAgent()
_impact_agent = ImpactAgent()
_security_agent = SecurityAgent()
_audit_agent = AuditAgent()


# ── Skills / public API ───────────────────────────────────────────────────

def detect_mutations(
    old_genome: DecisionGenome, new_genome: DecisionGenome
) -> list[GeneMutation]:
    """
    Skill: detect_mutations

    Run all five genome agents and return a list of GeneMutation objects.
    """
    return [
        _policy_agent.analyze(old_genome=old_genome, new_genome=new_genome),
        _contract_agent.analyze(old_genome=old_genome, new_genome=new_genome),
        _rule_agent.analyze(old_genome=old_genome, new_genome=new_genome),
        _doc_agent.analyze(old_genome=old_genome, new_genome=new_genome),
        _network_agent.analyze(old_genome=old_genome, new_genome=new_genome),
    ]


def calculate_mutation_score(
    old_genome: DecisionGenome,
    new_genome: DecisionGenome,
    gene_mutations: list[GeneMutation],
) -> MutationReport:
    """
    Skill: calculate_mutation_score

    Aggregate gene mutations into a scored MutationReport.
    """
    return _mutation_agent.analyze(
        old_genome=old_genome,
        new_genome=new_genome,
        gene_mutations=gene_mutations,
    )


def scan_security_risks(text: str) -> SecurityReport:
    """
    Skill: scan_security_risks

    Run the SecurityAgent on arbitrary text.
    """
    return _security_agent.analyze(input_text=text)


def generate_audit_report(
    mutation_report: MutationReport,
    impact: ImpactAssessment,
    security: SecurityReport,
    case_meta: Optional[dict[str, Any]] = None,
) -> AuditReport:
    """
    Skill: generate_audit_report

    Produce the final executive audit report.
    """
    return _audit_agent.analyze(
        mutation_report=mutation_report,
        impact=impact,
        security=security,
        case_meta=case_meta,
    )


def run_analysis_for_pair(
    old_genome: DecisionGenome,
    new_genome: DecisionGenome,
    case_meta: dict[str, Any],
) -> dict[str, Any]:
    """
    Run the multi-agent decision forensics analysis on a custom genome pair.
    """
    # 1. Detect gene-level mutations
    gene_mutations = detect_mutations(old_genome, new_genome)

    # 2. Aggregate into mutation report
    mutation_report = calculate_mutation_score(old_genome, new_genome, gene_mutations)

    # 3. Impact assessment
    impact = _impact_agent.analyze(
        mutation_report=mutation_report,
        decision_type=case_meta.get("decision_type", ""),
    )

    # 4. Security scan on original input
    security = scan_security_risks(
        case_meta.get("description", old_genome.case_id)
    )

    # 5. Audit report
    audit_report = generate_audit_report(
        mutation_report=mutation_report,
        impact=impact,
        security=security,
        case_meta=case_meta,
    )

    return {
        "old_genome": old_genome,
        "new_genome": new_genome,
        "gene_mutations": gene_mutations,
        "mutation_report": mutation_report,
        "impact": impact,
        "security": security,
        "audit_report": audit_report,
        "case_meta": case_meta,
    }


def run_full_analysis(case_id: str) -> dict[str, Any]:
    """
    End-to-end orchestration for a single case.

    Returns a dict with keys: old_genome, new_genome, gene_mutations,
    mutation_report, impact, security, audit_report, case_meta.
    """
    old_genome, new_genome = get_genome_pair(case_id)
    if old_genome is None or new_genome is None:
        raise ValueError(f"Could not load genome pair for case {case_id}")

    case_meta = _find_case_meta(case_id)
    return run_analysis_for_pair(old_genome, new_genome, case_meta)
