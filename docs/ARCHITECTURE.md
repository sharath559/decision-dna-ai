# Architecture — DecisionDNA AI

> Multi-Agent Temporal Decision Forensics Platform for Healthcare Networks

## System Architecture Overview

```mermaid
graph TB
    subgraph UserLayer["🖥️ Presentation Layer"]
        UI["Streamlit Dashboard<br/>(app.py — 1828 LOC)"]
        API["Future: REST API<br/>(FastAPI Gateway)"]
    end

    subgraph OrchestratorLayer["🔄 Orchestration Layer"]
        ME["MutationEngine<br/>(mutation_engine.py)"]
        GB["GenomeBuilder<br/>(genome_builder.py)"]
        TS["TimelineService<br/>(timeline_service.py)"]
    end

    subgraph AgentLayer["🤖 Agent Layer (9 Agents)"]
        subgraph GenomeAgents["Genome Analysis Agents"]
            PA["PolicyGenomeAgent"]
            CA["ContractGenomeAgent"]
            RA["RuleGenomeAgent"]
            DA["DocumentationGenomeAgent"]
            NA["NetworkGenomeAgent"]
        end
        subgraph SynthesisAgents["Synthesis Agents"]
            MDA["MutationDetectionAgent"]
            IA["ImpactAgent"]
            AA["AuditAgent"]
        end
        SA["SecurityAgent<br/>🛡️ Semantic Firewall"]
    end

    subgraph GeminiLayer["✨ Gemini 2.0 Flash Layer"]
        RCA["Root Cause Narrative<br/>(structured output)"]
        ESG["Executive Summary<br/>(structured output)"]
        STC["Security Classification<br/>(structured output)"]
    end

    subgraph ToolLayer["🔧 MCP Tool Layer"]
        PMC["PolicyMCP"]
        CMC["ContractMCP"]
        RMC["RulesMCP"]
        DMC["DocumentationMCP"]
        AMC["AuditMCP"]
    end

    subgraph DataLayer["💾 Data Layer"]
        PS["policy_versions.json"]
        CS["contract_versions.json"]
        RS["rule_versions.json"]
        DS["documentation_requirements.json"]
        SS["decision_snapshots.json"]
        SC["sample_cases.json"]
    end

    subgraph ModelLayer["📐 Schema Layer (Pydantic v2)"]
        PY["14 Pydantic Models<br/>(decision_models.py)"]
    end

    UI --> ME
    API -.-> ME
    ME --> GB
    ME --> SA
    ME --> PA & CA & RA & DA & NA
    ME --> MDA --> IA --> AA

    MDA -.-> RCA
    AA -.-> ESG
    SA -.-> STC

    PA --> PMC --> PS
    CA --> CMC --> CS
    RA --> RMC --> RS
    DA --> DMC --> DS
    AA --> AMC

    GB --> SS
    TS --> SC

    PA & CA & RA & DA & NA & MDA & IA & AA & SA --> PY
```

## ADK Agent Hierarchy

```mermaid
graph TD
    ROOT["DecisionDNA_Orchestrator<br/>(ADK Agent)"]
    ROOT --> FP["ForensicPipeline<br/>(SequentialAgent)"]
    
    FP --> SEC["SecurityAgent<br/>(Agent)"]
    FP --> GAH["GenomeAnalysisHub<br/>(ParallelAgent)"]
    FP --> MS["MutationSynthesizer<br/>(Agent)"]
    
    GAH --> P["PolicyGenomeAgent<br/>(Agent)"]
    GAH --> C["ContractGenomeAgent<br/>(Agent)"]
    GAH --> R["RuleGenomeAgent<br/>(Agent)"]
    
    P --> T1["compare_policy_versions()"]
    C --> T2["compare_provider_contracts()"]
    R --> T3["compare_business_rules()"]
    SEC --> T4["scan_security_threats()"]
    MS --> T5["run_mutation_analysis()"]
```

## Component Dependency Graph

