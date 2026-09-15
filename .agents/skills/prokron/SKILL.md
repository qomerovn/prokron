---
name: prokron
description: Maintain or resume a repository's Prokron project chronicle. Use for Prokron init, work, decision, checkpoint, and resume requests.
---

# Prokron

Read `.prokron/README.md`. Interpret the first argument as `init`, `work`,
`decide`, `checkpoint`, or `resume`, then follow the matching
`commands/prokron-<argument>.md` workflow. For `work`, pass remaining arguments
through as the requested task.

Maintain the chronicle during work. Checkpoint automatically before a handoff,
context compaction, session ending, or host warning that the five-hour or
seven-day usage limit is near.
