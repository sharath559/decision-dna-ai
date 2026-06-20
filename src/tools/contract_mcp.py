"""
DecisionDNA AI — ContractMCP Tool

Mock MCP tool that simulates a provider-contract / network-enrollment
lookup service.  Reads from local contract_versions.json.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("decisiondna.tools.contract_mcp")

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_CACHE: Optional[dict] = None


def _load_contracts() -> dict:
    global _CACHE
    if _CACHE is None:
        with open(_DATA_DIR / "contract_versions.json") as f:
            _CACHE = json.load(f)
    return _CACHE


_CUSTOM_CONTRACTS: dict[str, dict[str, Any]] = {}


def register_custom_contract(contract_id: str, contract_data: dict[str, Any]) -> None:
    """Register a custom contract version in memory."""
    _CUSTOM_CONTRACTS[contract_id] = contract_data


def get_contract(contract_id: str) -> dict[str, Any]:
    """Fetch a single contract by ID."""
    if contract_id in _CUSTOM_CONTRACTS:
        logger.info(
            "ContractMCP.get_contract (custom) | input=%s | ts=%s",
            contract_id, datetime.utcnow().isoformat(),
        )
        return {"status": "ok", "contract": _CUSTOM_CONTRACTS[contract_id]}

    data = _load_contracts()
    for c in data.get("contracts", []):
        if c["contract_id"] == contract_id:
            logger.info(
                "ContractMCP.get_contract | input=%s | ts=%s",
                contract_id, datetime.utcnow().isoformat(),
            )
            return {"status": "ok", "contract": c}
    return {"status": "not_found", "contract_id": contract_id}


def get_provider_contracts(provider_id: str) -> dict[str, Any]:
    """Fetch all contract versions for a provider, ordered by effective_date."""
    data = _load_contracts()
    matches = [c for c in data.get("contracts", []) if c["provider_id"] == provider_id]
    
    # Merge in-memory custom contracts for this provider
    for c in _CUSTOM_CONTRACTS.values():
        if c.get("provider_id") == provider_id and c not in matches:
            matches.append(c)

    matches.sort(key=lambda c: c["effective_date"])
    logger.info(
        "ContractMCP.get_provider_contracts | provider=%s | count=%d | ts=%s",
        provider_id, len(matches), datetime.utcnow().isoformat(),
    )
    return {"status": "ok", "provider_id": provider_id, "contracts": matches}


def compare_contracts(old_id: str, new_id: str) -> dict[str, Any]:
    """Compare two contract versions and highlight changes."""
    old = get_contract(old_id)
    new = get_contract(new_id)
    if old["status"] != "ok" or new["status"] != "ok":
        return {"status": "error", "detail": "One or both contracts not found."}

    oc, nc = old["contract"], new["contract"]
    changes: list[str] = []
    if oc["status"] != nc["status"]:
        changes.append(f"Status: {oc['status']} → {nc['status']}")
    if oc["network_status"] != nc["network_status"]:
        changes.append(f"Network: {oc['network_status']} → {nc['network_status']}")
    if oc.get("termination_date") != nc.get("termination_date"):
        changes.append(f"Termination date: {oc.get('termination_date')} → {nc.get('termination_date')}")

    result = {
        "status": "ok",
        "old_contract_id": old_id,
        "new_contract_id": new_id,
        "changes": changes,
        "continuity_of_care_flag": nc.get("continuity_of_care_flag", False),
        "termination_reason": nc.get("termination_reason", ""),
    }
    logger.info(
        "ContractMCP.compare_contracts | %s→%s | changes=%d | ts=%s",
        old_id, new_id, len(changes), datetime.utcnow().isoformat(),
    )
    return result