```mermaid
graph LR
    subgraph External["External Dependencies"]
        ST["streamlit ≥1.30"]
        PD["pandas ≥2.0"]
        PL["plotly ≥5.18"]
        PYD["pydantic ≥2.5"]
        DE["python-dotenv ≥1.0"]
        GG["google-genai ≥1.0"]
        GA["google-adk ≥1.0"]
    end

    subgraph Core["Core Modules"]
        DM["decision_models.py<br/>(274 LOC, 14 models)"]
        BA["base_agent.py<br/>(47 LOC)"]
        GI["gemini_integration.py<br/>(Gemini 2.0 Flash)"]
        ADK["adk_agents.py<br/>(ADK Agent defs)"]
    end

    subgraph Agents["Agent Modules (9 total)"]
        PGA["PolicyGenomeAgent"]
        CGA["ContractGenomeAgent"]
        RGA["RuleGenomeAgent"]
        DGA["DocumentationGenomeAgent"]
        NGA["NetworkGenomeAgent"]
        MDA2["MutationDetectionAgent"]
        IM["ImpactAgent"]
        SEC2["SecurityAgent"]
        AUD["AuditAgent"]
    end

    DM --> PYD
    BA --> DM
    GI --> GG
    ADK --> GA
    PGA & CGA & RGA & DGA & NGA & MDA2 & IM & SEC2 & AUD --> BA
```

## Data Flow Sequence

```mermaid
sequenceDiagram
    participant U as User/UI
    participant ME as MutationEngine
    participant SA as SecurityAgent
    participant GB as GenomeBuilder
    participant PA as PolicyGenomeAgent
    participant CA as ContractGenomeAgent
    participant RA as RuleGenomeAgent
    participant DA as DocGenomeAgent
    participant NA as NetworkGenomeAgent
    participant MDA as MutationDetectionAgent
    participant GM as Gemini 2.0 Flash
    participant IA as ImpactAgent
    participant AA as AuditAgent
    participant MCP as MCP Tools

    U->>ME: run_full_analysis(case_id)
    
    rect rgb(15, 23, 42)
        Note over ME,GB: Phase 1: Genome Hydration
        ME->>GB: get_genome_pair(case_id)
        GB->>MCP: Load decision_snapshots.json
        MCP-->>GB: Raw snapshot data
        GB->>GB: DecisionGenome.model_validate()
        GB-->>ME: (old_genome, new_genome)
    end

    rect rgb(88, 28, 135)
        Note over ME,NA: Phase 2: Gene Mutation Detection
        ME->>PA: analyze(old_genome, new_genome)
        PA->>MCP: PolicyMCP.compare_policy_versions()
        MCP-->>PA: clause_diff
        PA-->>ME: GeneMutation(policy)

        ME->>CA: analyze(old_genome, new_genome)
        CA->>MCP: ContractMCP.compare_contracts()
        MCP-->>CA: contract_diff
        CA-->>ME: GeneMutation(contract)

        ME->>RA: analyze(old_genome, new_genome)
        RA->>MCP: RulesMCP.compare_rules()
        MCP-->>RA: rule_diff
        RA-->>ME: GeneMutation(rule)

        ME->>DA: analyze(old_genome, new_genome)
        DA-->>ME: GeneMutation(documentation)

        ME->>NA: analyze(old_genome, new_genome)
        NA-->>ME: GeneMutation(network)
    end

    rect rgb(124, 45, 18)
        Note over ME,AA: Phase 3: Forensic Synthesis
        ME->>MDA: analyze(old, new, gene_mutations)
        MDA->>MDA: Calculate weighted mutation score
        MDA->>MDA: Determine primary/secondary mutations
        MDA->>MDA: compute_genome_hash()
        MDA-->>ME: MutationReport

        ME->>GM: generate_root_cause_narrative()
        GM-->>ME: GeminiRootCauseAnalysis (structured)

        ME->>IA: analyze(mutation_report)
        IA->>IA: Estimate population impact
        IA->>IA: Calculate financial exposure
        IA-->>ME: ImpactAssessment

        ME->>SA: analyze(input_text)
        SA->>SA: Regex: prompt injection + PII scan
        SA-->>ME: SecurityReport

        ME->>AA: analyze(mutation, impact, security)
        AA->>MCP: AuditMCP.store_audit_record()
        AA-->>ME: AuditReport

        ME->>GM: generate_executive_summary()
        GM-->>ME: GeminiExecutiveSummary (structured)
    end

    ME-->>U: Complete Analysis Result
```

