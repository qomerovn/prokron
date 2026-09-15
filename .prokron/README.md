# Project Prokron

Project Prokron is building a repository-native continuity protocol for human and AI software work.

Authority:

- `TASKS.md`: mutable canonical coordination state.
- `INTENTS.md`: mutable live execution state.
- `DECISIONS.md`: append-only historical authority.
- `JOURNAL.md`: append-only execution history.
- `TASK_GRAPH.md` and `STATE.md`: generated projections; do not edit manually.

If `BASELINE.md` exists, it records the approved adoption boundary and current
truth that could not be represented safely as tasks, decisions, or active intent.
`ADOPTION_REPORT.md` and `SOURCE_MAP.md` preserve its uncertainty and provenance.
`INTERVIEW.md` records coverage assessments, evidence-driven prompts, and human
confirmations used to establish that baseline.

Current implementation boundary: `../docs/deterministic-harness.md`, governed by
ADR-006. The agent supplies semantic state; Core validates and persists it.
T-HARNESS-01 is complete. Prior heuristic dogfood T-V02-05 is deferred to optional
fallback; its last active intent is preserved in JOURNAL.md.
