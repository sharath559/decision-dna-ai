"""
DecisionDNA AI — Timeline Service

Builds temporal timelines for the Decision Timeline view.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.models.decision_models import TimelineEvent

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_sample_cases() -> list[dict[str, Any]]:
    with open(_DATA_DIR / "sample_cases.json") as f:
        return json.load(f).get("cases", [])


def generate_temporal_timeline(case_id: str) -> list[TimelineEvent]:
    """
    Skill: generate_temporal_timeline

    Return the ordered timeline events for a case.
    """
    for case in _load_sample_cases():
        if case["case_id"] == case_id:
            events = []
            for ev in case.get("timeline_events", []):
                # Infer category from event text
                text_lower = ev["event"].lower()
                if "policy" in text_lower:
                    cat = "policy"
                elif "contract" in text_lower:
                    cat = "contract"
                elif "rule" in text_lower:
                    cat = "rule"
                elif "network" in text_lower:
                    cat = "network"
                elif "denied" in text_lower or "approved" in text_lower or "rejected" in text_lower or "paid" in text_lower or "terminated" in text_lower:
                    cat = "decision"
                else:
                    cat = "general"
                events.append(
                    TimelineEvent(date=ev["date"], event=ev["event"], category=cat)
                )
            return events
    return []
