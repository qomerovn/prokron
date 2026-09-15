# Tasks

## T-001: Define the approval states
- Status: DONE
- Validation: SYNTHETIC
- Dependencies: none
- Owner: claude/session-1
- Claimed: 2026-09-13
- Acceptance: Draft, submitted, approved, and rejected states are documented.
- Evidence: docs/thesis.md
- Governed by: ADR-002

## T-002: Implement approval transitions
- Status: WIP
- Validation: SYNTHETIC
- Dependencies: T-001
- Owner: codex/session-2
- Claimed: 2026-09-14
- Acceptance: Valid transitions succeed and invalid transitions fail explicitly.
- Evidence: tests pending
- Governed by: ADR-002

## T-003: Write reviewer guidance
- Status: TODO
- Validation: UNTESTED
- Dependencies: T-001
- Owner:
- Claimed:
- Acceptance: A reviewer can approve or reject without reading implementation code.
- Evidence:
- Governed by: ADR-002

## T-004: Validate the end-to-end workflow
- Status: TODO
- Validation: UNTESTED
- Dependencies: T-002, T-003
- Owner:
- Claimed:
- Acceptance: The full approval scenario passes from draft through final review.
- Evidence:
- Governed by: ADR-003
