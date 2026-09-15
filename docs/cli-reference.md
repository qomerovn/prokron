# Prokron CLI reference

Run every command from the root of the Git repository whose `.prokron/` state
you want to read or change.

## Commands

### `prokron init`

Creates `.prokron/` from packaged Markdown templates, installs a managed
bootstrap block in existing `AGENTS.md` and `CLAUDE.md` files, and generates
`STATE.md` and `TASK_GRAPH.md`. Repeated calls preserve existing canonical state.

### Agent-driven adoption

```text
prokron adopt prepare
prokron adopt schema
prokron adopt ingest CANDIDATE.json
prokron adopt confirm --by HUMAN --digest REVIEWED_DIGEST
prokron adopt apply
```

`adopt` without a subcommand is equivalent to `prepare`. Prepare prints JSON
containing Git facts, tree names, file extensions, exclusions, a repository
checkpoint, and instructions. It writes no project files and makes no semantic
conclusions. `schema` emits the candidate JSON Schema, without requiring a repo.

The coding agent reads relevant repository evidence and creates the candidate.
Copy `prepare.checkpoint` into its `checkpoint` field. Save the input outside the
repository or inside `.prokron-candidate/` so writing it does not invalidate the
repository checkpoint. The [example candidate](../examples/brownfield-candidate.json)
shows the shape; replace its placeholder checkpoint and sample statements.

`ingest` validates the schema, dependencies, decision lineage, and lossless
Markdown serialization. It stages `.prokron-candidate/candidate.json` and prints
the review digest. Ingestion does not write canonical state. Corrected candidates
must be re-ingested, which clears any prior confirmation.

The human reviews the staged candidate, including its unknowns. Only after that
approval may the agent call `confirm` with the reviewed digest and human identity.
This records an attestation; it is not an identity authentication service.
Unknowns remain valid, and confirmation never upgrades individual inferred claims.

`apply` requires matching confirmation, an unchanged branch/content snapshot, and
valid state. It builds the canonical directory before publication, preserves
custom bootstrap instructions, and refuses to replace an existing `.prokron/`.
The full reviewed candidate and confirmation become `ADOPTION.json`; current
tasks, decisions, intent and journal remain Markdown authority.

### `prokron resume`

Prints a JSON continuity pack with current canonical tasks, decisions, intents
and journal, plus the reviewed adoption snapshot and recorded next action.
A fresh session needs no conversational memory or full repository rediscovery.
Stale or blocked packs retain the canonical context but include a condition and
exit with code 2. The adoption snapshot is historical; live Markdown takes
precedence for operational work.

### `prokron status`

Validates canonical state, regenerates both derived files, and prints the current
project summary. The summary includes active work, eligible tasks, blocked tasks,
governing decisions, uncertainty, and next actions.

### `prokron next`

For agent-adopted repositories, returns the recorded next action, with a current
intent taking precedence over the initial adoption action. It checks explicit
dependencies and task blockers. It never searches repository prose or invents
an action. Changed branch or working-tree content yields `STATE_STALE` with
checkpoint/current HEAD and `/prokron-sync` guidance. HEAD remains provenance;
commits containing only excluded generated state do not make the snapshot stale. Blocked or completed
action targets produce explicit conditions rather than a semantic guess.

Repositories initialized with `init` retain the existing ordered `TODO`
eligibility listing; they have no agent-adoption checkpoint.

### `prokron graph`

Validates state, regenerates derived files, and prints the deterministic task
graph with dependencies, downstream unlocks, and current eligibility.

### `prokron doctor [--ci]`

Checks canonical integrity and verifies that derived files are current. `--ci`
is accepted for forward-compatible CI usage; output and exit behavior are already
CI-safe without it.

### `prokron context [TASK_ID]`

Prints a minimal context pack for one task: acceptance and evidence, direct
dependencies, immediate downstream tasks, active intent, and related decisions.
When `TASK_ID` is omitted, exactly one active or eligible task must be unambiguous.

### `prokron start TASK_ID --owner OWNER`

Starts one eligible `TODO` task. It sets the task to `WIP`, records the owner and
current date, creates an active intent, regenerates derived state, and prints the
task context. Blocked, missing, or already-started tasks are rejected.

### `prokron checkpoint`

Updates one active intent and appends a journal entry. For agent adoption it
also records the current repository checkpoint. The agent must first evaluate
changes and update affected canonical operational state. Checkpoint does not
revise the immutable adoption baseline. See the [sync lifecycle](deterministic-harness.md#lifecycle).

```text
prokron checkpoint
  [--task TASK_ID]
  --did TEXT
  --validation TEXT
  [--learned TEXT]
  --left-mid-air TEXT
  --next TEXT
  [--changed-file PATH]...
```

`--task` may be omitted only when one active intent exists. All values must fit
on one Markdown line. `--changed-file` may be repeated and cannot contain commas.
Input is validated before any file changes are written.

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Command completed successfully |
| `1` | `doctor` found unhealthy or stale state |
| `2` | Invalid command input or user-correctable project state |

Argument parsing errors also exit with code `2`.

## Canonical values

Task status must be `TODO`, `WIP`, `DONE`, or `BLOCKED`. Validation must be
`UNTESTED`, `SYNTHETIC`, `AI_REVIEWED`, or `HUMAN_VERIFIED`. Decision status must
be `PROPOSED`, `ACCEPTED`, `REJECTED`, or `SUPERSEDED`.

Task IDs use `T-...`; decision IDs use `ADR-...`. Active maintenance intents may
instead use `maintenance/<lowercase-hyphenated-name>`.

## Related documentation

- [Getting started](getting-started.md)
- [Architecture](architecture.md)
- [Project README](../README.md)
