# Contributing to DecisionDNA AI

Thank you for your interest in contributing to DecisionDNA AI! This document provides guidelines for contributing to the project.

## Getting Started

### Prerequisites

- Python 3.9+
- pip or uv package manager
- Git

### Setup

```bash
git clone https://github.com/sharath559/decision-dna-ai.git
cd decision-dna-ai
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### Running Locally

```bash
streamlit run app.py
```

### Running Tests

```bash
pytest tests/ -v --tb=short
```

## Project Structure

| Directory | Purpose |
|-----------|---------|
| `src/agents/` | AI agent implementations (9 agents + Gemini + ADK) |
| `src/models/` | Pydantic v2 data models |
| `src/services/` | Orchestration and business logic |
| `src/tools/` | MCP tool servers |
| `src/data/` | Synthetic healthcare data |
| `tests/` | Test suite |
| `docs/` | Extended documentation |

## Coding Standards

- **Python style:** Follow PEP 8, enforced by `ruff`
- **Type hints:** Required on all function signatures
- **Docstrings:** Module-level and function-level, Google style
- **Models:** All agent I/O must use Pydantic v2 `BaseModel` subclasses
- **Testing:** All new agents must include corresponding test cases

## Adding a New Agent

1. Create `src/agents/your_agent.py` inheriting from `BaseAgent`
2. Define input/output Pydantic models in `decision_models.py`
3. (Optional) Create MCP tool in `src/tools/your_mcp.py`
4. Register in `mutation_engine.py` pipeline
5. Add ADK agent definition in `adk_agents.py`
6. Add tests in `tests/`

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes with tests
4. Run `pytest tests/ -v` to verify
5. Submit a pull request with a clear description

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
