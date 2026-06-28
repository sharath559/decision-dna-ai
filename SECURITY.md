# Security Policy — DecisionDNA AI

## Threat Model

### Assets Under Protection

1. **Patient Health Information (PHI)** — Even synthetic, patterns must be safe for production migration
2. **Agent Reasoning Pipeline** — Must resist prompt injection and adversarial manipulation
3. **Audit Trail Integrity** — Reports must be tamper-evident with cryptographic hashes
4. **API Keys / Credentials** — Must never leak into LLM context windows
5. **Decision Lineage** — Must not be alterable after generation

### Threat Vectors & Mitigations

| Threat | Attack Vector | Mitigation | Implementation | Status |
|--------|--------------|------------|----------------|--------|
| Prompt Injection | User input manipulates agent behavior | SecurityAgent scans 10 injection patterns before processing | `security_agent.py` L30-60 | ✅ Implemented |
| PII Leakage | SSN/email in agent output | Regex-based PII detection + `[REDACTED]` token masking | `security_agent.py` L70-90 | ✅ Implemented |
| Unsafe Instructions | "Delete records", "reveal API key" | 7-pattern unsafe instruction scanner with CRITICAL classification | `security_agent.py` L50-65 | ✅ Implemented |
| Credential Exposure | API keys in LLM context window | MCP tool decoupling — agents never see raw credentials | Architectural pattern | ✅ By Design |
| Audit Tampering | Modified report after generation | SHA-256 `genome_hash` + `scenario_fingerprint` on every report | `mutation_detection_agent.py` | ✅ Implemented |
| Data Exfiltration | "Export patient data" commands | Unsafe instruction pattern match | `security_agent.py` | ✅ Implemented |
| Role Hijacking | "You are now a..." prompts | Role hijacking pattern detection | `security_agent.py` | ✅ Implemented |
| LLM Hallucination | Gemini generates false clinical data | Hybrid architecture — deterministic scores are authoritative | `mutation_engine.py` | ✅ By Design |
| Schema Injection | Malformed JSON bypasses validation | Pydantic v2 strict mode with `model_validate()` | `decision_models.py` | ✅ Implemented |

### SecurityAgent Pattern Coverage

**Prompt Injection Detection (10 patterns):**

| # | Pattern | Severity |
|---|---------|----------|
| 1 | `ignore previous instructions` | CRITICAL |
| 2 | `bypass policy` | CRITICAL |
| 3 | `override approval` | CRITICAL |
| 4 | `auto-approve` | CRITICAL |
| 5 | `force approval` | CRITICAL |
| 6 | `ignore policy` | CRITICAL |
| 7 | `approve claim immediately` | CRITICAL |
| 8 | `instead of the above` | CRITICAL |
| 9 | `disregard all/previous` | CRITICAL |
| 10 | `you are now` (role hijacking) | CRITICAL |

**Unsafe Instruction Detection (7 patterns):**

| # | Pattern | Severity |
|---|---------|----------|
| 1 | `delete records` | CRITICAL |
| 2 | `reveal api key` | CRITICAL |
| 3 | `send PHI` | CRITICAL |
| 4 | `export patient data` | CRITICAL |
| 5 | `disable audit` | CRITICAL |
| 6 | `drop table` | CRITICAL |
| 7 | `truncate table` | CRITICAL |

**PII Detection (4 patterns):**

| # | Pattern | Example | Action |
|---|---------|---------|--------|
| 1 | SSN format | `123-45-6789` | Redact to `[REDACTED]` |
| 2 | Email addresses | `user@example.com` | Redact to `[REDACTED]` |
| 3 | Phone numbers | `555-123-4567` | Redact to `[REDACTED]` |
| 4 | Member ID format | `MBR-12345-X` | Redact to `[REDACTED]` |

### Gemini-Enhanced Security (Layer 2)

When Gemini 2.0 Flash is available, the SecurityAgent performs an additional **semantic threat classification** using the `GeminiSecurityAssessment` structured output schema:

```python
class GeminiSecurityAssessment(BaseModel):
    threat_level: str    # SAFE, WARNING, or CRITICAL
    analysis: str        # Detailed threat analysis
    recommendations: list[str]  # Security recommendations
```

This catches adversarial patterns that regex alone cannot detect (e.g., obfuscated injection, encoded PII, multi-step social engineering).

## Data Safety Rules

1. **Never commit `.env`** — may contain API keys and personal settings
2. **Never commit real PHI** — all data in this project is 100% synthetic
3. **Never commit API keys** — use `.env.example` as template
4. **Run in MOCK_MODE by default** — no external services required
5. **Use synthetic data only** — all JSON files in `src/data/` are fabricated

## HIPAA Compliance Considerations

- All sample data is synthetic — no real patient information exists in this repository
- PII detection runs on **all inputs** before any agent processes them
- Audit trails include timestamps, SHA-256 hashes, and scenario fingerprints
- Agent outputs are Pydantic-validated to prevent unstructured data leakage
- The SecurityAgent acts as a semantic firewall at the pipeline entry point

## Cryptographic Integrity

### Genome Hash
Every `MutationReport` includes a `genome_hash` — a SHA-256 hash of the complete genome state. This provides tamper-evidence for the audit trail.

### Scenario Fingerprint
Each analysis produces a `scenario_fingerprint` — a deterministic hash of the input parameters. Running the same case twice produces the same fingerprint, enabling reproducibility verification.

### Author Verification
The `generate_project_signature.py` script produces a cryptographic author verification hash, ensuring the submission can be traced to its original creator.

## Reporting Vulnerabilities

If you discover a security issue in the synthetic data or code logic, please open a GitHub issue with the label `security`.

## What Is Safe to Share

- ✅ The full public repository (no `.env`, no `.local/`)
- ✅ Screenshots of the Streamlit UI (synthetic data only)
- ✅ Video demos (use `PRIVATE_DEMO_MODE` for personalised fingerprints)
- ❌ `.env` files with API keys
- ❌ `.local/` directory with project signatures
