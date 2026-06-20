"""
DecisionDNA AI — ContractGenomeAgent

Detects mutations in the Contract Gene by comparing provider
contract / network enrollment state across two decision snapshots.
"""

from __future__ import annotations

from typing import Any

from src.agents.base_agent import BaseAgent
from src.models.decision_models import DecisionGenome, GeneMutation
from src.tools import contract_mcp


class ContractGenomeAgent(BaseAgent):
    """Detects mutations in the Contract Gene."""

    def __init__(self) -> None:
        super().__init__(
            name="ContractGenomeAgent",
            description="Compare provider contract/network status and detect contract gene mutations.",
        )

    def analyze(
        self,
        old_genome: DecisionGenome,
        new_genome: DecisionGenome,
        **kwargs: Any,
    ) -> GeneMutation:
        self._log_invocation(case_id=old_genome.case_id)

        old_cg = old_genome.genes.contract_gene
        new_cg = new_genome.genes.contract_gene

        if (
            old_cg.version == new_cg.version
            and old_cg.network_status == new_cg.network_status
            and old_cg.provider_status == new_cg.provider_status
        ):
            return GeneMutation(
                gene_name="Contract Gene",
                mutated=False,
                severity="none",
                before=old_cg.model_dump(),
                after=new_cg.model_dump(),
                details="Contract gene unchanged.",
            )

        # Use MCP tool for detailed comparison
        diff = contract_mcp.compare_contracts(old_cg.version, new_cg.version)

        severity = "medium"
        if new_cg.provider_status == "TERMINATED":
            severity = "critical"
        elif new_cg.network_status == "OUT_OF_NETWORK":
            severity = "high"

        details_parts = [
            f"Contract version changed: {old_cg.version} → {new_cg.version}.",
        ]
        for change in diff.get("changes", []):
            details_parts.append(f"  • {change}")
        if diff.get("termination_reason"):
            details_parts.append(f"  Termination reason: {diff['termination_reason']}")
        if diff.get("continuity_of_care_flag"):
            details_parts.append("  ⚠ Continuity of care review required.")

        return GeneMutation(
            gene_name="Contract Gene",
            mutated=True,
            severity=severity,
            before=old_cg.model_dump(),
            after=new_cg.model_dump(),
            details="\n".join(details_parts),
        )
