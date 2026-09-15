Prokron Thesis Supplement

Adoption Boundary, Current-State Reconstruction, and Developer Interview

Status: Proposed thesis addition
Target: Post-v0.1 / candidate for v0.2
Implementation status: Not assumed implemented
Related thesis sections: Existing Project Adoption, Context Packs, Reconciliation, Project Drift, Authority Model

Specification completeness contract: This document is complete only if it ends with the literal marker PROKRON_ADOPTION_SPEC_EOF_v2. If that marker is absent, treat the specification as truncated and do not invent missing semantics.

1. Problem

Existing software projects often contain years of accumulated implementation history:

source code;

Git commits;

old branches;

architecture documents;

issue trackers;

task files;

ADRs;

handoff notes;

migration records;

test suites;

CI configuration;

deployment evidence;

abandoned approaches;

superseded decisions.

A naïve adoption strategy would attempt to reconstruct the entire history before Prokron can become useful.

That is the wrong requirement.

For a large project, complete historical reconstruction is expensive, ambiguous, token-intensive, and frequently impossible.

A project may contain:

hundreds of commits
+ tens of thousands of lines of code
+ years of documentation
+ stale task files
+ conflicting architecture notes
+ undocumented human decisions

No agent should be required to understand all of this before Prokron can establish useful project state.

The adoption problem is therefore not:

How can Prokron reconstruct everything that ever happened?

The correct question is:

What must Prokron know to establish trustworthy current project truth from this point forward?

2. Core Principle

Adopt the present. Preserve the future. Retrieve the past only when necessary.

When Prokron enters an existing project, it should establish a trustworthy Adoption Baseline.

The baseline defines the current state of the project at the moment Prokron becomes authoritative for coordination.

Prokron does not need complete historical lineage before that boundary.

PRE-PROKRON HISTORY
────────────────────────────────
best-effort evidence
may be incomplete
may contain contradictions
not required to be fully reconstructed

          ↓

ADOPTION BOUNDARY
════════════════════════════════
current project truth established
uncertainty made explicit
human confirms high-impact facts

          ↓

PROKRON-GOVERNED HISTORY
────────────────────────────────
decisions
tasks
intent
evidence
journal
state
lineage
continuity

Before the Adoption Boundary, history is evidence.

After the Adoption Boundary, Prokron begins preserving project meaning systematically.

3. Adoption Success Condition

An existing project is sufficiently adopted when a fresh human or AI can answer:

What is this project?

What architecture is authoritative now?

What constraints govern current implementation?

What decisions are currently governing?

What work is currently active?

What work is eligible next?

What is blocked or waiting?

What remains unverified?

What must not be changed?

What exact action should happen next?

The fresh agent does not need to know every historical decision that preceded adoption.

Historical information is required only when it materially affects current project truth.

4. Current Truth vs Historical Archaeology

During adoption, discovered information should be classified into three groups.

4.1 Current truth

Information required to operate the project safely now.

Examples:

current architecture;

active domain model;

current constraints;

governing policies;

active tasks;

current dependencies;

current WIP;

current blockers;

current validation state;

release gates;

current production restrictions;

current next actions.

This information should be imported, verified, or explicitly marked unknown.

4.2 Historical information required to understand current truth

Some past information remains relevant because it explains a current constraint or governing decision.

Example:

Current rule:
Do not merge inventory batches across contracts.

Relevant historical rationale:
One inventory batch corresponds to one contract/customer accounting unit.

The historical detail matters because removing it could cause a future agent to "simplify" the implementation incorrectly.

This history should be preserved selectively.

4.3 Historical information with no current governing effect

Examples:

abandoned experiments;

obsolete task sequences;

old implementation details;

superseded architecture no longer referenced;

completed sessions that do not affect current state.

This information does not need to be reconstructed during adoption.

It remains available through Git, archived documentation, legacy handoff files, or other project evidence.

5. Adoption Is Retrieval, Not Full Ingestion

Prokron should not load an entire repository into an AI context window.

The adoption process should use staged retrieval.

repository
    ↓
deterministic discovery
    ↓
candidate project-state sources
    ↓
targeted parsing
    ↓
current-state hypotheses
    ↓
high-impact unknowns
    ↓
developer interview
    ↓
candidate baseline
    ↓
review / approval
    ↓
.prokron/

The principle is:

Find where truth is likely to live before reading everything that could contain truth.

