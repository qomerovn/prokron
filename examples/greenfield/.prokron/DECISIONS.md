# Decisions

## ADR-001: Allow free-form workflow states
- Date: 2026-09-13
- Status: SUPERSEDED
- Authority: product owner
- Supersedes: none
- Amends: none
- Corrects: none
- Rejects: none
- Affects: T-001
- Context: The prototype initially optimized for flexibility.
- Decision: Store arbitrary state names.

## ADR-002: Use four explicit approval states
- Date: 2026-09-14
- Status: ACCEPTED
- Authority: product owner
- Supersedes: ADR-001
- Amends: none
- Corrects: none
- Rejects: none
- Affects: T-001, T-002, T-003
- Context: Review evidence showed free-form names made eligibility ambiguous.
- Decision: Use draft, submitted, approved, and rejected as the complete state set.

## ADR-003: Require reviewer guidance before validation
- Date: 2026-09-14
- Status: ACCEPTED
- Authority: product owner
- Supersedes: none
- Amends: ADR-002
- Corrects: none
- Rejects: none
- Affects: T-004
- Context: End-to-end validation needs a human-readable review contract.
- Decision: Complete reviewer guidance before validating the whole workflow.
