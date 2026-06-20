"""
DecisionDNA AI — BaseAgent

Abstract base class that every genome / mutation / impact / audit agent
implements.  Provides a uniform interface so the orchestrator
(``genome_builder.py``) can invoke agents polymorphically.

Design decisions:
  • ``analyze()`` is the single entry point — keeps the call protocol simple.
  • Every agent logs its own invocation for audit traceability.
  • Agents are stateless callables; all context comes through arguments.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class BaseAgent(ABC):
    """Common contract for all DecisionDNA agents."""

    def __init__(self, name: str, description: str = "") -> None:
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"decisiondna.agents.{name}")

    @abstractmethod
    def analyze(self, **kwargs: Any) -> dict[str, Any]:
        """
        Run the agent's analysis and return structured results.

        Each concrete agent decides which kwargs it needs.
        """
        ...

    def _log_invocation(self, **kwargs: Any) -> None:
        """Emit a structured log line for the audit trail."""
        self.logger.info(
            "%s invoked | kwargs_keys=%s | ts=%s",
            self.name,
            list(kwargs.keys()),
            datetime.utcnow().isoformat(),
        )