6. Deterministic Discovery

The first adoption stage should require little or no LLM reasoning.

Prokron Core can inspect:

repository tree
Git status
Git branch
Git log metadata
package manifests
README
AGENTS.md
CLAUDE.md
docs/
handoff/
ADR files
task files
roadmaps
architecture documents
tests
migrations
CI configuration
working tree

This stage should primarily identify sources and metadata.

It should not attempt semantic reconstruction of the project.

Example discovery:

Detected possible project-state sources:

HIGH PRIORITY
✓ handoff/TASKS.md
✓ handoff/TASKS_DEPENDENCIES.md
✓ handoff/DECISIONS.md
✓ handoff/STATE.md

MEDIUM PRIORITY
✓ docs/domain-model.md
✓ docs/architecture.md
✓ implementation_plan/

IMPLEMENTATION EVIDENCE
✓ tests/
✓ migrations/
✓ .github/workflows/
✓ src/

7. Source Priority

Adoption should prefer explicit project-state artifacts over broad source-code inspection.

Recommended initial priority:

Priority 1 — explicit state

.prokron/
handoff/
project-state/
TASKS*
STATE*
INTENT*
DECISIONS*
ADR*
JOURNAL*
ROADMAP*
product-thesis*
implementation-plan*

Priority 2 — project documentation

README
architecture
domain model
requirements
specifications

Priority 3 — implementation evidence

Git
tests
migrations
CI
package manifests
source code
deployment evidence

Source code should usually be inspected to verify a specific claim, not as the first source of project meaning.

8. Source Authority During Adoption

Discovery does not imply authority.

A source may be:

CURRENT_CANONICAL
CURRENT_SUPPORTING
HISTORICAL
DERIVED
IMPLEMENTATION_EVIDENCE
STALE_OR_CONFLICTING
UNKNOWN

Prokron should avoid silently deciding authority where the repository contains contradictions.

Example:

docs/architecture-old.md
    says: ledger_scope

current schema
    says: accounting_unit

handoff/DECISIONS.md
    says: accounting_unit superseded ledger_scope

Prokron may form a hypothesis that accounting_unit is current.

If this affects project semantics, the hypothesis should be verified rather than silently promoted to authority.

9. Confidence Model

Candidate facts should preserve their epistemic status.

Recommended classes:

CONFIRMED_REPOSITORY
CONFIRMED_HUMAN
INFERRED_HIGH
INFERRED_LOW
UNKNOWN
CONFLICTING

Example:

claim: inventory is tracked by contract and batch
confidence: CONFIRMED_REPOSITORY
sources:
  - docs/domain-model.md
  - src/inventory/models.py

Example:

claim: partial settlement superseded full settlement
confidence: INFERRED_HIGH
sources:
  - git history
  - current service implementation
requires_confirmation: true

Prokron must never convert uncertainty into false certainty merely to produce complete documents.

10. Developer Interview

Repository evidence cannot answer every important question.

Some project facts live only in human understanding:

why an architecture was chosen;

which old direction was explicitly rejected;

whether an implementation is experimental or governing;

whether a task is actually active;

whether "DONE" means production-verified or only coded;

which constraint must not be changed;

what the real next action is.

Prokron should therefore support an adoption interview.

The interview should not ask the developer to explain the entire project from scratch.

It should ask only questions that repository evidence cannot answer confidently.

11. Interview Design

Interview questions should be generated from:

high-impact UNKNOWN
+
high-impact INFERRED
+
CONFLICTING evidence

Bad question:

What does this project do?

when the README already answers it clearly.

Better question:

I found both legacy/full_settlement.py and services/partial_settlement.py.
Current tests primarily exercise partial settlement.
Did partial settlement formally replace full settlement, or is it still experimental?

The interview should minimize human cognitive load.

A mature adoption flow should prefer approximately:

5–15 high-value questions

over:

50 generic onboarding questions

for a reasonably documented project.

The exact number should depend on uncertainty, not a fixed questionnaire.

11A. Interview Coverage Map

The interview must be dynamic in wording but deterministic in coverage.

Prokron should not ship a fixed generic questionnaire. Instead, it should maintain a fixed set of current-state domains that adoption must evaluate.

For each domain, the system should determine whether repository evidence is sufficient. It should ask the developer only when the domain remains materially uncertain, inferred, or conflicting.

Recommended coverage map:

Domain

Requirement

Adoption must establish

