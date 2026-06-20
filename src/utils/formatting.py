"""
DecisionDNA AI — Formatting Utilities

Shared helpers for colour-coding risk levels, rendering status badges,
and building display-friendly labels used across the Streamlit UI and
report generators.
"""

from __future__ import annotations


# ---------------------------------------------------------------------------
# Risk / status colour maps
# ---------------------------------------------------------------------------

RISK_COLOURS: dict[str, str] = {
    "LOW": "#28a745",
    "MEDIUM": "#ffc107",
    "HIGH": "#fd7e14",
    "CRITICAL": "#dc3545",
}

DECISION_COLOURS: dict[str, str] = {
    "APPROVED": "#28a745",
    "PAID": "#28a745",
    "ACTIVE": "#28a745",
    "DENIED": "#dc3545",
    "REJECTED": "#dc3545",
    "TERMINATED": "#dc3545",
    "PENDING": "#ffc107",
}

GENE_ICONS: dict[str, str] = {
    "Policy Gene": "📜",
    "Contract Gene": "📋",
    "Rule Gene": "⚙️",
    "Documentation Gene": "📄",
    "Network Gene": "🌐",
    "Evidence Gene": "🔍",
}

SEVERITY_ICONS: dict[str, str] = {
    "none": "✅",
    "low": "🟢",
    "medium": "🟡",
    "high": "🟠",
    "critical": "🔴",
}


def risk_badge(level: str) -> str:
    """Return an HTML span styled as a coloured badge for the given risk level."""
    colour = RISK_COLOURS.get(level.upper(), "#6c757d")
    return (
        f'<span style="background:{colour};color:#fff;padding:2px 10px;'
        f'border-radius:4px;font-weight:600;font-size:0.85em;">{level}</span>'
    )


def decision_badge(status: str) -> str:
    """Return an HTML span styled for a decision status."""
    colour = DECISION_COLOURS.get(status.upper(), "#6c757d")
    return (
        f'<span style="background:{colour};color:#fff;padding:2px 10px;'
        f'border-radius:4px;font-weight:600;font-size:0.85em;">{status}</span>'
    )


def gene_label(gene_name: str) -> str:
    """Return icon + name for a Decision Gene."""
    icon = GENE_ICONS.get(gene_name, "🧬")
    return f"{icon} {gene_name}"


def severity_label(severity: str) -> str:
    """Return icon + severity text."""
    icon = SEVERITY_ICONS.get(severity.lower(), "❓")
    return f"{icon} {severity.upper()}"


def pct_bar(value: int, max_val: int = 100) -> str:
    """Simple text-based percentage bar for terminal/notebook output."""
    filled = int(value / max_val * 20)
    return f"[{'█' * filled}{'░' * (20 - filled)}] {value}%"
