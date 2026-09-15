# Deterministic state harness

## Audit and governing boundary

This specification supersedes semantic adoption requirements in the earlier
thesis supplement. The coding agent interprets the repository, scopes authority,
identifies active work, proposes next actions, and asks material questions.
Core validates and preserves the submitted state without interpreting prose.

| Classification | Existing code | Treatment |
|---|---|---|
| KEEP | `models.py`, `markdown.py`, `core.py` | Typed operational state, parsing, dependency and decision lineage validation |
| KEEP | `rendering.py`, `operations.py` | Derived views, bootstrap, task claims, intent and journal checkpoints |
| REFACTOR | `cli.py` | Agent adoption becomes the default; explicit fallback dispatch |
| REFACTOR | Git helpers and canonical serialization in adoption | Extract deterministic seams; no Core imports from fallback |
| DEMOTE_TO_FALLBACK | Source classification/ranking, concept matching, domain assessment, interview generation and semantic materialization | Retain under `fallback/adoption.py` |
| LEGACY_ADAPTER | Structured handoff selection/import in the old adoption engine | Retain with fallback; preserve source files |
| DELETE_LATER | Semantic ranking, summaries, question/default heuristics | Remove only when the optional fallback is retired |
| UNCERTAIN | Fallback legacy payload carry-through for incompatible task tables | Known existing dogfood failure; excluded from primary ingestion |

Audit evidence: the original adoption module contained 2,061 lines and imported
the deterministic modules; none of those modules imported adoption. The CLI
eagerly imported adoption. Existing canonical models already cover task edges,
decision relationships, intents and journal history. There was no candidate JSON
schema or repository checkpoint freshness guard. All 52 original tests passed.
Existing uncommitted navigation-regression work is preserved in fallback.

## Resulting flow

```text
coding agent: native repository inspection, semantic reasoning, human questions
  -> adopt prepare / schema
  -> agent-authored JSON candidate
  -> adopt ingest (schema + existing graph validation; staged review)
  -> human reviews/corrects
  -> adopt confirm (reviewed digest + human identity)
  -> adopt apply (revalidate + freshness + confirmation)
  -> .prokron/ -> resume / next / checkpoint

CLI -> adoption protocol -> candidate schema + repository facts
                        -> existing models / validation / rendering / operations
CLI -> explicit adopt fallback -> heuristic engine + legacy importer
```

No provider calls or semantic scanning belong in the primary path. Unknowns are
valid state; confirming a candidate accepts its recorded uncertainty and does
not silently turn inferred statements into observed or confirmed facts.

## Lifecycle

ADOPT establishes a reviewed baseline. WORK updates canonical tasks, decisions
and intent. Checkpoint records the agent's stopping point and repository facts.
RESUME loads baseline plus current operational state from `.prokron/`.

Future SYNC uses deterministic changes since the checkpoint, interpreted by the
agent, followed by a validated structured update. No semantic diff engine is
planned. Until that update protocol exists, the agent reviews changes, updates
canonical Markdown and checkpoints its intent. Baseline-wide revisions need a
future structured sync operation; a checkpoint does not rewrite baseline claims.

## Verification and remaining debt

The acceptance suite creates a brownfield Git repository with only source code,
submits an agent-authored candidate, confirms its digest, and applies it. A new
CLI process then recovers objective, work, task dependencies, blockers, governing
decision lineage, constraints, validation, uncertainty and exact next action.
It also verifies candidate rejection, confirmation invalidation, bootstrap
rollback, empty work, and staleness after dirty changes and new commits. Boundary
tests fail if primary adoption calls the heuristic engine or imports fallback.

The full suite passes, including all 52 existing regressions moved to explicit
fallback where necessary. Ruff and strict mypy pass. Wheel and source
archive builds and clean installed-wheel adoption/resume checks pass.
This proves process/session independence; a live cross-model human interview was
not exercised.

Remaining debt is confined to the retained fallback: the known incompatible
legacy task-table payload issue is not repaired by this extraction. The fallback
ranking and interview code remains live behind its explicit command, so it is
not dead code and was not deleted. Structured baseline-wide SYNC is a future
protocol operation, as scoped above.
