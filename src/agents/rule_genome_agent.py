"""
DecisionDNA AI — RuleGenomeAgent

Detects mutations in the Rule Gene by comparing business-rule
versions and their validation checks.
"""

from __future__ import annotations

from typing import Any

from src.agents.base_agent import BaseAgent
from src.models.decision_models import DecisionGenome, GeneMutation
from src.tools import rules_mcp


class RuleGenomeAgent(BaseAgent):
    """Detects mutations in the Rule Gene."""

    def __init__(self) -> None:
        super().__init__(
            name="RuleGenomeAgent",
            description="Compare business rule versions and detect rule gene mutations.",
        )

    def analyze(
        self,
        old_genome: DecisionGenome,
        new_genome: DecisionGenome,
        **kwargs: Any,
    ) -> GeneMutation:
        self._log_invocation(case_id=old_genome.case_id)

        old_rg = old_genome.genes.rule_gene
        new_rg = new_genome.genes.rule_gene

        if old_rg.version == new_rg.version:
            # Even same version can have new failures
            if set(old_rg.validations_failed) == set(new_rg.validations_failed):
                return GeneMutation(
                    gene_name="Rule Gene",
                    mutated=False,
                    severity="none",
                    before=old_rg.model_dump(),
                    after=new_rg.model_dump(),
                    details="Rule gene unchanged.",
                )

        diff = rules_mcp.compare_rules(old_rg.version, new_rg.version)

        added = diff.get("added_validations", [])
        removed = diff.get("removed_validations", [])

        # New validation failures are the most impactful
        new_failures = [
            v for v in new_rg.validations_failed
            if v not in old_rg.validations_failed
        ]

        severity = "low"
        if new_failures:
            severity = "high"
        if added:
            severity = max(severity, "medium", key=lambda s: ["low", "medium", "high", "critical"].index(s))

        details_parts = []
        if old_rg.version != new_rg.version:
            details_parts.append(f"Rule version changed: {old_rg.version} → {new_rg.version}.")
        if added:
            for v in added:
                details_parts.append(f"  + New validation: {v['description']}")
        if removed:
            for v in removed:
                details_parts.append(f"  − Removed validation: {v['description']}")
        if new_failures:
            details_parts.append(f"  New failing validations: {', '.join(new_failures)}")

        mutated = bool(
            old_rg.version != new_rg.version
            or new_failures
            or added
            or removed
        )

        return GeneMutation(
            gene_name="Rule Gene",
            mutated=mutated,
            severity=severity if mutated else "none",
            before=old_rg.model_dump(),
            after=new_rg.model_dump(),
            details="\n".join(details_parts) if details_parts else "No rule mutation detected.",
        )
