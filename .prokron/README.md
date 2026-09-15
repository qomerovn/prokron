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
`ADOPTION.json` preserves its uncertainty, provenance, and human confirmation.

Current implementation boundary: `../docs/deterministic-harness.md`, governed by
ADR-006 and ADR-007. The agent supplies semantic state; Core validates and
persists it. The retired heuristic engine remains recorded only in Git history.
