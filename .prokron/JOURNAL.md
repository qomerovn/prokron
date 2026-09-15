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
