# Project Prokron
## Full Product Thesis & Prototype Architecture

**Working name:** Project Prokron
**Working tagline:** **Build with AI without losing the thread.**
**Core positioning:** **A shared project language for humans and AI.**
**Secondary positioning:** A persistent project companion for the owner, PM, developer, and AI agents working on the same codebase.

---

# 0. Executive Summary

Modern AI coding tools are increasingly good at remembering a conversation, resuming a session, delegating work to subagents, and sharing context inside one vendor's ecosystem.

That solves only one layer of continuity.

A software project has a longer life than any single session, model, agent, chat, or vendor. Over time it accumulates product intent, architectural choices, rejected ideas, superseded decisions, task dependencies, partial work, validation evidence, deployments, corrections, owner overrides, production constraints, and unresolved uncertainty.

Today those facts are usually fragmented across chat history, issue trackers, Git commits, documentation, terminal output, agent memory, deployment systems, and the project owner's head.

This creates a recurring failure mode:

> **The project keeps moving, but everyone gradually loses the thread.**

Project Prokron exists to prevent that.

Its core thesis is:

> **Project state should live outside the model.**

Project Prokron provides a repository-native, human-readable, AI-readable protocol that preserves project meaning over time.

It should let a fresh human or AI answer:

- What is the project trying to achieve?
- What is authoritative now?
- Why did the architecture move in this direction?
- Which earlier decisions were superseded, amended, corrected, or rejected?
- What is currently in flight?
- What may be worked on next?
- What is blocked?
- What remains unverified?
- What happened in the previous session?
- What exact action should happen next?
- Can another model continue without access to prior chat history?

The product is therefore not merely a handoff mechanism.

It is a **Project Prokron**: a durable record of how a project became what it is, combined with the execution state required to keep building it.

---

# 1. Origin of the Problem

The problem often starts innocently.

A project begins with:

```text
Thesis
  ↓
Plan
  ↓
Break down tasks
  ↓
Build
```

This works well at first.

Then execution accelerates:

```text
many coding sessions
+ multiple models
+ changing requirements
+ fixes
+ audits
+ production incidents
+ deployment evidence
+ owner decisions
+ human validation
+ partial implementation
```

The task list may still exist. The Git history may still exist. The chats may still exist.

But the owner can no longer answer, with confidence:

> Why is this task here?
> Why did we change this architecture?
> Which version of this decision is current?
> Which work is safe to start?
> What did the last model leave half-finished?

The project has not necessarily failed.

The project has become **illegible**.

That is the problem Project Prokron is designed to solve.

---

# 2. State Fragmentation

Project state is usually fragmented across systems that preserve only part of the truth:

```text
Conversation history
Git history
Issue tracker
Markdown documentation
Agent memory
Current working tree
Test results
CI logs
Deployment evidence
Architecture decisions
Release notes
Human corrections
Unfinished work
```

Git answers:

> What changed?

Chat history answers:

> What did we discuss?

An issue tracker answers:

> What work item exists?

A deployment system answers:

> What was released?

None of them reliably answers:

> **What is currently authoritative, why, and what should happen next?**

Project Prokron does not replace these systems.

It connects their meanings.

---

# 3. Core Thesis

> **Project Prokron gives humans and AI a shared language for understanding and changing project state.**

The important phrase is **shared language**.

Humans tend to think in:

```text
why
intent
priority
trade-offs
risk
change of mind
ownership
business meaning
```

AI systems need:

```text
structured state
authority
dependencies
current intent
acceptance criteria
validation evidence
explicit history
```

Project Prokron creates a common representation both can use.

The same project language should describe:

```text
WHY              thesis / specification
WHY THIS WAY     decisions
WHAT             tasks
WHAT NEXT        task graph
NOW              intent
WHAT HAPPENED    journal / evidence
WHERE WE ARE     state
WHY IT CHANGED   decision lineage
```

---

# 4. A Project Prokron, Not a Chat Memory System

Project Prokron should not compete with model-native history.

Claude should continue to remember Claude conversations. Codex should continue to remember Codex sessions. IDE tools should continue to manage their own transcripts.

Those systems answer:

> What happened in this conversation?

Project Prokron should answer:

> What is true about the project now?

A conversation may contain:

```text
09:00 — use ledger_scope
10:00 — implement ledger_scope
14:00 — evidence shows the model is wrong
16:00 — owner clarifies there are actually two accounting units
18:00 — ledger_scope is withdrawn
```

Conversation recall must reason over all four states.

A Prokron should expose the current truth directly:

```text
ADR-078
Status: Accepted

Decision:
ledger_scope is withdrawn.

Supersedes:
ADR-076

Current model:
accounting_unit
```

History remains available, but history is not the current state.

---

# 5. Product Identity

Project Prokron is:

> **A shared project language for humans and AI.**

It can also behave like:

> **A persistent project companion for the owner or PM.**

