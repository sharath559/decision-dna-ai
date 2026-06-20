# DecisionDNA AI — Architecture

## System Architecture

```
┌───────────────────────────────────────────────────────────────────┐
│                        Streamlit UI (app.py)                       │
│  Dashboard │ Case Explorer │ DNA View │ Mutation │ Timeline │ ... │
└──────────────────────────────┬────────────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Mutation Engine    │
                    │   (Orchestrator)     │
                    └──────────┬──────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
    ┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐
    │ Genome      │    │ Mutation    │    │ Impact /    │
    │ Agents ×5   │    │ Detection   │    │ Security /  │
    │ (Policy,    │    │ Agent       │    │ Audit       │
    │ Contract,   │    │             │    │ Agents      │
    │ Rule, Doc,  │    │             │    │             │
    │ Network)    │    │             │    │             │
    └──────┬──────┘    └─────────────┘    └──────┬──────┘
           │                                      │
    ┌──────▼──────────────────────────────────────▼──────┐
    │              MCP-Style Tool Layer                    │
    │  PolicyMCP │ ContractMCP │ RulesMCP │ DocMCP │ Audit │
    └──────────────────────────┬──────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Local JSON Data    │
                    │   (Synthetic Only)   │
                    └─────────────────────┘
```

## Data Flow

1. User selects a case in the Streamlit UI
2. Mutation Engine loads the genome pair (old + new snapshots)
3. Five genome agents analyze their respective genes
4. MutationDetectionAgent aggregates findings
5. ImpactAgent estimates business impact
6. SecurityAgent scans the input
7. AuditAgent generates the executive report
8. Results are displayed across all eight UI tabs

## Agent Responsibilities

| Agent | Input | Output | MCP Tool |
|-------|-------|--------|----------|
| PolicyGenomeAgent | Old/new genome | GeneMutation | PolicyMCP |
| ContractGenomeAgent | Old/new genome | GeneMutation | ContractMCP |
| RuleGenomeAgent | Old/new genome | GeneMutation | RulesMCP |
| DocumentationGenomeAgent | Old/new genome | GeneMutation | DocumentationMCP |
| NetworkGenomeAgent | Old/new genome | GeneMutation | — |
| MutationDetectionAgent | Gene mutations | MutationReport | — |
| ImpactAgent | MutationReport | ImpactAssessment | — |
| SecurityAgent | Input text | SecurityReport | — |
| AuditAgent | All results | AuditReport | AuditMCP |
