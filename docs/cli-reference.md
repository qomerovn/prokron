# Prokron CLI reference

Run every command from the root of the Git repository whose `.prokron/` state
you want to read or change.

## Commands

### `prokron init`

Creates `.prokron/` from packaged Markdown templates, installs a managed
bootstrap block in existing `AGENTS.md` and `CLAUDE.md` files, and generates
`STATE.md` and `TASK_GRAPH.md`. Repeated calls preserve existing canonical state.

### `prokron adopt [--dry-run | --apply | --questions-json | --answer-json JSON] [--from DIR] [--interactive]`

Discovers likely current-state sources without reconstructing repository history.
`--dry-run` prints deterministic Git, tree, documentation, state-source, and
implementation-evidence discovery without writing files. A normal run stages a
reviewable candidate under `.prokron-adoption/`; `--from DIR` prefers structured
legacy `TASKS.md`, `DECISIONS.md`, and `INTENTS.md` from that directory.

`--interactive` evaluates a fixed coverage schema, then presents a guided quiz
only for blocking evidence gaps. Answers are persisted after each question, so a
later interactive run resumes without asking confirmed questions again.
`INTERVIEW.md` is the generated audit record; it is not edited by users or agents.
`--questions-json` retrieves unresolved structured items and `--answer-json`
records one structured answer through Core. Core does not call a model provider.
Confirmed work, dependencies, blockers, validation, decisions, and next action
are materialized into the appropriate candidate state files.

Required and relevant conditional domains block apply until established;
optional historical domains never block. `--apply` validates candidate canonical
state, promotes it to `.prokron/`, accepts the baseline decision, links generated
operational tasks to it, and installs the normal bootstrap and derived views.
Legacy sources remain untouched.

### `prokron status`

Validates canonical state, regenerates both derived files, and prints the current
project summary. The summary includes active work, eligible tasks, blocked tasks,
governing decisions, uncertainty, and next actions.

### `prokron next`

Prints every `TODO` task whose dependencies are `DONE`, followed by the first
eligible task as the recommendation. Task order follows `TASKS.md`.

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

Updates one active intent and appends a journal entry.

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
