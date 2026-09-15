# Prokron project chronicle

This directory is shared project memory for people and agents. The product
specification describes what was intended; this chronicle records what is true
now. It should explain the project before anyone reads implementation code.

## Read order

1. `STATE.md` for the current position.
2. `TASK_GRAPH.md` for in-flight, ready, and blocked work.
3. The selected entry in `TASKS.md`.
4. Its governing entries in `DECISIONS.md`.
5. `INTENT.md` for the single task in progress.
6. Recent `JOURNAL.md` entries when handoff detail is needed.
7. Read specifications or code only when the selected task requires them.

## Authority

- `TASKS.md` is the work board: status, validation, ownership, dependencies,
  acceptance, evidence, and governing ADRs.
- `INTENT.md` is overwritten and holds zero or one current task.
- `DECISIONS.md` and `JOURNAL.md` are append-only history.
- `STATE.md` and `TASK_GRAPH.md` are current views. Synchronize them whenever
  tasks or intent change; they never override their sources.

## Working rules

1. Work on one task at a time. Mark it `WIP`, record owner and claim date, and
   put the exact execution point in `INTENT.md`.
2. Hard dependencies come from `TASKS.md`. Label suggested ordering as a
   suggestion; do not silently turn it into a dependency.
3. Mark a task `DONE` only when its acceptance condition is met and its evidence
   is recorded. Keep completion status separate from validation strength:
   `UNTESTED`, `SYNTHETIC`, `AI_REVIEWED`, or `HUMAN_VERIFIED`.
4. Only a named human may record `HUMAN_VERIFIED`.
5. When a decision changes, append a new ADR that supersedes the earlier ADR.
   Preserve the old entry.
6. Append a journal entry before leaving work mid-air. `Left mid-air` and
   `Next` must be explicit even when the answer is “nothing.”
7. Keep entries concise. Put product rules in the specification and durable
   implementation choices in ADRs, not in the session diary.

## Checkpoint trigger

Update the chronicle while working. Before a handoff, interruption, context
compaction, or host warning that a five-hour or seven-day usage limit is near:

1. update task status, validation, evidence, and governing ADRs;
2. synchronize the task graph and state;
3. update or clear the single intent;
4. append a journal entry with the exact next action.

If the host cannot report quota usage, checkpoint after meaningful milestones
and before ending. Do not wait until the last message.

## Entry modes

- **New repository:** derive initial tasks and the task graph from the product
  specification with the developer. Record material decisions as ADRs.
- **Existing repository:** start with an empty chronicle and record from the
  current session onward. Do not reconstruct historical tasks or decisions.