But it should not position itself primarily as another project-management product.

"AI PM" creates the wrong expectations: sprint planning, resource allocation, Jira replacement, stakeholder reporting, and team management.

Prokron is deeper and narrower.

It preserves **project meaning and execution continuity**.

---

# 6. What Project Prokron Is

Project Prokron is a repository-native coordination and project-memory protocol for:

- human ↔ human work;
- human ↔ AI work;
- AI ↔ AI work;
- model ↔ model transitions;
- session ↔ session transitions;
- long-running software projects;
- projects where decisions evolve;
- projects where the owner wants to preserve rationale, not just tasks.

It should work whether the team is one developer and one model, one owner and several coding agents, a human engineering team using AI assistants, or multiple AI agents operating on the same repository.

---

# 7. What Project Prokron Is Not

Project Prokron should not attempt to replace:

- Git;
- GitHub / GitLab;
- Jira / Linear / Asana;
- model-native conversation memory;
- IDE session history;
- CI/CD;
- source-code indexing;
- observability;
- deployment platforms;
- architecture documentation;
- agent orchestration frameworks.

It should coordinate and explain their relationship.

A key boundary:

> **Git is implementation reality. Prokron is project meaning and coordination state.**

If the repository, migration state, tests, or verified deployment evidence contradict Prokron, Prokron must be reconciled.

---

# 8. The Prokron Model

Project Prokron is composed of:

```text
THESIS / SPEC
DECISIONS
TASKS
TASK GRAPH
INTENT
JOURNAL
STATE
EVIDENCE
```

They are not equal in authority. Each answers a different question.

---

# 9. Thesis and Specification

The thesis explains why the project exists, the problem being solved, target users, core constraints, intended product shape, assumptions, and non-goals.

The specification explains intended behavior.

For a greenfield project, Prokron should begin from these documents.

The ideal flow is:

```text
Product thesis
    ↓
Goals / constraints / assumptions
    ↓
Decision candidates
    ↓
Milestones
    ↓
Tasks
    ↓
Task Graph
```

The important principle is:

> **Do not break a project into tasks and throw away the reasoning that created those tasks.**

Every meaningful task should remain traceable back to a product requirement, decision, constraint, validation need, production incident, or later correction.

---

# 10. Decisions

`DECISIONS.md` is the durable record of project choices.

It is not just a changelog.

A decision should answer:

- What forced a choice?
- Who made it?
- What authority did they have?
- What was chosen?
- What alternatives were rejected?
- What consequences follow?
- What tasks/specs are affected?
- What earlier decision does it alter?

Decisions form a **Decision Graph**.

---

# 11. Decision Lineage

A project evolves through decisions.

```text
Decision A
   ↓
implementation
   ↓
new evidence
   ↓
Decision B
   ↓
task graph changes
   ↓
implementation changes
```

Prokron should preserve that causal chain.

The Decision Graph answers:

> **Why is the project shaped this way?**

Example:

```text
ADR-021
  ledger_scope
      │
      └── superseded by
               ↓
ADR-024
  accounting_unit
      │
      ├── affects T-M1-09
      └── affects T-M8-09
```

This is more useful than merely remembering that both decisions once existed.

---

# 12. Decision Relationships

The prototype should distinguish:

```text
supersedes
amends
corrects
rejects
```

### `supersedes`

The newer decision replaces the governing effect of the old decision.

### `amends`

The prior decision remains valid, but its scope or wording is changed.

### `corrects`

A historical factual statement was inaccurate, but the underlying decision may remain unchanged.

This matters because:

```text
SUPERSEDE ≠ CORRECT
```

### `rejects`

A proposal or candidate direction was explicitly rejected.

This prevents a future model from rediscovering and re-proposing the same abandoned direction without context.

---

# 13. Decision Status

A practical status model:

```text
PROPOSED
ACCEPTED
REJECTED
SUPERSEDED
```

Historical accepted decisions should not be deleted.

A new record should explain how authority changed.

This gives the project a constitutional history rather than a mutable pile of notes.

---

# 14. Tasks

`TASKS.md` is the canonical coordination board.

Each task should contain at minimum:

```text
ID
Task
Dependencies
Status
Validation
Owner
Claimed
Acceptance
```

A task should answer:

- What work exists?
- What does it depend on?
- Who owns it?
- Is it eligible?
- What counts as done?
- What evidence supports its current validation level?

---

# 15. Status and Validation Are Separate

Prokron should distinguish engineering completion from evidence / validation level.

Example:

```text
Status: DONE
Validation: SYNTHETIC
```

means engineering is complete against the current specification, with synthetic evidence.

It does not mean a qualified human validated the real-world behavior.

A possible validation ladder:

```text
UNTESTED
SYNTHETIC
AI_REVIEWED
HUMAN_VERIFIED
```

The exact ladder may be configurable by project type. The principle is not.

---

