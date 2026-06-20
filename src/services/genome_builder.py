"""
DecisionDNA AI — Genome Builder Service

Loads decision snapshots from JSON, hydrates DecisionGenome models,
and provides the ``build_decision_genome`` / ``compare_genomes`` skills.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from src.models.decision_models import DecisionGenome

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_CACHE: Optional[dict] = None


def _load_snapshots() -> list[dict]:
    global _CACHE
    if _CACHE is None:
        with open(_DATA_DIR / "decision_snapshots.json") as f:
            _CACHE = json.load(f)
    return _CACHE.get("snapshots", [])


def build_decision_genome(case_id: str, snapshot_date: str) -> Optional[DecisionGenome]:
    """
    Skill: build_decision_genome

    Load a Decision Genome for the given case and snapshot date.
    Returns None if no matching snapshot exists.
    """
    for snap in _load_snapshots():
        if snap["case_id"] == case_id and snap["snapshot_date"] == snapshot_date:
            return DecisionGenome.model_validate(snap)
    return None


def get_genome_pair(case_id: str) -> tuple[Optional[DecisionGenome], Optional[DecisionGenome]]:
    """
    Convenience: return (old_genome, new_genome) for a case.
    Assumes exactly two snapshots sorted chronologically.
    """
    matches = [s for s in _load_snapshots() if s["case_id"] == case_id]
    matches.sort(key=lambda s: s["snapshot_date"])
    if len(matches) < 2:
        return (None, None)
    return (
        DecisionGenome.model_validate(matches[0]),
        DecisionGenome.model_validate(matches[1]),
    )


def compare_genomes(
    old: DecisionGenome, new: DecisionGenome
) -> dict[str, dict]:
    """
    Skill: compare_genomes

    Produce a gene-by-gene diff dictionary suitable for display.
    """
    result: dict[str, dict] = {}
    for gene_name in ("policy_gene", "contract_gene", "rule_gene",
                       "documentation_gene", "network_gene", "evidence_gene"):
        old_gene = getattr(old.genes, gene_name).model_dump()
        new_gene = getattr(new.genes, gene_name).model_dump()
        changed = old_gene != new_gene
        result[gene_name] = {
            "before": old_gene,
            "after": new_gene,
            "changed": changed,
        }
    return result


def list_case_ids() -> list[str]:
    """Return distinct case IDs from the snapshot store."""
    return sorted({s["case_id"] for s in _load_snapshots()})
