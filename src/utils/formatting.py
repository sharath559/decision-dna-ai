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


def mutation_score_bar(score: float | int) -> str:
    """Return an HTML progress bar styled with a gradient based on the mutation score."""
    if score < 30:
        bar_color = "linear-gradient(90deg, #10b981, #34d399)"
    elif score < 70:
        bar_color = "linear-gradient(90deg, #eab308, #facc15)"
    else:
        bar_color = "linear-gradient(90deg, #f97316, #ef4444)"
    return (
        f'<div style="width:100%;background:rgba(128,128,128,0.1);border:1px solid rgba(128,128,128,0.15);'
        f'border-radius:8px;height:16px;overflow:hidden;position:relative;">'
        f'<div style="width:{score}%;background:{bar_color};height:100%;border-radius:6px;transition:width 0.5s ease-in-out;"></div>'
        f'</div>'
    )


def kpi_card(icon: str, label: str, value: str | int, color: str = "#a855f7") -> str:
    """Return a styled HTML KPI card."""
    return (
        f'<div class="glass-card" style="padding:1.2rem;margin-bottom:0px;text-align:center;border-top:3px solid {color};">'
        f'<div style="font-size:1.8rem;margin-bottom:0.3rem;">{icon}</div>'
        f'<div style="font-size:0.75rem;font-weight:600;text-transform:uppercase;color:var(--text-color);opacity:0.6;letter-spacing:0.05em;margin-bottom:0.3rem;">{label}</div>'
        f'<div style="font-size:1.6rem;font-weight:700;color:var(--text-color);">{value}</div>'
        f'</div>'
    )


def status_pill(text: str, color: str) -> str:
    """Return a small inline HTML status pill badge."""
    return (
        f'<span style="background:{color}20;color:{color};border:1px solid {color}40;'
        f'padding:3px 10px;border-radius:12px;font-weight:600;font-size:0.8em;display:inline-block;">'
        f'{text}</span>'
    )


def agent_card(name: str, icon: str, description: str, status: str = "Active") -> str:
    """Return a styled HTML card for the agent view."""
    status_color = "#10b981" if status.lower() == "active" else "#94a3b8"
    return (
        f'<div class="glass-card" style="padding:1.2rem;margin-bottom:1rem;border-left:4px solid #a855f7;">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">'
        f'<span style="font-weight:700;font-size:1.1rem;color:var(--text-color);">{icon} {name}</span>'
        f'<span style="font-size:0.75rem;background:{status_color}20;color:{status_color};border:1px solid {status_color}40;padding:2px 8px;border-radius:8px;">{status}</span>'
        f'</div>'
        f'<div style="font-size:0.85rem;color:var(--text-color);opacity:0.7;line-height:1.4;">{description}</div>'
        f'</div>'
    )


def mcp_tool_card(name: str, purpose: str, source: str, status: str = "Active") -> str:
    """Return a styled HTML card for the MCP tools view."""
    status_color = "#10b981" if status.lower() == "active" else "#94a3b8"
    return (
        f'<div class="glass-card" style="padding:1.2rem;margin-bottom:1rem;border-left:4px solid #38bdf8;">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.5rem;">'
        f'<span style="font-weight:700;font-size:1.1rem;color:var(--text-color);">🛠️ {name}</span>'
        f'<span style="font-size:0.75rem;background:{status_color}20;color:{status_color};border:1px solid {status_color}40;padding:2px 8px;border-radius:8px;">{status}</span>'
        f'</div>'
        f'<div style="font-size:0.85rem;color:var(--text-color);opacity:0.9;margin-bottom:0.5rem;"><strong>Purpose:</strong> {purpose}</div>'
        f'<div style="font-size:0.8rem;color:var(--text-color);opacity:0.6;"><strong>Source:</strong> <code>{source}</code></div>'
        f'</div>'
    )

