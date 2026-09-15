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

Maintain the chronicle as project truth changes. Keep at most one active intent.
Append decisions and journal entries; supersede decisions instead of overwriting
them. Keep `TASK_GRAPH.md` synchronized with `TASKS.md`.

Checkpoint without waiting for a request when the host reports an approaching
session, context, five-hour, or seven-day usage limit. If quota telemetry is not
available, checkpoint after meaningful milestones and before ending the session.

<!-- project-prokron:end -->