## Security Agent Scanning Sequence

```mermaid
sequenceDiagram
    participant Input as Raw Input Text
    participant SA as SecurityAgent
    participant GM as Gemini 2.0 Flash
    participant PI as Prompt Injection Scanner
    participant UI as Unsafe Instruction Scanner
    participant PII as PII Pattern Scanner
    participant Out as SecurityReport

    Input->>SA: analyze(input_text)
    
    SA->>PI: Scan 10 injection patterns
    alt Injection detected
        PI-->>SA: CRITICAL finding
    else Clean
        PI-->>SA: No findings
    end

    SA->>UI: Scan 7 unsafe patterns
    alt Unsafe instruction
        UI-->>SA: CRITICAL finding
    else Clean
        UI-->>SA: No findings
    end

    SA->>PII: Scan 4 PII patterns
    alt PII detected
        PII-->>SA: WARNING finding + redact
    else Clean
        PII-->>SA: No findings
    end

    SA->>GM: classify_security_threat() (optional)
    GM-->>SA: GeminiSecurityAssessment (structured)

    SA->>SA: allowed = no CRITICAL findings?
    SA->>Out: SecurityReport(allowed, findings, sanitized_text)
```

## Directory Structure

```
decision-dna-ai/
├── app.py                          # Streamlit UI (1828 LOC)
├── requirements.txt                # Dependencies (incl. google-genai, google-adk)
├── Dockerfile                      # Container build
├── pyproject.toml                  # Project config + linting
├── README.md                       # Comprehensive documentation
├── SECURITY.md                     # Threat model & security policy
├── CONTRIBUTING.md                 # Contribution guide
├── LICENSE                         # MIT License
├── .env.example                    # Environment template
├── docs/                           # Extended documentation
│   ├── ARCHITECTURE.md             # This file
│   ├── AGENTS.md                   # Agent registry & design
│   ├── EVALUATION.md               # Eval framework
│   ├── DEPLOYMENT.md               # Deployment guide
│   └── PRODUCTION.md               # Production readiness
├── src/
│   ├── agents/                     # 9 AI agents + Gemini + ADK
│   │   ├── base_agent.py           # ABC for all agents
│   │   ├── gemini_integration.py   # Gemini 2.0 Flash (google-genai)
│   │   ├── adk_agents.py           # ADK agent definitions
│   │   ├── policy_genome_agent.py
│   │   ├── contract_genome_agent.py
│   │   ├── rule_genome_agent.py
│   │   ├── documentation_genome_agent.py
│   │   ├── network_genome_agent.py
│   │   ├── mutation_detection_agent.py
│   │   ├── impact_agent.py
│   │   ├── security_agent.py
│   │   └── audit_agent.py
│   ├── models/
│   │   └── decision_models.py      # 14 Pydantic v2 models
│   ├── services/
│   │   ├── mutation_engine.py      # Pipeline orchestrator + Gemini
│   │   ├── genome_builder.py       # Genome hydration
│   │   └── timeline_service.py     # Temporal event builder
│   ├── tools/                      # 5 MCP tool servers
│   │   ├── policy_mcp.py
│   │   ├── contract_mcp.py
│   │   ├── rules_mcp.py
│   │   ├── documentation_mcp.py
│   │   └── audit_mcp.py
│   ├── data/                       # Synthetic healthcare data
│   └── utils/
│       └── formatting.py           # UI formatting helpers
├── tests/
│   └── test_genome_forensics.py    # 4 test classes
├── scripts/
│   └── generate_project_signature.py
└── .github/workflows/
    └── deploy.yml                  # CI/CD pipeline
```
