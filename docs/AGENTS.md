# Agent Registry — DecisionDNA AI

> Comprehensive documentation for all 9 specialised agents in the DecisionDNA multi-agent system.

## Agent Overview

| # | Agent | Type | Input | Output | MCP Tool | LOC |
|---|-------|------|-------|--------|----------|-----|
| 1 | PolicyGenomeAgent | Genome Analyser | DecisionGenome × 2 | GeneMutation | PolicyMCP | 82 |
| 2 | ContractGenomeAgent | Genome Analyser | DecisionGenome × 2 | GeneMutation | ContractMCP | 78 |
| 3 | RuleGenomeAgent | Genome Analyser | DecisionGenome × 2 | GeneMutation | RulesMCP | 93 |
| 4 | DocumentationGenomeAgent | Genome Analyser | DecisionGenome × 2 | GeneMutation | DocumentationMCP | 70 |
| 5 | NetworkGenomeAgent | Genome Analyser | DecisionGenome × 2 | GeneMutation | — | 66 |
| 6 | MutationDetectionAgent | Synthesiser | GeneMutation[] | MutationReport | — | 130 |
| 7 | ImpactAgent | Forecaster | MutationReport | ImpactAssessment | — | 110 |
| 8 | SecurityAgent | Firewall | str | SecurityReport | — | 123 |
| 9 | AuditAgent | Reporter | MutationReport + Impact + Security | AuditReport | AuditMCP | 112 |

## Architecture Pattern

All agents inherit from `BaseAgent` (ABC) and implement the `analyze()` method:

```python
class BaseAgent(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def analyze(self, **kwargs) -> Any:
        """Core analysis method — each agent defines its own signature."""

    def _log_invocation(self, case_id: str) -> None:
        """Structured audit logging for every agent invocation."""
```

## Agent Detail Cards

### 1. PolicyGenomeAgent

- **Purpose:** Detects mutations in the Policy Gene by comparing medical necessity guideline versions across temporal snapshots.
- **ADK System Prompt:** "You are a clinical guidelines auditor in DecisionDNA AI. Compare two policy versions using the compare_policy_versions tool, identify clause mutations (added/removed rules), and classify severity."
- **Severity Logic:**
  - `low` — version changed, no clause additions/removals
  - `high` — new clauses added (stricter requirements)
  - `critical` — clauses removed (coverage gaps)
- **MCP Dependency:** `PolicyMCP.compare_policy_versions(old_id, new_id)`
- **Gemini Enhancement:** ADK agent definition uses Gemini 2.0 Flash for clause-level reasoning

---

### 2. ContractGenomeAgent

- **Purpose:** Identifies provider contract and network enrollment changes (fees, network status, terminations).
- **ADK System Prompt:** "You are a provider contract investigator. Use compare_provider_contracts to identify changes in network status, provider status, and termination flags."
- **Severity Logic:**
  - `medium` — version changed
  - `high` — network status changed to OUT_OF_NETWORK
  - `critical` — provider status TERMINATED
- **MCP Dependency:** `ContractMCP.compare_contracts(old_id, new_id)`

---

### 3. RuleGenomeAgent

- **Purpose:** Audits business rule version changes and their impact on validation outcomes.
- **ADK System Prompt:** "You are a business rules auditor. Compare rule versions to identify added/removed validations and new validation failures."
- **Severity Logic:**
  - `low` — version changed, no new failures
  - `medium` — new validations added
  - `high` — new validation failures detected
- **MCP Dependency:** `RulesMCP.compare_rules(old_id, new_id)`

---

### 4. DocumentationGenomeAgent

- **Purpose:** Compares required vs. submitted clinical documentation across temporal snapshots.
- **Severity Logic:**
  - `medium` — documentation requirements changed
  - `high` — required documents are missing
- **MCP Dependency:** `DocumentationMCP` (optional — gap analysis computed locally)

---

### 5. NetworkGenomeAgent

- **Purpose:** Monitors provider network participation roster changes.
- **Severity Logic:**
  - `medium` — network affiliation changed
  - `critical` — provider now OUT_OF_NETWORK
- **MCP Dependency:** None (self-contained comparison)

---

### 6. MutationDetectionAgent (Lead Synthesiser)

- **Purpose:** Aggregates all 5 gene findings into a weighted MutationReport with a scored severity.
- **Mathematical Model:**

```
M(g₁, g₂) = min(100, Σᵢ wᵢ · Sᵢ)
```

Where:
- `wᵢ` = severity weight: `none=0, low=10, medium=25, high=50, critical=75`
- `Sᵢ` = 1 if gene *i* mutated, 0 otherwise

- **Gemini Enhancement:** Root cause narrative generated via Gemini 2.0 Flash with `GeminiRootCauseAnalysis` structured output schema.
- **Outputs:** `primary_mutation`, `secondary_mutations`, `mutation_score`, `confidence`, `root_cause`, `human_review_required`, `genome_hash`

---

### 7. ImpactAgent

- **Purpose:** Estimates population-scale operational and financial impact from decision mutations.
- **Risk Classification:**
  - Score ≥ 75 → CRITICAL (30% of population base affected)
  - Score ≥ 50 → HIGH (15%)
  - Score ≥ 25 → MEDIUM (5%)
  - Score < 25 → LOW (1%)
- **Outputs:** `risk_level`, `estimated_affected`, `financial_impact`, `operational_impact`

---

### 8. SecurityAgent (Semantic Firewall)

- **Purpose:** Scans all input for prompt injection, PII, and unsafe instructions. Acts as the security perimeter for the entire pipeline.
- **Pattern Libraries:**
  - **10 prompt injection patterns:** "ignore previous instructions", "bypass policy", "override approval", "auto-approve", "force approval", "ignore policy", "approve claim immediately", "instead of the above", "disregard all/previous", "you are now"
  - **7 unsafe instruction patterns:** "delete records", "reveal api key", "send PHI", "export patient data", "disable audit", "drop table", "truncate table"
  - **4 PII detection patterns:** SSN, email, phone, member ID
- **Gemini Enhancement:** Optional semantic threat classification via `GeminiSecurityAssessment` structured output.
- **Output:** `SecurityReport` with `allowed`/`blocked`, findings, and `sanitized_text`

---

### 9. AuditAgent (Compliance Reporter)

- **Purpose:** Generates the final executive audit report with decision lineage and compliance recommendations.
- **Gemini Enhancement:** Executive summary generated via Gemini 2.0 Flash with `GeminiExecutiveSummary` structured output schema.
- **Output:** `AuditReport` with:
  - `executive_summary` — natural language summary for VP-level review
  - `decision_lineage` — chronological decision chain
  - `root_cause` — primary mutation driver
  - `evidence` — supporting data points
  - `recommendation` — suggested remediation
  - `genome_hash` — SHA-256 integrity hash
  - `scenario_fingerprint` — deterministic scenario ID

## Pipeline Execution Order

```
1. SecurityAgent.analyze(input_text)     → SecurityReport (gate)
2. PolicyGenomeAgent.analyze()           ┐
3. ContractGenomeAgent.analyze()         │ Parallel genome
4. RuleGenomeAgent.analyze()             │ analysis
5. DocumentationGenomeAgent.analyze()    │
6. NetworkGenomeAgent.analyze()          ┘
7. MutationDetectionAgent.analyze()      → MutationReport
8. Gemini: generate_root_cause_narrative → Enhanced narrative
9. ImpactAgent.analyze()                 → ImpactAssessment
10. AuditAgent.analyze()                 → AuditReport
11. Gemini: generate_executive_summary   → Enhanced summary
```