# 16. Task Graph

The Task Graph is a **derived execution topology**.

It answers:

- What is ready now?
- What is in flight?
- What is blocked?
- What tasks unlock other tasks?
- What may proceed in parallel?
- Which ordering is hard dependency?
- Which ordering is only suggested?

Example:

```text
T-A ──→ T-B ──→ T-D
  └──→ T-C ──→ T-E
```

The Task Graph answers:

> **What can happen next?**

This is different from the Decision Graph:

```text
Task Graph      → what can happen next?
Decision Graph  → why is the project shaped this way?
```

Together they form the project's execution and authority spine.

---

# 17. Generated Task Graph

The Task Graph should eventually be generated.

Architecture target:

```text
TASKS.md
   ↓
parser
   ↓
Task Graph engine
   ↓
TASK_GRAPH.md
```

Not:

```text
agent edits TASKS
agent remembers to edit TASK_GRAPH
hope they stay synchronized
```

A derived view that requires manual synchronization is a known drift vector.

---

# 18. Intent

`INTENTS.md` holds **live execution state**.

It is not a history file.

It answers:

- What is being attempted right now?
- Why is this attempt active?
- What exact execution point has been reached?
- What is the next action?
- What constraints apply?
- What changed during the attempt?
- What is unresolved?

A valid empty state is:

```text
No intent in flight.
```

Completed work should leave Intent and move into task state, journal, evidence, and derived snapshot.

---

# 19. Intent Belongs to the Work

Intent should not belong to the model.

This enables:

```text
Claude
  ↓
INTENT
  ↓
checkpoint
  ↓
Codex
  ↓
resume
```

The model may change.

The execution state remains.

This is the foundation of cross-model continuity.

---

# 20. Journal

`JOURNAL.md` is append-only execution history.

Each session should record:

```text
Did
Validation
Learned
Left mid-air
Next
```

The most important field is:

```text
Left mid-air
```

because it describes discontinuity explicitly.

Journal is historical evidence, not the primary source of current project truth.

---

# 21. State

`STATE.md` is a derived current snapshot.

Recommended structure:

```text
Current
In flight
Ready
Blocked / waiting
Risks
Next
```

State is a projection, not an independent authority.

A practical rule:

> If STATE takes twenty minutes to read, it is no longer a snapshot.

---

# 22. Evidence

Prokron should explicitly distinguish claims from evidence.

Evidence may include:

- tests;
- scenario runs;
- review reports;
- migration checks;
- deployment results;
- production probes;
- human validation;
- uploaded documents;
- external confirmations.

Prokron should never silently treat one evidence class as another.

```text
Tests pass
```

is not equivalent to:

```text
Accountant confirmed behavior
```

---

# 23. Authority Model

Recommended baseline:

```text
Git / code / migrations / tests / verified deployment evidence
    = implementation reality

TASKS
    = canonical coordination state

INTENTS
    = live execution state

DECISIONS
    = decision authority and lineage

JOURNAL
    = historical execution record

STATE
    = derived current projection

TASK GRAPH
    = derived execution projection
```

If Prokron contradicts implementation reality, Prokron must be reconciled.

If derived views contradict canonical records, the canonical records win.

---

# 24. Project Prokron Loop

A healthy project should follow this loop:

```text
1. Thesis defines intent.
2. Decisions establish governing choices.
3. Tasks materialize executable work.
4. Task Graph exposes execution topology.
5. Intent records the active attempt.
6. Code changes.
7. Tests / reviews / deployment create evidence.
8. Task state is reconciled.
9. Journal records what happened.
10. Derived State and Task Graph are rebuilt.
11. New evidence may create or supersede decisions.
12. Repeat.
```

This loop preserves:

```text
WHY
→ WHAT
→ NOW
→ WHAT HAPPENED
→ WHY IT CHANGED
```

---

# 25. Project Drift

Project drift is not inherently bad. Projects should change when evidence changes.

The problem is **unexplained drift**.

Prokron should make drift visible:

```text
initial model
    ↓
new evidence
    ↓
decision change
    ↓
task graph change
    ↓
implementation change
```

A Prokron should allow the owner to see when direction changed, who changed it, why, what was invalidated, what tasks moved, and what code may have become stale.

This becomes a form of real-time project archaeology.

---

# 26. Greenfield Workflow

The preferred Prokron experience begins at project inception.

```bash
prokron init
prokron thesis docs/product-thesis.md
```

Prokron may propose:

- goals;
- constraints;
- assumptions;
- open decisions;
- milestones;
- decision candidates;
- task decomposition;
- dependencies;
- acceptance criteria.

Human review should happen before execution begins.

This preserves:

```text
WHY → WHAT
```

from day one.

---

# 27. Existing Project Adoption

Existing projects use:

```bash
prokron adopt
```

The adoption flow may inspect:

