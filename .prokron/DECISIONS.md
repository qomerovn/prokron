# Decisions

## ADR-001: Use repository-native Markdown as authority
- Date: 2026-09-15
- Status: ACCEPTED
- Authority: product thesis
- Supersedes: none
- Amends: none
- Corrects: none
- Rejects: none
- Affects: T-V01-01, T-V01-02, T-V01-03, T-V01-04, T-V01-05
- Context: Prokron state must remain human-readable, AI-readable, Git-diffable, local, and visible.
- Decision: Canonical state is Markdown under .prokron; structured objects exist only in process and derived files are regenerated.

## ADR-002: Implement v0.1 with Python standard library
- Date: 2026-09-15
- Status: ACCEPTED
- Authority: implementation agent
- Supersedes: none
- Amends: none
- Corrects: none
- Rejects: none
- Affects: T-V01-01, T-V01-02, T-V01-03
- Context: The greenfield repository has Python 3.14 and no established application stack.
- Decision: Use typed Python dataclasses and the standard library only; keep the persistence format reversible and dependency-free.

## ADR-003: Standardize product identifiers as Prokron
- Date: 2026-09-15
- Status: ACCEPTED
- Authority: product owner
- Supersedes: none
- Amends: none
- Corrects: none
- Rejects: none
- Affects: T-V01-06
- Context: The repository, Python package, command, and state directory need one consistent public identity.
- Decision: Use Prokron, prokron, and .prokron for all product, executable, package, and protocol identifiers.

## ADR-004: Distribute future releases under Apache-2.0
- Date: 2026-09-15
- Status: ACCEPTED
- Authority: product owner
- Supersedes: none
- Amends: none
- Corrects: none
- Rejects: none
- Affects: T-V011-01
- Context: The published v0.1 release used MIT even though Apache-2.0 was intended; that historical grant and its artifacts must remain intact.
- Decision: Beginning with v0.1.1, distribute Prokron code under Apache-2.0 while keeping Prokron, Qomero, and associated logos subject to a separate trademark policy.
