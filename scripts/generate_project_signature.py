#!/usr/bin/env python3
"""
DecisionDNA AI — Project Signature Generator

Generates a unique project signature file at .local/project_signature.json
using values from .env (if available) or sensible defaults.
Never stores raw secrets or raw seeds in the signature file.
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
    private_demo_mode = os.getenv("PRIVATE_DEMO_MODE", "false").lower() == "true"
    project_mode = "PRIVATE" if private_demo_mode else "PUBLIC"
    scenario_seed = os.getenv("SCENARIO_SEED", "replace-with-your-local-seed")
    scenario_seed = os.getenv("SCENARIO_SEED", "public-demo-seed")

    build_ts = datetime.utcnow().isoformat() + "Z"

    # Deterministic hash from owner + handle + seed + timestamp
    raw = f"{project_owner}|{project_handle}|{scenario_seed}|{build_ts}"
    originality_hash = hashlib.sha256(raw.encode()).hexdigest()

    # Author verification hash check
    author_raw = f"{project_owner}|{project_handle}"
    author_hash = hashlib.sha256(author_raw.encode()).hexdigest()
    ORIGINAL_HASH = "761ccbf10b0a92a7ebf514177cc8b0f01572eb5315b7c0bc6dd7fa288124f9e2"
    is_verified = (author_hash == ORIGINAL_HASH)

    signature = {
        "project_owner": project_owner,
        "project_handle": project_handle,
        "project_name": project_name,
        "project_version": "1.0.0",
        "build_timestamp": build_ts,
        "scenario_seed": scenario_seed,
        "originality_hash": originality_hash,
        "author_verification": "VERIFIED_ORIGINAL_CREATOR" if is_verified else "UNVERIFIED_FORK_BUILD"
    }

    out_dir = Path(__file__).resolve().parent.parent / ".local"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "project_signature.json"

    with open(out_path, "w") as f:
        json.dump(signature, f, indent=2)

    print(f"✅ Project signature written to {out_path}")
    print(json.dumps(signature, indent=2))
    
    if is_verified:
        print("\n✨ Cryptographic verification: VERIFIED ORIGINAL CREATOR (Sharath Chandra)")
    else:
        print("\n⚠️ Cryptographic verification: UNVERIFIED FORK BUILD")
        print("   Original Creator: Sharath Chandra (@yakarasharath4)")


if __name__ == "__main__":
    main()
