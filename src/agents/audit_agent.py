"""
DecisionDNA AI — AuditAgent

Generates the final executive audit report by combining mutation
analysis, impact assessment, and security review into a single
structured AuditReport, then persists it via the AuditMCP tool.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Any, Optional

from src.agents.base_agent import BaseAgent
from src.models.decision_models import (
    AuditReport,
    ImpactAssessment,
    MutationReport,
    SecurityReport,
)
from src.tools import audit_mcp


class AuditAgent(BaseAgent):
    """Generate and persist the final executive audit report."""

    def __init__(self) -> None:
        super().__init__(
            name="AuditAgent",
            description="Generate final executive audit report.",
        )

    def analyze(
        self,
        mutation_report: MutationReport,
        impact: ImpactAssessment,
        security: SecurityReport,
        case_meta: Optional[dict[str, Any]] = None,
        **kwargs: Any,
    ) -> AuditReport:
        self._log_invocation(case_id=mutation_report.case_id)

        meta = case_meta or {}
        build_mode = "PRIVATE" if os.getenv("PRIVATE_DEMO_MODE", "").lower() == "true" else "PUBLIC"

        report = AuditReport(
            report_id=audit_mcp.generate_audit_id(mutation_report.case_id),
            case_id=mutation_report.case_id,
            generated_at=datetime.utcnow().isoformat(),
            executive_summary=self._build_summary(mutation_report, meta),
            decision_lineage=self._build_lineage(mutation_report),
            root_cause=mutation_report.root_cause,
            supporting_evidence=self._extract_evidence(mutation_report, "supporting"),
            missing_evidence=self._extract_evidence(mutation_report, "missing"),
            recommendation=mutation_report.recommendation,
            human_review_flag=mutation_report.human_review_required,
            risk_level=impact.risk_level,
            impact=impact,
            security_status="PASSED" if security.allowed else "BLOCKED",
            build_mode=build_mode,
            scenario_fingerprint=mutation_report.scenario_fingerprint,
            genome_hash=mutation_report.genome_hash,
        )

        # Persist via MCP tool
        audit_mcp.store_audit_record(report.model_dump())

        return report

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_summary(report: MutationReport, meta: dict) -> str:
        title = meta.get("title", report.case_id)
        return (
            f"Decision Forensics Report for {title}.\n"
            f"Decision changed from {report.old_decision} to {report.new_decision} "
            f"between {report.old_snapshot_date} and {report.new_snapshot_date}.\n"
            f"Primary mutation: {report.primary_mutation}. "
            f"Mutation score: {report.mutation_score}/100 "
            f"(confidence {report.confidence:.0%}).\n"
            f"Human review {'required' if report.human_review_required else 'not required'}."
        )

    @staticmethod
    def _build_lineage(report: MutationReport) -> str:
        lines = [
            f"Case {report.case_id}: {report.old_decision} ({report.old_snapshot_date}) → "
            f"{report.new_decision} ({report.new_snapshot_date})",
        ]
        for gm in report.gene_mutations:
            status = "MUTATED" if gm.mutated else "STABLE"
            lines.append(f"  {gm.gene_name}: {status} ({gm.severity})")
        return "\n".join(lines)

    @staticmethod
    def _extract_evidence(report: MutationReport, kind: str) -> list[str]:
        """Pull supporting or missing evidence from gene mutations."""
        items: list[str] = []
        for gm in report.gene_mutations:
            if kind == "missing" and gm.gene_name == "Documentation Gene":
                after = gm.after
                items.extend(after.get("missing", []))
            elif kind == "supporting" and not gm.mutated:
                items.append(f"{gm.gene_name}: stable — no contribution to drift.")
            elif kind == "supporting" and gm.mutated:
                items.append(f"{gm.gene_name}: {gm.details.splitlines()[0]}")
        return items
