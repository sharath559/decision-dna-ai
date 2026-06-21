# DecisionDNA AI — Demo Capture Checklist

## Screenshots to Capture

1. **Dashboard tab** — shows all three cases, mutation scores bar chart, summary table
2. **Case Explorer** — expanded view of PA-MRI-1001 with metrics
3. **Decision DNA** — side-by-side genome comparison (old vs new)
4. **Mutation Analysis** — mutation score, confidence, root cause, radar chart
5. **Timeline** — temporal event timeline with color-coded categories
6. **Evidence** — supporting vs contradicting evidence, missing documents
7. **Security** — clean scan + malicious input scan result
8. **Audit Report** — executive summary, decision lineage, originality metadata

## Video Sections (5 minutes)

| Time | Section | What to Show |
|------|---------|-------------|
| 0:00 | Problem | Title slide, problem statement |
| 0:45 | Why agents | Architecture diagram |
| 1:15 | Architecture | Dashboard tab |
| 2:00 | Demo Case 1 | Decision DNA + Mutation Analysis for PA-MRI-1001 |
| 3:15 | Other Cases | Quick CLM-5502 and NET-P680 views |
| 4:00 | Security | Security scanner demo |
| 4:40 | Closing | Audit report + project signature |

## What to Show Judges

- [ ] App running locally at `http://localhost:8501`
- [ ] All eight tabs functional
- [ ] Three demo cases producing different mutation patterns
- [ ] Security scanner detecting prompt injection and PII
- [ ] Audit report with originality metadata
- [ ] Radar chart showing mutation severity distribution
- [ ] Timeline view with temporal events
- [ ] Terminal showing `streamlit run app.py` running

## How to Prove Local Execution

1. Show terminal with `streamlit run app.py` command
2. Show browser URL bar with `localhost:8501`
3. Show sidebar with build mode and timestamp
4. Show audit report with scenario fingerprint and genome hash
5. Interact with the security scanner in real-time

## How to Show Project Signature Without Revealing Secrets

1. Run `python scripts/generate_project_signature.py`
2. Show the terminal output (it prints the signature)
3. Do NOT show `.env` contents
4. The signature includes your name/handle but not secrets
5. The `.local/project_signature.json` file is gitignored

## Private Demo Mode

For personalized video evidence:
1. Copy `.env.example` to `.env`
2. Set `PRIVATE_DEMO_MODE=true`
3. Set your custom `SCENARIO_SEED`
4. Regenerate signature: `python scripts/generate_project_signature.py`
5. Restart Streamlit — sidebar shows `PRIVATE` build mode
6. Audit reports will show unique fingerprints
