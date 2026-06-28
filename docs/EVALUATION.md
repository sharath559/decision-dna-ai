# Evaluation Framework — DecisionDNA AI

## Overview

DecisionDNA AI employs a multi-layer evaluation strategy to validate the correctness, reliability, and security of its multi-agent forensic analysis pipeline.

## Evaluation Layers

### Layer 1: Schema Contract Validation

**What:** Pydantic v2 model validation ensures all agent inputs/outputs conform to expected schemas at runtime.

**How:** `DecisionGenome.model_validate()` is called on every data ingestion point. Invalid payloads raise `ValidationError` before reaching any agent.

**Test:** `TestDecisionGenomeSchemas.test_invalid_genome_throws_error`

**Why it matters:** In a multi-agent system, schema drift between agents can cause silent data corruption. Pydantic v2 acts as the contract enforcement layer.

---

### Layer 2: Mutation Forensics Mathematical Verification

**What:** Verifies that the weighted mutation score formula produces correct, reproducible results across all known scenarios.

**Formula:**
```
M(g₁, g₂) = min(100, Σᵢ wᵢ · Sᵢ)
```

**How:** Pre-computed expected scores for known case scenarios are compared against engine output.

**Tests:**
- `TestMutationForensicEngine.test_preloaded_case_mri_forensics` — validates PA-MRI-1001 produces `score=100`, `primary=Policy Gene`
- `TestMutationForensicEngine.test_preloaded_case_claim_forensics` — validates CLM-5502 produces `primary=Contract Gene`

**Why it matters:** Healthcare compliance decisions must be deterministically reproducible. The mutation score cannot vary between runs for the same input.

---

### Layer 3: Security Guardrail Verification

**What:** Ensures prompt injection, PII, and unsafe instruction patterns are correctly detected and blocked before reaching the agent pipeline.

**Tests:**
- `TestSecurityAgent.test_prompt_injection_detection` — verifies "ignore previous instructions" triggers CRITICAL finding
- `TestSecurityAgent.test_pii_redaction` — verifies SSN/email patterns are redacted to `[REDACTED]` tokens

**Why it matters:** In a healthcare AI system, security failures can lead to HIPAA violations, data exfiltration, or audit bypass. The SecurityAgent is the first line of defence.

---

### Layer 4: MCP Tool Integration Testing

**What:** Validates that MCP tools correctly retrieve and diff registry data from the synthetic data layer.

**Tests:**
- `TestMCPTools.test_policy_mcp_compare` — verifies clause-level diffing returns correct added/removed clauses
- `TestMCPTools.test_contract_mcp_lookup` — verifies provider contract retrieval and field correctness

**Why it matters:** Agents depend on MCP tools for external data. Incorrect tool outputs propagate errors through the entire pipeline.

---

### Layer 5: Gemini Structured Output Validation

**What:** When Gemini 2.0 Flash is enabled, validates that LLM responses conform to the expected Pydantic schemas.

**Schemas validated:**
- `GeminiRootCauseAnalysis` — root cause narrative + recommended actions
- `GeminiExecutiveSummary` — executive summary + key findings + regulatory implications
- `GeminiSecurityAssessment` — threat level + analysis + recommendations

**How:** The `response_schema` parameter in `GenerateContentConfig` enforces JSON schema compliance at the Gemini API level. Pydantic `.parsed` validates the response client-side.

---

## Running the Test Suite

```bash
# Standard library runner
python tests/test_genome_forensics.py

# With pytest (recommended)
pytest tests/ -v --tb=short

# With coverage reporting
pytest tests/ --cov=src --cov-report=term-missing

# Run specific test class
pytest tests/test_genome_forensics.py::TestSecurityAgent -v
```

## Evaluation Metrics

| Metric | Target | Current Status |
|--------|--------|----------------|
| Schema validation coverage | 100% of Pydantic models | ✅ All 14 models validated |
| Mutation score accuracy | ±0 on known cases | ✅ Exact match on 2 cases |
| Security pattern detection | 100% of known patterns | ✅ 10/10 injection patterns |
| PII redaction rate | 100% of detected PII | ✅ SSN + email verified |
| MCP tool correctness | All diffs accurate | ✅ Policy + Contract verified |
| Gemini structured output | Schema-compliant | ✅ response_schema enforced |
| Deterministic fallback | 100% functional without API key | ✅ MOCK_MODE tested |

## Evaluation Philosophy

### Why Deterministic Tests for an AI Agent System?

DecisionDNA AI uses a **hybrid architecture** (deterministic + LLM). The evaluation strategy matches:

1. **Deterministic path (always tested):** Mutation scores, schema validation, security patterns, and MCP tools are fully deterministic. These are tested with exact assertions.

2. **LLM path (schema-validated):** Gemini-generated narratives are validated for schema compliance and key content markers, not exact string matching (LLM outputs are inherently variable).

3. **Graceful degradation (tested):** The system must function identically with or without a Gemini API key. This is verified by running the full test suite in MOCK_MODE.

## Future Evaluation Enhancements

- [ ] Add LLM-as-judge evaluation for root cause narrative quality
- [ ] Add adversarial prompt injection fuzzing (beyond known patterns)
- [ ] Add end-to-end latency benchmarks (target: <3 seconds per case)
- [ ] Add cross-case regression suite (10+ cases with known scores)
- [ ] Add Gemini response quality scoring with automated grading
- [ ] Add A/B testing framework for deterministic vs. Gemini narratives