- current repository;
- Git history;
- existing docs;
- task files;
- ADRs;
- migrations;
- tests;
- CI configuration;
- deployment evidence;
- current working tree.

The tool may reconstruct candidate state, but must mark uncertainty explicitly and never fabricate missing historical decisions.

---

# 28. Repository Layout

Recommended installed layout:

```text
project/
├── .prokron/
│   ├── README.md
│   ├── TASKS.md
│   ├── TASK_GRAPH.md
│   ├── INTENTS.md
│   ├── DECISIONS.md
│   ├── JOURNAL.md
│   └── STATE.md
│
├── AGENTS.md
├── CLAUDE.md
└── ...
```

Prokron should live in the same repository and revision history as the code it describes.

It should not live on a permanent separate branch.

---

# 29. Same Repository, Same Revision

A useful property:

```text
git checkout <sha>
```

should recover:

```text
code
+ decisions
+ tasks
+ state
+ historical execution context
```

This enables project time travel.

A temporary branch may be used to modify Prokron itself, but Prokron should not be permanently separated from implementation history.

---

# 30. Bootstrap Files

`AGENTS.md`, `CLAUDE.md`, and future adapter files should act as **bootstrap loaders**.

They should not duplicate the full Prokron protocol.

Recommended flow:

```text
Agent enters repo
      ↓
AGENTS.md / CLAUDE.md
      ↓
.prokron/README.md
      ↓
Task Graph
      ↓
relevant task
      ↓
active intent
      ↓
governing decisions / spec
      ↓
relevant code / tests
```

The Prokron protocol is canonical.

Provider-specific files are only adapters.

---

# 31. Shared Language Means Shared Operations

Prokron should not only create files that humans and AI read.

It should also expose the **same vocabulary for changing project state**.

Human:

```bash
prokron checkpoint
```

AI:

```text
/prokron checkpoint
```

Both should invoke the same semantic operation.

This is a stronger form of shared language.

---

# 32. One Engine, Multiple Interaction Surfaces

Architecture principle:

> **One Prokron engine, multiple interaction surfaces.**

```text
                    Prokron Core
          parser / graph / validator / state
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
         CLI        AI Commands       CI/API
       human/dev       agents        automation
```

There should not be separate implementations for terminal, Claude slash commands, Codex commands, and CI.

All should call the same core.

---

# 33. CLI Surface

The CLI is the canonical executable interface.

```bash
prokron init
prokron adopt
prokron status
prokron doctor
prokron graph

prokron claim T-M6-03
prokron start T-M6-03
prokron pause
prokron resume
prokron checkpoint
prokron handoff
prokron complete T-M6-03

prokron decision
prokron decisions graph
prokron why ADR-024

prokron reconcile
prokron context T-M6-03
```

The CLI should be scriptable, deterministic, usable in CI, usable by humans, and callable by AI tools.

---

# 34. AI Slash Commands

AI-native adapters should expose higher-level workflow commands:

```text
/prokron
/prokron status
/prokron next
/prokron start T-M6-03
/prokron checkpoint
/prokron handoff
/prokron decide
/prokron finish
/prokron reconcile
```

Slash commands should not contain project logic.

They should map into Prokron Core.

---

# 35. Command Vocabulary

A useful command grammar has three groups.

## Observe

```text
status
next
doctor
why
graph
```

## Act

```text
start
claim
decide
complete
```

## Continuity

```text
checkpoint
pause
resume
handoff
reconcile
```

This grammar is intentionally understandable by both humans and models.

---

# 36. `/prokron next`

The command answers:

> What am I allowed to do next?

Example:

```text
READY
T-G-16  Release-gate evidence
T-M6-03 Two-way match
T-M6-05 Cost classification

RECOMMENDED
T-G-16

Reason:
largest unresolved release-evidence gap

Do not touch:
production writes — freeze active
```

---

# 37. `/prokron start`

Example:

```text
/prokron start T-M6-03
```

The operation should:

```text
validate task exists
↓
validate hard dependencies
↓
validate ownership
↓
claim task
↓
create Intent
↓
regenerate Task Graph
↓
regenerate State
↓
produce minimal task context
```

The returned context should include task, rationale, dependencies, acceptance, governing decisions, relevant files, constraints, and current intent.

---

# 38. Checkpoint

`checkpoint` is the core continuity primitive.

It should persist:

```text
current task
current execution point
completed work
changed files
validation already run
unresolved failures
deviations from intent
exact next action
```

Checkpoint is not necessarily the end of work.

It is a durable save point.

---

# 39. Handoff

`handoff` is checkpoint plus resume preparation.

```text
checkpoint
    +
context packaging
    =
handoff
```

Example:

```text
/prokron handoff sol
```

A Resume Pack should include:

```text
Task
Current state
Why
Relevant decisions
Files touched
Tests
Failures
Next action
Suggested role
```

This enables clean:

```text
Terra → Sol
Claude → Codex
session 1 → session 2
human → AI
```