Ask when

Project identity

REQUIRED

What the project currently does and its active scope

Repository evidence is missing or contradictory

Current authority

REQUIRED

Which sources currently govern project truth

Authority cannot be resolved safely

Current architecture / domain model

REQUIRED

The architecture or domain model currently governing implementation

Evidence conflicts or only weak inference exists

Constraints / invariants

REQUIRED

What future agents must not violate

Constraints are implicit, incomplete, or conflicting

Active work

REQUIRED

Current WIP, owner, execution point, and immediate objective

WIP cannot be established confidently

Tasks / dependencies

REQUIRED

Remaining work and hard dependencies relevant to current execution

Current task state or dependency edges are ambiguous

Blocked / waiting

REQUIRED

Current engineering blockers, external waits, and human gates

Blocking semantics are unclear

Validation / evidence

REQUIRED

What is actually validated and to what level

DONE/verified claims are unsupported or ambiguous

Current governing decisions

REQUIRED

Decisions that materially govern current work

Multiple plausible governing decisions exist

Next action

REQUIRED

The exact safe next action or next eligible work

Repository state does not establish it confidently

Production / release restrictions

CONDITIONAL

Freeze, migration, deployment, release, or production-write restrictions

Relevant production/release surfaces exist and restrictions are unclear

Deployment state

CONDITIONAL

Current deployed/released state when operationally relevant

Deployment claims conflict with evidence

Human validation gates

CONDITIONAL

Required owner/domain-expert confirmation still outstanding

Human approval affects current execution

Security / destructive-operation constraints

CONDITIONAL

Current safeguards around destructive or sensitive actions

Relevant surfaces exist and policy is unclear

Pre-adoption rationale

OPTIONAL

Historical rationale needed to understand a current rule

Only when current truth cannot be understood safely without it

Rejected historical approaches

OPTIONAL

Past rejected options

Only when a current agent is likely to rediscover/re-propose them

Complete pre-adoption history

OPTIONAL

Full historical chronology

Never required merely to complete adoption

The categories mean:

REQUIRED
    Must be sufficiently established before adoption can become canonical.

CONDITIONAL
    Required only when the repository/project makes the domain relevant.

OPTIONAL
    May remain unknown without blocking adoption.

The coverage map defines what must be known, not what exact question must be asked.

11B. Question Generation

Questions should be generated from the intersection of:

coverage gap
+
confidence state
+
source conflict
+
impact on current execution

Conceptually:

Coverage Map
      ↓
inspect evidence for each domain
      ↓
sufficiently confirmed?
      ├── yes → do not ask
      └── no
           ↓
UNKNOWN / INFERRED / CONFLICTING
           ↓
impact scoring
           ↓
generate contextual question

The system should not ask questions whose answers are already strongly supported by current authoritative evidence.

Example:

Bad:

What architecture does this project use?

Better:

docs/modeling.md describes ledger_scope, but the current schema contains accounting_unit_id and the latest decision record references accounting_unit. Is accounting_unit the current governing model?

The interview engine should optimize for information gain, not questionnaire completion.

11C. Blocking vs Non-Blocking Unknowns

Adoption does not require zero uncertainty.

Unknowns should be classified by whether they block establishment of the current baseline.

Example:

BLOCKING UNKNOWN
- Which task is currently WIP?
- Which of two conflicting domain models is authoritative?
- Is production writing currently frozen?

NON-BLOCKING UNKNOWN
- Why was an obsolete implementation abandoned two years ago?
- Who originally proposed an old superseded architecture?

prokron adopt --apply should be permitted when:

all REQUIRED domains are sufficiently established
+
all relevant CONDITIONAL domains are sufficiently established
+
no unresolved conflict can materially change current execution safety

Optional historical unknowns must not block adoption.

This is essential to the Adoption Boundary principle.

11D. Interview Output as Evidence

Developer answers must be persisted as adoption evidence.

At minimum, each material answer should retain:

domain
question or subject
answer
confirmation timestamp/date
confidence = CONFIRMED_HUMAN
affected candidate facts

Not every interview answer should create an ADR.

Create or propose a decision only when the answer establishes or changes governing project semantics.

12. Interactive Adoption Flow

A possible interface:

prokron adopt --interactive

Example:

Scanning repository...

Detected:
✓ Git repository
✓ README
✓ 18 project documents
✓ legacy handoff directory
✓ 43 tracked tasks
✓ 27 ADR-like decisions
✓ test suite
✓ CI configuration

