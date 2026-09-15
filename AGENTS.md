<!-- project-prokron:start -->

# Prokron

This repository uses `.prokron/` as its project chronicle. Read
`.prokron/README.md` before substantial work and follow its read order.

Recognize these workflows:

- `/prokron-init [new|existing]` → `commands/prokron-init.md`
- `/prokron-work [task]` → `commands/prokron-work.md`
- `/prokron-decide` → `commands/prokron-decide.md`
- `/prokron-checkpoint` → `commands/prokron-checkpoint.md`
- `/prokron-resume` → `commands/prokron-resume.md`

Maintain the chronicle automatically; do not wait for a Prokron command. Before
starting newly requested work, create or claim its task and set the single
`INTENT.md` entry. When a material project choice is made, accepted, or acted
on, append its ADR immediately and link affected tasks. Supersede decisions
instead of overwriting them. Keep `TASK_GRAPH.md` and `STATE.md` synchronized.

Checkpoint early enough to finish writing whenever the agent or host approaches
any context, token, time, session, rate, or quota limit, including five-hour and
seven-day windows, or before compaction or handoff. If no meter is exposed,
checkpoint after each meaningful milestone, before a long-running step, and
before ending. Preserve the active task, exact stopping point, unfinished work,
and next action.

<!-- project-prokron:end -->