---

# 40. Decision Command

`/prokron decide` should help structure a decision without silently making it.

Example:

```text
Candidate decision

Context:
...

Conflict:
...

Options:
A ...
B ...

Recommended:
...

Authority required:
human/owner

Potentially supersedes:
ADR-037

Affected tasks:
T-M3-09
T-G-19
```

Once approved:

```text
append ADR
↓
update Decision Graph
↓
identify affected tasks
↓
recompute Task Graph
↓
flag possible drift
```

---

# 41. Context Packs

Prokron should create minimal task-specific context.

```bash
prokron context T-M6-03
```

A context pack should include only what the task requires:

```text
task
hard dependencies
active intent
governing decisions
relevant spec sections
known constraints
validation requirements
relevant files
known failures
next action
```

The goal is not to dump the repository.

The goal is to reduce reconstruction cost.

---

# 42. Reconciliation

`prokron reconcile` is a major capability.

It should:

```text
inspect implementation reality
        ↓
compare canonical Prokron state
        ↓
detect contradictions
        ↓
repair stale coordination state
        ↓
preserve append-only history
        ↓
rebuild derived views
        ↓
record corrections
```

Examples of drift it should detect:

- duplicate IDs;
- stale WIP claims;
- task marked DONE while acceptance evidence is absent;
- old decision still referenced after supersession;
- Task Graph disagrees with TASKS;
- STATE claims a deployment not supported by evidence;
- active intent references a completed task;
- historical factual claim later proven wrong.

---

# 43. Doctor

`prokron doctor` is the health command.

Example:

```text
Project Prokron

✓ Task IDs unique
✓ All dependencies resolve
✓ No dependency cycles
✓ Active intent references valid task
✓ WIP tasks have owners
✓ Decision references resolve
✓ Task Graph matches TASKS
✓ STATE matches canonical state

⚠ 2 stale WIP claims
⚠ ADR-018 is superseded but still referenced by T-M3-04
⚠ STATE references a release not supported by deployment evidence

Health: 84/100
```

The health score is optional. Deterministic integrity findings are the important part.

---

# 44. Automatic Continuity

Prokron should not depend on a user remembering to checkpoint.

A future process:

```bash
prokron watch
```

can monitor continuity risk.

Possible triggers:

```text
provider usage limit approaching
context window approaching limit
session ending
model switch
IDE process termination
explicit pause
user handoff
compact/context refresh
```

The principle is:

> **Any impending loss of execution continuity should trigger persistence.**

---

# 45. Quota Guard

AI coding plans often have usage windows or weekly limits.

Prokron should support provider-aware quota adapters.

```text
Provider
   ↓
Usage Adapter
   ↓
Quota Guard
   ↓
threshold
   ↓
checkpoint
```

Possible policy:

```yaml
quota_guard:
  checkpoint_at:
    - remaining: 15%
    - remaining: 8%
```

The first threshold may create a light checkpoint.

The second may create a handoff-grade checkpoint.

---

# 46. Quota Detection Strategy

Quota detection should degrade gracefully:

```text
1. Native provider event / warning
2. Provider status inspection
3. Local usage heuristic
4. Manual checkpoint
```

Prokron Core must not depend on any one vendor exposing a quota API.

Quota awareness belongs in adapters.

---

# 47. Incremental Persistence

Prokron must not wait until the final few percent of quota to save state.

Correct architecture:

```text
meaningful action
      ↓
Intent updated
      ↓
meaningful action
      ↓
Intent updated
      ↓
quota warning
      ↓
final checkpoint
```

Quota Guard is insurance.

The primary protection is incremental persistence.

---

# 48. Emergency Checkpoint Without the Model

If a model becomes unavailable, Prokron should still capture deterministic local state:

```text
Git HEAD
git status
git diff --stat
changed files
current task
current intent
last recorded validation
```

The system may lose a fresh semantic summary, but it should not lose the mechanical execution state.

---

# 49. Vendor Strategy

Project Prokron should be:

> **vendor-neutral at the core, first-class for Claude Code and Codex in v0.1.**

This balances portability, maintainability, and adoption.

---

# 50. Support Tiers

## Tier 1 — First-class

```text
Claude Code
Codex
```

These should receive:

- native bootstrap adapters;
- native command integration where available;
- lifecycle hooks where available;
- quota/context awareness where possible.

## Tier 2 — Generic

Any coding agent that can:

- read repository files;
- run shell commands;
- follow instructions.

Generic agents can use:

```bash
prokron status
prokron next
prokron checkpoint
prokron context <task>
```

## Tier 3 — Later native adapters

Potential examples:

```text
Cursor
Gemini CLI
Cline
OpenCode
Windsurf
Aider
```

Add these based on actual demand.

---

# 51. Why Claude + Codex First

They provide sufficiently different environments to pressure-test the abstraction.

