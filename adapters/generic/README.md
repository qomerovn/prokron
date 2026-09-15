# Project Prokron — Generic adapter

## /prokron-adopt

1. Run `prokron adopt prepare` and `prokron adopt schema` from the repo root.
2. Inspect relevant repository files with your native tools. You own semantic
   interpretation: project purpose, current state, authority by scope,
   architecture, constraints, active work, tasks/dependencies, blockers,
   validation evidence, governing decisions and exact next action.
3. Answer from evidence where sufficient. Record uncertainty explicitly. Ask
   the human only material unresolved questions; Core does not generate questions.
4. Build a candidate matching the schema. Copy prepare's `checkpoint`. Use
   OBSERVED / INFERRED / CONFIRMED with sources and confirmation metadata where
   applicable. Empty task/decision/intent arrays and unknowns are legitimate;
   do not manufacture tasks or reconstruct history to fill a schema.
5. Save the candidate outside the repository or under `.prokron-candidate/`.
   Run `prokron adopt ingest <candidate>`. Show the human the actual staged
   candidate, its assumptions, unknowns and next action. Corrections require
   re-ingest and a new review digest.
6. After explicit human approval, run `prokron adopt confirm --by <human>
   --digest <reviewed-digest>`, then `prokron adopt apply`. Never claim approval
   on the human's behalf. Run `prokron doctor` and `prokron resume`.

## /prokron-resume

Run `prokron resume`. Load current objective/work, tasks and dependencies,
blockers, decisions, constraints, validation state, unknowns and exact next
step from the returned canonical pack. The adoption baseline is a snapshot;
current TASKS.md, INTENTS.md, DECISIONS.md and JOURNAL.md govern operational work.
Use `prokron context <task>` and selective verification only when needed.
Do not rediscover the entire repository or use chat history as authority.
If a stale/blocked condition is returned, resolve it before executing the action.

## /prokron-sync

This is an agent workflow; there is no `prokron sync` mutation command yet.
Compare `prokron adopt prepare` facts with `.prokron/CHECKPOINT.json`. Inspect
Git changes and affected sources using native tools. You interpret the delta.
Update affected canonical tasks, decisions and intent using the existing field
vocabulary; preserve decision and journal lineage. Ask the human for material
uncertainty. Run `prokron status`, then checkpoint one active intent with the
explicit stopping point, validation and exact next action, then `prokron doctor`.
A checkpoint refreshes Git freshness and does not rewrite the adoption baseline.
If no active intent exists, record an appropriate task or maintenance intent
before checkpointing. Broad baseline revisions await structured sync support;
do not edit ADOPTION.json or fabricate a new confirmation digest.

## Work and checkpoint

Start eligible work with `prokron start <task> --owner <owner>`.
Before ending or switching sessions, run:

```text
prokron checkpoint --did ... --validation ... --left-mid-air ... --next ...
```