Current-state reconstruction:

14 high-confidence facts
6 medium-confidence inferences
4 high-impact unknowns
2 conflicts

Developer confirmation required.

Prokron can then ask targeted questions.

After the interview:

Baseline confidence improved:

18 confirmed facts
2 accepted inferences
1 unresolved unknown
0 blocking conflicts

13. Candidate State Before Canonical State

Adoption must not immediately overwrite or create authoritative state from uncertain reconstruction.

The first output should be a candidate.

Example:

.prokron-adoption/
├── BASELINE.md
├── TASKS.md
├── DECISIONS.md
├── INTENTS.md
├── ADOPTION_REPORT.md
└── SOURCE_MAP.md

The candidate can then be reviewed.

Only after approval should Prokron write or promote the state into:

.prokron/

This keeps adoption auditable.

14. Adoption Report

Every non-trivial adoption should produce an ADOPTION_REPORT.md.

Recommended structure:

ADOPTION DATE

PROJECT SOURCES INSPECTED

CURRENT TRUTH CONFIRMED FROM REPOSITORY

CURRENT TRUTH CONFIRMED BY HUMAN

INFERRED FACTS ACCEPTED

UNRESOLVED UNKNOWNS

CONFLICTING SOURCES

HISTORICAL MATERIAL NOT MIGRATED

LEGACY STATE SOURCES PRESERVED

IMPLEMENTATION EVIDENCE CHECKED

ADOPTION LIMITATIONS

The report establishes what Prokron knows and what it deliberately does not claim to know.

15. Adoption Baseline Decision

Instead of reconstructing every pre-existing ADR, Prokron may create a baseline decision recording the current governing state.

Example:

ADR-A001
Adoption baseline

As of the adoption date, the following project state is confirmed:

- current accounting model: ...
- current inventory model: ...
- current production-write policy: ...
- current reconciliation semantics: ...

Evidence:
- current repository documentation;
- implementation evidence;
- developer confirmation.

Historical rationale prior to Prokron adoption was not fully reconstructed.

This ADR establishes current governing truth for future Prokron lineage.

This creates a clean origin point.

Future changes can then form normal lineage:

ADR-A001
    ↓
new evidence
    ↓
ADR-A002
    ↓
new requirement
    ↓
ADR-A003

16. Legacy Handoff Migration

Some projects already contain a structured handoff system.

These projects should not be treated the same as undocumented repositories.

Prokron should support a migration path where legacy state is treated as a high-priority source.

Conceptually:

prokron migrate handoff/

or:

prokron adopt --from handoff/

The exact command is an implementation decision.

The semantic distinction matters more than the CLI spelling.

Possible mapping:

legacy TASKS
    → candidate Prokron TASKS

legacy dependency map
    → canonical task dependencies
    → generated TASK_GRAPH

legacy decisions / ADRs
    → candidate governing decisions

legacy current handoff
    → candidate INTENT

legacy session history
    → optional historical evidence

legacy STATE
    → evidence only
    → regenerate Prokron STATE

Derived legacy files must not automatically become canonical Prokron authority.

17. Migration Should Prefer Current State

A legacy handoff system may contain years of historical records.

Prokron does not need to migrate them all.

The migration should prioritize:

current tasks
current dependencies
current governing decisions
current WIP
current constraints
current blockers
current validation
current next actions

Historical records should be imported only when:

necessary for current rationale;

required to preserve a still-governing constraint;

needed to resolve a current contradiction;

explicitly requested by the user.

Otherwise they may remain in their legacy location.

18. Preserving Legacy Sources

Migration should normally avoid deleting the old state system immediately.

Example:

handoff/
    legacy frozen or retained as evidence

.prokron/
    new canonical coordination state

During an initial migration period, the project may retain both.

The old system should eventually stop receiving authoritative updates once Prokron becomes canonical.

This avoids two competing sources of truth indefinitely.

19. Source Code Inspection Should Be Targeted

Source-code scanning is valuable for verification, but code does not explain project meaning by itself.

Git answers:

What changed?

Source code answers:

What exists?

Tests answer:

What behavior is currently exercised?

None of them necessarily answers:

Why is this the governing design?

Therefore adoption should use code selectively.

Example:

Candidate claim:
T-M3-04 is complete.

Acceptance:
settlement invariant passes.

