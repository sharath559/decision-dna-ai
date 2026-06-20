# DecisionDNA AI — Kaggle Writeup

## Title
**DecisionDNA AI: Temporal Decision Forensics for Healthcare Networks**

## Subtitle
Reconstructing why healthcare decisions change over time through multi-agent decision genome analysis.

## Track
**Agents for Business**

## Problem

Healthcare payer organizations process millions of decisions annually — prior authorizations, claims, provider network enrollments. When a decision changes from APPROVED to DENIED, PAID to REJECTED, or ACTIVE to TERMINATED, stakeholders need to understand *why*.

Today, answering "why did this decision change?" requires manual cross-referencing across:
- Policy management systems
- Provider contract databases
- Business rule engines
- Document management systems
- Network directories

This is slow, error-prone, and creates compliance risk.

## Solution

DecisionDNA AI models every healthcare decision as a **Decision Genome** — a structured fingerprint of all factors that influenced the decision at a point in time. When a decision changes, the system detects which "genes" mutated and explains the root cause.

**Decision Genes:**
- **Policy Gene** — which policy version governs the decision
- **Contract Gene** — provider contract and network enrollment state
- **Rule Gene** — business rule version and validation checks
- **Documentation Gene** — required vs. submitted evidence
- **Network Gene** — provider network participation status
- **Evidence Gene** — supporting and contradicting clinical/administrative evidence

## Architecture

Nine specialized agents collaborate through a multi-agent pipeline:

1. **PolicyGenomeAgent** — compares policy versions, detects clause changes
2. **ContractGenomeAgent** — compares contracts, detects network status changes
3. **RuleGenomeAgent** — compares rule versions, detects validation changes
4. **DocumentationGenomeAgent** — computes documentation gaps
5. **NetworkGenomeAgent** — detects network participation changes
6. **MutationDetectionAgent** — aggregates findings, ranks mutations, scores confidence
7. **ImpactAgent** — estimates business impact (population, systems, financial)
8. **SecurityAgent** — scans for prompt injection, PII, unsafe instructions
9. **AuditAgent** — generates executive audit report with full lineage

## MCP Tools

Five MCP-style tools simulate external system access:
- PolicyMCP, ContractMCP, RulesMCP, DocumentationMCP, AuditMCP

Each tool logs invocations for audit traceability.

## Security

Built-in security scanning:
- Prompt injection detection (10+ patterns)
- PII pattern detection (SSN, email, phone, member ID)
- Unsafe instruction detection (delete, reveal, disable)
- Input sanitization with redaction

## Demo

Three synthetic healthcare cases demonstrate decision drift:
1. **MRI Prior Auth:** APPROVED → DENIED (policy + documentation mutation)
2. **Claim Payment:** PAID → REJECTED (contract + rule + network mutation)
3. **Provider Network:** ACTIVE → TERMINATED (contract mutation)

## Impact

DecisionDNA AI could help healthcare organizations:
- Reduce time to answer "why did this change?" from hours to seconds
- Improve compliance by documenting decision lineage automatically
- Reduce appeal rates by identifying addressable documentation gaps
- Detect systemic decision drift across populations

## Limitations

- Synthetic data only — no real healthcare system connections
- Mock MCP tools — no real API calls
- Heuristic impact estimates — not actuarial
- Pattern-based security — not production-grade

## Future Scope

- Real MCP connections to payer systems
- Gemini-powered natural language explanations
- Real-time decision monitoring
- FHIR clinical data integration
- Multi-tenant deployment

---

*Built by Sharath Chandra · Synthetic Demo Only · No PHI*
