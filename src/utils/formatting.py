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


# ---------------------------------------------------------------------------
# NEW: Competition & branding helpers
# ---------------------------------------------------------------------------

def competition_badge() -> str:
    """Return a styled competition badge for the sidebar."""
    return (
        '<div style="background:linear-gradient(135deg, rgba(56,189,248,0.12), rgba(168,85,247,0.12));'
        'border:1px solid rgba(168,85,247,0.25);border-radius:10px;padding:0.6rem 1rem;'
        'text-align:center;margin-bottom:1rem;">'
        '<div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;'
        'color:#a855f7;margin-bottom:2px;">🏆 Kaggle × Google Gemini</div>'
        '<div style="font-size:0.7rem;color:var(--text-color);opacity:0.6;">AI Agent Competition 2025</div>'
        '</div>'
    )


def github_button(url: str) -> str:
    """Return a styled GitHub link button."""
    return (
        f'<a href="{url}" target="_blank" style="display:flex;align-items:center;justify-content:center;'
        f'gap:8px;background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.12);'
        f'border-radius:10px;padding:0.6rem 1rem;text-decoration:none;color:var(--text-color);'
        f'font-weight:600;font-size:0.85rem;transition:all 0.2s ease;margin-bottom:0.5rem;">'
        f'<svg width="18" height="18" viewBox="0 0 16 16" fill="currentColor">'
        f'<path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>'
        f'</svg> View on GitHub</a>'
    )


def youtube_button(url: str) -> str:
    """Return a styled YouTube link button."""
    return (
        f'<a href="{url}" target="_blank" style="display:flex;align-items:center;justify-content:center;'
        f'gap:8px;background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.2);'
        f'border-radius:10px;padding:0.6rem 1rem;text-decoration:none;color:#ef4444;'
        f'font-weight:600;font-size:0.85rem;transition:all 0.2s ease;margin-bottom:0.5rem;">'
        f'<svg width="18" height="18" viewBox="0 0 24 24" fill="#ef4444">'
        f'<path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>'
        f'</svg> Watch Demo Video</a>'
    )


def value_stat_card(number: str, label: str, sublabel: str, color: str = "#ef4444") -> str:
    """Return a large stat card for the value proposition section."""
    return (
        f'<div class="glass-card" style="text-align:center;padding:1.8rem 1.2rem;border-top:3px solid {color};">'
        f'<div style="font-size:2.4rem;font-weight:800;color:{color};line-height:1;">{number}</div>'
        f'<div style="font-size:0.9rem;font-weight:700;color:var(--text-color);margin-top:0.5rem;">{label}</div>'
        f'<div style="font-size:0.75rem;color:var(--text-color);opacity:0.5;margin-top:0.3rem;">{sublabel}</div>'
        f'</div>'
    )


def architecture_flow_html() -> str:
    """Return an HTML visual architecture flow (replaces ASCII diagram)."""
    node_style = (
        "background:var(--card-bg);border:1px solid var(--card-border);border-radius:12px;"
        "padding:0.8rem 1rem;text-align:center;min-width:120px;font-size:0.8rem;"
        "font-weight:600;color:var(--text-color);box-shadow:var(--card-shadow);"
    )
    arrow = (
        '<div style="display:flex;align-items:center;justify-content:center;color:var(--text-color);opacity:0.35;font-size:1.5rem;">'
        '→</div>'
    )
    down_arrow = (
        '<div style="display:flex;align-items:center;justify-content:center;color:var(--text-color);'
        'opacity:0.35;font-size:1.5rem;padding:0.3rem 0;">↓</div>'
    )

    # Layer 1: Input
    layer1 = (
        '<div style="display:flex;align-items:center;justify-content:center;gap:12px;flex-wrap:wrap;margin-bottom:0.5rem;">'
        f'<div style="{node_style} border-top:3px solid #38bdf8;"><div style="font-size:1.3rem;">📄</div>Case Snapshot</div>'
        f'{arrow}'
        f'<div style="{node_style} border-top:3px solid #ef4444;"><div style="font-size:1.3rem;">🛡️</div>Security<br/>Guardrail</div>'
        f'{arrow}'
        f'<div style="{node_style} border-top:3px solid #38bdf8;"><div style="font-size:1.3rem;">🛠️</div>MCP Tool<br/>Hydration</div>'
        '</div>'
    )

    # Layer 2: Genome Agents
    agents_row = (
        '<div style="display:flex;align-items:center;justify-content:center;gap:8px;flex-wrap:wrap;margin-bottom:0.5rem;">'
        f'<div style="{node_style} border-top:3px solid #a855f7;flex:1;min-width:90px;"><div style="font-size:1.1rem;">📜</div><div style="font-size:0.7rem;">Policy</div></div>'
        f'<div style="{node_style} border-top:3px solid #a855f7;flex:1;min-width:90px;"><div style="font-size:1.1rem;">📋</div><div style="font-size:0.7rem;">Contract</div></div>'
        f'<div style="{node_style} border-top:3px solid #a855f7;flex:1;min-width:90px;"><div style="font-size:1.1rem;">⚙️</div><div style="font-size:0.7rem;">Rules</div></div>'
        f'<div style="{node_style} border-top:3px solid #a855f7;flex:1;min-width:90px;"><div style="font-size:1.1rem;">📄</div><div style="font-size:0.7rem;">Docs</div></div>'
        f'<div style="{node_style} border-top:3px solid #a855f7;flex:1;min-width:90px;"><div style="font-size:1.1rem;">🌐</div><div style="font-size:0.7rem;">Network</div></div>'
        f'<div style="{node_style} border-top:3px solid #a855f7;flex:1;min-width:90px;"><div style="font-size:1.1rem;">🔍</div><div style="font-size:0.7rem;">Evidence</div></div>'
        '</div>'
    )

    # Layer 3: Output
    layer3 = (
        '<div style="display:flex;align-items:center;justify-content:center;gap:12px;flex-wrap:wrap;">'
        f'<div style="{node_style} border-top:3px solid #f59e0b;"><div style="font-size:1.3rem;">🔬</div>Mutation<br/>Detection</div>'
        f'{arrow}'
        f'<div style="{node_style} border-top:3px solid #f59e0b;"><div style="font-size:1.3rem;">📈</div>Impact<br/>Assessment</div>'
        f'{arrow}'
        f'<div style="{node_style} border-top:3px solid #10b981;"><div style="font-size:1.3rem;">📋</div>Audit<br/>Report</div>'
        '</div>'
    )

    return (
        '<div class="glass-card" style="padding:1.5rem;">'
        '<h4 style="text-align:center;color:#a855f7;margin-top:0;margin-bottom:1rem;">Forensic Orchestration Pipeline</h4>'
        f'{layer1}'
        f'{down_arrow}'
        '<div style="text-align:center;font-size:0.7rem;font-weight:700;color:#a855f7;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.3rem;">6 Genome Agents (Parallel Execution)</div>'
        f'{agents_row}'
        f'{down_arrow}'
        f'{layer3}'
        '</div>'
    )
