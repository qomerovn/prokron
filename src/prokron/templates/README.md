# Project Prokron

This repository uses `.prokron/` as persistent project coordination state.

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

Before substantial work, run `prokron status`, then `prokron context <task>`.
Checkpoint before ending or switching sessions.
