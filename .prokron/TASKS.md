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
