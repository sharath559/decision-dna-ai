"""
DecisionDNA AI — ImpactAgent

Estimates the business impact of a mutation-driven decision drift.
Uses heuristic rules based on decision type, severity, and gene mutations.
"""

from __future__ import annotations

from typing import Any

from src.agents.base_agent import BaseAgent
from src.models.decision_models import ImpactAssessment, MutationReport


# Heuristic affected-population estimates per decision type
_POPULATION_ESTIMATES: dict[str, int] = {
    "prior_authorization": 1200,
    "claim": 5400,
    "network": 8500,
}


class ImpactAgent(BaseAgent):
    """Estimate business impact of a decision mutation."""

    def __init__(self) -> None:
        super().__init__(
            name="ImpactAgent",
            description="Estimate business impact of decision drift.",
        )

    def analyze(
        self,
        mutation_report: MutationReport,
        decision_type: str = "",
        **kwargs: Any,
    ) -> ImpactAssessment:
        self._log_invocation(case_id=mutation_report.case_id)

        dt = decision_type or "prior_authorization"
        pop_estimate = _POPULATION_ESTIMATES.get(dt, 500)

        # Scale population by mutation severity
        if mutation_report.mutation_score >= 75:
            pop_estimate = int(pop_estimate * 0.3)
            risk = "CRITICAL"
        elif mutation_report.mutation_score >= 50:
            pop_estimate = int(pop_estimate * 0.15)
            risk = "HIGH"
        elif mutation_report.mutation_score >= 25:
            pop_estimate = int(pop_estimate * 0.05)
            risk = "MEDIUM"
        else:
            pop_estimate = int(pop_estimate * 0.01)
            risk = "LOW"

        systems = ["Claims Processing"]
        if "Contract Gene" in mutation_report.primary_mutation:
            systems.extend(["Provider Network Directory", "Credentialing System"])
        if "Policy Gene" in mutation_report.primary_mutation:
            systems.extend(["Prior Auth Engine", "Medical Policy Database"])
        if "Network Gene" in [mutation_report.primary_mutation] + mutation_report.secondary_mutations:
            systems.append("Provider Network Directory")
        systems = sorted(set(systems))

        ops_impact = self._describe_operational_impact(mutation_report, dt)

        return ImpactAssessment(
            case_id=mutation_report.case_id,
            affected_decision_type=dt,
            affected_population_estimate=pop_estimate,
            affected_systems=systems,
            operational_impact=ops_impact,
            risk_level=risk,
            financial_estimate=self._estimate_financial(dt, pop_estimate),
            compliance_note=self._compliance_note(mutation_report),
        )

    @staticmethod
    def _describe_operational_impact(report: MutationReport, dt: str) -> str:
        if dt == "prior_authorization":
            return (
                "Prior authorization workflow affected. Denials may increase "
                "for members who do not submit newly required documentation."
            )
        if dt == "claim":
            return (
                "Claims adjudication affected. Previously payable claims may "
                "now reject due to rule/network changes."
            )
        return (
            "Provider network directory affected. Member-facing lookups and "
            "referral routing may show stale data."
        )

    @staticmethod
    def _estimate_financial(dt: str, population: int) -> str:
        if dt == "claim":
            return f"Estimated claim volume impact: ~${population * 250:,} in rework/appeals."
        if dt == "prior_authorization":
            return f"Estimated appeal volume: ~{population} cases over next quarter."
        return f"Estimated member impact: ~{population} affected members."

    @staticmethod
    def _compliance_note(report: MutationReport) -> str:
        if report.human_review_required:
            return "Compliance review recommended. Decision drift may trigger regulatory reporting."
        return "Within normal operational parameters."
