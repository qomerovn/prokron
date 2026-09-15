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

## ADR-005: Keep adoption interviews provider-neutral and resumable
- Date: 2026-09-16
- Status: ACCEPTED
- Authority: product specification
- Supersedes: none
- Amends: none
- Corrects: none
- Rejects: none
- Affects: T-V02-03
- Context: Existing-project adoption needs a guided human interview without requiring model providers or treating a generated Markdown report as an input interface.
- Decision: Core exposes structured questions and answers, the CLI provides the guided interview, answers persist with provenance for deterministic resume, and INTERVIEW.md remains generated audit output.

## ADR-006: Make Core a deterministic state harness
- Date: 2026-09-16
- Status: ACCEPTED
- Authority: user-supplied deterministic state harness specification
- Supersedes: none
- Amends: ADR-001, ADR-005
- Corrects: none
- Rejects: none
- Affects: T-HARNESS-01
- Context: Semantic ranking and interviews grew inside adoption even though the current coding agent already owns repository understanding.
- Decision: Primary adoption accepts agent-authored structured state, validates it, records digest-bound human confirmation and publishes canonical state. Core owns deterministic facts and integrity; the agent owns semantics and questions. Preserve operational Markdown authority and store the reviewed adoption snapshot and checkpoint as JSON. Keep heuristic adoption and legacy migration behind explicit fallback.

## ADR-007: Remove semantic adoption fallback
- Date: 2026-09-16
- Status: ACCEPTED
- Authority: product owner
- Supersedes: none
- Amends: ADR-006
- Corrects: none
- Rejects: none
- Affects: T-HARNESS-01
- Context: The deterministic adoption path is proven and the retained semantic engine adds maintenance weight without serving the intended product architecture.
- Decision: Remove semantic ranking, generated interviews, and legacy import from the product and CLI. Git history remains the recovery path if a concrete compatibility need returns.

## ADR-008: Make Prokron an agent working convention
- Date: 2026-09-16
- Status: ACCEPTED
- Authority: product owner
- Supersedes: ADR-002, ADR-005, ADR-006
- Amends: ADR-001
- Corrects: none
- Rejects: none
- Affects: T-WORKFLOW-01
- Context: Capable agents already understand repositories and can maintain a project chronicle directly. The executable adoption and validation product obscures the useful behavior.
- Decision: Prokron consists of six Markdown chronicle files, shared agent instructions, and thin host-native command wrappers. New repositories derive their first task graph from a product specification; existing repositories begin with an empty chronicle and accumulate state during normal work. Agents maintain one active intent and checkpoint automatically before session or usage limits.

## ADR-009: Use a disposable shell bootstrap
- Date: 2026-09-16
- Status: ACCEPTED
- Authority: product owner request
- Supersedes: none
- Amends: ADR-008
- Corrects: none
- Rejects: none
- Affects: T-INSTALL-01
- Context: Manual copying makes the first Prokron session harder to start than the workflow itself.
- Decision: Provide one POSIX shell bootstrap that downloads and copies the static chronicle, workflows, and agent adapters into the current repository. It preserves existing chronicle and project instruction files and does not become an application runtime.
