"""
DecisionDNA AI — SecurityAgent

Scans user input (and agent-generated text) for:
  1. Prompt injection patterns
  2. PII-like patterns (fake SSN, email, phone, member ID)
  3. Unsafe instruction patterns (delete, override, reveal)

The agent does NOT block the application — it emits findings that
the UI surfaces in the Security Review tab and that the AuditAgent
includes in the compliance report.
"""

from __future__ import annotations

import re
from typing import Any

from src.agents.base_agent import BaseAgent
from src.models.decision_models import SecurityFinding, SecurityReport, SecuritySeverity


# ---------------------------------------------------------------------------
# Pattern libraries
# ---------------------------------------------------------------------------

PROMPT_INJECTION_PATTERNS: list[tuple[str, str]] = [
    (r"ignore\s+previous\s+instructions", "ignore previous instructions"),
    (r"bypass\s+policy", "bypass policy"),
    (r"override\s+approval", "override approval"),
    (r"auto[- ]?approve", "auto-approve"),
    (r"force\s+approval", "force approval"),
    (r"ignore\s+policy", "ignore policy"),
    (r"instead\s+of\s+the\s+above", "instead of the above"),
    (r"disregard\s+(all|previous)", "disregard instructions"),
    (r"you\s+are\s+now", "role hijacking attempt"),
]

UNSAFE_INSTRUCTION_PATTERNS: list[tuple[str, str]] = [
    (r"delete\s+records", "delete records"),
    (r"reveal\s+api\s+key", "reveal api key"),
    (r"send\s+phi", "send PHI"),
    (r"export\s+patient\s+data", "export patient data"),
    (r"disable\s+audit", "disable audit"),
    (r"drop\s+table", "drop table"),
    (r"truncate\s+table", "truncate table"),
]

PII_PATTERNS: list[tuple[str, str]] = [
    (r"\b\d{3}-\d{2}-\d{4}\b", "SSN-like pattern"),
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "Email address"),
    (r"\b\d{3}[- ]?\d{3}[- ]?\d{4}\b", "Phone number"),
    (r"\bMBR-\w+-\d+\b", "Member ID pattern"),
]


class SecurityAgent(BaseAgent):
    """Scan input text for prompt injection, PII, and unsafe instructions."""

    def __init__(self) -> None:
        super().__init__(
            name="SecurityAgent",
            description="Detect prompt injection, PII-like patterns, and unsafe instructions.",
        )

    def analyze(self, input_text: str, **kwargs: Any) -> SecurityReport:
        self._log_invocation(input_length=len(input_text))

        findings: list[SecurityFinding] = []
        text_lower = input_text.lower()

        # 1. Prompt injection
        for pattern, label in PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, text_lower):
                findings.append(
                    SecurityFinding(
                        finding_type="prompt_injection",
                        severity=SecuritySeverity.CRITICAL,
                        detail=f"Prompt injection detected: '{label}'",
                        matched_pattern=label,
                    )
                )

        # 2. Unsafe instructions
        for pattern, label in UNSAFE_INSTRUCTION_PATTERNS:
            if re.search(pattern, text_lower):
                findings.append(
                    SecurityFinding(
                        finding_type="unsafe_instruction",
                        severity=SecuritySeverity.CRITICAL,
                        detail=f"Unsafe instruction detected: '{label}'",
                        matched_pattern=label,
                    )
                )

        # 3. PII patterns
        for pattern, label in PII_PATTERNS:
            matches = re.findall(pattern, input_text)
            if matches:
                findings.append(
                    SecurityFinding(
                        finding_type="pii_detected",
                        severity=SecuritySeverity.WARNING,
                        detail=f"PII-like pattern detected: {label} (count: {len(matches)})",
                        matched_pattern=label,
                    )
                )

        # Sanitise: mask PII in output
        sanitized = input_text
        for pattern, label in PII_PATTERNS:
            sanitized = re.sub(pattern, f"[REDACTED {label.upper()}]", sanitized)

        allowed = not any(f.severity == SecuritySeverity.CRITICAL for f in findings)

        return SecurityReport(
            input_text=input_text,
            sanitized_text=sanitized,
            allowed=allowed,
            findings=findings,
        )
