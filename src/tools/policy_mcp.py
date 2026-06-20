"""
DecisionDNA AI — PolicyMCP Tool

Mock MCP (Model Context Protocol) tool that simulates an external
policy-version lookup service.  In production this would call a
policy-management API; here it reads from local JSON.

Every call is logged with tool name, input, output, and timestamp
so the AuditAgent can reconstruct the forensic trail.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("decisiondna.tools.policy_mcp")

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_CACHE: Optional[dict] = None


def _load_policies() -> dict:
    global _CACHE
    if _CACHE is None:
        with open(_DATA_DIR / "policy_versions.json") as f:
            _CACHE = json.load(f)
    return _CACHE


_CUSTOM_POLICIES: dict[str, dict[str, Any]] = {}


def register_custom_policy(policy_id: str, policy_data: dict[str, Any]) -> None:
    """Register a custom policy version in memory."""
    _CUSTOM_POLICIES[policy_id] = policy_data


def get_policy_version(policy_id: str) -> dict[str, Any]:
    """
    Fetch a single policy version by ID.

    Parameters
    ----------
    policy_id : str
        e.g. "MRI-MED-NEC-v1"

    Returns
    -------
    dict with policy details, or an error payload.
    """
    if policy_id in _CUSTOM_POLICIES:
        version = _CUSTOM_POLICIES[policy_id]
        result = {"status": "ok", "policy": version}
        logger.info(
            "PolicyMCP.get_policy_version (custom) | input=%s | output_keys=%s | ts=%s",
            policy_id,
            list(version.keys()),
            datetime.utcnow().isoformat(),
        )
        return result

    data = _load_policies()
    for version in data.get("versions", []):
        if version["policy_id"] == policy_id:
            result = {"status": "ok", "policy": version}
            logger.info(
                "PolicyMCP.get_policy_version | input=%s | output_keys=%s | ts=%s",
                policy_id,
                list(version.keys()),
                datetime.utcnow().isoformat(),
            )
            return result
    logger.warning("PolicyMCP.get_policy_version | policy_id=%s NOT FOUND", policy_id)
    return {"status": "not_found", "policy_id": policy_id}


def compare_policy_versions(old_id: str, new_id: str) -> dict[str, Any]:
    """
    Compare two policy versions and return clause-level diff.

    Returns
    -------
    dict with old_policy, new_policy, added_clauses, removed_clauses.
    """
    old = get_policy_version(old_id)
    new = get_policy_version(new_id)
    if old["status"] != "ok" or new["status"] != "ok":
        return {"status": "error", "detail": "One or both policy versions not found."}

    old_clauses = {c["clause_id"]: c for c in old["policy"]["clauses"]}
    new_clauses = {c["clause_id"]: c for c in new["policy"]["clauses"]}

    added = [new_clauses[cid] for cid in new_clauses if cid not in old_clauses]
    removed = [old_clauses[cid] for cid in old_clauses if cid not in new_clauses]

    result = {
        "status": "ok",
        "old_policy_id": old_id,
        "new_policy_id": new_id,
        "old_policy_name": old["policy"]["policy_name"],
        "new_policy_name": new["policy"]["policy_name"],
        "added_clauses": added,
        "removed_clauses": removed,
        "clause_count_before": len(old_clauses),
        "clause_count_after": len(new_clauses),
    }
    logger.info(
        "PolicyMCP.compare_policy_versions | %s→%s | added=%d removed=%d | ts=%s",
        old_id, new_id, len(added), len(removed), datetime.utcnow().isoformat(),
    )
    return result


def list_policies() -> list[dict[str, Any]]:
    """Return all policy version summaries."""
    data = _load_policies()
    return [
        {
            "policy_id": v["policy_id"],
            "policy_name": v["policy_name"],
            "effective_date": v["effective_date"],
            "category": v["category"],
        }
        for v in data.get("versions", [])
    ]
