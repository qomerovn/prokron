# Task Graph

Generated from `TASKS.md`; do not edit manually.

## Summary
- DONE: T-V01-01, T-V01-02, T-V01-03, T-V01-04, T-V01-05, T-V01-06, T-V011-01, T-V011-02, T-V02-01, T-V02-02
- WIP: none
- TODO: none
- BLOCKED: none
- Eligible now: none
- Blocked / waiting: none

## Tasks
- T-V01-01 [DONE] Harden typed parsers and integrity validation
  - depends on: none
  - unlocks: T-V01-02, T-V01-03
  - eligible: no
- T-V01-02 [DONE] Complete initialization and adoption
  - depends on: T-V01-01
  - unlocks: T-V01-04
  - eligible: no
- T-V01-03 [DONE] Complete deterministic context and checkpoint continuity
  - depends on: T-V01-01
  - unlocks: T-V01-04
  - eligible: no
- T-V01-04 [DONE] Add adapters and realistic example
  - depends on: T-V01-02, T-V01-03
  - unlocks: T-V01-05
  - eligible: no
- T-V01-05 [DONE] Validate and hand off v0.1
  - depends on: T-V01-04
  - unlocks: T-V01-06
  - eligible: no
- T-V01-06 [DONE] Publish Prokron identity and project documentation
  - depends on: T-V01-05
  - unlocks: T-V011-01
  - eligible: no
- T-V011-01 [DONE] Correct the governing license for the next release
  - depends on: T-V01-06
  - unlocks: T-V011-02
  - eligible: no
- T-V011-02 [DONE] Verify the v0.1.1 release artifact
  - depends on: T-V011-01
  - unlocks: T-V02-01
  - eligible: no
- T-V02-01 [DONE] Establish the adoption boundary
  - depends on: T-V011-02
  - unlocks: T-V02-02
  - eligible: no
- T-V02-02 [DONE] Align adoption semantics with the v2 supplement
  - depends on: T-V02-01
  - unlocks: none
  - eligible: no
