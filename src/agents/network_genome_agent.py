"""
DecisionDNA AI — NetworkGenomeAgent

Detects mutations in the Network Gene by comparing provider
network participation status across decision snapshots.
"""

from __future__ import annotations

from typing import Any

from src.agents.base_agent import BaseAgent
from src.models.decision_models import DecisionGenome, GeneMutation


class NetworkGenomeAgent(BaseAgent):
    """Detects mutations in the Network Gene."""

    def __init__(self) -> None:
        super().__init__(
            name="NetworkGenomeAgent",
            description="Analyze provider network participation changes.",
        )

    def analyze(
        self,
        old_genome: DecisionGenome,
        new_genome: DecisionGenome,
        **kwargs: Any,
    ) -> GeneMutation:
        self._log_invocation(case_id=old_genome.case_id)

        old_ng = old_genome.genes.network_gene
        new_ng = new_genome.genes.network_gene

        if old_ng.status == new_ng.status and old_ng.network == new_ng.network:
            return GeneMutation(
                gene_name="Network Gene",
                mutated=False,
                severity="none",
                before=old_ng.model_dump(),
                after=new_ng.model_dump(),
                details="Network gene unchanged.",
            )

        severity = "medium"
        if new_ng.status == "OUT_OF_NETWORK":
            severity = "critical"

        details_parts = []
        if old_ng.status != new_ng.status:
            details_parts.append(f"Network status changed: {old_ng.status} → {new_ng.status}.")
        if old_ng.network != new_ng.network:
            details_parts.append(f"Network affiliation changed: {old_ng.network} → {new_ng.network}.")
        if new_ng.status == "OUT_OF_NETWORK":
            details_parts.append("Provider is now out-of-network. Claims may be affected.")

        return GeneMutation(
            gene_name="Network Gene",
            mutated=True,
            severity=severity,
            before=old_ng.model_dump(),
            after=new_ng.model_dump(),
            details="\n".join(details_parts),
        )
