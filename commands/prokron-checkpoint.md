# /prokron-checkpoint

Prepare the chronicle for another person or agent:

1. Update task status, validation strength, acceptance evidence, and governing ADRs.
2. Synchronize `TASK_GRAPH.md` and `STATE.md`.
3. Update `INTENT.md` with the exact stopping point and next action, or clear it
   when the task is complete.
4. Append a `JOURNAL.md` entry containing work done, validation, learning,
   unfinished work, and the exact next action.

Run this automatically, early enough to complete it, before a handoff,
interruption, compaction, or any known or estimated agent or host context, token,
time, session, rate, or quota limit, including five-hour and seven-day windows.
If the host exposes no meter, run it after meaningful milestones, before a
long-running step, and before ending the session.