Targeted verification:
find settlement-related tests
→ inspect relevant implementation
→ run appropriate tests

Prokron should not inspect every source file merely because the repository is available.

20. Token and Context Efficiency

Adoption architecture should minimize context reconstruction cost.

Example:

100 MB repository
    ↓
filesystem discovery
    ↓
0 LLM tokens required

34 candidate project-state files identified
    ↓
local parsing / indexing
    ↓
0 LLM tokens required

6 documents selected for semantic review
    ↓
targeted AI reasoning

4 high-impact questions
    ↓
developer interview

baseline generated

The system should scale by retrieving less, not by expanding the model context window.

21. Core vs AI-Assisted Responsibilities

Prokron Core should remain usable without a language model.

Core responsibilities

discover
parse
index
classify known file types
validate
build graphs
render derived state
record source references
persist approved baseline

AI-assisted responsibilities

interpret ambiguous legacy documents
summarize relevant current state
propose source authority
detect semantic conflicts
generate interview questions
propose candidate decisions
propose baseline documentation

AI suggestions are not project authority.

Approval promotes candidate state into authoritative project state.

22. Non-Goals

Adoption should not attempt to become:

a full Git archaeology engine;

a complete historical reconstruction system;

a source-code understanding platform;

a universal code index;

an autonomous project historian;

an excuse to ingest the entire repository into an LLM.

Historical reconstruction can be performed later when needed.

It is not a prerequisite for Prokron adoption.

23. Relationship to Reconciliation

Adoption establishes the first current baseline.

Reconciliation maintains consistency after adoption.

ADOPTION
existing repository
    ↓
establish current truth

RECONCILIATION
current Prokron project
    ↓
detect later divergence

These are related but distinct operations.

Adoption should not require the full future reconciliation engine.

24. Relationship to Context Packs

Adoption and context generation should follow the same retrieval philosophy.

A context pack should not contain the entire project.

Adoption should not ingest the entire project.

Both should traverse only the evidence needed to answer the current question.

Question
   ↓
relevant state
   ↓
relevant decisions
   ↓
relevant evidence
   ↓
relevant files

This keeps Prokron useful even as projects grow.

25. Candidate Commands

Possible future command surface:

prokron adopt
prokron adopt --interactive
prokron adopt --dry-run
prokron adopt --apply

prokron migrate handoff/

Potential supporting commands:

prokron adoption report
prokron adoption sources
prokron adoption unknowns

The exact CLI should be validated through real use before becoming stable.

26. Suggested v0.2 Scope

A minimal implementation should prioritize:

1. deterministic repository discovery;
2. project-state source detection;
3. source priority/classification;
4. current-state candidate extraction;
5. explicit UNKNOWN / CONFLICTING representation;
6. adoption report;
7. candidate baseline generation;
8. interactive confirmation;
9. safe apply into .prokron/;
10. legacy handoff migration support.

Do not begin with:

full repository semantic indexing
complete historical reconstruction
autonomous decision inference
complex embeddings infrastructure
remote vector databases

Those are not required to prove the adoption thesis.

27. Validation Questions

The adoption capability should be evaluated empirically.

Important questions:

Can Prokron establish useful current state without reading the entire repository?

How many files must an AI actually inspect?

How many questions must the developer answer?

How often does adoption incorrectly infer current authority?

Can legacy project-state systems migrate without losing governing information?

Can a fresh model resume the project using only the resulting .prokron/ state?

How much context is required before and after adoption?

How often must pre-adoption history be retrieved later?

Which source types provide the highest-value current-state information?

Which adoption inferences are too dangerous to automate?

28. Success Criteria

A strong adoption implementation should make this possible:

large existing repository
        ↓
prokron adopt --interactive
        ↓
targeted repository discovery
        ↓
small number of high-value questions
        ↓
approved current baseline
        ↓
fresh agent enters
        ↓
understands current project truth
        ↓
productive work

without requiring:

complete Git-history reconstruction
complete source-code ingestion
complete historical ADR reconstruction
prior chat history
large-context brute force

29. Product Principle

The purpose of Prokron adoption is not to make the past perfectly legible.

It is to establish a trustworthy boundary after which project meaning remains legible.

Prokron does not need to know your project's entire past to preserve its future.

The adoption principle is:

Adopt the present. Preserve the future. Retrieve the past only when necessary.

PROKRON_ADOPTION_SPEC_EOF_v2