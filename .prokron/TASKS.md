# Tasks

## T-V01-01: Harden typed parsers and integrity validation
- Status: DONE
- Validation: SYNTHETIC
- Dependencies: none
- Owner: codex/primary
- Claimed: 2026-09-15
- Acceptance: Typed task, decision, intent, and journal parsing rejects malformed canonical state and all required integrity tests pass.
- Evidence: 14 unittest cases and compileall passed on 2026-09-15.
- Governed by: ADR-001, ADR-002

## T-V01-02: Complete initialization and adoption
- Status: DONE
- Validation: SYNTHETIC
- Dependencies: T-V01-01
- Owner: codex/primary
- Claimed: 2026-09-15
- Acceptance: Init and adopt safely install templates and managed bootstrap blocks and repeated init is idempotent.
- Evidence: 15 unittest cases plus live repeated init/adopt checks passed on 2026-09-15.
- Governed by: ADR-001

## T-V01-03: Complete deterministic context and checkpoint continuity
- Status: DONE
- Validation: SYNTHETIC
- Dependencies: T-V01-01
- Owner: codex/primary
- Claimed: 2026-09-15
- Acceptance: Context is minimal and checkpoint updates live intent while appending a resumable Journal entry.
- Evidence: Context and checkpoint integration checks passed in tests/test_cli.py on 2026-09-15.
- Governed by: ADR-001

## T-V01-04: Add adapters and realistic example
- Status: DONE
- Validation: SYNTHETIC
- Dependencies: T-V01-02, T-V01-03
- Owner: codex/primary
- Claimed: 2026-09-15
- Acceptance: Thin Claude, Codex, and generic adapters exist and one realistic example passes integration validation.
- Evidence: Example doctor and 16 unittest cases passed on 2026-09-15.
- Governed by: ADR-001

## T-V01-05: Validate and hand off v0.1
- Status: DONE
- Validation: SYNTHETIC
- Dependencies: T-V01-04
- Owner: codex/primary
- Claimed: 2026-09-15
- Acceptance: Tests, build, CLI fixture, Prokron doctor, generated state, and final checkpoint all pass.
- Evidence: Ruff, strict mypy, 17 unittests, wheel/sdist build, clean-wheel milestone fixture, and example doctor passed on 2026-09-15.
- Governed by: ADR-001

## T-V01-06: Publish Prokron identity and project documentation
- Status: DONE
- Validation: SYNTHETIC
- Dependencies: T-V01-05
- Owner: codex/primary
- Claimed: 2026-09-15
- Acceptance: Product identifiers are consistent and GitHub readers can install, use, understand, and verify the project from linked documentation.
- Evidence: Legacy-name scan is empty; Ruff, strict mypy, 26 unittests, package build, CLI health checks, and documentation link checks pass.
- Governed by: ADR-001, ADR-003

## T-V011-01: Correct the governing license for the next release
- Status: DONE
- Validation: SYNTHETIC
- Dependencies: T-V01-06
- Owner: codex/primary
- Claimed: 2026-09-15
- Acceptance: Version 0.1.1 package metadata, repository documentation, and release artifacts consistently use Apache-2.0 while the v0.1 MIT history remains explicit and unchanged.
- Evidence: Canonical Apache-2.0 text verified; 0.1.1 wheel metadata reports License-Expression Apache-2.0 and includes LICENSE, NOTICE, and TRADEMARKS.md; Ruff, strict mypy, 26 unittests, package build, and Prokron doctor pass.
- Governed by: ADR-004

## T-V011-02: Verify the v0.1.1 release artifact
- Status: DONE
- Validation: SYNTHETIC
- Dependencies: T-V011-01
- Owner: codex/primary
- Claimed: 2026-09-15
- Acceptance: A clean isolated installation from the v0.1.1 artifact reports the correct version and passes fresh init, idempotency, core commands, and existing-project adoption without source-checkout dependencies.
- Evidence: 27 unittests, Ruff, strict mypy, build, and doctor pass; clean wheel and sdist installations report 0.1.1; fresh init, repeat init, status, next, graph, and three-commit adoption smoke tests pass outside the source checkout.
- Governed by: ADR-004

