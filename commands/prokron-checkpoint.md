# /prokron-checkpoint

Prepare the chronicle for another person or agent:

1. Update task status, validation strength, acceptance evidence, and governing ADRs.
2. Synchronize `TASK_GRAPH.md` and `STATE.md`.
3. Update `INTENT.md` with the exact stopping point and next action, or clear it
   when the task is complete.
4. Append a `JOURNAL.md` entry containing work done, validation, learning,
   unfinished work, and the exact next action.

Run this automatically before a handoff, interruption, context compaction, or
host warning that the five-hour or seven-day usage limit is near.