Claude Code can test slash commands, hooks, session lifecycle, `CLAUDE.md`, and context/quota continuity.

Codex can test `AGENTS.md`, terminal-first operation, coding/review workflows, and session/model switching.

If Prokron works cleanly across both, the abstraction is less likely to be vendor-specific.

---

# 52. Adapter Architecture

Provider adapters should remain thin.

Conceptual interface:

```ts
interface ProkronAdapter {
  id: string

  installBootstrap(): Promise<void>
  installCommands?(): Promise<void>

  detectSession?(): Promise<SessionInfo>
  detectUsage?(): Promise<UsageInfo | null>

  requestCheckpoint?(): Promise<void>
}
```

Adapters should never own project semantics.

Wrong:

```text
Claude adapter decides whether a task is eligible.
```

Correct:

```text
Claude adapter
      ↓
Prokron Core
      ↓
eligibility validation
```

---

# 53. Generic Adapter

The generic adapter can install an instruction snippet:

```markdown
This repository uses Project Prokron.

Before substantial work:
1. Run `prokron status`.
2. Run `prokron context <task>` before implementing.
3. Claim work through Prokron.
4. Keep active intent current.
5. Run `prokron checkpoint` before ending or switching sessions.
6. Do not manually reinterpret derived state.
```

This makes Prokron usable beyond supported vendors from day one.

---

# 54. Prototype Architecture

```text
                 ┌──────────────────────┐
                 │ Human / AI / PM      │
                 └──────────┬───────────┘
                            │
              CLI / Slash Commands / CI
                            │
                 ┌──────────▼───────────┐
                 │   Prokron Core     │
                 └──────────┬───────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
   Task Parser         Decision Parser      Intent Parser
        │                   │                   │
        └──────────────┬────┴──────────────┬────┘
                       │                   │
                       ▼                   ▼
                 Task Graph          Decision Graph
                       │                   │
                       └─────────┬─────────┘
                                 ▼
                         Integrity Engine
                                 │
          ┌──────────────────────┼──────────────────────┐
          ▼                      ▼                      ▼
        doctor                 status                reconcile
          │                      │                      │
          └──────────────────────┴──────────────────────┘
                                 │
                                 ▼
                       Derived Renderers
                                 │
                       STATE / TASK_GRAPH
                                 │
                                 ▼
                       Context / Handoff Pack
```

Provider adapters wrap this architecture.

---

# 55. Prototype Components

Suggested packages:

```text
packages/
├── core/
├── parser/
├── task-graph/
├── decision-graph/
├── validator/
├── renderer/
├── context/
├── continuity/
└── cli/
```

Adapters:

```text
adapters/
├── claude/
├── codex/
└── generic/
```

---

# 56. Storage Format

Markdown should remain the primary user-facing format.

Reasons:

```text
human-readable
AI-readable
Git-diffable
portable
local-first
offline
zero infrastructure
```

The CLI parses Markdown into structured internal objects.

Markdown is the interface.

The structured model is the engine.

---

# 57. Internal Task Model

Example:

```yaml
id: T-M3-04
title: Settle obligation

deps:
  - T-M3-03

status: WIP
validation: SYNTHETIC

owner: codex/session-8
claimed: 2026-09-12

acceptance:
  - settlement invariant passes
  - required scenario passes

governed_by:
  - ADR-004
  - ADR-039
```

The exact serialization may remain Markdown. This illustrates the semantic model.

---

# 58. Internal Decision Model

Example:

```yaml
id: ADR-024
date: 2026-09-12
status: accepted
authority: human/owner

supersedes:
  - id: ADR-021
    scope: ledger_scope

affects:
  - T-M1-09
  - T-M8-09

context: >
  Production evidence showed that the earlier model represented two accounting
  units rather than two scopes of one ledger.

decision: >
  Replace ledger_scope with accounting_unit.
```

---

# 59. Intent Model

Example:

```yaml
task: T-M6-03
owner: Claude/session-14
updated: 2026-09-12

goal:
  implement two-way match

current_point:
  reconciliation path implemented; two tests failing

constraints:
  - do not alter VAT semantics
  - no production writes

changed_files:
  - backend/...
  - tests/...

next_action:
  fix rounding branch and rerun SC-014
```

---

# 60. Derived Files

Canonical / historical:

```text
TASKS.md
INTENTS.md
DECISIONS.md
JOURNAL.md
```

Derived:

```text
TASK_GRAPH.md
STATE.md
```

Prototype target:

> **Derived files should be generated, not manually maintained.**

---

# 61. Integrity Rules

The first validator should enforce deterministic rules.

## Tasks

- unique task IDs;
- valid status values;
- valid validation values;
- all dependency targets exist;
- no accidental cycles;
- WIP requires owner and claim date;
- DONE requires acceptance evidence;
- no derived graph may invent hard dependencies.

## Intent

