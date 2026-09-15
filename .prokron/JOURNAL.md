# Journal

## 2026-09-15 — v0.1 implementation resumed
- Task: T-V01-01
- Owner: codex/primary
- Did: Read the authoritative thesis and implementation brief; inventoried the partial CLI.
- Validation: Existing end-to-end test passed before the v0.1 hardening work.
- Learned: The repository has a useful vertical slice but lacks strict parsers, full integrity checks, idempotent bootstrap, checkpoint, adoption, adapters, and a realistic fixture.
- Left mid-air: Typed parser and integrity implementation is about to begin.
- Next: Claim T-V01-01 and replace permissive parsing with typed deterministic canonical parsing.

## 2026-09-15T09:14:41Z — T-V01-01
- Task: T-V01-01
- Owner: codex/primary
- Did: Added typed task, decision, intent, and journal models; strict Markdown parsers; validation; deterministic renderers; and required core tests.
- Validation: 14 unittest cases pass; compileall passes.
- Learned: Strict one-line canonical fields keep Markdown deterministic while fenced examples remain safe.
- Left mid-air: Core parsing and integrity are complete; initialization and adoption remain.
- Next: Complete idempotent init/adopt and managed bootstrap validation.

## 2026-09-15T09:15:15Z — T-V01-02
- Task: T-V01-02
- Owner: codex/primary
- Did: Completed idempotent init/adopt, packaged templates, and managed AGENTS.md/CLAUDE.md bootstrap installation that preserves custom content.
- Validation: 15 unittest cases pass; repeated init and adoption checked in temporary Git repositories.
- Learned: Adoption can safely initialize explicit empty state without pretending to reconstruct missing history.
- Left mid-air: Initialization and adoption are complete; context/checkpoint continuity remains.
- Next: Claim T-V01-03 and validate deterministic context and checkpoint edge cases.

## 2026-09-15T09:16:20Z — T-V01-03
- Task: T-V01-03
- Owner: codex/primary
- Did: Completed deterministic context traversal and resumable checkpoint updates with append-only Journal entries and input validation before mutation.
- Validation: 15 unittest cases pass, including context minimality, append preservation, invalid checkpoint rollback behavior, and refreshed doctor state.
- Learned: One-line CLI validation is necessary because command values are written directly into canonical Markdown.
- Left mid-air: Context and checkpoint are complete; adapters and the checked-in realistic example remain.
- Next: Close T-V01-03, claim T-V01-04, add thin adapters, and generate the example derived files.

## 2026-09-15T09:17:33Z — T-V01-04
- Task: T-V01-04
- Owner: codex/primary
- Did: Added thin Codex, Claude, and generic CLI adapters plus a realistic greenfield fixture with decision lineage, parallel work, active intent, journal handoff, and generated views.
- Validation: 16 unittest cases pass; example prokron doctor reports healthy; generated graph identifies T-003 as independently eligible.
- Learned: Bootstrap instructions are sufficient adapters for v0.1 because every semantic operation remains in the shared CLI core.
- Left mid-air: Adapters and example are complete; final architecture cleanup, build checks, documentation, and handoff remain.
- Next: Close T-V01-04, claim T-V01-05, split the oversized core module, run all release checks, and leave the final checkpoint.

## 2026-09-15T09:24:05Z — T-V01-05
- Task: T-V01-05
- Owner: codex/primary
- Did: Completed v0.1: typed canonical models and parsers, integrity engine, deterministic graph/state/context, init/adopt/bootstrap, checkpoint continuity, thin adapters, realistic fixture, documentation, packaging, and release tooling.
- Validation: Ruff passes; strict mypy passes for 8 source files; 17 unittest cases pass; wheel and sdist build; built wheel passes init, doctor, graph, status, next, and repeated init in a clean Git fixture; example doctor passes.
- Learned: The smallest viable architecture is four boundaries: canonical parsing, integrity core, deterministic rendering, and lifecycle operations behind one CLI.
- Left mid-air: No v0.1 implementation work remains; release artifacts are built locally and the repository has not been committed or published.
- Next: Review the v0.1 CLI, then commit or publish it when approved; begin v0.2 only after real protocol feedback.

