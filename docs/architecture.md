# Prokron architecture

Prokron keeps project meaning close to implementation reality. Its architecture
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
| `adoption.py` | Deterministic discovery, candidate reconstruction, review gates, and apply |
| `cli.py` | Argument parsing, command output, and exit-code policy |

Adapters remain thin instructions that call the same CLI. They do not implement
their own parser or project semantics.

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

Adoption discovers filenames and Git metadata without recursively interpreting
source code. It stages current-state candidates under `.prokron-adoption/` with
source classifications, per-domain coverage assessments, contextual interview
prompts, confidence labels, unknowns, conflicts, and a proposed baseline decision.
Operational confirmations are materialized in candidate tasks and intents;
governing confirmations are summarized by the baseline decision. Discovered
filenames remain distinct from content actually parsed. Only an explicit,
unblocked `prokron adopt --apply` promotes that directory to canonical `.prokron/`
state. Legacy sources remain evidence.

## License and trademarks

Prokron source code is distributed under the Apache License 2.0. The Prokron and
Qomero names and associated logos remain subject to the separate
[trademark policy](../TRADEMARKS.md).

## Further reading

- [CLI reference](cli-reference.md)
- [Getting started](getting-started.md)
- [Full product thesis](project-prokron-full-thesis-architecture-v2.md)
- [Adoption boundary supplement](prokron-thesis-supplement-adoption-boundary.md)
