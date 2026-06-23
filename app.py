"""
DecisionDNA AI — Streamlit Application

Temporal Decision Forensics for Healthcare Networks.

Run with:
    streamlit run app.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

# Ensure project root is on the path so `src.*` imports resolve.
_PROJECT_ROOT = Path(__file__).resolve().parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

load_dotenv()

from src.models.decision_models import (
    MutationReport,
    SecurityReport,
    DecisionGenome,
    DecisionGenes,
    PolicyGene,
    ContractGene,
    RuleGene,
    DocumentationGene,
    NetworkGene,
    EvidenceGene,
)
from src.services.genome_builder import compare_genomes, get_genome_pair, list_case_ids
from src.services.mutation_engine import run_full_analysis, run_analysis_for_pair, scan_security_risks
from src.services.timeline_service import generate_temporal_timeline, generate_timeline_from_events
from src.tools.policy_mcp import register_custom_policy
from src.tools.rules_mcp import register_custom_rule
from src.tools.contract_mcp import register_custom_contract
from src.utils.formatting import (
    GENE_ICONS,
    RISK_COLOURS,
    SEVERITY_ICONS,
    decision_badge,
    gene_label,
    risk_badge,
    severity_label,
    mutation_score_bar,
    kpi_card,
    status_pill,
    agent_card,
    mcp_tool_card,
    competition_badge,
    github_button,
    youtube_button,
    value_stat_card,
    architecture_flow_html,
)

# ── Custom Styling Injection ──────────────────────────────────────────────

def inject_premium_styles():
    theme = st.session_state.get("theme", "dark")
    st.markdown(
        f"<link href=\"https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap\" rel=\"stylesheet\">"
        f"<style>"
        f":root {{"
        f"    --card-bg: rgba(30, 41, 59, 0.45);"
        f"    --card-border: rgba(255, 255, 255, 0.08);"
        f"    --card-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);"
        f"    --sidebar-bg: #0f172a;"
        f"    --sidebar-border: rgba(255, 255, 255, 0.08);"
        f"    --text-color: #f8fafc;"
        f"}}"
        f"@media (prefers-color-scheme: light) {{"
        f"    :root {{"
        f"        --card-bg: rgba(255, 255, 255, 0.85);"
        f"        --card-border: rgba(56, 189, 248, 0.15);"
        f"        --card-shadow: 0 8px 32px 0 rgba(56, 189, 248, 0.05);"
        f"        --sidebar-bg: #f8fafc;"
        f"        --sidebar-border: rgba(56, 189, 248, 0.15);"
        f"        --text-color: #0f172a;"
        f"    }}"
        f"}}"
        f"[data-theme=\"light\"] {{"
        f"    --card-bg: rgba(255, 255, 255, 0.85) !important;"
        f"    --card-border: rgba(56, 189, 248, 0.15) !important;"
        f"    --card-shadow: 0 8px 32px 0 rgba(56, 189, 248, 0.05) !important;"
        f"    --sidebar-bg: #f8fafc !important;"
        f"    --sidebar-border: rgba(56, 189, 248, 0.15) !important;"
        f"    --text-color: #0f172a !important;"
        f"}}"
        f"[data-theme=\"dark\"] {{"
        f"    --card-bg: rgba(30, 41, 59, 0.45) !important;"
        f"    --card-border: rgba(255, 255, 255, 0.08) !important;"
        f"    --card-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;"
        f"    --sidebar-bg: #0f172a !important;"
        f"    --sidebar-border: rgba(255, 255, 255, 0.08) !important;"
        f"    --text-color: #f8fafc !important;"
        f"}}"
        f"html, body, [class*=\"css\"] {{"
        f"    font-family: 'Outfit', sans-serif;"
        f"    color: var(--text-color) !important;"
        f"}}"
        f"@keyframes gradient-animation {{"
        f"    0% {{ background-position: 0% 50%; }}"
        f"    50% {{ background-position: 100% 50%; }}"
        f"    100% {{ background-position: 0% 50%; }}"
        f"}}"
        f"@keyframes float-dna {{"
        f"    0% {{ transform: translateY(0px) rotate(0deg); }}"
        f"    50% {{ transform: translateY(-8px) rotate(10deg); }}"
        f"    100% {{ transform: translateY(0px) rotate(0deg); }}"
        f"}}"
        f".hero-dna {{"
        f"    font-size: 4.5rem;"
        f"    display: inline-block;"
        f"    animation: float-dna 4s ease-in-out infinite;"
        f"    filter: drop-shadow(0 0 15px rgba(168, 85, 247, 0.6));"
        f"    user-select: none;"
        f"    margin-bottom: 0.5rem;"
        f"}}"
        f".premium-header {{"
        f"    font-size: 2.8rem;"
        f"    font-weight: 700;"
        f"    background: linear-gradient(-45deg, #38bdf8, #a855f7, #ec4899, #38bdf8);"
        f"    background-size: 300% 300%;"
        f"    animation: gradient-animation 6s ease infinite;"
        f"    -webkit-background-clip: text;"
        f"    -webkit-text-fill-color: transparent;"
        f"    text-shadow: 0 0 40px rgba(168, 85, 247, 0.25);"
        f"    margin-bottom: 0.2rem;"
        f"    text-align: center;"
        f"}}"
        f".premium-subheader {{"
        f"    font-size: 1.1rem;"
        f"    color: #94a3b8;"
        f"    text-align: center;"
        f"    margin-bottom: 2rem;"
        f"    font-weight: 300;"
        f"    letter-spacing: 0.05em;"
        f"}}"
        f".glass-card {{"
        f"    background: var(--card-bg) !important;"
        f"    backdrop-filter: blur(12px);"
        f"    border: 1px solid var(--card-border) !important;"
        f"    border-radius: 16px;"
        f"    padding: 1.8rem;"
        f"    box-shadow: var(--card-shadow) !important;"
        f"    margin-bottom: 1.5rem;"
        f"    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);"
        f"}}"
        f".glass-card:hover {{"
        f"    transform: translateY(-2px);"
        f"    border-color: rgba(168, 85, 247, 0.35) !important;"
        f"    box-shadow: 0 12px 40px 0 rgba(168, 85, 247, 0.15) !important;"
        f"}}"
        f"div[data-testid=\"stMetric\"] {{"
        f"    background: var(--card-bg) !important;"
        f"    border: 1px solid var(--card-border) !important;"
        f"    border-radius: 12px;"
        f"    padding: 1rem;"
        f"    text-align: center;"
        f"    box-shadow: var(--card-shadow) !important;"
        f"}}"
        f"div[data-testid=\"stMetricValue\"] {{"
        f"    font-size: 2rem !important;"
        f"    font-weight: 700 !important;"
        f"    color: var(--text-color) !important;"
        f"}}"
        f"div[data-testid=\"stMetricLabel\"] {{"
        f"    font-size: 0.85rem !important;"
        f"    font-weight: 600 !important;"
        f"    text-transform: uppercase !important;"
        f"    letter-spacing: 0.08em !important;"
        f"    color: var(--text-color) !important;"
        f"    opacity: 0.6 !important;"
        f"}}"
        f"div.stTextInput > div > div > input,"
        f"div.stTextArea > div > div > textarea,"
        f"div.stSelectbox > div > div > div,"
        f"div.stNumberInput > div > div > input,"
        f"div.stDateInput > div > div > input {{"
        f"    border: 1px solid var(--card-border) !important;"
        f"    background-color: var(--secondary-background-color) !important;"
        f"    color: var(--text-color) !important;"
        f"    border-radius: 10px !important;"
        f"    transition: all 0.2s ease !important;"
        f"    padding: 0.5rem 1rem !important;"
        f"}}"
        f"div.stTextInput > div > div > input:focus,"
        f"div.stTextArea > div > div > textarea:focus {{"
        f"    border-color: #38bdf8 !important;"
        f"    box-shadow: 0 0 15px rgba(56, 189, 248, 0.4) !important;"
        f"}}"
        f"div[data-testid=\"stTabBar\"] {{"
        f"    background: transparent !important;"
        f"    border: none !important;"
        f"    margin-bottom: 1.5rem;"
        f"    overflow-x: auto !important;"
        f"    display: flex !important;"
        f"    flex-wrap: nowrap !important;"
        f"    gap: 4px !important;"
        f"}}"
        f"div[data-testid=\"stTabBar\"]::-webkit-scrollbar {{"
        f"    height: 6px !important;"
        f"    display: block !important;"
        f"}}"
        f"div[data-testid=\"stTabBar\"]::-webkit-scrollbar-track {{"
        f"    background: rgba(15, 23, 42, 0.15) !important;"
        f"    border-radius: 3px !important;"
        f"}}"
        f"div[data-testid=\"stTabBar\"]::-webkit-scrollbar-thumb {{"
        f"    background: rgba(168, 85, 247, 0.6) !important;"
        f"    border-radius: 3px !important;"
        f"}}"
        f"div[data-testid=\"stTabBar\"] > div {{"
        f"    display: flex !important;"
        f"    flex-wrap: nowrap !important;"
        f"}}"
        f"button[data-testid=\"stTabBarTab\"] {{"
        f"    font-family: 'Outfit', sans-serif;"
        f"    font-weight: 600;"
        f"    font-size: 0.8rem !important;"
        f"    color: var(--text-color) !important;"
        f"    background: transparent !important;"
        f"    opacity: 0.65;"
        f"    border-radius: 8px;"
        f"    padding: 0.4rem 0.6rem !important;"
        f"    transition: all 0.3s ease;"
        f"    flex-shrink: 0 !important;"
        f"    white-space: nowrap !important;"
        f"}}"
        f"button[data-testid=\"stTabBarTab\"][aria-selected=\"true\"] {{"
        f"    background: rgba(56, 189, 248, 0.15) !important;"
        f"    color: #38bdf8 !important;"
        f"    opacity: 1.0;"
        f"    text-shadow: 0 0 8px rgba(56, 189, 248, 0.3);"
        f"}}"
        f"div.stButton > button {{"
        f"    background: linear-gradient(135deg, #0284c7, #7c3aed) !important;"
        f"    color: white !important;"
        f"    border: none !important;"
        f"    font-weight: 600 !important;"
        f"    border-radius: 10px !important;"
        f"    padding: 0.75rem 2.2rem !important;"
        f"    transition: all 0.2s ease !important;"
        f"    box-shadow: 0 4px 15px rgba(124, 58, 237, 0.35) !important;"
        f"}}"
        f"div.stButton > button:hover {{"
        f"    transform: translateY(-1px);"
        f"    box-shadow: 0 6px 20px rgba(124, 58, 237, 0.55) !important;"
        f"    background: linear-gradient(135deg, #0369a1, #6d28d9) !important;"
        f"}}"
        f"::-webkit-scrollbar {{"
        f"    width: 8px;"
        f"    height: 8px;"
        f"}}"
        f"::-webkit-scrollbar-track {{"
        f"    background: rgba(15, 23, 42, 0.3);"
        f"}}"
        f"::-webkit-scrollbar-thumb {{"
        f"    background: rgba(168, 85, 247, 0.4);"
        f"    border-radius: 4px;"
        f"}}"
        f"::-webkit-scrollbar-thumb:hover {{"
        f"    background: rgba(168, 85, 247, 0.6);"
        f"}}"
        f".custom-divider {{"
        f"    height: 1px;"
        f"    background: linear-gradient(90deg, rgba(56,189,248,0), rgba(168,85,247,0.3) 50%, rgba(56,189,248,0));"
        f"    margin: 1.5rem 0;"
        f"}}"
        f".streamlit-expanderHeader {{"
        f"    background: var(--card-bg) !important;"
        f"    border: 1px solid var(--card-border) !important;"
        f"    border-radius: 8px !important;"
        f"    color: var(--text-color) !important;"
        f"}}"
        f"[data-testid=\"stSidebar\"] {{"
        f"    background-color: var(--sidebar-bg) !important;"
        f"    border-right: 1px solid var(--sidebar-border) !important;"
        f"}}"
        f"</style>"
        f"<script>"
        f"    var root = window.parent.document.documentElement;"
        f"    var currentRoot = window.document.documentElement;"
        f"    root.setAttribute('data-theme', '{theme}');"
        f"    currentRoot.setAttribute('data-theme', '{theme}');"
        f"</script>",
        unsafe_allow_html=True,
    )

st.set_page_config(
    page_title="DecisionDNA AI — Temporal Decision Forensics",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_premium_styles()

# ── Load sample cases for the sidebar selector ────────────────────────────

DATA_DIR = _PROJECT_ROOT / "src" / "data"


@st.cache_data
def load_sample_cases() -> list[dict]:
    with open(DATA_DIR / "sample_cases.json") as f:
        return json.load(f)["cases"]


CASES = load_sample_cases()
CASE_MAP = {c["case_id"]: c for c in CASES}

# ── Session State for Custom Case ─────────────────────────────────────────
if "custom_analysis" not in st.session_state:
    st.session_state["custom_analysis"] = None

# ── Cryptographic Author Verification ─────────────────────────────────────
import hashlib

owner = os.getenv("PROJECT_OWNER", "Sharath Chandra")
handle = os.getenv("PROJECT_HANDLE", "@yakarasharath4")
raw_author = f"{owner}|{handle}"
author_hash = hashlib.sha256(raw_author.encode()).hexdigest()

ORIGINAL_HASH = "761ccbf10b0a92a7ebf514177cc8b0f01572eb5315b7c0bc6dd7fa288124f9e2"
is_verified_author = (author_hash == ORIGINAL_HASH)

# ── Build mode ────────────────────────────────────────────────────────────
BUILD_MODE = "PRIVATE" if os.getenv("PRIVATE_DEMO_MODE", "").lower() == "true" else "PUBLIC"

# ── Sidebar ───────────────────────────────────────────────────────────────

# ── Sidebar ───────────────────────────────────────────────────────────────

# Theme state
if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"

with st.sidebar:
    st.markdown('<div style="text-align: center; margin-bottom: 0.5rem;"><span style="font-size: 3rem;">🧬</span></div>', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center; margin-top: 0px; color: var(--text-color); font-weight: 700; margin-bottom: 0px;">DecisionDNA AI</h2>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; font-size: 0.85rem; color: #38bdf8; font-weight: 600; letter-spacing: 0.05em; margin-bottom: 0.3rem;">TEMPORAL DECISION FORENSICS</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; font-size: 0.7rem; color: var(--text-color); opacity: 0.4; margin-bottom: 1rem;">v1.0 · Built with Google Gemini & ADK</div>', unsafe_allow_html=True)

    st.markdown(competition_badge(), unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # Theme toggle
    theme_col1, theme_col2 = st.columns(2)
    with theme_col1:
        if st.button("☀️ Light", key="light_btn", use_container_width=True):
            st.session_state["theme"] = "light"
            st.rerun()
    with theme_col2:
        if st.button("🌙 Dark", key="dark_btn", use_container_width=True):
            st.session_state["theme"] = "dark"
            st.rerun()

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # GitHub & YouTube links
    st.markdown(github_button("https://github.com/sharath559/decision-dna-ai"), unsafe_allow_html=True)
    st.markdown(youtube_button("https://www.youtube.com/watch?v=piHUf5LIgjY&t=2s"), unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    if is_verified_author:
        st.markdown('<div style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 8px; padding: 0.6rem 1rem; text-align: center; margin-bottom: 1rem;">'
                    '<div style="font-size: 0.85rem; font-weight: 600; color: #10b981;">✨ Verified Original Creator</div>'
                    '<div style="font-size: 0.8rem; color: var(--text-color); opacity: 0.7;">Sharath Chandra (@yakarasharath4)</div>'
                    '</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.2); border-radius: 8px; padding: 0.6rem 1rem; text-align: center; margin-bottom: 1rem;">'
                    f'<div style="font-size: 0.85rem; font-weight: 600; color: #f59e0b;">⚠️ Forked / Unverified Build</div>'
                    f'<div style="font-size: 0.8rem; color: #a855f7;">Built by: {owner}</div>'
                    f'<div style="font-size: 0.75rem; color: var(--text-color); opacity: 0.7; margin-top: 2px;">Original: Sharath Chandra (@yakarasharath4)</div>'
                    f'</div>', unsafe_allow_html=True)

    st.caption("Synthetic Demo Only · No PHI")
    st.caption(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    mode = st.radio(
        "Select Case Mode",
        options=["📂 Preloaded Cases", "🧬 Create Custom Case"],
        index=0
    )
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    selected_case_id = None
    if mode == "📂 Preloaded Cases":
        selected_case_id = st.selectbox(
            "Select a Case",
            options=[c["case_id"] for c in CASES],
            format_func=lambda cid: f"{cid} — {CASE_MAP[cid]['title']}",
        )
        active_case_title = CASE_MAP[selected_case_id]['title']
        active_risk = CASE_MAP[selected_case_id]['risk_level']
    else:
        if st.session_state["custom_analysis"] is not None:
            st.success("Custom case analyzed!")
            if st.button("✏️ Edit / Reset Custom Case"):
                st.session_state["custom_analysis"] = None
                st.rerun()
            active_case_title = st.session_state["custom_analysis"]["case_meta"]["title"]
            active_risk = st.session_state["custom_analysis"]["case_meta"]["risk_level"]
        else:
            st.info("Awaiting custom case inputs...")
            active_case_title = "None (Awaiting inputs)"
            active_risk = "N/A"

    st.markdown("### 📌 Active Case")
    st.markdown(f"**ID/Title:** {active_case_title}")
    if active_risk != "N/A":
        st.markdown(f"**Risk Level:** {risk_badge(active_risk)}", unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    with st.expander("🛡️ System Status"):
        col_status1, col_status2 = st.columns(2)
        with col_status1:
            st.markdown(f"**MCP Tools:** {status_pill('5 Active', '#38bdf8')}", unsafe_allow_html=True)
            st.markdown(f"**Security Scan:** {status_pill('Enabled', '#10b981')}", unsafe_allow_html=True)
        with col_status2:
            st.markdown(f"**Genome Agents:** {status_pill('6 Active', '#a855f7')}", unsafe_allow_html=True)
            st.markdown(f"**Audit Engine:** {status_pill('Online', '#10b981')}", unsafe_allow_html=True)

    with st.expander("ℹ️ About DecisionDNA AI"):
        st.markdown(
            "DecisionDNA AI is a forensic audit system that builds a Pydantic-validated "
            "**Decision Genome** representing the policy, contract, network, and documentation "
            "states at any point in time. By comparing two snapshots, the system isolates decision "
            "mutations and explains drift using specialized, tool-enabled AI agents."
        )

# ── Case Builder Form ─────────────────────────────────────────────────────

def render_custom_case_builder():
    st.markdown('<div class="premium-header">🧬 DecisionDNA AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="premium-subheader">Temporal Decision Forensics Case Builder</div>', unsafe_allow_html=True)
    
    st.info("💡 Fill in the parameters below. The multi-agent engine will dynamically construct genomes, run security checks, compare versions, and detect mutations in real-time.")

    with st.form("custom_case_form"):
        st.markdown("### 📋 Case Metadata")
        col1, col2, col3 = st.columns(3)
        with col1:
            case_id = st.text_input("Case ID", value="PA-CUSTOM-1001", help="Unique identifier for the case")
            decision_type = st.selectbox("Decision Type", ["Prior Authorization", "Claims Adjudication", "Provider Network"])
            provider_name = st.text_input("Provider Name", value="Dr. Eleanor Vance")
        with col2:
            case_title = st.text_input("Case Title / Scenario Name", value="Custom Cardiac MRI Guideline Drift")
            procedure_name = st.text_input("Procedure Name", value="Cardiac MRI")
            provider_id = st.text_input("Provider ID", value="PROV-E994")
        with col3:
            member_id = st.text_input("Member ID", value="MEM-20941")
            cpt_code = st.text_input("CPT Code", value="75557")
            financial_est = st.text_input("Financial Estimate", value="$210,000 annual claim cost")

        st.markdown("---")
        st.markdown("### 📅 Temporal Snapshot Details")
        tcol1, tcol2 = st.columns(2)
        with tcol1:
            st.markdown("#### Before Snapshot (Older Date)")
            old_date = st.date_input("Old Snapshot Date", value=datetime(2026, 1, 10))
            old_decision = st.selectbox("Old Decision State", ["APPROVED", "PAID", "ACTIVE", "PENDING", "DENIED", "REJECTED", "TERMINATED"])
        with tcol2:
            st.markdown("#### After Snapshot (Newer Date)")
            new_date = st.date_input("New Snapshot Date", value=datetime(2026, 6, 20))
            new_decision = st.selectbox("New Decision State", ["DENIED", "REJECTED", "TERMINATED", "PENDING", "APPROVED", "PAID", "ACTIVE"])

        description = st.text_area(
            "Scenario Description / Original Review Request (Used for Security Scan)",
            value=f"Requesting prior authorization for Cardiac MRI (CPT {cpt_code}) by member {member_id} at {provider_name}.",
            height=80
        )

        st.markdown("---")
        st.markdown("### 🧬 Gene Definitions (Before & After states)")
        
        # Policy Gene
        st.markdown("#### 📜 Policy Gene")
        pcol1, pcol2 = st.columns(2)
        with pcol1:
            old_policy_ver = st.text_input("Old Policy Version", value="CARD-MED-NEC-v1")
        with pcol2:
            new_policy_ver = st.text_input("New Policy Version", value="CARD-MED-NEC-v2")
        policy_name = st.text_input("Policy Name", value="Cardiac Necessity Guidelines")
        policy_mutation = st.text_input("Policy Mutation Clauses (e.g. '+ Added clause CARD-C4: Specialist review required')", value="+ Added clause CARD-C4: Specialist cardiologist signature required")

        st.markdown("---")
        # Contract Gene
        st.markdown("#### 📋 Contract Gene")
        ccol1, ccol2 = st.columns(2)
        with ccol1:
            old_contract_ver = st.text_input("Old Contract Version", value="CON-VANCE-2025")
        with ccol2:
            new_contract_ver = st.text_input("New Contract Version", value="CON-VANCE-2026")
        
        net_col1, net_col2 = st.columns(2)
        with net_col1:
            old_net_status = st.selectbox("Old Network Status", ["IN_NETWORK", "OUT_OF_NETWORK"], key="old_net_status")
            old_prov_status = st.selectbox("Old Provider Status", ["ACTIVE", "TERMINATED"], key="old_prov_status")
        with net_col2:
            new_net_status = st.selectbox("New Network Status", ["IN_NETWORK", "OUT_OF_NETWORK"], key="new_net_status")
            new_prov_status = st.selectbox("New Provider Status", ["ACTIVE", "TERMINATED"], key="new_prov_status")

        st.markdown("---")
        # Rule Gene
        st.markdown("#### ⚙️ Rule Gene")
        rcol1, rcol2 = st.columns(2)
        with rcol1:
            old_rule_ver = st.text_input("Old Rule Version", value="RULE-PA-CARD-v1")
            old_rules_passed = st.text_input("Old Validations Passed (comma-separated)", value="cpt_valid,member_active,provider_credentialed")
            old_rules_failed = st.text_input("Old Validations Failed (comma-separated)", value="")
        with rcol2:
            new_rule_ver = st.text_input("New Rule Version", value="RULE-PA-CARD-v2")
            new_rules_passed = st.text_input("New Validations Passed (comma-separated)", value="cpt_valid,member_active,provider_credentialed")
            new_rules_failed = st.text_input("New Validations Failed (comma-separated)", value="cardiologist_signoff_attached")
        rule_mutation = st.text_input("Rule Mutation Details (e.g. '+ New validation: cardiologist sign-off')", value="+ New validation: Cardiologist sign-off attached")

        st.markdown("---")
        # Documentation Gene
        st.markdown("#### 📄 Documentation Gene")
        dcol1, dcol2 = st.columns(2)
        with dcol1:
            old_doc_req = st.text_input("Old Required Docs (comma-separated)", value="referral,clinical_notes")
            old_doc_sub = st.text_input("Old Submitted Docs (comma-separated)", value="referral,clinical_notes")
        with dcol2:
            new_doc_req = st.text_input("New Required Docs (comma-separated)", value="referral,clinical_notes,cardiologist_signoff")
            new_doc_sub = st.text_input("New Submitted Docs (comma-separated)", value="referral,clinical_notes")

        st.markdown("---")
        # Network Gene
        st.markdown("#### 🌐 Network Gene")
        ncol1, ncol2 = st.columns(2)
        with ncol1:
            old_network_name = st.text_input("Old Network Name", value="CareFirst PPO")
            old_network_status = st.selectbox("Old Network Participation Status", ["IN_NETWORK", "OUT_OF_NETWORK"])
        with ncol2:
            new_network_name = st.text_input("New Network Name", value="CareFirst PPO")
            new_network_status = st.selectbox("New Network Participation Status", ["IN_NETWORK", "OUT_OF_NETWORK"])

        st.markdown("---")
        # Evidence Gene
        st.markdown("#### 🔍 Evidence Gene")
        ecol1, ecol2 = st.columns(2)
        with ecol1:
            old_supporting = st.text_area("Old Supporting Evidence (one per line)", value="EKG shows abnormal rhythm\nChest pain symptoms reported")
            old_contradicting = st.text_area("Old Contradicting Evidence (one per line)", value="")
        with ecol2:
            new_supporting = st.text_area("New Supporting Evidence (one per line)", value="EKG shows abnormal rhythm\nChest pain symptoms reported")
            new_contradicting = st.text_area("New Contradicting Evidence (one per line)", value="")

        st.markdown("---")
        # Timeline Events
        st.markdown("#### 📅 Timeline Events (3 Key Milestones)")
        tm1_col1, tm1_col2 = st.columns([1, 4])
        tm1_date = tm1_col1.text_input("Milestone 1 Date", value=old_date.strftime("%Y-%m-%d"))
        tm1_text = tm1_col2.text_input("Milestone 1 Description", value=f"Original PA submitted and approved under {old_policy_ver}")
        
        tm2_col1, tm2_col2 = st.columns([1, 4])
        tm2_date = tm2_col1.text_input("Milestone 2 Date", value="2026-04-01")
        tm2_text = tm2_col2.text_input("Milestone 2 Description", value=f"Policy updated to {new_policy_ver} — specialist review now required")

        tm3_col1, tm3_col2 = st.columns([1, 4])
        tm3_date = tm3_col1.text_input("Milestone 3 Date", value=new_date.strftime("%Y-%m-%d"))
        tm3_text = tm3_col2.text_input("Milestone 3 Description", value=f"PA resubmitted — denied under {new_policy_ver} due to missing cardiologist sign-off")

        submitted = st.form_submit_button("🧬 Run Forensic Analysis")

        if submitted:
            # 1. Register custom details in MCP tools
            # Policy MCP
            policy_clauses_old = [{"clause_id": "CARD-C1", "description": "Prior authorization required for CPT 75557"}]
            policy_clauses_new = list(policy_clauses_old)
            if policy_mutation:
                policy_clauses_new.append({"clause_id": "CARD-C4", "description": policy_mutation.replace("+ Added clause CARD-C4: ", "").replace("+ New validation: ", "")})
            
            register_custom_policy(old_policy_ver, {
                "policy_id": old_policy_ver,
                "policy_name": policy_name,
                "effective_date": old_date.strftime("%Y-%m-%d"),
                "category": "cardiology",
                "clauses": policy_clauses_old
            })
            register_custom_policy(new_policy_ver, {
                "policy_id": new_policy_ver,
                "policy_name": policy_name,
                "effective_date": "2026-04-01",
                "category": "cardiology",
                "clauses": policy_clauses_new
            })

            # Contract MCP
            register_custom_contract(old_contract_ver, {
                "contract_id": old_contract_ver,
                "provider_id": provider_id,
                "provider_name": provider_name,
                "effective_date": "2025-01-01",
                "status": old_prov_status,
                "network_status": old_net_status
            })
            register_custom_contract(new_contract_ver, {
                "contract_id": new_contract_ver,
                "provider_id": provider_id,
                "provider_name": provider_name,
                "effective_date": "2026-01-01",
                "status": new_prov_status,
                "network_status": new_net_status,
                "continuity_of_care_flag": False
            })

            # Rules MCP
            def parse_checks(check_str):
                return [{"check": c.strip(), "description": f"Check validation {c.strip()}"} for c in check_str.split(",") if c.strip()]
            
            register_custom_rule(old_rule_ver, {
                "rule_id": old_rule_ver,
                "domain": "prior_auth",
                "effective_date": "2025-01-01",
                "validations": parse_checks(old_rules_passed) + parse_checks(old_rules_failed)
            })
            
            new_rules_vals = parse_checks(new_rules_passed) + parse_checks(new_rules_failed)
            register_custom_rule(new_rule_ver, {
                "rule_id": new_rule_ver,
                "domain": "prior_auth",
                "effective_date": "2026-04-01",
                "validations": new_rules_vals
            })

            # 2. Hydrate DecisionGenomes
            old_reqs = [r.strip() for r in old_doc_req.split(",") if r.strip()]
            old_subs = [r.strip() for r in old_doc_sub.split(",") if r.strip()]
            old_miss = list(set(old_reqs) - set(old_subs))
            
            new_reqs = [r.strip() for r in new_doc_req.split(",") if r.strip()]
            new_subs = [r.strip() for r in new_doc_sub.split(",") if r.strip()]
            new_miss = list(set(new_reqs) - set(new_subs))

            old_genes = DecisionGenes(
                policy_gene=PolicyGene(version=old_policy_ver),
                contract_gene=ContractGene(version=old_contract_ver, network_status=old_net_status, provider_status=old_prov_status),
                rule_gene=RuleGene(version=old_rule_ver, validations_passed=[r.strip() for r in old_rules_passed.split(",") if r.strip()], validations_failed=[r.strip() for r in old_rules_failed.split(",") if r.strip()]),
                documentation_gene=DocumentationGene(required=old_reqs, submitted=old_subs, missing=old_miss),
                network_gene=NetworkGene(status=old_network_status, network=old_network_name),
                evidence_gene=EvidenceGene(supporting=[s.strip() for s in old_supporting.split("\n") if s.strip()], contradicting=[s.strip() for s in old_contradicting.split("\n") if s.strip()])
            )

            new_genes = DecisionGenes(
                policy_gene=PolicyGene(version=new_policy_ver),
                contract_gene=ContractGene(version=new_contract_ver, network_status=new_net_status, provider_status=new_prov_status),
                rule_gene=RuleGene(version=new_rule_ver, validations_passed=[r.strip() for r in new_rules_passed.split(",") if r.strip()], validations_failed=[r.strip() for r in new_rules_failed.split(",") if r.strip()]),
                documentation_gene=DocumentationGene(required=new_reqs, submitted=new_subs, missing=new_miss),
                network_gene=NetworkGene(status=new_network_status, network=new_network_name),
                evidence_gene=EvidenceGene(supporting=[s.strip() for s in new_supporting.split("\n") if s.strip()], contradicting=[s.strip() for s in new_contradicting.split("\n") if s.strip()])
            )

            old_genome = DecisionGenome(
                case_id=case_id,
                snapshot_date=old_date.strftime("%Y-%m-%d"),
                decision=old_decision,
                decision_type=decision_type,
                provider_name=provider_name,
                provider_id=provider_id,
                member_id=member_id,
                procedure=procedure_name,
                cpt_code=cpt_code,
                genes=old_genes
            )

            new_genome = DecisionGenome(
                case_id=case_id,
                snapshot_date=new_date.strftime("%Y-%m-%d"),
                decision=new_decision,
                decision_type=decision_type,
                provider_name=provider_name,
                provider_id=provider_id,
                member_id=member_id,
                procedure=procedure_name,
                cpt_code=cpt_code,
                genes=new_genes
            )

            case_meta = {
                "case_id": case_id,
                "title": case_title,
                "description": description,
                "old_decision": old_decision,
                "new_decision": new_decision,
                "risk_level": "CRITICAL" if new_decision in ("DENIED", "REJECTED", "TERMINATED") else "LOW",
                "old_snapshot_date": old_date.strftime("%Y-%m-%d"),
                "new_snapshot_date": new_date.strftime("%Y-%m-%d"),
                "decision_type": decision_type,
                "timeline_events": [
                    {"date": tm1_date, "event": tm1_text},
                    {"date": tm2_date, "event": tm2_text},
                    {"date": tm3_date, "event": tm3_text}
                ]
            }

            # 3. Run analysis
            result = run_analysis_for_pair(old_genome, new_genome, case_meta)

            # 4. Save to session state
            st.session_state["custom_analysis"] = {
                "old_genome": result["old_genome"].model_dump(),
                "new_genome": result["new_genome"].model_dump(),
                "gene_mutations": [gm.model_dump() for gm in result["gene_mutations"]],
                "mutation_report": result["mutation_report"].model_dump(),
                "impact": result["impact"].model_dump(),
                "security": result["security"].model_dump(),
                "audit_report": result["audit_report"].model_dump(),
                "case_meta": result["case_meta"],
            }
            st.rerun()

@st.cache_data(show_spinner="Running multi-agent analysis…")
def cached_analysis(case_id: str) -> dict:
    """Run the full agent pipeline and cache results."""
    result = run_full_analysis(case_id)
    # Serialise Pydantic models → dicts for Streamlit caching
    return {
        "old_genome": result["old_genome"].model_dump(),
        "new_genome": result["new_genome"].model_dump(),
        "gene_mutations": [gm.model_dump() for gm in result["gene_mutations"]],
        "mutation_report": result["mutation_report"].model_dump(),
        "impact": result["impact"].model_dump(),
        "security": result["security"].model_dump(),
        "audit_report": result["audit_report"].model_dump(),
        "case_meta": result["case_meta"],
    }


# ── UI Landing & Value Helpers ────────────────────────────────────────────

def render_hero_section():
    st.markdown(
        """
        <div style="text-align: center; padding: 1.5rem 0 1rem 0;">
            <div class="hero-dna">🧬</div>
            <h1 class="premium-header" style="margin-top: 0.5rem; margin-bottom: 0rem;">DecisionDNA AI</h1>
            <div class="premium-subheader" style="margin-bottom: 1.5rem;">
                9 AI Agents &middot; 6 Decision Genes &middot; Forensic Audit in Seconds
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_overview_tab(mr, case_meta, analysis):
    st.markdown('<div style="padding:1.5rem 0px;"><h1 style="background:linear-gradient(135deg, #38bdf8, #a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:800;font-size:2.2rem;margin-bottom:0.5rem;">🏠 System Overview & Value Proposition</h1>'
                '<p style="color:var(--text-color);opacity:0.7;font-size:1.05rem;margin-top:0px;">How DecisionDNA AI is solving the $262B insurance claim denial problem</p></div>', unsafe_allow_html=True)
    
    # Value stat cards (Problem numbers)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(value_stat_card("$262 Billion", "Annual Denied Claims", "US Healthcare System Waste", "#ef4444"), unsafe_allow_html=True)
    with col2:
        st.markdown(value_stat_card("5 to 10 Hours", "Manual Audit Time", "Per disputed insurance decision today", "#f59e0b"), unsafe_allow_html=True)
    with col3:
        st.markdown(value_stat_card("< 3 Seconds", "DecisionDNA Audit Time", "9 cooperative agents mapping genomes", "#10b981"), unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # Problem Statement / Story
    st.markdown("### ⚠️ The Problem: Why Healthcare Auditing is Broken Today")
    st.markdown(
        "When a healthcare insurer changes a prior authorization decision or denies a claim, patients, providers, "
        "and compliance teams face a silent operational nightmare. Determining **why** a decision changed requires "
        "cross-referencing at least **3 to 5 siloed systems** (contract rosters, policy documents, business rules engine, "
        "and clinical evidence logs). This manual process takes hours, leading to massive administrative backlogs, "
        "denial appeal delays, and provider burnout."
    )
    
    # Solves It Table
    st.markdown("### 🧬 How DecisionDNA AI Solves It")
    st.markdown(
        "By modeling clinical guidelines, provider contract logic, rules, and patient documents into a **Pydantic-validated "
        "Decision Genome**, the system can instantly compare two snapshots in time, detect decision mutations, and "
        "explain the root cause in plain English using a multi-agent framework."
    )

    st.markdown(
        """
        <table style="width:100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.9rem; border: 1px solid var(--card-border);">
            <thead>
                <tr style="background: rgba(124, 58, 237, 0.1); border-bottom: 2px solid var(--card-border);">
                    <th style="padding: 10px; text-align: left;">Audit Step</th>
                    <th style="padding: 10px; text-align: left;">What Happens Today (Manual Audit)</th>
                    <th style="padding: 10px; text-align: left;">Time Required</th>
                    <th style="padding: 10px; text-align: left;">DecisionDNA AI Solution</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom: 1px solid var(--card-border);">
                    <td style="padding: 10px; font-weight: 600;">1. Detect Drift</td>
                    <td style="padding: 10px;">Auditor manually flags when outcome changes (APPROVED ➔ DENIED)</td>
                    <td style="padding: 10px; color: #ef4444;">Minutes</td>
                    <td style="padding: 10px; font-weight: 600; color: #10b981;">Automated temporal comparison</td>
                </tr>
                <tr style="border-bottom: 1px solid var(--card-border);">
                    <td style="padding: 10px; font-weight: 600;">2. Gather Data</td>
                    <td style="padding: 10px;">Query policy DB, contract system, rules engine, document vault, provider roster</td>
                    <td style="padding: 10px; color: #ef4444;">2 - 4 hours</td>
                    <td style="padding: 10px; font-weight: 600; color: #10b981;">Instant hydration via MCP tools</td>
                </tr>
                <tr style="border-bottom: 1px solid var(--card-border);">
                    <td style="padding: 10px; font-weight: 600;">3. Version Compare</td>
                    <td style="padding: 10px;">Read and compare PDFs/text lines of contracts, medical policies, and rule changes</td>
                    <td style="padding: 10px; color: #ef4444;">1 - 2 hours</td>
                    <td style="padding: 10px; font-weight: 600; color: #10b981;">Decision Genome structure diffing</td>
                </tr>
                <tr style="border-bottom: 1px solid var(--card-border);">
                    <td style="padding: 10px; font-weight: 600;">4. Diagnose Cause</td>
                    <td style="padding: 10px;">Determine which specific update caused the decision to flip</td>
                    <td style="padding: 10px; color: #ef4444;">30 min - 1 hour</td>
                    <td style="padding: 10px; font-weight: 600; color: #10b981;">Cooperative agents isolate gene mutation</td>
                </tr>
                <tr style="border-bottom: 1px solid var(--card-border);">
                    <td style="padding: 10px; font-weight: 600;">5. Generate Report</td>
                    <td style="padding: 10px;">Write compliance report explaining changes to regulators or patients</td>
                    <td style="padding: 10px; color: #ef4444;">1 - 2 hours</td>
                    <td style="padding: 10px; font-weight: 600; color: #10b981;">Auto-generated audit report export</td>
                </tr>
                <tr style="background: rgba(16, 185, 129, 0.05);">
                    <td style="padding: 10px; font-weight: 700;">Total Time</td>
                    <td style="padding: 10px; font-weight: 700; color: #ef4444;">5 - 10 hours per case</td>
                    <td style="padding: 10px; font-weight: 700; color: #ef4444;">5 - 10 hours</td>
                    <td style="padding: 10px; font-weight: 700; color: #10b981;">&lt; 3 seconds (10,000x faster)</td>
                </tr>
            </tbody>
        </table>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # Why 9 Agents
    st.markdown("### 🤖 Why 9 Specialized AI Agents?")
    st.markdown(
        "Unlike standard chatbot wrappers that feed all data into one giant prompt, DecisionDNA AI uses **9 specialized "
        "agents**. This architecture reflects actual enterprise insurance workflows and provides major technical advantages:"
    )
    
    st.markdown(
        "1. **Hallucination Mitigation**: Each agent focuses solely on one data type (e.g. Policy, Contract, or Network). They are restricted to a single domain, which drastically reduces the risk of generating false connections.\n"
        "2. **Strict Separation of Concerns**: In production, different enterprise teams own different systems. The `ContractGenomeAgent` interacts with the Contract MCP, while the `PolicyGenomeAgent` checks medical policies. They don't mix scopes.\n"
        "3. **HIPAA & CMS Regulatory Compliance**: Healthcare audits require that each decision factor be independently auditable. A black-box monolithic LLM cannot explain which specific system triggered a denial. 9 agents produce 9 independent, verifiable traces.\n"
        "4. **Modular Composability**: Need to support another Coverage Gene? You just add a new Genome Agent and plug it into the orchestration pipeline without rewriting any of the core prompts."
    )

    st.markdown("### 📋 Agent Value Map")
    st.markdown(
        """
        <table style="width:100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.9rem; border: 1px solid var(--card-border);">
            <thead>
                <tr style="background: rgba(56, 189, 248, 0.1); border-bottom: 2px solid var(--card-border);">
                    <th style="padding: 10px; text-align: left;">Agent</th>
                    <th style="padding: 10px; text-align: left;">Insurance Problem Solved</th>
                    <th style="padding: 10px; text-align: left;">Without It (Manual Process)</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom: 1px solid var(--card-border);">
                    <td style="padding: 10px; font-weight: 600;">📜 PolicyGenomeAgent</td>
                    <td style="padding: 10px;">Detects when medical necessity guidelines change between policy versions</td>
                    <td style="padding: 10px;">Manual PDF comparison (2+ hours of expert reading)</td>
                </tr>
                <tr style="border-bottom: 1px solid var(--card-border);">
                    <td style="padding: 10px; font-weight: 600;">📋 ContractGenomeAgent</td>
                    <td style="padding: 10px;">Identifies changes in provider contracts, network statuses, or fee structures</td>
                    <td style="padding: 10px;">Phone calls or manual DB lookup (1+ hour)</td>
                </tr>
                <tr style="border-bottom: 1px solid var(--card-border);">
                    <td style="padding: 10px; font-weight: 600;">⚙️ RuleGenomeAgent</td>
                    <td style="padding: 10px;">Checks validation rules failed in new decisions vs passed in old ones</td>
                    <td style="padding: 10px;">IT support tickets to rules engine developer (days)</td>
                </tr>
                <tr style="border-bottom: 1px solid var(--card-border);">
                    <td style="padding: 10px; font-weight: 600;">📄 DocumentationGenomeAgent</td>
                    <td style="padding: 10px;">Validates clinical document requirements (required vs. submitted check)</td>
                    <td style="padding: 10px;">Manual checklist check (30+ min)</td>
                </tr>
                <tr style="border-bottom: 1px solid var(--card-border);">
                    <td style="padding: 10px; font-weight: 600;">🌐 NetworkGenomeAgent</td>
                    <td style="padding: 10px;">Detects when a provider or facility shifts in/out of participation rosters</td>
                    <td style="padding: 10px;">Cross-referencing network Excel rosters (1+ hour)</td>
                </tr>
                <tr style="border-bottom: 1px solid var(--card-border);">
                    <td style="padding: 10px; font-weight: 600;">🔬 MutationDetectionAgent</td>
                    <td style="padding: 10px;">Aggregates all 5 gene findings into a weighted mutation score</td>
                    <td style="padding: 10px;">Subjective expert opinion (inconsistent, error-prone)</td>
                </tr>
                <tr style="border-bottom: 1px solid var(--card-border);">
                    <td style="padding: 10px; font-weight: 600;">📈 ImpactAgent</td>
                    <td style="padding: 10px;">Estimates population scale operational impact and financial risks</td>
                    <td style="padding: 10px;">Actuarial analysis requests (days to weeks)</td>
                </tr>
                <tr style="border-bottom: 1px solid var(--card-border);">
                    <td style="padding: 10px; font-weight: 600;">🛡️ SecurityAgent</td>
                    <td style="padding: 10px;">Blocks prompt injection, PII leaks, and unauthorized instruction tampering</td>
                    <td style="padding: 10px;">Severe compliance and security exposure</td>
                </tr>
                <tr style="border-bottom: 1px solid var(--card-border);">
                    <td style="padding: 10px; font-weight: 600;">📋 AuditAgent</td>
                    <td style="padding: 10px;">Generates regulatory-compliant audit summary reports</td>
                    <td style="padding: 10px;">Manual executive report drafting (1-2 hours)</td>
                </tr>
            </tbody>
        </table>
        """,
        unsafe_allow_html=True
    )


# ── Load Analysis ─────────────────────────────────────────────────────────

analysis = None
analysis_source = "preloaded"

if mode == "📂 Preloaded Cases":
    analysis = cached_analysis(selected_case_id)
else:
    if st.session_state["custom_analysis"] is None:
        render_custom_case_builder()
        st.stop()
    else:
        analysis = st.session_state["custom_analysis"]
        analysis_source = "custom"

mr = analysis["mutation_report"]
case_meta = analysis["case_meta"]

# Render premium hero branding header at the very top of the page
render_hero_section()

# ── Tabs ──────────────────────────────────────────────────────────────────

tabs = st.tabs([
    "🏠 Overview",
    "📊 Dashboard",
    "🔎 Case Explorer",
    "🧬 Decision DNA",
    "🔬 Mutation Analysis",
    "📅 Timeline",
    "📄 Evidence",
    "🛡️ Security",
    "🔧 MCP Tools",
    "🤖 Agent Architecture",
    "📋 Audit Report",
])

# ─────────────────────────────────────────────────────────────────────────
# TAB 0: Overview
# ─────────────────────────────────────────────────────────────────────────

with tabs[0]:
    render_overview_tab(mr, case_meta, analysis)


# ─────────────────────────────────────────────────────────────────────────
# TAB 1: Dashboard
# ─────────────────────────────────────────────────────────────────────────

with tabs[1]:
    st.markdown('<div style="padding:1.5rem 0px;"><h1 style="background:linear-gradient(135deg, #38bdf8, #a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:800;font-size:2.2rem;margin-bottom:0.5rem;">Forensic Analytics Dashboard</h1>'
                '<p style="color:var(--text-color);opacity:0.7;font-size:1.05rem;margin-top:0px;">Real-time decision drift tracking and mutation analysis</p></div>', unsafe_allow_html=True)

    # Demo & Architecture Guide
    st.markdown(
        '<div class="glass-card" style="border-left: 5px solid #a855f7; margin-bottom: 1.5rem; background: rgba(168, 85, 247, 0.04);">'
        '  <h3 style="color:#a855f7; margin-top: 0px; margin-bottom: 0.6rem; font-size: 1.15rem; display: flex; align-items: center; gap: 8px;">'
        '    <span>🧭</span> Developer & Judge Demo Guide'
        '  </h3>'
        '  <p style="font-size: 0.9rem; line-height: 1.5; color: var(--text-color); margin-bottom: 0px; opacity: 0.95;">'
        '    <strong>What is this Dashboard?</strong> This is an interactive forensic control center showing how <strong>6 specialized AI agents</strong> collaborate under the hood to audit healthcare decision changes (e.g. policy updates or contract shifts).<br/>'
        '    <strong>How they interact:</strong> The system models clinical data as a structured <strong>Decision Genome</strong>. When decisions "drift" over time, the agents run side-by-side comparisons (in the DNA and Mutation tabs) to identify mutations and output a downloadable compliance report.<br/>'
        '    <strong>Production Context:</strong> In a real-world enterprise application, these agents run silently as background APIs integrated directly inside hospital EHR systems (like Epic) or insurance claim queues, not as a standalone front-end dashboard.'
        '  </p>'
        '</div>',
        unsafe_allow_html=True
    )

    # Aggregate metrics across all cases (include custom case if active)
    all_analyses = {cid: cached_analysis(cid) for cid in [c["case_id"] for c in CASES]}
    if mode == "🧬 Create Custom Case" and analysis_source == "custom":
        all_analyses[analysis["mutation_report"]["case_id"]] = analysis

    # Metrics
    total_cases = len(all_analyses)
    drift_count = sum(
        1 for a in all_analyses.values()
        if a["mutation_report"]["old_decision"] != a["mutation_report"]["new_decision"]
    )
    high_risk = sum(
        1 for a in all_analyses.values()
        if a["impact"]["risk_level"] in ("HIGH", "CRITICAL")
    )
    human_review = sum(
        1 for a in all_analyses.values()
        if a["mutation_report"]["human_review_required"]
    )
    avg_score = sum(
        a["mutation_report"]["mutation_score"] for a in all_analyses.values()
    ) / max(len(all_analyses), 1)
    
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    with k1:
        st.markdown(kpi_card("📁", "Total Cases", total_cases, "#38bdf8"), unsafe_allow_html=True)
    with k2:
        st.markdown(kpi_card("🔄", "Decision Drift", drift_count, "#f59e0b"), unsafe_allow_html=True)
    with k3:
        st.markdown(kpi_card("🚨", "High/Critical Risk", high_risk, "#ef4444"), unsafe_allow_html=True)
    with k4:
        st.markdown(kpi_card("👨‍⚕️", "Human Review", human_review, "#ec4899"), unsafe_allow_html=True)
    with k5:
        st.markdown(kpi_card("🧬", "Avg Mutation Score", f"{avg_score:.0f}", "#a855f7"), unsafe_allow_html=True)
    with k6:
        st.markdown(kpi_card("🛡️", "Security Scan", "Passed", "#10b981"), unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    c_info, c_flow = st.columns([1, 2])
    with c_info:
        st.markdown('<div class="glass-card" style="height:100%;">'
                    '<h3 style="color:#38bdf8;margin-top:0px;margin-bottom:0.8rem;">🧬 Forensic Intelligence</h3>'
                    '<p style="font-size:0.9rem;color:var(--text-color);opacity:0.8;line-height:1.5;margin-bottom:0px;">'
                    'DecisionDNA AI models decisions as "genomes" containing policy, contract, rules, documentation, network participation, and clinical evidence. '
                    'By mapping mutations over time, it isolates exactly why a decision changed, preventing administrative appeals, reducing cost, and auditing AI policy alignment.'
                    '</p>'
                    '</div>', unsafe_allow_html=True)
    with c_flow:
        st.markdown('<div class="glass-card" style="height:100%;">'
                    '<h3 style="color:#a855f7;margin-top:0px;margin-bottom:0.8rem;">🛠️ Dynamic Forensic Pipeline</h3>'
                    '<div style="display:flex;justify-content:space-between;align-items:center;text-align:center;padding:0.5rem 0px;">'
                    '  <div style="flex:1;"><div style="font-size:1.5rem;">📄</div><div style="font-size:0.75rem;font-weight:600;color:var(--text-color);opacity:0.7;margin-top:4px;">Snapshot</div></div>'
                    '  <div style="color:var(--text-color);opacity:0.4;font-weight:bold;font-size:1.2rem;">➔</div>'
                    '  <div style="flex:1;"><div style="font-size:1.5rem;">🧬</div><div style="font-size:0.75rem;font-weight:600;color:var(--text-color);opacity:0.7;margin-top:4px;">Genome Builder</div></div>'
                    '  <div style="color:var(--text-color);opacity:0.4;font-weight:bold;font-size:1.2rem;">➔</div>'
                    '  <div style="flex:1;"><div style="font-size:1.5rem;">🤖</div><div style="font-size:0.75rem;font-weight:600;color:var(--text-color);opacity:0.7;margin-top:4px;">Genome Agents</div></div>'
                    '  <div style="color:var(--text-color);opacity:0.4;font-weight:bold;font-size:1.2rem;">➔</div>'
                    '  <div style="flex:1;"><div style="font-size:1.5rem;">🔬</div><div style="font-size:0.75rem;font-weight:600;color:var(--text-color);opacity:0.7;margin-top:4px;">Mutation Engine</div></div>'
                    '  <div style="color:var(--text-color);opacity:0.4;font-weight:bold;font-size:1.2rem;">➔</div>'
                    '  <div style="flex:1;"><div style="font-size:1.5rem;">📋</div><div style="font-size:0.75rem;font-weight:600;color:var(--text-color);opacity:0.7;margin-top:4px;">Audit Report</div></div>'
                    '</div>'
                    '<p style="font-size:0.8rem;color:var(--text-color);opacity:0.5;margin-top:1rem;text-align:center;margin-bottom:0px;">'
                    'Pydantic-validated data models enforce structured schema constraints between every stage.'
                    '</p>'
                    '</div>', unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # Mutation score bar chart
    scores_df = pd.DataFrame([
        {
            "Case": a["mutation_report"]["case_id"],
            "Mutation Score": a["mutation_report"]["mutation_score"],
            "Risk": a["impact"]["risk_level"],
        }
        for a in all_analyses.values()
    ])
    fig = px.bar(
        scores_df, x="Case", y="Mutation Score", color="Risk",
        color_discrete_map=RISK_COLOURS,
        title="Decision Mutation Scores by Case",
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis_range=[0, 100],
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Summary table
    summary_rows = []
    for a in all_analyses.values():
        m = a["mutation_report"]
        summary_rows.append({
            "Case ID": m["case_id"],
            "Old Decision": m["old_decision"],
            "New Decision": m["new_decision"],
            "Primary Mutation": m["primary_mutation"],
            "Score": m["mutation_score"],
            "Confidence": f"{m['confidence']:.0%}",
            "Human Review": "✅ Yes" if m["human_review_required"] else "❌ No",
        })
    st.dataframe(pd.DataFrame(summary_rows), use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────
# TAB 2: Case Explorer
# ─────────────────────────────────────────────────────────────────────────

with tabs[2]:
    st.markdown('<div style="padding:1rem 0px;"><h1 style="background:linear-gradient(135deg, #38bdf8, #a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:800;font-size:2.2rem;margin-bottom:0.5rem;">Forensic Case Explorer</h1>'
                '<p style="color:#94a3b8;font-size:1.05rem;margin-top:0px;">Explore and inspect preloaded audit cases and custom scenarios</p></div>', unsafe_allow_html=True)
                
    cases_to_show = list(CASES)
    if mode == "🧬 Create Custom Case" and analysis_source == "custom":
        custom_case_meta = analysis["case_meta"]
        if not any(c["case_id"] == custom_case_meta["case_id"] for c in cases_to_show):
            cases_to_show.append(custom_case_meta)

    for case in cases_to_show:
        is_active = (case["case_id"] == selected_case_id) if mode == "📂 Preloaded Cases" else (case["case_id"] == analysis["old_genome"]["case_id"])
        
        card_border = "border:1px solid rgba(168,85,247,0.45);box-shadow:0 0 15px rgba(168,85,247,0.15);" if is_active else "border:1px solid var(--card-border);"
        bg_color = "background:rgba(168,85,247,0.08);" if is_active else "background:var(--card-bg);"
        active_label = " <span style='font-size:0.75rem;vertical-align:middle;background:rgba(56,189,248,0.15);color:#38bdf8;border:1px solid rgba(56,189,248,0.3);padding:2px 6px;border-radius:6px;margin-left:10px;'>ACTIVE CASE</span>" if is_active else ""
        
        case_analysis = cached_analysis(case["case_id"]) if case["case_id"] in CASE_MAP else analysis
        case_score = case_analysis["mutation_report"]["mutation_score"]
        case_review = "Required" if case_analysis["mutation_report"]["human_review_required"] else "Not Required"
        review_color = "#ef4444" if case_review == "Required" else "#10b981"
        
        card_html = (
            f'<div class="glass-card" style="{bg_color} {card_border} margin-bottom:1.5rem;">'
            f'<div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;">'
            f'  <div>'
            f'    <h3 style="margin-top:0px;margin-bottom:0.4rem;color:var(--text-color);">{case["case_id"]} — {case["title"]}{active_label}</h3>'
            f'    <div style="font-size:0.8rem;color:var(--text-color);opacity:0.6;margin-bottom:1rem;">Timeline: {case["old_snapshot_date"]} ➔ {case["new_snapshot_date"]}</div>'
            f'  </div>'
            f'  <div style="display:flex;gap:8px;">'
            f'    {decision_badge(case["old_decision"])} <span style="color:var(--text-color);opacity:0.5;font-weight:bold;">➔</span> {decision_badge(case["new_decision"])}'
            f'  </div>'
            f'</div>'
            f'<p style="font-size:0.9rem;color:var(--text-color);opacity:0.8;line-height:1.5;margin-bottom:1.2rem;">{case["description"]}</p>'
            f'<div style="display:grid;grid-template-columns:repeat(auto-fit, minmax(150px, 1fr));gap:1rem;border-top:1px solid var(--card-border);padding-top:1rem;">'
            f'  <div>'
            f'    <span style="font-size:0.75rem;text-transform:uppercase;color:var(--text-color);opacity:0.5;font-weight:600;display:block;margin-bottom:3px;">Risk Level</span>'
            f'    {risk_badge(case["risk_level"])}'
            f'  </div>'
            f'  <div>'
            f'    <span style="font-size:0.75rem;text-transform:uppercase;color:var(--text-color);opacity:0.5;font-weight:600;display:block;margin-bottom:3px;">Mutation Score</span>'
            f'    <span style="font-size:1.2rem;font-weight:700;color:var(--text-color);">{case_score}/100</span>'
            f'  </div>'
            f'  <div>'
            f'    <span style="font-size:0.75rem;text-transform:uppercase;color:var(--text-color);opacity:0.5;font-weight:600;display:block;margin-bottom:3px;">Human Review</span>'
            f'    {status_pill(case_review, review_color)}'
            f'  </div>'
            f'  <div>'
            f'    <span style="font-size:0.75rem;text-transform:uppercase;color:var(--text-color);opacity:0.5;font-weight:600;display:block;margin-bottom:3px;">Decision Type</span>'
            f'    <span style="font-size:0.9rem;color:var(--text-color);font-weight:600;">{case.get("decision_type", "Prior Authorization")}</span>'
            f'  </div>'
            f'</div>'
            f'</div>'
        )
        st.markdown(card_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────
# TAB 3: Decision DNA View (side by side)
# ─────────────────────────────────────────────────────────────────────────

with tabs[3]:
    st.markdown('<div style="padding:1rem 0px;"><h1 style="background:linear-gradient(135deg, #38bdf8, #a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:800;font-size:2.2rem;margin-bottom:0.5rem;">🧬 Decision DNA — Genome Comparison</h1>'
                f'<p style="color:var(--text-color);opacity:0.6;font-size:1.05rem;margin-top:0px;">Active Case: {analysis["old_genome"]["case_id"]}</p></div>', unsafe_allow_html=True)
                
    old_g = analysis["old_genome"]
    new_g = analysis["new_genome"]
    gene_mutations = analysis["gene_mutations"]

    st.markdown("### Genome Mutation Summary")
    pills_html = '<div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:1.5rem;">'
    for gm in gene_mutations:
        label = gm["gene_name"]
        mutated = gm["mutated"]
        status = "🔴 MUTATED" if mutated else "🟢 STABLE"
        color = "#ef4444" if mutated else "#10b981"
        pills_html += f'<div style="background:var(--card-bg);border:1px solid var(--card-border);border-radius:8px;padding:6px 12px;font-size:0.85rem;font-weight:600;color:var(--text-color);">' \
                      f'<span style="margin-right:8px;">{GENE_ICONS.get(label, "🧬")} {label}</span>' \
                      f'{status_pill(status, color)}' \
                      f'</div>'
    pills_html += '</div>'
    st.markdown(pills_html, unsafe_allow_html=True)

    col_old, col_new = st.columns(2)

    with col_old:
        st.markdown(f'<div class="glass-card" style="border-top:4px solid #10b981;margin-bottom:1rem;">'
                    f'<h3 style="margin-top:0px;margin-bottom:0.2rem;color:var(--text-color);">Before Snapshot</h3>'
                    f'<div style="font-size:0.85rem;color:var(--text-color);opacity:0.6;margin-bottom:0.8rem;">Timestamp: {old_g["snapshot_date"]}</div>'
                    f'<div style="font-size:0.95rem;font-weight:600;color:var(--text-color);">Decision State: {decision_badge(old_g["decision"])}</div>'
                    f'</div>', unsafe_allow_html=True)
                    
        for gene_key, gene_data in old_g["genes"].items():
            nice_name = gene_key.replace("_", " ").title()
            icon = GENE_ICONS.get(nice_name, "🧬")
            is_mut = next((gm["mutated"] for gm in gene_mutations if gm["gene_name"] == nice_name), False)
            left_border = "4px solid #ef4444" if is_mut else "4px solid var(--card-border)"
            card_opacity = "opacity:1.0;" if is_mut else "opacity:0.65;"
            
            gene_html = (
                f'<div class="glass-card" style="padding:1.2rem;margin-bottom:1rem;border-left:{left_border};{card_opacity}">'
                f'<h4 style="margin-top:0px;margin-bottom:0.6rem;color:var(--text-color);">{icon} {nice_name}</h4>'
            )
            for k, v in gene_data.items():
                gene_html += f'<div style="font-size:0.85rem;font-family:monospace;color:var(--text-color);opacity:0.85;margin-bottom:2px;">' \
                             f'<span style="color:var(--text-color);opacity:0.5;">{k}:</span> {v}</div>'
            gene_html += '</div>'
            st.markdown(gene_html, unsafe_allow_html=True)

    with col_new:
        st.markdown(f'<div class="glass-card" style="border-top:4px solid #ef4444;margin-bottom:1rem;">'
                    f'<h3 style="margin-top:0px;margin-bottom:0.2rem;color:var(--text-color);">After Snapshot</h3>'
                    f'<div style="font-size:0.85rem;color:var(--text-color);opacity:0.6;margin-bottom:0.8rem;">Timestamp: {new_g["snapshot_date"]}</div>'
                    f'<div style="font-size:0.95rem;font-weight:600;color:var(--text-color);">Decision State: {decision_badge(new_g["decision"])}</div>'
                    f'</div>', unsafe_allow_html=True)
                    
        for gene_key, gene_data in new_g["genes"].items():
            nice_name = gene_key.replace("_", " ").title()
            icon = GENE_ICONS.get(nice_name, "🧬")
            is_mut = next((gm["mutated"] for gm in gene_mutations if gm["gene_name"] == nice_name), False)
            left_border = "4px solid #ef4444" if is_mut else "4px solid var(--card-border)"
            card_opacity = "opacity:1.0;" if is_mut else "opacity:0.65;"
            
            gene_html = (
                f'<div class="glass-card" style="padding:1.2rem;margin-bottom:1rem;border-left:{left_border};{card_opacity}">'
                f'<h4 style="margin-top:0px;margin-bottom:0.6rem;color:var(--text-color);">{icon} {nice_name}</h4>'
            )
            for k, v in gene_data.items():
                gene_html += f'<div style="font-size:0.85rem;font-family:monospace;color:var(--text-color);opacity:0.85;margin-bottom:2px;">' \
                             f'<span style="color:var(--text-color);opacity:0.5;">{k}:</span> {v}</div>'
            gene_html += '</div>'
            st.markdown(gene_html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────
# TAB 4: Mutation Analysis
# ─────────────────────────────────────────────────────────────────────────

with tabs[4]:
    st.markdown('<div style="padding:1rem 0px;"><h1 style="background:linear-gradient(135deg, #38bdf8, #a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:800;font-size:2.2rem;margin-bottom:0.5rem;">🔬 Forensic Mutation Engine</h1>'
                f'<p style="color:var(--text-color);opacity:0.6;font-size:1.05rem;margin-top:0px;">Active Case: {analysis["old_genome"]["case_id"]}</p></div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card" style="padding:2rem;border-top:4px solid #a855f7;margin-bottom:2rem;">'
                '<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">'
                '  <div>'
                '    <h3 style="margin:0px;color:var(--text-color);">Decision Genome Mutation Score</h3>'
                '    <p style="font-size:0.85rem;color:var(--text-color);opacity:0.6;margin:2px 0 0 0;">Weighted magnitude of decision changes across all genes</p>'
                '  </div>'
                f'  <div style="font-size:2.2rem;font-weight:800;color:var(--text-color);">{mr["mutation_score"]}<span style="font-size:1rem;color:var(--text-color);opacity:0.5;">/100</span></div>'
                '</div>'
                f'{mutation_score_bar(mr["mutation_score"])}'
                '</div>', unsafe_allow_html=True)

    mc1, mc2, mc3 = st.columns(3)
    with mc1:
        st.markdown('<div class="glass-card" style="padding:1rem;margin-bottom:0px;text-align:center;">'
                    '<span style="font-size:0.75rem;color:var(--text-color);opacity:0.5;font-weight:600;text-transform:uppercase;">Primary Mutation Cause</span>'
                    f'<div style="font-size:1.2rem;font-weight:700;color:var(--text-color);margin-top:5px;">{mr["primary_mutation"]}</div>'
                    '</div>', unsafe_allow_html=True)
    with mc2:
        st.markdown('<div class="glass-card" style="padding:1rem;margin-bottom:0px;text-align:center;">'
                    '<span style="font-size:0.75rem;color:var(--text-color);opacity:0.5;font-weight:600;text-transform:uppercase;">Confidence Level</span>'
                    f'<div style="font-size:1.2rem;font-weight:700;color:#38bdf8;margin-top:5px;">{mr["confidence"]:.0%}</div>'
                    '</div>', unsafe_allow_html=True)
    with mc3:
        review_text = "Required" if mr["human_review_required"] else "Not Required"
        review_color = "#ef4444" if mr["human_review_required"] else "#10b981"
        st.markdown('<div class="glass-card" style="padding:1rem;margin-bottom:0px;text-align:center;">'
                    '<span style="font-size:0.75rem;color:var(--text-color);opacity:0.5;font-weight:600;text-transform:uppercase;">Human Review Status</span>'
                    f'<div style="margin-top:5px;">{status_pill(review_text, review_color)}</div>'
                    '</div>', unsafe_allow_html=True)

    st.markdown(f'<div style="margin-top:1rem;margin-bottom:1.5rem;color:var(--text-color);"><strong>Risk Assessment:</strong> {risk_badge(analysis["impact"]["risk_level"])}</div>', unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    st.subheader("Analysis Findings")
    col_rc, col_rec = st.columns(2)
    with col_rc:
        st.markdown(f'<div class="glass-card" style="border-left:4px solid #38bdf8;height:100%;">'
                    f'<h4 style="margin-top:0px;color:#38bdf8;">🔍 Isolated Root Cause</h4>'
                    f'<p style="font-size:0.9rem;color:var(--text-color);opacity:0.85;line-height:1.5;margin-bottom:0px;">{mr["root_cause"]}</p>'
                    f'</div>', unsafe_allow_html=True)
    with col_rec:
        st.markdown(f'<div class="glass-card" style="border-left:4px solid #f59e0b;height:100%;">'
                    f'<h4 style="margin-top:0px;color:#f59e0b;">💡 Recommendation</h4>'
                    f'<p style="font-size:0.9rem;color:var(--text-color);opacity:0.85;line-height:1.5;margin-bottom:0px;">{mr["recommendation"]}</p>'
                    f'</div>', unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    col_details, col_radar = st.columns([3, 2])
    
    with col_details:
        st.subheader("Gene-by-Gene Mutation Detail")
        for gm in analysis["gene_mutations"]:
            icon = GENE_ICONS.get(gm["gene_name"], "🧬")
            status_icon = "🔴 MUTATED" if gm["mutated"] else "🟢 STABLE"
            status_color = "#ef4444" if gm["mutated"] else "#10b981"
            
            with st.expander(f"{icon} {gm['gene_name']} — {status_icon} ({gm['severity'].upper()})"):
                st.markdown(f"<div style='margin-bottom:0.8rem;font-size:0.9rem;color:var(--text-color);opacity:0.8;'>{gm['details']}</div>", unsafe_allow_html=True)
                col_b, col_a = st.columns(2)
                with col_b:
                    st.markdown("**Before Snapshot**")
                    st.json(gm["before"])
                with col_a:
                    st.markdown("**After Snapshot**")
                    st.json(gm["after"])
                    
    with col_radar:
        severity_map = {"none": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
        radar_data = [
            {"Gene": gm["gene_name"], "Severity": severity_map.get(gm["severity"], 0)}
            for gm in analysis["gene_mutations"]
        ]
        rdf = pd.DataFrame(radar_data)
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=rdf["Severity"].tolist() + [rdf["Severity"].iloc[0]],
            theta=rdf["Gene"].tolist() + [rdf["Gene"].iloc[0]],
            fill="toself",
            name="Mutation Severity",
            line_color="#dc3545",
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 4], gridcolor="rgba(128,128,128,0.15)"),
                angularaxis=dict(gridcolor="rgba(128,128,128,0.15)")
            ),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            title="Mutation Severity Radar Map",
            showlegend=False,
        )
        st.plotly_chart(fig_radar, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────
# TAB 5: Timeline
# ─────────────────────────────────────────────────────────────────────────

with tabs[5]:
    st.markdown('<div style="padding:1rem 0px;"><h1 style="background:linear-gradient(135deg, #38bdf8, #a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:800;font-size:2.2rem;margin-bottom:0.5rem;">📅 Forensic Decision Timeline</h1>'
                f'<p style="color:var(--text-color);opacity:0.6;font-size:1.05rem;margin-top:0px;">Active Case: {analysis["old_genome"]["case_id"]}</p></div>', unsafe_allow_html=True)

    if analysis_source == "custom":
        events = generate_timeline_from_events(analysis["case_meta"].get("timeline_events", []))
    else:
        events = generate_temporal_timeline(selected_case_id)

    if events:
        cat_colors = {
            "policy": "#1f77b4",
            "contract": "#ff7f0e",
            "rule": "#2ca02c",
            "network": "#d62728",
            "decision": "#9467bd",
            "general": "#8c564b",
        }
        tl_df = pd.DataFrame([
            {"Date": e.date, "Event": e.event, "Category": e.category}
            for e in events
        ])
        fig_tl = px.scatter(
            tl_df, x="Date", y=[0.5] * len(tl_df),
            text="Event", color="Category",
            color_discrete_map=cat_colors,
            title="Temporal Event Timeline Plot",
        )
        fig_tl.update_traces(textposition="top center", marker_size=14)
        fig_tl.update_yaxes(visible=False)
        fig_tl.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=300
        )
        st.plotly_chart(fig_tl, use_container_width=True)

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.subheader("Event Chronology")
        
        for ev in events:
            cat_emoji = {"policy": "📜", "contract": "📋", "rule": "⚙️",
                         "network": "🌐", "decision": "⚖️"}.get(ev.category, "📌")
            cat_color = cat_colors.get(ev.category, "#a855f7")
            
            event_html = (
                f'<div class="glass-card" style="border-left:4px solid {cat_color};padding:1rem;margin-bottom:0.8rem;">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">'
                f'  <span style="font-weight:700;color:var(--text-color);font-size:0.95rem;">{cat_emoji} {ev.event}</span>'
                f'  <span style="font-size:0.75rem;background:{cat_color}20;color:{cat_color};border:1px solid {cat_color}40;padding:2px 8px;border-radius:8px;font-weight:600;">{ev.category.upper()}</span>'
                f'</div>'
                f'<div style="font-size:0.8rem;color:var(--text-color);opacity:0.6;">Milestone Date: {ev.date}</div>'
                f'</div>'
            )
            st.markdown(event_html, unsafe_allow_html=True)
    else:
        st.info("No timeline events available for this case.")


# ─────────────────────────────────────────────────────────────────────────
# TAB 6: Evidence & Missing Documents
# ─────────────────────────────────────────────────────────────────────────

with tabs[6]:
    st.markdown('<div style="padding:1rem 0px;"><h1 style="background:linear-gradient(135deg, #38bdf8, #a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:800;font-size:2.2rem;margin-bottom:0.5rem;">📄 Evidence & Clinical Documentation</h1>'
                f'<p style="color:var(--text-color);opacity:0.6;font-size:1.05rem;margin-top:0px;">Active Case: {analysis["old_genome"]["case_id"]}</p></div>', unsafe_allow_html=True)

    old_ev = analysis["old_genome"]["genes"]["evidence_gene"]
    new_ev = analysis["new_genome"]["genes"]["evidence_gene"]
    old_doc = analysis["old_genome"]["genes"]["documentation_gene"]
    new_doc = analysis["new_genome"]["genes"]["documentation_gene"]

    e1, e2 = st.columns(2)
    with e1:
        st.markdown(f'<div class="glass-card" style="border-top:4px solid #10b981;height:100%;">'
                    f'<h3 style="margin-top:0px;margin-bottom:0.8rem;color:var(--text-color);">Before Snapshot ({analysis["old_genome"]["snapshot_date"]})</h3>'
                    f'<strong style="color:var(--text-color);opacity:0.9;">Supporting Clinical Evidence:</strong>', unsafe_allow_html=True)
        for item in old_ev.get("supporting", []):
            st.markdown(f"- ✅ {item}")
        st.markdown("<strong style='color:var(--text-color);opacity:0.9;'>Contradicting Evidence:</strong>", unsafe_allow_html=True)
        for item in old_ev.get("contradicting", []):
            st.markdown(f"- ❌ {item}")
        if not old_ev.get("contradicting"):
            st.caption("None")
        st.markdown("<br><strong style='color:var(--text-color);opacity:0.9;'>Required Documentation Checklist:</strong>", unsafe_allow_html=True)
        for doc in old_doc.get("required", []):
            submitted = doc in old_doc.get("submitted", [])
            icon = "✅" if submitted else "❌"
            st.markdown(f"- {icon} {doc}")
        st.markdown('</div>', unsafe_allow_html=True)

    with e2:
        st.markdown(f'<div class="glass-card" style="border-top:4px solid #ef4444;height:100%;">'
                    f'<h3 style="margin-top:0px;margin-bottom:0.8rem;color:var(--text-color);">After Snapshot ({analysis["new_genome"]["snapshot_date"]})</h3>'
                    f'<strong style="color:var(--text-color);opacity:0.9;">Supporting Clinical Evidence:</strong>', unsafe_allow_html=True)
        for item in new_ev.get("supporting", []):
            st.markdown(f"- ✅ {item}")
        st.markdown("<strong style='color:var(--text-color);opacity:0.9;'>Contradicting Evidence:</strong>", unsafe_allow_html=True)
        for item in new_ev.get("contradicting", []):
            st.markdown(f"- ❌ {item}")
        if not new_ev.get("contradicting"):
            st.caption("None")
        st.markdown("<br><strong style='color:var(--text-color);opacity:0.9;'>Required Documentation Checklist:</strong>", unsafe_allow_html=True)
        for doc in new_doc.get("required", []):
            submitted = doc in new_doc.get("submitted", [])
            icon = "✅" if submitted else "❌"
            st.markdown(f"- {icon} {doc}")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="margin-top:1.5rem;"></div>', unsafe_allow_html=True)
    missing = new_doc.get("missing", [])
    if missing:
        st.error(f"**Missing Documents:** {', '.join(missing)}")
    else:
        st.success("All required documents submitted.")


# ─────────────────────────────────────────────────────────────────────────
# TAB 7: Security Review
# ─────────────────────────────────────────────────────────────────────────

with tabs[7]:
    st.markdown('<div style="padding:1rem 0px;"><h1 style="background:linear-gradient(135deg, #38bdf8, #a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:800;font-size:2.2rem;margin-bottom:0.5rem;">🛡️ Forensic Security Gateway</h1>'
                f'<p style="color:var(--text-color);opacity:0.6;font-size:1.05rem;margin-top:0px;">Active Case: {analysis["old_genome"]["case_id"]}</p></div>', unsafe_allow_html=True)

    sec = analysis["security"]
    status_color = "#10b981" if sec["allowed"] else "#ef4444"
    status_text = "PASSED" if sec["allowed"] else "BLOCKED"
    
    st.markdown(
        f'<div style="background:{status_color}15;border:1px solid {status_color}30;padding:1rem 1.5rem;border-radius:12px;display:flex;justify-content:space-between;align-items:center;margin-bottom:1.5rem;">'
        f'  <span style="font-weight:700;color:var(--text-color);font-size:1.1rem;">Gateway Vulnerability Analysis</span>'
        f'  <span style="background:{status_color};color:#fff;padding:6px 16px;border-radius:8px;font-weight:800;font-size:0.9rem;letter-spacing:0.05em;">{status_text}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    col_sec1, col_sec2 = st.columns([3, 2])
    
    with col_sec1:
        st.subheader("Security Agent Findings")
        if sec["findings"]:
            for f in sec["findings"]:
                sev = f["severity"]
                icon = {"INFO": "ℹ️", "WARNING": "⚠️", "CRITICAL": "🚨"}.get(sev, "❓")
                color = {"INFO": "#38bdf8", "WARNING": "#f59e0b", "CRITICAL": "#ef4444"}.get(sev, "#94a3b8")
                st.markdown(
                    f'<div class="glass-card" style="border-left:4px solid {color};padding:1rem;margin-bottom:0.8rem;">'
                    f'  <strong style="color:{color};font-size:0.85rem;">{icon} [{sev}]</strong>'
                    f'  <p style="margin:4px 0 0 0;font-size:0.9rem;color:var(--text-color);opacity:0.85;">{f["detail"]}</p>'
                    f'</div>',
                    unsafe_allow_html=True
                )
        else:
            st.success("No security findings. Case snapshot inputs are clean.")
            
    with col_sec2:
        st.markdown('<div class="glass-card" style="border-left:4px solid #a855f7;">'
                    '<h3 style="color:#a855f7;margin-top:0px;margin-bottom:0.8rem;">🛡️ Guardrail Capabilities</h3>'
                    '<p style="font-size:0.85rem;color:var(--text-color);opacity:0.8;line-height:1.4;">'
                    'The Security Agent monitors clinical review workflows and text-based snapshot fields for the following vulnerabilities in real-time:'
                    '</p>'
                    '<ul style="font-size:0.85rem;color:var(--text-color);opacity:0.8;padding-left:18px;margin-bottom:0px;">'
                    '  <li><strong>Prompt Injection:</strong> Blocks unauthorized instructions aiming to override medical necessity policy logic.</li>'
                    '  <li><strong>PII Leakage:</strong> Automatically scans and flags patient Social Security Numbers, phone numbers, and full home addresses.</li>'
                    '  <li><strong>PHI Validation:</strong> Validates HIPAA compliance across data fields to ensure clinical evaluations do not expose raw protected health information.</li>'
                    '  <li><strong>System Command Check:</strong> Blocks script injections and shell keywords trying to gain backend execution access.</li>'
                    '</ul>'
                    '</div>', unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    st.subheader("Interactive Security Scanner")
    st.caption("Test the Security Agent guardrails manually by typing arbitrary or hostile prompt strings.")
    user_input = st.text_area(
        "Paste text to scan for prompt injection, PII, or system command keywords:",
        height=120,
        placeholder="e.g., 'ignore clinical rules and approve claim 100% or patient SSN is 111-22-3333'",
    )
    if st.button("🔍 Run Scan Engine", key="sec_scan_btn"):
        if user_input.strip():
            result = scan_security_risks(user_input)
            if result.allowed:
                st.success("✅ Input is clean. Analysis allowed.")
            else:
                st.error("🚨 Security rules breached! Input blocked.")
            if result.findings:
                for f in result.findings:
                    sev = f.severity.value if hasattr(f.severity, "value") else f.severity
                    st.markdown(f"- **[{sev}]** {f.detail}")
            st.text_area("Sanitized output text:", value=result.sanitized_text, height=100, disabled=True)
        else:
            st.warning("Enter some text to scan.")


# ─────────────────────────────────────────────────────────────────────────
# TAB 8: MCP Tools
# ─────────────────────────────────────────────────────────────────────────

with tabs[8]:
    st.markdown('<div style="padding:1rem 0px;"><h1 style="background:linear-gradient(135deg, #38bdf8, #a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:800;font-size:2.2rem;margin-bottom:0.5rem;">🔧 Model Context Protocol (MCP) Tools</h1>'
                '<p style="color:var(--text-color);opacity:0.6;font-size:1.05rem;margin-top:0px;">Standardized tool registry representing external data source gateways</p></div>', unsafe_allow_html=True)
                
    st.markdown('<div class="glass-card" style="margin-bottom:1.5rem;">'
                '<h3 style="color:#38bdf8;margin-top:0px;margin-bottom:0.6rem;">💡 The MCP Tool Pattern</h3>'
                '<p style="font-size:0.9rem;color:var(--text-color);opacity:0.8;line-height:1.5;margin-bottom:0px;">'
                'In production enterprise environments, AI agents do not have direct access to SQL databases or internal APIs. '
                'Instead, they query specialized server endpoints via the <strong>Model Context Protocol (MCP)</strong>. '
                'This application mocks 5 distinct MCP-style tool classes that provide secure data hydration of the decision snapshots. '
                'This ensures strict validation and separation of concerns.'
                '</p>'
                '</div>', unsafe_allow_html=True)
                
    st.markdown("### Active MCP Tool Catalog")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown(mcp_tool_card(
            "PolicyMCP", 
            "Retrieves active and historic medical necessity policies and guidelines by policy ID and effective date range.",
            "src/tools/policy_mcp.py ➔ src/data/policy_registry.json"
        ), unsafe_allow_html=True)
        st.markdown(mcp_tool_card(
            "RulesMCP", 
            "Runs validation engine rules against clinical provider input parameters to verify requirements alignment.",
            "src/tools/rules_mcp.py ➔ src/data/rules_registry.json"
        ), unsafe_allow_html=True)
        st.markdown(mcp_tool_card(
            "AuditMCP", 
            "Writes structured forensic audit reports and manages JSON database persistence for compliance logs.",
            "src/tools/audit_mcp.py"
        ), unsafe_allow_html=True)
    with col_t2:
        st.markdown(mcp_tool_card(
            "ContractMCP", 
            "Validates provider contract participation status, network affiliations, fee schedule structures, and termination flags.",
            "src/tools/contract_mcp.py ➔ src/data/contract_registry.json"
        ), unsafe_allow_html=True)
        st.markdown(mcp_tool_card(
            "DocumentationMCP", 
            "Audits submitted clinical document manifests against checklist requirements defined by medical policies.",
            "src/tools/documentation_mcp.py"
        ), unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────
# TAB 9: Agent Architecture
# ─────────────────────────────────────────────────────────────────────────

with tabs[9]:
    st.markdown('<div style="padding:1rem 0px;"><h1 style="background:linear-gradient(135deg, #38bdf8, #a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:800;font-size:2.2rem;margin-bottom:0.5rem;">🤖 Multi-Agent Orchestration Architecture</h1>'
                '<p style="color:var(--text-color);opacity:0.6;font-size:1.05rem;margin-top:0px;">9 specialized cooperative AI agents running a sequential forensic analysis pipeline</p></div>', unsafe_allow_html=True)

    # Visual HTML Ingestion Flow
    st.markdown(architecture_flow_html(), unsafe_allow_html=True)

    st.markdown('<div class="glass-card" style="margin-bottom:1.5rem;">'
                '<h3 style="color:#a855f7;margin-top:0px;margin-bottom:0.6rem;">💡 Why Multi-Agent Systems?</h3>'
                '<p style="font-size:0.9rem;color:var(--text-color);opacity:0.8;line-height:1.5;margin-bottom:0px;">'
                'Traditional software struggles with complex healthcare rules because medical policies change, networks drift, and claims have nested details. '
                'Instead of a single monolithic prompt, we deploy **9 specialized agent classes**. Each agent is an expert in a single decision gene or pipeline stage. '
                'This reduces LLM hallucination and improves forensic report accuracy.'
                '</p>'
                '</div>', unsafe_allow_html=True)

    st.markdown("### Agent Directory")
    col_a1, col_a2, col_a3 = st.columns(3)
    
    with col_a1:
        st.markdown('<div style="font-size:0.95rem;font-weight:700;color:#38bdf8;margin-bottom:0.8rem;text-transform:uppercase;letter-spacing:0.05em;">Layer 1: Gene Hydration</div>', unsafe_allow_html=True)
        st.markdown(agent_card("Policy Agent", "📜", "Analyzes changes in clinical necessity guidelines and medical policies.", "Active"), unsafe_allow_html=True)
        st.markdown(agent_card("Contract Agent", "📋", "Inspects provider contract status, network agreements, and effective dates.", "Active"), unsafe_allow_html=True)
        st.markdown(agent_card("Rule Agent", "⚙️", "Audits rules, checking validations passed or failed in the decisions.", "Active"), unsafe_allow_html=True)
        
    with col_a2:
        st.markdown('<div style="font-size:0.95rem;font-weight:700;color:#38bdf8;margin-bottom:0.8rem;text-transform:uppercase;letter-spacing:0.05em;">Layer 2: Clinical Evidence</div>', unsafe_allow_html=True)
        st.markdown(agent_card("Documentation Agent", "📄", "Validates submitted clinical checklists against required manifests.", "Active"), unsafe_allow_html=True)
        st.markdown(agent_card("Network Agent", "🌐", "Monitors provider network status participation changes.", "Active"), unsafe_allow_html=True)
        st.markdown(agent_card("Evidence Agent", "🔍", "Correlates clinical supporting evidence with decisions.", "Active"), unsafe_allow_html=True)
        
    with col_a3:
        st.markdown('<div style="font-size:0.95rem;font-weight:700;color:#38bdf8;margin-bottom:0.8rem;text-transform:uppercase;letter-spacing:0.05em;">Layer 3: Forensic Output</div>', unsafe_allow_html=True)
        st.markdown(agent_card("Mutation Detector", "🔬", "Compares genomes, computes scores, and determines review flag.", "Active"), unsafe_allow_html=True)
        st.markdown(agent_card("Impact Assessment", "📈", "Models risk levels and population scale operational impact.", "Active"), unsafe_allow_html=True)
        st.markdown(agent_card("Audit Report Agent", "📋", "Synthesizes final forensic reports and executive summaries.", "Active"), unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    st.markdown("### 🔮 Enterprise Vision & Future Agents")
    st.markdown(
        "To scale this system into a multi-billion dollar healthcare network, we designed a modular blueprint. "
        "Adding coverage domains is as simple as dropping in new gene-specific agents. Here is our product roadmap:"
    )
    st.markdown(
        """
        <table style="width:100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.9rem; border: 1px solid var(--card-border);">
            <thead>
                <tr style="background: rgba(168, 85, 247, 0.1); border-bottom: 2px solid var(--card-border);">
                    <th style="padding: 10px; text-align: left; color:#a855f7;">Future Agent</th>
                    <th style="padding: 10px; text-align: left; color:#a855f7;">Purpose & Scope</th>
                    <th style="padding: 10px; text-align: left; color:#a855f7;">Enterprise Integration</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom: 1px solid var(--card-border);">
                    <td style="padding: 10px; font-weight: 600;">💊 FormularyGenomeAgent</td>
                    <td style="padding: 10px;">Detects drug formulary tier updates, exclusions, and prior auth requirement drift</td>
                    <td style="padding: 10px; font-family: monospace;">RxNorm / Formulary Registry API</td>
                </tr>
                <tr style="border-bottom: 1px solid var(--card-border);">
                    <td style="padding: 10px; font-weight: 600;">🩺 ClinicalGenomeAgent</td>
                    <td style="padding: 10px;">Compares EHR clinical evidence (lab values, diagnoses, vital signs) over time</td>
                    <td style="padding: 10px; font-family: monospace;">HL7 FHIR API (Epic, Cerner)</td>
                </tr>
                <tr style="border-bottom: 1px solid var(--card-border);">
                    <td style="padding: 10px; font-weight: 600;">⚖️ ComplianceAgent</td>
                    <td style="padding: 10px;">Validates identified mutations against CMS national coverage guidelines and state rules</td>
                    <td style="padding: 10px; font-family: monospace;">CMS Regulations Database / API</td>
                </tr>
                <tr style="border-bottom: 1px solid var(--card-border);">
                    <td style="padding: 10px; font-weight: 600;">✉️ AppealsAgent</td>
                    <td style="padding: 10px;">Auto-generates custom, legally-defensible appeal letters for denied cases</td>
                    <td style="padding: 10px; font-family: monospace;">CRM & Appeals Workflow Queue</td>
                </tr>
            </tbody>
        </table>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("**Enterprise Orchestration Pipeline:**")
    st.info("EHR Ingestion (Epic/FHIR) ➔ Event Bus ➔ HIPAA/Security Guardrail ➔ MCP Data Hydration ➔ Parallel Genome Agents ➔ Root Cause Mutation Detection ➔ Impact/Compliance Assessment ➔ Auto-Generated Appeals / EHR Webhooks.")


# ─────────────────────────────────────────────────────────────────────────
# TAB 10: Audit Report
# ─────────────────────────────────────────────────────────────────────────

with tabs[10]:
    st.markdown('<div style="padding:1rem 0px;"><h1 style="background:linear-gradient(135deg, #38bdf8, #a855f7);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:800;font-size:2.2rem;margin-bottom:0.5rem;">📋 Executive Audit Report</h1>'
                f'<p style="color:var(--text-color);opacity:0.6;font-size:1.05rem;margin-top:0px;">Active Case: {analysis["old_genome"]["case_id"]}</p></div>', unsafe_allow_html=True)

    ar = analysis["audit_report"]

    st.markdown(f'<div class="glass-card" style="border-top:4px solid #a855f7;margin-bottom:1.5rem;">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:1rem;">'
                f'  <div>'
                f'    <h3 style="margin:0px;color:var(--text-color);">Forensic Report Summary</h3>'
                f'    <div style="font-size:0.8rem;color:var(--text-color);opacity:0.6;margin-top:2px;">Report ID: {ar["report_id"]} | Generated: {ar["generated_at"]}</div>'
                f'  </div>'
                f'  <div style="display:flex;gap:10px;">'
                f'    {risk_badge(ar["risk_level"])}'
                f'  </div>'
                f'</div>'
                f'<strong style="color:var(--text-color);">Human Review Flag:</strong> <span style="color:var(--text-color);opacity:0.95;">{"✅ REQUIRED" if ar["human_review_flag"] else "❌ NOT REQUIRED"}</span>'
                f'</div>', unsafe_allow_html=True)

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.subheader("Executive Summary")
    st.info(ar["executive_summary"])

    st.subheader("Decision Lineage Map")
    st.code(ar["decision_lineage"], language="text")

    st.subheader("Primary Root Cause")
    st.warning(ar["root_cause"])

    col_sup, col_miss = st.columns(2)
    with col_sup:
        st.subheader("Supporting Clinical Evidence")
        for item in ar.get("supporting_evidence", []):
            st.markdown(f"- {item}")
    with col_miss:
        st.subheader("Missing Document Evidence")
        for item in ar.get("missing_evidence", []):
            st.markdown(f"- ❌ {item}")
        if not ar.get("missing_evidence"):
            st.caption("None")

    st.subheader("Actionable Recommendations")
    st.success(ar["recommendation"])

    if ar.get("impact"):
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.subheader("System Operational Impact")
        imp = ar["impact"]
        ic1, ic2, ic3 = st.columns(3)
        ic1.metric("Affected Population", f"~{imp['affected_population_estimate']:,}")
        ic2.metric("Risk Level", imp["risk_level"])
        ic3.metric("Decision Type", imp["affected_decision_type"])
        st.markdown(f"**Operational Impact:** {imp['operational_impact']}")
        st.markdown(f"**Financial Estimate:** {imp['financial_estimate']}")
        st.markdown(f"**Affected Systems:** {', '.join(imp['affected_systems'])}")
        st.caption(f"Compliance: {imp['compliance_note']}")

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.subheader("Originality & Verification Metadata")
    om1, om2 = st.columns(2)
    om1.markdown(f"**Project:** {ar.get('project_name', 'DecisionDNA AI')}")
    om1.markdown(f"**Author:** {ar.get('author', 'Sharath Chandra')}")
    if is_verified_author:
        om1.markdown("**Verification:** ✨ Verified Original Creator")
    else:
        om1.markdown("**Verification:** ⚠️ Forked / Unverified Build (Original Creator: Sharath Chandra)")
    om1.markdown(f"**Build Mode:** `{ar.get('build_mode', BUILD_MODE)}`")
    om2.markdown(f"**Scenario Fingerprint:** `{ar.get('scenario_fingerprint', 'N/A')}`")
    om2.markdown(f"**Genome Hash:** `{ar.get('genome_hash', 'N/A')}`")

    md_report = f"""# DecisionDNA AI — Forensic Audit Report
Report ID: {ar['report_id']}
Generated: {ar['generated_at']}
Risk Level: {ar['risk_level']}
Human Review Required: {'Yes' if ar['human_review_flag'] else 'No'}

## Executive Summary
{ar['executive_summary']}

## Decision Lineage
```
{ar['decision_lineage']}
```

## Root Cause
{ar['root_cause']}

## Recommendation
{ar['recommendation']}
"""
    if ar.get("impact"):
        imp = ar["impact"]
        md_report += f"""
## Impact Assessment
- Affected Population Estimate: {imp['affected_population_estimate']}
- Risk Level: {imp['risk_level']}
- Decision Type: {imp['affected_decision_type']}
- Operational Impact: {imp['operational_impact']}
- Financial Estimate: {imp['financial_estimate']}
- Affected Systems: {', '.join(imp['affected_systems'])}
- Compliance Note: {imp['compliance_note']}
"""

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown("### Export Forensic Report")
    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
        st.download_button(
            label="📥 Download Audit Report (Markdown)",
            data=md_report,
            file_name=f"audit_report_{ar['report_id']}.md",
            mime="text/markdown",
            key=f"dl_md_{ar['report_id']}"
        )
    with col_dl2:
        st.download_button(
            label="📥 Download Audit Report (JSON)",
            data=json.dumps(ar, indent=2),
            file_name=f"audit_report_{ar['report_id']}.json",
            mime="application/json",
            key=f"dl_json_{ar['report_id']}"
        )

# ── Footer ────────────────────────────────────────────────────────────────

st.markdown("---")
if is_verified_author:
    st.caption(
        "🧬 DecisionDNA AI — Temporal Decision Forensics for Healthcare Networks · "
        "Built by Sharath Chandra · ✨ Verified Original Creator (@yakarasharath4) · Synthetic Demo Only · No PHI"
    )
else:
    st.caption(
        f"🧬 DecisionDNA AI — Temporal Decision Forensics for Healthcare Networks · "
        f"Built by {owner} · ⚠️ Forked Build (Original Creator: Sharath Chandra) · Synthetic Demo Only · No PHI"
    )