## 2026-09-15 — T-V01-06
- Task: T-V01-06
- Owner: codex/primary
- Did: Standardized all product identifiers as Prokron and added a GitHub README, tutorial, CLI reference, and architecture guide.
- Validation: Legacy-name scan is empty; Ruff, strict mypy, 26 unittests, package build, CLI health checks, and documentation link checks pass.
- Learned: A short README plus three focused documents keeps the public entry point readable while preserving complete operational detail.
- Left mid-air: Implementation and documentation are verified; commits and the initial remote push remain.
- Next: Commit the implementation and documentation, then push main to the Prokron repository.

## 2026-09-15 — T-V011-01
- Task: T-V011-01
- Owner: codex/primary
- Did: Changed the next release to Apache-2.0, added NOTICE and trademark policy, documented the v0.1 MIT history, and audited package metadata and contributors.
- Validation: Canonical license text and 0.1.1 artifact payloads match; Ruff, strict mypy, 26 unittests, package build, and Prokron doctor pass.
- Learned: Main history has one project-owner author identity and a Codex co-author trailer on the substantive v0.1 commit; no external human or vendored code license was found.
- Left mid-air: No licensing implementation remains; legal ownership cannot be proven from Git metadata alone.
- Next: Review and publish v0.1.1 without modifying the historical v0.1 artifacts or license grant.

## 2026-09-15 — T-V011-02
- Task: T-V011-02
- Owner: codex/primary
- Did: Added the missing installed-version command, rebuilt wheel and sdist artifacts, and ran clean-room initialization, idempotency, and adoption workflows outside the source checkout.
- Validation: Ruff, strict mypy, 27 unittests, build, doctor, offline wheel install, sdist install, fresh repository workflow, and three-commit adoption all pass.
- Learned: Release validation must invoke the installed console script because source tests did not expose the missing --version interface.
- Left mid-air: Verification is complete; GitHub release publishing is unavailable because the configured gh tokens are invalid.
- Next: Re-authenticate gh, push the verified commit, and create the v0.1.1 release with both artifacts.

## 2026-09-15T11:17:17Z — T-V02-01
- Task: T-V02-01
- Owner: codex/primary
- Did: Added deterministic adoption discovery and source classification, non-canonical candidate state, explicit confidence and provenance, targeted confirmation, legacy handoff import, a baseline decision, and guarded apply.
- Validation: 29 unittests, Ruff, strict mypy, isolated-output package build, installed-wheel dry-run smoke test, and Prokron doctor pass.
- Learned: Filename discovery can bound retrieval, but architecture prose must remain unknown until a human confirms it; source priority alone cannot establish authority.
- Left mid-air: Adoption-boundary implementation is complete; no candidate or canonical project state was changed by the live dry-run.
- Next: Exercise the adoption workflow on real external repositories before expanding semantic extraction.

## 2026-09-15T11:40:11Z — T-V02-02
- Task: T-V02-02
- Owner: codex/primary
- Did: Replaced presence-only coverage and generic questions with a fixed evidence-backed coverage schema, contextual structured prompts, conditional and optional domain semantics, canonical operational materialization, and honest discovery-versus-inspection reporting.
- Validation: 33 unittests, Ruff, strict mypy, isolated wheel/sdist build, installed-wheel dry-run smoke test, Git diff check, and Prokron doctor pass.
- Learned: Human confirmation is useful only when its operational effects enter canonical tasks and intents; optional history can remain explicitly unknown without blocking adoption.
- Left mid-air: The requested v2 semantic remediation is complete; broader semantic interpretation remains intentionally external to Core.
- Next: Validate the bounded heuristics and structured interview handoff against real existing repositories.

## 2026-09-16 — T-V02-03
- Task: T-V02-03
- Owner: codex/primary
- Did: Added a guided six-domain adoption interview, persisted resumable answers with human-confirmation provenance, structured JSON question and answer primitives for agents, and canonical materialization of confirmed operational state.
- Validation: Ruff, strict mypy, 49 unittests, wheel/sdist build, installed-wheel non-interactive and interactive adoption, apply and doctor smoke tests, K-Ledger dogfood, and Git diff check pass.
- Learned: A generated interview report is useful audit evidence, while stable structured primitives are the safer interface for both humans and agents.
- Left mid-air: The validated implementation and documentation remain uncommitted as requested.
- Next: Review the diff and commit only when explicitly approved.

