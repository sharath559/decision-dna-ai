"""
DecisionDNA AI — RulesMCP Tool

Mock MCP tool for business-rule version lookups and validation-diff.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("decisiondna.tools.rules_mcp")

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_CACHE: Optional[dict] = None


def _load_rules() -> dict:
    global _CACHE
    if _CACHE is None:
        with open(_DATA_DIR / "rule_versions.json") as f:
            _CACHE = json.load(f)
    return _CACHE


_CUSTOM_RULES: dict[str, dict[str, Any]] = {}


def register_custom_rule(rule_id: str, rule_data: dict[str, Any]) -> None:
    """Register a custom rule version in memory."""
    _CUSTOM_RULES[rule_id] = rule_data


def get_rule(rule_id: str) -> dict[str, Any]:
    """Fetch a single business rule by ID."""
    if rule_id in _CUSTOM_RULES:
        logger.info(
            "RulesMCP.get_rule (custom) | input=%s | ts=%s",
            rule_id, datetime.utcnow().isoformat(),
        )
        return {"status": "ok", "rule": _CUSTOM_RULES[rule_id]}

    data = _load_rules()
    for r in data.get("rules", []):
        if r["rule_id"] == rule_id:
            logger.info(
                "RulesMCP.get_rule | input=%s | ts=%s",
                rule_id, datetime.utcnow().isoformat(),
            )
            return {"status": "ok", "rule": r}
    return {"status": "not_found", "rule_id": rule_id}


def compare_rules(old_id: str, new_id: str) -> dict[str, Any]:
    """Compare two rule versions and return added/removed validations."""
    old = get_rule(old_id)
    new = get_rule(new_id)
    if old["status"] != "ok" or new["status"] != "ok":
        return {"status": "error", "detail": "One or both rules not found."}

    old_checks = {v["check"] for v in old["rule"]["validations"]}
    new_checks = {v["check"] for v in new["rule"]["validations"]}

    added = [
        v for v in new["rule"]["validations"] if v["check"] not in old_checks
    ]
    removed = [
        v for v in old["rule"]["validations"] if v["check"] not in new_checks
    ]

    result = {
        "status": "ok",
        "old_rule_id": old_id,
        "new_rule_id": new_id,
        "added_validations": added,
        "removed_validations": removed,
        "validation_count_before": len(old_checks),
        "validation_count_after": len(new_checks),
    }
    logger.info(
        "RulesMCP.compare_rules | %s→%s | added=%d removed=%d | ts=%s",
        old_id, new_id, len(added), len(removed), datetime.utcnow().isoformat(),
    )
    return result
