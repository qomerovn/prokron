# Get started with Prokron

This tutorial initializes Prokron in a Git repository, creates a task, starts it,
and records enough state for another person or agent to resume the work.

## What you need

- Git
- Python 3.11 or newer
- A local checkout of this repository

## 1. Install the CLI

From the Prokron checkout:

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
```

The executable is now available at `.venv/bin/prokron`.

## 2. Initialize a project

Create a disposable repository for this tutorial:

```bash
mkdir prokron-demo
cd prokron-demo
git init
/path/to/prokron/.venv/bin/prokron init
```

You should see `Initialized .prokron/`. Run the health check:

```bash
/path/to/prokron/.venv/bin/prokron doctor
```

The final line reports zero tasks, decisions, and active intents.

## 3. Add a task

Open `.prokron/TASKS.md` and replace its fenced example with a real task:

```markdown
# Tasks

## T-001: Add a project greeting
- Status: TODO
- Validation: UNTESTED
- Dependencies: none
- Owner:
- Claimed:
- Acceptance: Running the application prints a project greeting.
- Evidence:
- Governed by: none
```

Ask Prokron what can start:

```bash
/path/to/prokron/.venv/bin/prokron next
```

`T-001` appears under both `READY` and `RECOMMENDED`.

## 4. Start the task

```bash
/path/to/prokron/.venv/bin/prokron start T-001 --owner human/alex
```

Prokron changes the task to `WIP`, records its owner and claim date, creates an
active intent, refreshes the generated views, and prints a focused context pack.

## 5. Record a resumable checkpoint

After making a code change, save the exact stopping point:

```bash
/path/to/prokron/.venv/bin/prokron checkpoint \
  --did "Added the greeting output." \
  --validation "Ran the application locally." \
  --left-mid-air "Implementation works; review is pending." \
  --next "Review the output and mark T-001 complete." \
  --changed-file "src/app.py"
```

The command updates `.prokron/INTENTS.md` and appends an entry to
`.prokron/JOURNAL.md`. A new session can now run:

```bash
/path/to/prokron/.venv/bin/prokron status
/path/to/prokron/.venv/bin/prokron context T-001
```

## What you built

The repository now carries its task, current execution position, changed-file
list, validation claim, and next action in versionable Markdown. See the
[CLI reference](cli-reference.md) for every command and [architecture](architecture.md)
for the boundary between canonical and generated files.

## Troubleshooting

- `Prokron requires a Git repository`: run `git init` in the target directory.
- `Project Prokron is not initialized`: run `prokron init` or `prokron adopt`.
- `canonical state is invalid`: fix every listed error, then run `prokron doctor`.
- `TASK_GRAPH.md is stale` or `STATE.md is stale`: run `prokron status` to regenerate both.

## Adopt an existing repository

Use the [agent adoption instructions](../adapters/generic/README.md#prokron-adopt).
The agent supplies a structured candidate after inspecting the repository. Core
validates it, records explicit human confirmation, and generates `.prokron/`.
No legacy handoff files are required. Run `prokron resume` in the next session.
