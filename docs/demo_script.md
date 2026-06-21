# DecisionDNA AI — Demo Video Script (5 minutes)

## 0:00–0:45 — The Problem

*[Show title slide: "DecisionDNA AI — Temporal Decision Forensics"]*

"Every day, healthcare payer organizations make thousands of decisions — prior authorizations, claims, provider network enrollments. And sometimes, a decision that was approved last month gets denied this month. A claim that was paid in February gets rejected in June. A provider that was in-network in March is suddenly terminated.

When this happens, the question everyone asks is: *why did this change?*

Today, answering that question requires hours of manual cross-referencing across policy systems, contract databases, rule engines, and document management systems. DecisionDNA AI solves this."

## 0:45–1:15 — Why Agents

*[Show architecture diagram]*

"DecisionDNA AI uses a multi-agent system because each factor in a healthcare decision requires domain-specific reasoning. We have nine specialized agents — one for each aspect of a decision's DNA: policy, contract, rules, documentation, network, plus agents for mutation detection, impact assessment, security, and audit reporting.

Each agent uses MCP-style tools to access external data — in this demo, local JSON files that simulate real healthcare systems."

## 1:15–2:00 — Architecture Walkthrough

*[Show Streamlit Dashboard tab]*

"Here's the dashboard. We have three demo cases showing decision drift:
- An MRI prior authorization that changed from Approved to Denied
- A claim that changed from Paid to Rejected
- A provider network enrollment that changed from Active to Terminated

Each case has been analyzed by our nine-agent pipeline. You can see mutation scores, risk levels, and which cases require human review."

## 2:00–3:15 — Demo: MRI Prior Authorization

*[Click on PA-MRI-1001, show Decision DNA tab]*

"Let's look at the MRI case. On the left, we see the Decision Genome from January — the MRI was approved under policy MRI-MED-NEC-v1, all required documents were submitted, and the provider was in-network.

On the right, the June snapshot — now under policy v2, the decision is Denied. The new policy requires a specialist review, which wasn't submitted."

*[Switch to Mutation Analysis tab]*

"The Mutation Analysis shows that the primary mutation is in the Policy Gene — the policy version changed and added a new clause. The secondary mutation is in the Documentation Gene — the newly required specialist review was not submitted.

The mutation score is 75 out of 100, with high confidence. The recommendation is to request the specialist review and route to a clinical reviewer."

*[Show radar chart]*

"The radar chart shows mutation severity across all five genes — you can see Policy and Documentation are elevated while Contract, Rule, and Network are stable."

## 3:15–4:00 — Mutation Analysis for Other Cases

*[Quick switch to CLM-5502]*

"For the claim case, we see a different pattern — the Contract Gene is the primary mutation because the provider was terminated from the network, and the Rule Gene mutated to require a referral ID. Multiple genes contributed to this decision drift."

*[Quick switch to NET-P680]*

"The provider network case shows a Contract Gene mutation as primary — the network was restructured and the provider didn't meet new tier requirements. The continuity of care flag is raised for human review."

## 4:00–4:40 — Security, MCP Tools, and Agent Skills

*[Switch to Security tab]*

"DecisionDNA AI includes a built-in SecurityAgent that scans for prompt injection, PII patterns, and unsafe instructions. Let me demonstrate..."

*[Type malicious input in the security scanner]*

"The scanner immediately detects the prompt injection attempt and PII pattern, blocks the input, and shows redacted output."

*[Briefly show Audit Report tab]*

"Every analysis produces a full executive audit report with decision lineage, root cause, impact assessment, and originality metadata including a scenario fingerprint and genome hash."

## 4:40–5:00 — Closing

"DecisionDNA AI demonstrates how multi-agent systems can solve real enterprise healthcare problems — not by building a chatbot, but by building a forensic analysis platform that traces the DNA of healthcare decisions over time.

Thank you for watching. The full source code, synthetic data, and documentation are available on GitHub."

*[Show final slide with GitHub URL and project signature]*
