# Prokron

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

Repository-native project continuity for humans and AI agents.

Prokron stores tasks, decisions, active intent, and handoff history as readable
Markdown beside the code. Git records how that project state changes. The CLI
validates the files and produces deterministic summaries, so a new session can
resume from repository evidence instead of reconstructing context from chat.

## Quick start

Prokron requires Python 3.11 or newer and a Git repository.

```bash
git clone https://github.com/qomerovn/prokron.git
cd prokron
python3 -m venv .venv
.venv/bin/pip install -e .

cd /path/to/your/git-project
/path/to/prokron/.venv/bin/prokron init
```

Initialization creates `.prokron/` and adds a managed bootstrap section to an
existing `AGENTS.md` or `CLAUDE.md` without replacing custom instructions.

```bash
prokron status
prokron next
prokron start T-001 --owner codex/session-1
prokron context T-001
prokron checkpoint \
  --did "Implemented task parsing." \
  --validation "Unit tests pass." \
  --left-mid-air "Ready for review." \
  --next "Run human validation."
prokron doctor
```

Use `prokron adopt --dry-run` to inspect an existing project without changing it.
`prokron adopt` stages an auditable candidate under `.prokron-adoption/`; review
and resolve its blocking unknowns or conflicts before `prokron adopt --apply`
promotes it to canonical state. Use `--from handoff/` for structured legacy state
and `--interactive` for a guided evidence-driven interview. `INTERVIEW.md` is the
generated audit record, not an input form. Agents can retrieve unresolved items
with `--questions-json` and submit answers with `--answer-json`. Confirmed active
execution is written to candidate `TASKS.md` and `INTENTS.md`; historical tasks
and decisions are not reconstructed automatically.

## How it works

The files under `.prokron/` have clear ownership:

| File | Role |
|---|---|
| `TASKS.md` | Mutable task graph, ownership, acceptance, and evidence |
| `INTENTS.md` | Current execution position and next action |
| `DECISIONS.md` | Append-only decision history and relationships |
| `JOURNAL.md` | Append-only checkpoint and handoff history |
| `STATE.md` | Generated current-state summary |
| `TASK_GRAPH.md` | Generated dependency and eligibility view |

`doctor` rejects malformed or contradictory state, including broken references,
dependency cycles, decision supersession cycles, invalid active intents, missing
completion evidence, and stale generated views.

## Documentation

- [Getting started](docs/getting-started.md): initialize a repository and complete a handoff loop.
- [CLI reference](docs/cli-reference.md): commands, arguments, behavior, and exit codes.
- [Architecture](docs/architecture.md): state ownership, runtime boundaries, and design trade-offs.
- [Product thesis](docs/project-prokron-full-thesis-architecture-v2.md): the full protocol direction.
- [Adoption boundary supplement](docs/prokron-thesis-supplement-adoption-boundary.md): current-state reconstruction and existing-project migration semantics.
- [Greenfield example](examples/greenfield): a checked-in project-state fixture.

## Development

The runtime uses only the Python standard library. Development tools are optional.

```bash
python3 -m venv .venv
.venv/bin/pip install -e '.[dev]'
.venv/bin/ruff check .
.venv/bin/mypy src
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m build
```

Prokron v0.1 deliberately excludes remote services, dashboards, model routing,
watch mode, code indexing, and project-management integrations.

## License

Prokron source code is distributed under the [Apache License 2.0](LICENSE).
The Prokron and Qomero names and associated logos are governed separately; see
the [trademark policy](TRADEMARKS.md).
