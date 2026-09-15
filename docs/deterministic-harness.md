# Deterministic state harness

## Boundary

The coding agent interprets the repository, scopes authority, identifies active
work, proposes next actions, and asks material questions. Prokron validates and
preserves the submitted state without interpreting repository prose.

| Classification | Code | Treatment |
|---|---|---|
| KEEP | `models.py`, `markdown.py`, `core.py` | Operational state, parsing, graph and lineage validation |
| KEEP | `rendering.py`, `operations.py` | Views, bootstrap, task claims, intent and checkpoints |
| REFACTOR | `adoption.py`, `candidate.py`, `repository.py`, `persistence.py` | Deterministic protocol, validation, freshness and publication |
| DELETE | Semantic ranking, interviews and legacy import | Removed from the product and CLI |

## Adoption flow

```text
coding agent: inspect repository, reason, ask material questions
  -> adopt prepare / schema
  -> agent-authored JSON candidate
  -> adopt ingest (schema + graph validation)
  -> human reviews or corrects
  -> adopt confirm (digest + human identity)
  -> adopt apply (revalidate + freshness + confirmation)
  -> .prokron/ -> resume / next / checkpoint
```

Unknowns remain valid state. Confirmation accepts recorded uncertainty; it does
not silently upgrade inferred claims. Core performs no provider calls, semantic
repository scanning, filename ranking, or question generation.

## Lifecycle

ADOPT establishes a reviewed baseline. WORK updates canonical tasks, decisions
and intent. CHECKPOINT records the stopping point and repository facts. RESUME
loads the approved baseline plus current operational state.

Future SYNC should follow the same boundary: Prokron provides deterministic delta
facts, the agent interprets them, and Core validates the proposed update. Until
then, the agent reviews changes, updates canonical Markdown, and checkpoints the
active intent.

## Verification

The acceptance suite creates a brownfield Git repository containing only source
code, submits an agent-authored candidate, confirms its digest, and applies it.
A new CLI process recovers objective, work, dependencies, blockers, decisions,
constraints, validation, uncertainty, and the exact next action. The suite also
covers invalid candidates, confirmation invalidation, atomic publication and
rollback, empty work, checkpoint freshness, and bootstrap preservation.

Structured baseline-wide SYNC remains future work. No semantic fallback remains.