## 2026-09-15T17:51:16Z — T-V02-03
- Task: T-V02-03
- Owner: codex/primary
- Did: Committed the interactive adoption interview as cb65c19 and pushed it to origin/main.
- Validation: The push advanced origin/main from b37a29f to cb65c19; the worktree was clean immediately afterward.
- Learned: Publication completed without changing the validated implementation.
- Left mid-air: Only this Prokron continuity update remains uncommitted.
- Next: Begin new work from the current clean implementation baseline; commit this state reconciliation when approved.

## 2026-09-15T18:03:04Z — T-V02-04
- Task: T-V02-04
- Owner: codex/primary
- Did: Replaced six current-state forms with one default-preserving proposal, made selective active-work edits retain inferred identity fields, removed adoption/interview ownership, separated recent commit evidence from execution point, and tightened agent adapter guidance.
- Validation: Ruff, strict mypy, 51 unittests, wheel/sdist build, installed-wheel K-Ledger grouped-confirmation and apply smoke tests, Prokron doctor, and Git diff check pass.
- Learned: Conservative defaults let one explicit human confirmation establish several related domains without moving validation or authority into adapters.
- Left mid-air: The validated UX refinement and its Prokron checkpoint remain uncommitted as requested.
- Next: Review the grouped K-Ledger interaction and commit only when explicitly approved.

## 2026-09-16 — T-V02-05
- Task: T-V02-05
- Owner: codex/primary
- Did: Reproduced and fixed Markdown navigation being inferred as a next action, added a focused regression, and reran the real K-Ledger grouped proposal without supplying human answers.
- Validation: Ruff, strict mypy, 52 unittests, and Git diff check pass; K-Ledger now reports its next safe action as unknown.
- Learned: Planning-document summaries require executable verb semantics before they can become an action hypothesis.
- Left mid-air: K-Ledger confirmation, apply, continuity validation, distribution gates, final commit, and push remain.
- Next: Ask the developer to confirm or correct the grouped proposal and provide the exact next safe action.

## 2026-09-16 — T-V02-05 K-Ledger apply failure
- Task: T-V02-05
- Owner: codex/primary
- Did: Persisted all six human confirmations, applied the K-Ledger candidate, ran doctor, status, next, and an isolated fresh-agent continuity read.
- Validation: Apply, doctor, status, next, build, installed-wheel generic smoke, and state recovery pass; no-history-reconstruction fails because canonical TASKS.md contains roughly 128 legacy table rows while the parsed graph contains one task.
- Learned: A legacy file can parse as zero canonical records yet still be carried forward as canonical Markdown when unrelated fenced content bypasses the incompatibility guard.
- Left mid-air: K-Ledger now has an applied .prokron directory exhibiting this continuity defect; Prokron closure remains uncommitted.
- Next: Prevent zero-record legacy payloads from becoming canonical text, add a regression, then rerun adoption from a clean K-Ledger pre-adoption state only with explicit authorization for that reset.

## 2026-09-15T19:17:06.221046+00:00 — deterministic harness extraction
- Task: T-HARNESS-01
- Owner: codex/primary
- Did: Audited module boundaries and implemented agent-authored adoption while demoting the existing heuristic engine to explicit fallback.
- Validation: 68 unittests, Ruff and strict mypy pass; artifact build pending.
- Learned: Existing deterministic models, graph validation, parsers and lifecycle operations were separable; a wholesale rewrite was unnecessary.
- Left mid-air: Package verification and final acceptance record remain. T-V02-05 is prior fallback dogfood work; its existing edits and failure evidence are preserved.
- Next: Verify the installed artifact and finalize T-HARNESS-01.

## 2026-09-15T19:17:06.221310+00:00 — deterministic harness acceptance
- Task: T-HARNESS-01
- Owner: codex/primary
- Did: Completed the agent-driven primary path, explicit fallback extraction, provider-neutral adapters, and continuity acceptance checks on refactor/deterministic-state-harness.
- Validation: 68 unittests, Ruff, strict mypy, wheel/sdist build, clean installed-wheel brownfield adoption and fresh-process resume, stale-state rejection, fallback import, and Git diff check pass on 2026-09-16.
- Learned: Fresh-process continuity succeeds from the canonical snapshot and operational Markdown; no repository rediscovery is required. A live cross-model human interview was not exercised.
- Left mid-air: Implementation is complete and uncommitted for branch review. Prior T-V02-05 dogfood is blocked/deferred because its remaining incompatible-table issue is now confined to optional fallback. Existing navigation fix and regression are preserved there.
- Next: Review the deterministic harness branch; address fallback legacy payload carry-through only if that importer is needed.

