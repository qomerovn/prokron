# Intents

## T-002
- Owner: codex/session-2
- Updated: 2026-09-15
- Goal: Implement deterministic approval transitions.
- Current point: Transition table exists; invalid-transition errors remain untested.
- Constraints: Preserve the four states in ADR-002
- Changed files: src/workflow.py, tests/test_workflow.py
- Next action: Add invalid-transition checks and run the workflow tests.
