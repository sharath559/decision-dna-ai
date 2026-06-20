# Security Policy — DecisionDNA AI

## Data Safety Rules

1. **Never commit `.env`** — it may contain personal project settings.
2. **Never commit real PHI** — all data in this project is synthetic.
3. **Never commit API keys** — use `.env.example` as a template.
4. **Run in MOCK_MODE by default** — no external services required.
5. **Use synthetic data only** — all JSON files in `src/data/` are fabricated.

## Sensitive Patterns

The built-in `SecurityAgent` scans for:
- Prompt injection attempts ("ignore previous instructions", "bypass policy")
- PII-like patterns (SSN, email, phone, member ID formats)
- Unsafe instructions ("delete records", "reveal api key", "disable audit")
- PHI exfiltration attempts ("send PHI", "export patient data")

## Reporting Vulnerabilities

If you discover a security issue in the synthetic data or code logic,
open a GitHub issue with the label `security`.

## What Is Safe to Share

- The full public repo (no `.env`, no `.local/`)
- Screenshots of the Streamlit UI (synthetic data only)
- Video demos (use PRIVATE_DEMO_MODE for personalized fingerprints)