### Preserved prior T-V02-05 intent

```text
- Owner: codex/primary
- Updated: 2026-09-16
- Goal: Close Adoption Boundary only after the real K-Ledger adoption and continuity checks pass.
- Current point: Next-action inference and the K-Ledger apply flow pass, but adoption copied the legacy tabular task board into canonical TASKS.md even though zero legacy tasks were imported.
- Constraints: do not fabricate confirmation, do not weaken the apply guard, do not commit before end-to-end passage
- Changed files: src/prokron/adoption.py, tests/test_adoption.py
- Next action: Fix empty or incompatible legacy state payload carry-through before rerunning K-Ledger adoption from a clean pre-adoption state.
```

## 2026-09-15T19:23:58.545428+00:00 — deterministic harness cleanup
- Task: T-HARNESS-02
- Owner: codex/primary
- Did: Reused validated snapshots through apply/next/resume, moved Markdown renderers into rendering.py, reused schema definitions and replaced the suppressed candidate-conversion type error with typed record conversion.
- Validation: 69 tests, Ruff, strict mypy, doctor, and synced CodeGraph status pass.
- Learned: CodeGraph confirmed that next and resume reached publication-only Markdown round-trip validation through adopted_state; reads now use schema and graph validation while ingest and apply retain the round trip.
- Left mid-air: Cleanup complete; branch changes remain uncommitted. CodeGraph 1.6.0 is installed, connected to Codex, and its 19-file project index is current.
- Next: Review and commit the deterministic harness branch.

## 2026-09-15T20:46:18+00:00 — semantic fallback removal
- Task: maintenance/fallback-removal
- Owner: codex/primary
- Did: Removed the semantic adoption engine, fallback CLI, legacy tests, and superseded adoption supplement; compacted deterministic docs and CLI tests.
- Validation: 50 tests, Ruff, strict mypy, wheel/sdist build, doctor, Git diff check, and synced CodeGraph status pass.
- Learned: The deterministic harness fully replaces the semantic fallback; no source or test callers remain.
- Left mid-air: Local main is ready to push after explicit approval for the GitHub destination.
- Next: Push local main to the approved origin.

## 2026-09-15T21:17:27+00:00 — workflow-only rebuild
- Task: T-WORKFLOW-01
- Owner: codex/primary
- Did: Rebuilt Prokron as a six-file project chronicle with two entry modes, five agent workflows, a Codex skill, Claude slash commands, and automatic checkpoint instructions; removed the Python runtime, package, tests, adoption artifacts, and obsolete specifications.
- Validation: New- and existing-repository template smoke checks, README link checks, Codex skill metadata validation, requirement scans, and Git whitespace checks pass.
- Learned: The K-Ledger handoff confirms that task dependencies, one live intent, decision lineage, current state, and a concise session diary are sufficient for useful human and agent continuity.
- Left mid-air: Nothing. The working tree is ready for commit.
- Next: Use the workflow in a real project and refine only from observed friction.

## 2026-09-16 — GitHub documentation rewrite
- Task: T-DOCS-01
- Owner: codex/primary
- Did: Rewrote the README and specification around the six-file chronicle, the two entry modes, exact Claude and Codex commands, automatic checkpoints, and the workflow-only product boundary.
- Validation: All 10 README links resolve; requirement and repository-shape checks pass; Git reports no changes to LICENSE, NOTICE, or TRADEMARKS.md and no whitespace errors.
- Learned: The GitHub entry point is clearest when it explains the task graph and decision lineage first, then installation and commands.
- Left mid-air: Nothing.
- Next: Use Prokron in a real repository and change the workflow only when observed use reveals friction.

## 2026-09-16 — one-command bootstrap
- Task: T-INSTALL-01
- Owner: codex/primary
- Did: Added one POSIX shell bootstrap that installs the chronicle, workflows, Codex skill, Claude commands, and managed agent instructions; documented one-line new and existing repository setup.
- Validation: POSIX syntax and installer smoke checks pass for both modes, all copied assets, repeat installation, state and instruction preservation, and invalid input; documentation links, legal-file preservation, and Git whitespace checks pass.
- Learned: Installation needs one disposable copier; the working product remains the Markdown chronicle and agent instructions.
- Left mid-air: Nothing.
- Next: Run the published curl command from a real target repository and begin with the printed agent command.
