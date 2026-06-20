"""
DecisionDNA AI — DocumentationMCP Tool

Mock MCP tool for documentation-requirement lookups and gap analysis.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("decisiondna.tools.documentation_mcp")

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_CACHE: Optional[dict] = None


def _load_docs() -> dict:
    global _CACHE
    if _CACHE is None:
        with open(_DATA_DIR / "documentation_requirements.json") as f:
            _CACHE = json.load(f)
    return _CACHE


def get_required_documents(
    category: str, subcategory: str, policy_id: str
) -> dict[str, Any]:
    """
    Look up required and optional documents for a given policy version.
    """
    data = _load_docs()
    reqs = (
        data.get("requirements", {})
        .get(category, {})
        .get(subcategory, {})
        .get(policy_id, {})
    )
    if not reqs:
        return {"status": "not_found", "policy_id": policy_id}
    logger.info(
        "DocumentationMCP.get_required_documents | policy=%s | ts=%s",
        policy_id, datetime.utcnow().isoformat(),
    )
    return {"status": "ok", "policy_id": policy_id, **reqs}


def get_submitted_documents(case_id: str, snapshot_date: str) -> dict[str, Any]:
    """
    Look up what documents were actually submitted for a case at a point in time.
    """
    data = _load_docs()
    submissions = data.get("submissions", {}).get(case_id, {})
    docs = submissions.get(snapshot_date, [])
    logger.info(
        "DocumentationMCP.get_submitted_documents | case=%s date=%s count=%d | ts=%s",
        case_id, snapshot_date, len(docs), datetime.utcnow().isoformat(),
    )
    return {"status": "ok", "case_id": case_id, "snapshot_date": snapshot_date, "submitted": docs}


def compute_documentation_gap(
    required: list[str], submitted: list[str]
) -> dict[str, Any]:
    """
    Compute the gap between required and submitted documents.
    """
    missing = [doc for doc in required if doc not in submitted]
    extra = [doc for doc in submitted if doc not in required]
    result = {
        "required_count": len(required),
        "submitted_count": len(submitted),
        "missing": missing,
        "extra": extra,
        "gap_score": len(missing) / max(len(required), 1),
    }
    logger.info(
        "DocumentationMCP.compute_gap | missing=%d extra=%d | ts=%s",
        len(missing), len(extra), datetime.utcnow().isoformat(),
    )
    return result
