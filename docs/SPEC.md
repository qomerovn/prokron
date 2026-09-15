# Prokron specification

## 1. Purpose

Prokron is a working agreement for developers and coding agents. It keeps a
project understandable across people, agents, and sessions without making a
newcomer read implementation code first.

The task graph answers **what can happen next**. Decision lineage answers **why
the project has its current shape**. Together they form the spine of the project
chronicle.

Prokron consists of Markdown records, agent instructions, and reusable command
prompts. It requires no application runtime.

## 2. Chronicle

Every participating repository has one `.prokron/` directory:

| File | Role |
|---|---|
| `TASKS.md` | Canonical tasks, dependencies, ownership, acceptance, and evidence |
| `TASK_GRAPH.md` | Current dependency and eligibility view derived from tasks |
| `DECISIONS.md` | Append-only ADR history and supersession lineage |
| `STATE.md` | Short snapshot of the project now |
| `INTENT.md` | Zero or one task currently being attempted |
| `JOURNAL.md` | Append-only session diary and handoff history |

The product specification records intended behavior. The chronicle records
current project truth. When they disagree, the agent surfaces and reconciles
the difference.

## 3. Entry modes

Prokron has exactly two entry modes.

### 3.1 New repository

The developer supplies a product specification. The agent works with the
developer to:

1. resolve material ambiguity;
2. create the initial tasks and hard dependencies;
3. render the task graph;
4. record material product and implementation decisions as ADRs;
5. write the current state;
6. leave intent empty until work starts; and
7. append the first journal entry.

The chronicle must explain the project before implementation begins.

### 3.2 Existing repository

The agent installs an empty chronicle. It does not scan the repository to infer
past tasks, decisions, or intent. The current request becomes the first task
when work starts, and later sessions maintain the chronicle as part of normal
work.

A developer may explicitly request historical reconstruction. It is outside the
default workflow.

## 4. Working lifecycle

### 4.1 Resume

Read, in order:

1. `STATE.md`;
2. `TASK_GRAPH.md`;
3. the active or selected entry in `TASKS.md`;
4. its governing ADRs in `DECISIONS.md`;
5. `INTENT.md`; and
6. only the recent journal entries needed for the handoff.

State the current goal and exact next action. Read specifications or code only
after the chronicle points to the relevant work.

### 4.2 Work

Create a task if the request has none. Work on one task at a time. Mark it
`WIP`, record its owner and claim date, and overwrite `INTENT.md` with the exact
execution point.

Update the chronicle whenever project truth changes. `DONE` means the acceptance
condition is met and evidence is recorded. Validation is separate and uses one
of these values:

- `UNTESTED`
- `SYNTHETIC`
- `AI_REVIEWED`
- `HUMAN_VERIFIED`

Only a named human may record `HUMAN_VERIFIED`.

### 4.3 Decide

Append an ADR with its date, authority, context, decision, consequences,
affected tasks, and any decision it supersedes. Never edit or delete an earlier
ADR to change its meaning. Follow the supersession chain for the current rule.

### 4.4 Checkpoint

Before another person or agent takes over:

1. update task status, validation, evidence, and governing ADRs;
2. synchronize `TASK_GRAPH.md` and `STATE.md`;
3. update the single active intent, or clear it if the task is complete; and
4. append a journal entry with work done, validation, learning, work left
   mid-air, and the exact next action.

## 5. Automatic continuity

Chronicle maintenance happens during work. The agent checkpoints without
waiting for the developer when the host reports that:

- the five-hour usage window is nearly exhausted;
- the seven-day usage window is nearly exhausted;
- context compaction is approaching; or
- the session is stopping, pausing, or handing off.

Agent instructions cannot read quota counters that the host does not expose.
Without a host signal, the agent checkpoints after meaningful milestones and
before ending so an abrupt cutoff loses little project state.

## 6. Commands

The portable workflows are:

- `/prokron-init [new|existing]`
- `/prokron-work [task]`
- `/prokron-decide`
- `/prokron-checkpoint`
- `/prokron-resume`

Claude Code exposes these as project slash commands. Codex exposes the same
workflows through `$prokron <mode>` and follows the repository's `AGENTS.md`.
Other agents can follow the Markdown files in `commands/` directly.

## 7. Invariants

- `TASKS.md` is the source of hard task dependencies.
- `TASK_GRAPH.md` mirrors tasks; suggested order never becomes a hidden dependency.
- At most one intent exists.
- Every `DONE` task has acceptance evidence.
- ADRs and journal entries remain in history.
- A changed decision gets a new, superseding ADR.
- State and intent describe the present and are overwritten as truth changes.
- Entries use stable IDs and absolute dates.

## 8. Scope

Prokron provides the chronicle format and agent workflow. The working agent does
the reasoning and file editing, while Git keeps file history. A CLI, service,
database, dashboard, semantic repository scanner, inference engine, schema
framework, locking system, model API, and automatic historical migration are
outside this specification.

## 9. Acceptance

1. Given a product specification, an agent and developer can create a chronicle
   another agent can use before reading code.
2. In an existing repository, initialization starts empty and records the first
   session without fabricated history.
3. A fresh agent can recover current work, hard dependencies, governing
   decisions, validation, unfinished work, and the exact next action from
   `.prokron/`.
4. A superseding decision leaves the earlier ADR intact and discoverable.
5. A host limit or session-ending signal triggers a checkpoint; without a
   signal, milestone checkpoints preserve continuity.
6. A human reading the same files reaches the same project-level understanding.