- active intent references valid task or named maintenance operation;
- completed task does not remain active intent;
- ownership is consistent;
- empty intent is explicit.

## Decisions

- unique ADR IDs;
- relationship targets exist;
- `supersedes`, `amends`, `corrects`, and `rejects` are distinct;
- current governing decision can be determined;
- affected task references resolve;
- historical accepted records are not silently rewritten.

## Journal

- append-only;
- session entry contains `Left mid-air`;
- historical correction uses a new entry.

## Derived views

- Task Graph matches canonical task state;
- State matches current task/intent state;
- derived views can be flagged stale.

---

# 62. Append-Only Semantics

Recommended:

```text
DECISIONS  append-only
JOURNAL    append-only

TASKS      mutable canonical board
INTENTS    mutable live state

STATE      generated
TASK GRAPH generated
```

This gives both historical integrity and practical operability.

---

# 63. Concurrency

Prokron should support multiple agents without pretending Markdown provides database locking.

The initial protocol may use:

```text
one active claim per task
owner recorded explicitly
stale claim detection
task takeover recorded
```

Later versions may add lock files, branch/worktree awareness, atomic claim operations, and merge conflict helpers.

Concurrency behavior should remain understandable in Git.

---

# 64. Worktrees and Branches

Each worktree or feature branch may carry its own Prokron snapshot.

When branches merge, Prokron should reconcile task state, decisions, Journal entries, and derived views.

Prokron should not be stored on a permanent separate coordination branch.

The code revision and project state should travel together.

---

# 65. CI Integration

A basic CI check:

```bash
prokron doctor --ci
```

It should fail on structural corruption such as duplicate IDs, broken dependency references, invalid graph state, malformed decision lineage, and stale generated outputs where generation is mandatory.

It may warn rather than fail on softer issues such as stale claims, old snapshots, or missing optional human validation.

---

# 66. Git Hooks

Optional hooks:

```text
pre-commit
pre-push
post-merge
```

Possible behavior:

### pre-commit
Validate changed Prokron files.

### post-merge
Regenerate derived views.

### pre-push
Warn if active intent exists but no checkpoint was written.

Hooks should remain optional.

---

# 67. `prokron init`

Responsibilities:

- detect Git repository;
- create `.prokron/`;
- install templates;
- detect supported AI tools;
- install managed bootstrap blocks;
- avoid overwriting user instructions;
- optionally initialize from thesis.

Example:

```text
Detected:
✓ Git repository
✓ AGENTS.md
✓ CLAUDE.md

Install Prokron into:
> .prokron/

Configure:
✓ Codex
✓ Claude Code

Initialize from thesis?
> Yes
```

---

# 68. Managed Bootstrap Blocks

Prokron should never overwrite custom instruction files.

Use managed blocks:

```markdown
<!-- project-prokron:start -->

## Project Prokron

This repository uses `.prokron/` as persistent project coordination state.

Before implementation:
1. Read `.prokron/README.md`.
2. Inspect `.prokron/TASK_GRAPH.md`.
3. Locate the relevant task in `.prokron/TASKS.md`.
4. Read `.prokron/INTENTS.md` if work is in flight.
5. Read only the governing spec, decisions, and code required for that task.

Do not reconstruct current project truth from chat history.

<!-- project-prokron:end -->
```

Updates must be idempotent.

---

# 69. Public Repository Structure

Suggested repository:

```text
project-prokron/
├── README.md
├── LICENSE
├── package.json
│
├── packages/
│   ├── core/
│   ├── parser/
│   ├── task-graph/
│   ├── decision-graph/
│   ├── validator/
│   ├── renderer/
│   ├── continuity/
│   └── cli/
│
├── templates/
│   ├── README.md
│   ├── TASKS.md
│   ├── TASK_GRAPH.md
│   ├── INTENTS.md
│   ├── DECISIONS.md
│   ├── JOURNAL.md
│   └── STATE.md
│
├── adapters/
│   ├── claude/
│   ├── codex/
│   └── generic/
│
├── examples/
│   ├── greenfield/
│   └── existing-project-recovery/
│
└── docs/
    ├── concepts.md
    ├── authority-model.md
    ├── task-graph.md
    ├── decision-lineage.md
    ├── continuity.md
    └── reconciliation.md
```

---

# 70. MVP v0.1

The MVP should be deliberately narrow.

Ship:

```text
prokron init
prokron adopt
prokron status
prokron next
prokron doctor
prokron graph
prokron context
prokron checkpoint
```

Plus:

- Markdown templates;
- Claude adapter;
- Codex adapter;
- generic adapter;
- task parser;
- decision parser;
- task dependency validator;
- decision relationship validator;
- generated Task Graph;
- generated State;
- managed bootstrap installation;
- one realistic example project.

---

# 71. v0.1 Slash Commands

First-class adapters should expose:

```text
/prokron
/prokron status
/prokron next
/prokron start
/prokron checkpoint
/prokron handoff
/prokron decide
```

