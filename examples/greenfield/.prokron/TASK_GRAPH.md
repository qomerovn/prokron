# Task Graph

Generated from `TASKS.md`; do not edit manually.

## Summary
- DONE: T-001
- WIP: T-002
- TODO: T-003, T-004
- BLOCKED: none
- Eligible now: T-003
- Blocked / waiting: T-004

## Tasks
- T-001 [DONE] Define the approval states
  - depends on: none
  - unlocks: T-002, T-003
  - eligible: no
- T-002 [WIP] Implement approval transitions
  - depends on: T-001
  - unlocks: T-004
  - eligible: no
- T-003 [TODO] Write reviewer guidance
  - depends on: T-001
  - unlocks: T-004
  - eligible: yes
- T-004 [TODO] Validate the end-to-end workflow
  - depends on: T-002, T-003
  - unlocks: none
  - eligible: no
