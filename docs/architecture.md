# Prokron architecture

Prokron externalizes state; the coding agent supplies intelligence. Its architecture
is intentionally local: Markdown is durable state, Python is the integrity and
lifecycle engine, and Git is the history and collaboration layer.

## The problem

Chat history and model memory are poor project authorities. They are hard to diff,
easy to lose, and often detached from the code revision they describe. A handoff
also needs more than a task title: it needs the current point, constraints,
validation evidence, and the next action.

## State ownership

```text
TASKS.md ───────┐
DECISIONS.md ───┼─> parse + validate ─> STATE.md
INTENTS.md ─────┤                    └> TASK_GRAPH.md
JOURNAL.md ─────┘
       canonical                         generated
```

`TASKS.md`, `INTENTS.md`, `DECISIONS.md`, and `JOURNAL.md` are canonical.
Humans and agents may edit them through the CLI or directly while preserving the
documented field vocabulary. `STATE.md` and `TASK_GRAPH.md` are projections and
are always safe to regenerate.

## Runtime boundaries

| Module | Responsibility |
|---|---|
| `models.py` | Immutable task, decision, intent, journal, and aggregate state types |
| `markdown.py` | Strict parsing and field updates for canonical Markdown |
| `core.py` | State loading, eligibility, and cross-file integrity validation |
| `rendering.py` | Deterministic state, graph, and context rendering |
| `operations.py` | Initialization, task starts, and checkpoints |
| `repository.py` | Git facts and content fingerprints; no semantic interpretation |
| `candidate.py` | Agent candidate schema, provenance/status rules, operational validation |
| `persistence.py` | Strict JSON reads and atomic metadata writes |
| `adoption.py` | Agent ingestion, digest-bound confirmation, publication and continuity |
| `cli.py` | Argument parsing, command output, and exit-code policy |

Adapters teach the current coding agent to inspect evidence, reason about project
semantics, ask material questions, and submit structured state through the CLI.
Core never scans repository content or generates semantic questions.

## Read and write flow

Read-only commands load all canonical files into immutable dataclasses, validate
cross-file invariants, then render output. Mutating commands validate before the
write, update the smallest canonical surface, reload and validate again when
needed, and regenerate derived files.

Important invariants include:

- every dependency and governing decision exists;
- task and decision relationship graphs contain no cycles;
- `WIP` tasks have an owner and claim date;
- `DONE` tasks carry acceptance criteria and evidence;
- active intents point to non-complete `WIP` tasks with the same owner;
- superseded decisions have exactly one valid superseding relationship;
- every journal entry records what was left mid-air.

## Design choices and trade-offs

### Markdown as authority

Markdown is readable, editable, diffable, and available in every repository. The
trade-off is a stricter field vocabulary: canonical values must stay on one line,
and malformed hand edits are rejected instead of guessed.

### Python standard library runtime

The core has no runtime dependencies, which keeps installation and auditing
simple. The trade-off is a deliberately small parser and CLI instead of a richer
schema or terminal framework.

### Derived views instead of duplicated state

The task graph and state summary are generated from canonical files. This prevents
multiple writable representations from drifting, at the cost of requiring
`prokron status` after direct canonical edits.

### Explicit uncertainty and the adoption boundary

The primary adoption path accepts agent-authored JSON under a small published
schema. Claims preserve OBSERVED, INFERRED or CONFIRMED status, source references,
and optional creation/confirmation metadata. Unknowns are legitimate state.

Human confirmation binds the reviewed candidate digest. Apply validates again,
checks repository freshness and publishes a fully prepared `.prokron/` directory.
`ADOPTION.json` preserves the immutable approved snapshot; `BASELINE.md` presents
it for readers. Operational Markdown remains independently mutable authority.
`CHECKPOINT.json` records HEAD for provenance plus branch and repository-content
fingerprints for freshness. Commits containing only excluded generated state do
not invalidate the checkpoint.
Resume returns the snapshot together with current operational Markdown, with
explicit stale/blocked conditions. No repository understanding is performed.

See the [audit and current boundary](deterministic-harness.md).

## License and trademarks

Prokron source code is distributed under the Apache License 2.0. The Prokron and
Qomero names and associated logos remain subject to the separate
[trademark policy](../TRADEMARKS.md).

## Further reading

- [CLI reference](cli-reference.md)
- [Getting started](getting-started.md)
- [Full product thesis](project-prokron-full-thesis-architecture-v2.md)
