"""
DecisionDNA AI — DocumentationGenomeAgent

Detects mutations in the Documentation Gene by comparing
required vs. submitted documents across decision snapshots.
"""

from __future__ import annotations

from typing import Any

from src.agents.base_agent import BaseAgent
from src.models.decision_models import DecisionGenome, GeneMutation
from src.tools import documentation_mcp


class DocumentationGenomeAgent(BaseAgent):
    """Detects mutations in the Documentation Gene."""

    def __init__(self) -> None:
        super().__init__(
            name="DocumentationGenomeAgent",
            description="Compare required vs. submitted documents and detect documentation gene mutations.",
        )

    def analyze(
        self,
        old_genome: DecisionGenome,
        new_genome: DecisionGenome,
        **kwargs: Any,
    ) -> GeneMutation:
        self._log_invocation(case_id=old_genome.case_id)

        old_dg = old_genome.genes.documentation_gene
        new_dg = new_genome.genes.documentation_gene

        # Detect requirement changes
        new_requirements = [r for r in new_dg.required if r not in old_dg.required]
        removed_requirements = [r for r in old_dg.required if r not in new_dg.required]

        # Current gap
        missing = new_dg.missing

        mutated = bool(new_requirements or removed_requirements or missing != old_dg.missing)

        severity = "none"
        if mutated:
            severity = "medium"
            if missing:
                severity = "high"

        details_parts = []
        if new_requirements:
            details_parts.append(f"New documentation requirements: {', '.join(new_requirements)}")
        if removed_requirements:
            details_parts.append(f"Removed requirements: {', '.join(removed_requirements)}")
        if missing:
            details_parts.append(f"Missing documents: {', '.join(missing)}")
        if not details_parts:
            details_parts.append("Documentation gene unchanged.")

        return GeneMutation(
            gene_name="Documentation Gene",
            mutated=mutated,
            severity=severity,
            before=old_dg.model_dump(),
            after=new_dg.model_dump(),
            details="\n".join(details_parts),
        )
