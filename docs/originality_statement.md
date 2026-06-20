# DecisionDNA AI — Originality Statement

## Declaration

This project, **DecisionDNA AI**, is original work created for the Kaggle / Google AI Agents Capstone.

## Key Facts

1. **Synthetic data only** — All healthcare data in this project is fabricated. No real Protected Health Information (PHI), employer data, or proprietary healthcare data is included.

2. **Original concept** — The core idea is **temporal decision forensics** using a **decision genome metaphor**. Every healthcare decision is modeled as a DNA fingerprint with specific genes (Policy, Contract, Rule, Documentation, Network, Evidence). When a decision changes, the system detects which genes "mutated" and explains the root cause.

3. **Multi-agent implementation** — The project uses nine specialized agents, each with domain-specific reasoning, collaborating through a structured pipeline. This is not a wrapper around a single LLM call.

4. **MCP-style tools** — Five mock MCP tools simulate external healthcare system access with structured inputs, outputs, and audit logging.

5. **Security features** — Built-in prompt injection detection, PII scanning, and unsafe instruction detection.

6. **AI-assisted development** — AI coding assistance (Antigravity) was used to accelerate development. All generated code was reviewed, customized, and integrated by the project author. The conceptual design and domain expertise are original.

7. **No real secrets** — The `.env` file is gitignored. The `.env.example` template contains only configuration knobs, not secrets.

8. **Reproducible** — The demo runs fully with `pip install -r requirements.txt && streamlit run app.py`. No API keys, paid services, or external dependencies are required.

## Contact

- **Author:** Sharath Chandra
- **Handle:** @yakarasharath4
- **Project:** DecisionDNA AI
- **Track:** Agents for Business

## Date

Created: June 2026
