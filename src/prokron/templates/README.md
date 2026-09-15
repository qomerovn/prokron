# Project Prokron

This repository uses `.prokron/` as persistent project coordination state.

Authority:

- `TASKS.md`: mutable canonical coordination state.
- `INTENTS.md`: mutable live execution state.
- `DECISIONS.md`: append-only historical authority.
- `JOURNAL.md`: append-only execution history.
- `TASK_GRAPH.md` and `STATE.md`: generated projections; do not edit manually.

Before substantial work, run `prokron status`, then `prokron context <task>`.
Checkpoint before ending or switching sessions.
