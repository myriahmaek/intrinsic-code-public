# The Proof Boundary

This repository is the front window; the private binder remains the audit
vault. The boundary below (Break the Line doctrine §18) governs EVERY
artifact published here, not just the boards. The public version shows
that a control is Qualified, its First Catch Yield, when it was last
requalified, and its regression history; the private binder holds the
exact injected payloads, gate internals, repair traces, raw model outputs,
and failure packets.

## What the public board MAY show

- **Safety:** escape rate, fail-closed rate, critical-gate qualification status
- **Quality:** First Catch Yield, Total Catch Yield, repair convergence rate, control regression signal, qualification status by control/standard
- **Service:** builds completed, time-to-receipt, release-ready throughput, pipeline success rate
- **Cost:** average cost per build, average cost per repair, cost-per-qualified-battery, model cost trend
- **Maintainability:** requalification burden, flake rate, prompt/schema drift signals, model regression count, controls awaiting requalification
- Coverage by standard/control, catch-yield trends over time, regression history, model auditor skill summaries, representative non-sensitive examples

## What the public board MUST NOT expose

- customer code
- signing secrets
- proprietary prompts
- bypass recipes or sensitive exploit payloads
- internal weaknesses not yet remediated
- raw artifacts that would help an attacker defeat the gates

Anything not clearly on the MAY list stays private until explicitly
cleared. Publication is a founder action.
