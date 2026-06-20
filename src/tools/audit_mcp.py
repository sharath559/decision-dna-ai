"""
DecisionDNA AI — AuditMCP Tool

Mock MCP tool that generates and stores audit trail records.
In production this would write to a compliance database;
here it builds structured audit payloads in memory.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime
from typing import Any

logger = logging.getLogger("decisiondna.tools.audit_mcp")

# In-memory audit store (would be a database in production)
_AUDIT_STORE: list[dict[str, Any]] = []


def generate_audit_id(case_id: str) -> str:
    """Deterministic audit ID from case_id + timestamp."""
    ts = datetime.utcnow().isoformat()
    raw = f"{case_id}|{ts}"
    return "AUD-" + hashlib.sha256(raw.encode()).hexdigest()[:10].upper()


def store_audit_record(record: dict[str, Any]) -> dict[str, Any]:
    """Persist an audit record and return confirmation."""
    record.setdefault("audit_id", generate_audit_id(record.get("case_id", "UNKNOWN")))
    record.setdefault("stored_at", datetime.utcnow().isoformat())
    _AUDIT_STORE.append(record)
    logger.info(
        "AuditMCP.store_audit_record | audit_id=%s case=%s | ts=%s",
        record["audit_id"],
        record.get("case_id"),
        record["stored_at"],
    )
    return {"status": "ok", "audit_id": record["audit_id"]}


def get_audit_trail(case_id: str) -> dict[str, Any]:
    """Retrieve all audit records for a case."""
    records = [r for r in _AUDIT_STORE if r.get("case_id") == case_id]
    logger.info(
        "AuditMCP.get_audit_trail | case=%s records=%d | ts=%s",
        case_id, len(records), datetime.utcnow().isoformat(),
    )
    return {"status": "ok", "case_id": case_id, "records": records}


def get_all_audits() -> list[dict[str, Any]]:
    """Return all stored audit records."""
    return list(_AUDIT_STORE)
