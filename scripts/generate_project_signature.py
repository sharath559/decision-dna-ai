#!/usr/bin/env python3
"""
DecisionDNA AI — Project Signature Generator

Generates a unique project signature file at .local/project_signature.json
using values from .env (if available) or sensible defaults.

Usage:
    python scripts/generate_project_signature.py
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Allow running from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional for this script


def main() -> None:
    project_owner = os.getenv("PROJECT_OWNER", "Sharath Chandra")
    project_handle = os.getenv("PROJECT_HANDLE", "@yakarasharath4")
    project_name = os.getenv("PROJECT_NAME", "DecisionDNA AI")
    scenario_seed = os.getenv("SCENARIO_SEED", "public-demo-seed")

    build_ts = datetime.utcnow().isoformat() + "Z"

    # Deterministic hash from owner + handle + seed + timestamp
    raw = f"{project_owner}|{project_handle}|{scenario_seed}|{build_ts}"
    originality_hash = hashlib.sha256(raw.encode()).hexdigest()

    signature = {
        "project_owner": project_owner,
        "project_handle": project_handle,
        "project_name": project_name,
        "project_version": "1.0.0",
        "build_timestamp": build_ts,
        "scenario_seed": scenario_seed,
        "originality_hash": originality_hash,
    }

    out_dir = Path(__file__).resolve().parent.parent / ".local"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "project_signature.json"

    with open(out_path, "w") as f:
        json.dump(signature, f, indent=2)

    print(f"✅ Project signature written to {out_path}")
    print(json.dumps(signature, indent=2))


if __name__ == "__main__":
    main()
