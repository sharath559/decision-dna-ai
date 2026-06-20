"""
DecisionDNA AI — PolicyGenomeAgent

Compares old and new policy versions through the PolicyMCP tool
and emits a GeneMutation describing what changed in the Policy Gene.
"""

from __future__ import annotations

from typing import Any

from src.agents.base_agent import BaseAgent
from src.models.decision_models import DecisionGenome, GeneMutation
from src.tools import policy_mcp


class PolicyGenomeAgent(BaseAgent):
    """Detects mutations in the Policy Gene between two decision snapshots."""

    def __init__(self) -> None:
        super().__init__(
            name="PolicyGenomeAgent",
            description="Compare policy versions and detect policy gene mutations.",
        )

    def analyze(
        self,
        old_genome: DecisionGenome,
        new_genome: DecisionGenome,
        **kwargs: Any,
    ) -> GeneMutation:
        self._log_invocation(case_id=old_genome.case_id)

        old_pg = old_genome.genes.policy_gene
        new_pg = new_genome.genes.policy_gene

        # If versions are identical, no mutation
        if old_pg.version == new_pg.version:
            return GeneMutation(
                gene_name="Policy Gene",
                mutated=False,
                severity="none",
                before=old_pg.model_dump(),
                after=new_pg.model_dump(),
                details="Policy version unchanged.",
            )

        # Use MCP tool to get clause-level diff
        diff = policy_mcp.compare_policy_versions(old_pg.version, new_pg.version)

        added = diff.get("added_clauses", [])
        removed = diff.get("removed_clauses", [])

        severity = "low"
        if added:
            severity = "high"
        if removed:
            severity = "critical"

        details_parts = [
            f"Policy version changed: {old_pg.version} → {new_pg.version}.",
        ]
        if added:
            for clause in added:
                details_parts.append(
                    f"  + Added clause {clause['clause_id']}: {clause['description']}"
                )
        if removed:
            for clause in removed:
                details_parts.append(
                    f"  − Removed clause {clause['clause_id']}: {clause['description']}"
                )

        return GeneMutation(
            gene_name="Policy Gene",
            mutated=True,
            severity=severity,
            before=old_pg.model_dump(),
            after=new_pg.model_dump(),
            details="\n".join(details_parts),
        )