## T-V02-01: Establish the adoption boundary
- Status: DONE
- Validation: SYNTHETIC
- Dependencies: T-V011-02
- Owner: codex/primary
- Claimed: 2026-09-15
- Acceptance: Adoption deterministically discovers and classifies current-state evidence, stages an auditable candidate without changing canonical state, preserves uncertainty and provenance, and applies only after explicit approval.
- Evidence: 29 unittests, Ruff, strict mypy, package build in an isolated output directory, installed-wheel dry-run smoke test, and Prokron doctor pass on 2026-09-15.
- Governed by: ADR-001

## T-V02-02: Align adoption semantics with the v2 supplement
- Status: DONE
- Validation: SYNTHETIC
- Dependencies: T-V02-01
- Owner: codex/primary
- Claimed: 2026-09-15
- Acceptance: Adoption uses explicit evidence-backed domain assessments and contextual prompts, covers conditional and optional domains correctly, materializes confirmed operational state, and reports discovery separately from inspected content.
- Evidence: 33 unittests, Ruff, strict mypy, isolated wheel/sdist build, installed-wheel dry-run smoke test, Git diff check, and Prokron doctor pass on 2026-09-15.
- Governed by: ADR-001

## T-V02-03: Add the interactive adoption interview
- Status: DONE
- Validation: SYNTHETIC
- Dependencies: T-V02-02
- Owner: codex/primary
- Claimed: 2026-09-16
- Acceptance: Adoption provides a guided resumable interview, provider-neutral structured question and answer primitives, evidence-backed human confirmation, and guarded materialization without weakening non-interactive adoption.
- Evidence: Ruff, strict mypy, 49 unittests, wheel/sdist build, installed-wheel non-interactive and interactive adoption, apply and doctor smoke tests, K-Ledger six-question dogfood, and Git diff check passed; commit cb65c19 was pushed to origin/main on 2026-09-16.
- Governed by: ADR-001, ADR-005

## T-V02-04: Consolidate the current-state adoption review
- Status: DONE
- Validation: SYNTHETIC
- Dependencies: T-V02-03
- Owner: codex/primary
- Claimed: 2026-09-16
- Acceptance: A six-blocker adoption presents one default-preserving current-state proposal, supports selective correction, keeps agent adapters conversational and thin, and preserves structured Core validation, provenance, resume, and apply behavior.
- Evidence: Ruff, strict mypy, 51 unittests, wheel/sdist build, installed-wheel K-Ledger grouped-confirmation and apply smoke tests, Prokron doctor, and Git diff check passed on 2026-09-16.
- Governed by: ADR-005

## T-V02-05: Close Adoption Boundary dogfood
- Status: BLOCKED
- Validation: SYNTHETIC
- Dependencies: T-V02-04
- Owner: codex/primary
- Claimed: 2026-09-16
- Acceptance: Navigation content is never inferred as a next action, real K-Ledger adoption applies only confirmed state, all release gates pass, and a fresh agent can recover current truth from the adopted Prokron state alone.
- Evidence: Navigation regression, grouped interview regressions, Ruff, strict mypy, 52 unittests, wheel/sdist build, installed-wheel generic smoke, and Git diff check pass. Real K-Ledger apply, doctor, status, and next pass, but canonical TASKS.md copied roughly 128 inert legacy rows despite importing zero tasks; fresh-agent continuity therefore fails the no-reconstruction requirement.
- Governed by: ADR-005

## T-HARNESS-01: Extract the deterministic state harness
- Status: DONE
- Validation: SYNTHETIC
- Dependencies: none
- Owner: codex/primary
- Claimed: 2026-09-16
- Acceptance: Agent-authored brownfield candidates validate and require digest-bound human confirmation before publication; semantic heuristics are explicit fallback; fresh-process resume preserves current state; stale next actions are rejected; existing deterministic integrity and fallback regressions pass.
- Evidence: 68 unittests, Ruff, strict mypy, wheel/sdist build, clean installed-wheel brownfield adoption and fresh-process resume, stale-state rejection, fallback import, and Git diff check pass on 2026-09-16.
- Governed by: ADR-006

## T-HARNESS-02: Clean up the deterministic adoption implementation
- Status: DONE
- Validation: SYNTHETIC
- Dependencies: T-HARNESS-01
- Owner: codex/primary
- Claimed: 2026-09-16
- Acceptance: Remove redundant adoption reads and validation, centralize rendering and confirmation schema, and preserve CLI behavior and integrity checks.
- Evidence: The full suite, Ruff, strict mypy, doctor, build, and CodeGraph status pass. CodeGraph traced the primary adoption path and verified the index is current. Read paths skip publication-only Markdown round trips.
- Governed by: ADR-006
