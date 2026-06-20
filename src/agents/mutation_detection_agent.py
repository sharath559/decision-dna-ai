"""
DecisionDNA AI — MutationDetectionAgent

Orchestrator agent that aggregates findings from all five genome agents
(Policy, Contract, Rule, Documentation, Network) and produces a unified
MutationReport with primary/secondary mutations, confidence score,
root-cause explanation, and human-review flag.
"""

from __future__ import annotations

from typing import Any

from src.agents.base_agent import BaseAgent
from src.models.decision_models import (
    DecisionGenome,
    GeneMutation,
    MutationReport,
)


# Severity → numeric weight for scoring
_SEVERITY_WEIGHTS: dict[str, int] = {
    "none": 0,
    "low": 10,
    "medium": 25,
    "high": 50,
    "critical": 75,
}


class MutationDetectionAgent(BaseAgent):
    """
    Aggregate genome-agent findings, rank mutations, and produce
    the final MutationReport.
    """

    def __init__(self) -> None:
        super().__init__(
            name="MutationDetectionAgent",
            description="Aggregate all genome-agent findings. Determine primary/secondary mutations.",
        )

    def analyze(
        self,
        old_genome: DecisionGenome,
        new_genome: DecisionGenome,
        gene_mutations: list[GeneMutation],
        **kwargs: Any,
    ) -> MutationReport:
        self._log_invocation(case_id=old_genome.case_id)

        # Separate mutated from stable genes
        mutated = [gm for gm in gene_mutations if gm.mutated]
        mutated.sort(
            key=lambda gm: _SEVERITY_WEIGHTS.get(gm.severity, 0), reverse=True
        )

        primary = mutated[0].gene_name if mutated else "None"
        secondary = [gm.gene_name for gm in mutated[1:]]

        # Mutation score: weighted sum capped at 100
        raw_score = sum(_SEVERITY_WEIGHTS.get(gm.severity, 0) for gm in mutated)
        mutation_score = min(raw_score, 100)
        confidence = round(mutation_score / 100, 2)

        # Root cause narrative
        root_cause = self._build_root_cause(mutated)

        # Human review required if any critical/high mutation or decision changed
        human_review = any(
            gm.severity in ("critical", "high") for gm in mutated
        ) or (old_genome.decision != new_genome.decision)

        recommendation = self._build_recommendation(mutated, human_review)

        report = MutationReport(
            case_id=old_genome.case_id,
            old_decision=old_genome.decision,
            new_decision=new_genome.decision,
            old_snapshot_date=old_genome.snapshot_date,
            new_snapshot_date=new_genome.snapshot_date,
            primary_mutation=primary,
            secondary_mutations=secondary,
            gene_mutations=gene_mutations,
            mutation_score=mutation_score,
            confidence=confidence,
            root_cause=root_cause,
            human_review_required=human_review,
            recommendation=recommendation,
        )
        report.compute_genome_hash()
        report.compute_scenario_fingerprint()
        return report

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_root_cause(mutated: list[GeneMutation]) -> str:
        if not mutated:
            return "No mutations detected. Decision genes are stable."
        parts = []
        for gm in mutated:
            parts.append(f"• {gm.gene_name} ({gm.severity}): {gm.details.splitlines()[0]}")
        return "\n".join(parts)

    @staticmethod
    def _build_recommendation(
        mutated: list[GeneMutation], human_review: bool
    ) -> str:
        if not mutated:
            return "No action required. Decision is consistent."
        tips: list[str] = []
        gene_names = {gm.gene_name for gm in mutated}
        if "Documentation Gene" in gene_names:
            tips.append("Request missing documentation from the submitter.")
        if "Policy Gene" in gene_names:
            tips.append("Verify whether the new policy version applies retroactively.")
        if "Contract Gene" in gene_names:
            tips.append("Check contract termination effective date and continuity-of-care obligations.")
        if "Network Gene" in gene_names:
            tips.append("Confirm provider network status at date of service.")
        if "Rule Gene" in gene_names:
            tips.append("Review new validation requirements for applicability.")
        if human_review:
            tips.append("Route to clinical/compliance reviewer for final determination.")
        return " ".join(tips)