Where the provider supports command installation cleanly.

If not, the agent should still be able to invoke the CLI.

---

# 72. v0.2 Candidate

After v0.1 proves useful:

```text
prokron claim
prokron pause
prokron resume
prokron complete
prokron decisions graph
prokron reconcile
prokron watch
```

Potential additions:

- quota guard;
- context-window guard;
- stale claim automation;
- intent drift detection;
- decision impact analysis;
- Git hooks;
- CI mode;
- structured JSON export.

---

# 73. v0.3+ Opportunities

Only after real adoption:

### Decision impact

```bash
prokron impact ADR-024
```

Show affected tasks, specifications, code areas, and validation.

### Code-to-decision trace

```bash
prokron why src/accounting/unit.py
```

Possible path:

```text
code
  ↑
task
  ↑
decision
  ↑
thesis / requirement
```

### Project drift analysis

Detect divergence between governing decisions, task state, actual code, and deployment state.

### Context optimization

Generate minimal context for a model based on Task Graph and Decision Graph traversal.

### Model routing

Suggest a model based on task type, prior failures, validation needs, cost, and context size.

This is optional and should not become the core identity.

---

# 74. Product Boundaries

Project Prokron should resist becoming:

- another Jira;
- another agent orchestrator;
- another chat-memory product;
- another code graph product;
- another generic knowledge base;
- another SaaS dashboard before the protocol works.

The durable wedge is:

> **Preserve project meaning across time, people, models, and sessions.**

---

# 75. Relationship to Code Intelligence

Source-code indexing tools solve a different question.

```text
Code intelligence:
How is the code structured?

Project Prokron:
Why is the project structured this way, what is active, and what should happen next?
```

Prokron should use code intelligence on demand.

It should not depend on it for basic continuity.

---

# 76. Relationship to PM Tools

PM tools can remain useful for team planning, deadlines, assignment, and external reporting.

Prokron should focus on task causality, authority, active intent, decision lineage, validation, and AI/human continuity.

Integrations can come later.

---

# 77. Human Value

Prokron is not only for AI.

A human should be able to leave a project for ten days, return, and answer:

```text
What changed?
Why?
What is in flight?
What is safe to do next?
What is still uncertain?
```

Human cognitive continuity is finite too.

---

# 78. AI Value

A fresh model should be able to enter a repository and answer:

```text
What is this project?
What is authoritative?
What task is active?
What tasks are eligible?
What decisions govern this area?
What must I not change?
What was left mid-air?
What exact action comes next?
```

without access to prior chat history.

That is a key success condition.

---

# 79. Core User Promise

Project Prokron should eventually make these statements true:

> A fresh model can enter the repository and understand what matters without reading the whole project.

> A human can return after ten days and understand why the project moved in its current direction.

> A decision can be superseded without erasing why the old implementation existed.

> A task can be traced back to the reasoning that created it.

> A model switch does not require reconstructing the project from conversation history.

> Conversation history is useful, but never required to establish current project truth.

---

# 80. Success Metrics

Do not evaluate Prokron only by stars.

Useful operational metrics:

- time for a fresh model to begin productive work;
- number of context-reconstruction questions;
- tokens spent reconstructing project state;
- stale-decision implementation errors;
- task/dependency contradictions;
- owner interventions required to explain context;
- percentage of active work with explicit intent;
- percentage of decisions with valid lineage;
- Prokron doctor failure rate;
- successful cross-model resume rate.

A strong proof point:

> A fresh model can correctly identify current state, current authority, eligible work, blocking conditions, governing decisions, and the next action without access to prior conversation history.

---

# 81. Product Positioning

## Hero

> **Build with AI without losing the thread.**

## Subheadline

> **Project Prokron gives humans and AI a shared language for decisions, tasks, intent, and project history.**

## Technical positioning

> **A repository-native state protocol for human + AI software projects.**

## Alternative concise line

> **Project memory that does not belong to any model or session.**

---

# 82. Why This Can Matter

Session continuity is becoming a commodity.

Model vendors will continue improving history recall, session resumption, agent communication, and context compression.

Prokron should not compete there.

Its durable value is different:

```text
vendor-neutral
repository-native
causal
authority-aware
decision-aware
task-aware
human-readable
AI-readable
Git-native
```

The project itself becomes the memory substrate.

---

# 83. Final Principle

Project Prokron began from a practical failure:

> **Breaking a project into tasks was not enough to preserve understanding once execution accelerated.**

The solution is not a bigger task list.

The solution is to preserve the relationships between:

```text
why
decision
task
intent
execution
evidence
history
change
```

for the lifetime of the project.

The final design principle is:

> **The project state lives outside the model.**

And the product promise is:

> **Humans and AI should be able to build the same project using the same language, even when the people, models, sessions, and decisions change.**

That is Project Prokron.
