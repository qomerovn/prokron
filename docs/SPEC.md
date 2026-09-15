# Prokron specification

## Purpose

Prokron is a working convention for developers and coding agents. It keeps a
project understandable across agents, people, and sessions without requiring a
newcomer to read implementation code first.

The task graph answers **what can happen next**. Decision lineage answers **why
the project has its current shape**. Together they are the project chronicle’s
spine.

Prokron is Markdown plus agent configuration. It has no application runtime.

## Chronicle

A participating repository contains `.prokron/` with six records:

| File | Authority |
|---|---|
| `TASKS.md` | Canonical work, hard dependencies, ownership, acceptance, and evidence |
| `TASK_GRAPH.md` | Current dependency and eligibility view derived from tasks |
| `DECISIONS.md` | Append-only ADR history and supersession lineage |
| `STATE.md` | Short current snapshot |
| `INTENT.md` | Zero or one task currently being attempted |
| `JOURNAL.md` | Append-only session diary and handoff history |

The product specification describes intended behavior. The chronicle records
actual project state. When they disagree, the agent exposes and reconciles the
difference instead of silently choosing one.

## Entry mode 1: new repository

The developer provides a product specification. The agent:

1. discusses only material ambiguity with the developer;
2. creates the initial tasks and hard dependencies;
3. renders the first task graph;
4. records product and implementation choices as ADRs;
5. writes the current state;
6. leaves intent empty until work begins;
7. appends the first journal entry.

The result must be understandable before any implementation exists.

## Entry mode 2: existing repository

The agent creates an empty chronicle. It does not scan the repository to invent
past tasks, decisions, or intent. The current request becomes the first task when
work begins. From then on, agents update the chronicle as part of normal work.

Historical reconstruction may be requested explicitly by a developer, but it is
outside the default Prokron workflow.

## Working lifecycle

### Resume

Read `STATE.md`, `TASK_GRAPH.md`, the relevant task, its governing ADRs,
`INTENT.md`, and only the recent journal entries needed for the handoff. State
the current goal and next action. Read specifications or code only after the
chronicle points to what is relevant.

### Work

Create a task if the requested work has none. Work on one task at a time. Mark it
`WIP`, record the owner and claim date, and overwrite `INTENT.md` with the exact
execution point. Update tasks, graph, state, decisions, and journal whenever
project truth changes.

Task completion and validation are separate. `DONE` means the acceptance
condition is met and evidence is recorded. Validation states how the result was
checked: `UNTESTED`, `SYNTHETIC`, `AI_REVIEWED`, or `HUMAN_VERIFIED`. Only a
named human may record `HUMAN_VERIFIED`.

### Decide

Append an ADR with date, authority, context, decision, consequences, affected
tasks, and any decision it supersedes. Never rewrite or delete an earlier ADR,
including its original status. Current meaning comes from following the
supersession chain.

### Checkpoint

Before another person or agent takes over:

1. update task status, validation, evidence, and governing ADRs;
2. synchronize `TASK_GRAPH.md` and `STATE.md`;
3. update or clear the single `INTENT.md` entry;
4. append a journal entry with work done, validation, learning, work left
   mid-air, and the exact next action.

## Automatic continuity

Chronicle maintenance is part of work, not an end-of-session batch job. The
agent must invoke the checkpoint workflow without waiting for the developer when
the host reports any of these conditions:

- the five-hour usage window is nearly exhausted;
- the seven-day usage window is nearly exhausted;
- context compaction is approaching;
- the session is stopping, pausing, or handing off.

Repository instructions cannot read private quota counters that a host does not
expose. When no signal exists, the agent checkpoints after each meaningful
milestone and before ending so a hard cutoff loses little or no project state.

## Agent commands

The portable workflows are:

- `/prokron-init [new|existing]`
- `/prokron-work [task]`
- `/prokron-decide`
- `/prokron-checkpoint`
- `/prokron-resume`

Claude Code exposes project slash-command wrappers. Codex exposes the same modes
through `$prokron <mode>` and also follows the always-loaded `AGENTS.md` rules.
Other agents may use the command Markdown files directly.

## Invariants

- `TASKS.md` is the source for hard task dependencies.
- `TASK_GRAPH.md` reflects tasks; suggestions are labeled and never become hidden dependencies.
- At most one intent exists.
- `DONE` tasks have acceptance evidence.
- ADRs and journal entries remain in history.
- Changed decisions use a new superseding ADR.
- State and intent describe the present, so agents overwrite them when truth changes.
- Entries use stable IDs and absolute dates.

## Non-goals

Prokron does not provide a CLI, service, database, dashboard, semantic repository
scanner, inference engine, schema framework, locking system, model API, or
historical migration process. The working agent supplies reasoning and file
editing; Git supplies version history.

## Acceptance

1. From a product specification, an agent and developer can create an initial
   chronicle that another agent can use without reading code.
2. In an existing repository, initialization creates an empty chronicle and the
   first working session begins recording it without fabricated history.
3. A fresh agent can identify current work, hard dependencies, governing
   decisions, validation, unfinished work, and the exact next action from
   `.prokron/` alone.
4. A superseding decision leaves the earlier ADR intact and discoverable.
5. A host limit or session-ending signal causes a checkpoint; without such a
   signal, milestone checkpoints preserve useful continuity.
6. A human can read the same files and reach the same project-level understanding.
