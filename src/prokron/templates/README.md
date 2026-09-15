# Project Prokron

This repository uses `.prokron/` as persistent project coordination state.

Authority:

- `TASKS.md`: mutable canonical coordination state.
- `INTENTS.md`: mutable live execution state.
- `DECISIONS.md`: append-only historical authority.
- `JOURNAL.md`: append-only execution history.
- `TASK_GRAPH.md` and `STATE.md`: generated projections; do not edit manually.

If `ADOPTION.json` exists, it is the immutable reviewed adoption snapshot,
including statement provenance, uncertainty and the human confirmation digest.
`BASELINE.md` is its readable snapshot. Current operational Markdown takes
precedence over adoption-time tasks, decisions and intent. `CHECKPOINT.json`
records the Git HEAD, branch and working-tree fingerprint at the last checkpoint.

Before substantial work, run `prokron resume`, then `prokron context <task>`
for selective detail. If state is stale, follow `/prokron-sync` in the agent
adapter: evaluate the changes and record an explicit checkpoint.
Checkpoint before ending or switching sessions.
