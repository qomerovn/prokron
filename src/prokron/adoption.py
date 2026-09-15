from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, replace
from datetime import UTC, date, datetime
from enum import StrEnum
from importlib.resources import files
from pathlib import Path, PurePosixPath
from typing import Callable, TypeVar

from .core import CANONICAL_FILES, VALIDATION_LEVELS, eligible_tasks, prokron_dir, validate
from .markdown import DECISION_HEADER, TASK_HEADER, parse_decisions, parse_intents, parse_journal, parse_tasks, update_section_fields
from .models import Decision, Intent, ProkronError, ProkronState, Task
from .operations import install_bootstrap, is_git_repository
from .rendering import sync_derived

ADOPTION_DIR = ".prokron-adoption"
BASELINE_TITLE = "Adoption baseline"
Parsed = TypeVar("Parsed")
ARCHIVE_MARKERS = {"archive", "_archive", "archived", "old", "deprecated", "superseded"}
IMPLEMENTATION_DIRS = {"src", "lib", "app", "tests", "test", "migrations", ".github", ".circleci", "examples"}
LEGACY_STATE_DIRS = {"handoff", "project-state"}


class SourceClassification(StrEnum):
    CURRENT_CANONICAL = "CURRENT_CANONICAL"
    CURRENT_SUPPORTING = "CURRENT_SUPPORTING"
    HISTORICAL = "HISTORICAL"
    DERIVED = "DERIVED"
    IMPLEMENTATION_EVIDENCE = "IMPLEMENTATION_EVIDENCE"
    STALE_OR_CONFLICTING = "STALE_OR_CONFLICTING"
    UNKNOWN = "UNKNOWN"


class Confidence(StrEnum):
    CONFIRMED_REPOSITORY = "CONFIRMED_REPOSITORY"
    CONFIRMED_HUMAN = "CONFIRMED_HUMAN"
    INFERRED_HIGH = "INFERRED_HIGH"
    INFERRED_LOW = "INFERRED_LOW"
    UNKNOWN = "UNKNOWN"
    CONFLICTING = "CONFLICTING"


class Requirement(StrEnum):
    REQUIRED = "REQUIRED"
    CONDITIONAL = "CONDITIONAL"
    OPTIONAL = "OPTIONAL"


class AssessmentStatus(StrEnum):
    ESTABLISHED = "ESTABLISHED"
    NEEDS_CONFIRMATION = "NEEDS_CONFIRMATION"
    CONFLICTING = "CONFLICTING"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    DEFERRED = "DEFERRED"


@dataclass(frozen=True)
class Source:
    path: str
    priority: int
    classification: SourceClassification
    reason: str


@dataclass(frozen=True)
class Discovery:
    branch: str
    head: str
    dirty: bool
    recent_commit: str | None
    changed_files: tuple[str, ...]
    recent_files: tuple[str, ...]
    files: tuple[str, ...]
    has_prokron: bool
    sources: tuple[Source, ...]


@dataclass(frozen=True)
class AdoptionResult:
    discovery: Discovery
    unknowns: tuple[str, ...]
    conflicts: tuple[str, ...]
    incompatibilities: tuple[str, ...]


@dataclass(frozen=True)
class InspectedSource:
    path: str
    summary: str
    concepts: tuple[str, ...]


@dataclass(frozen=True)
class CoverageDomain:
    domain: str
    requirement: Requirement


@dataclass(frozen=True)
class DomainAssessment:
    domain: str
    requirement: Requirement
    status: AssessmentStatus
    confidence: Confidence
    evidence: tuple[str, ...]
    blocking: bool
    reason: str


@dataclass(frozen=True)
class InterviewPrompt:
    domain: str
    context: str
    question: str


COVERAGE_SCHEMA = (
    CoverageDomain("project identity", Requirement.REQUIRED),
    CoverageDomain("current authority", Requirement.REQUIRED),
    CoverageDomain("current architecture / domain model", Requirement.REQUIRED),
    CoverageDomain("constraints / invariants", Requirement.REQUIRED),
    CoverageDomain("active work", Requirement.REQUIRED),
    CoverageDomain("tasks / dependencies", Requirement.REQUIRED),
    CoverageDomain("blocked / waiting", Requirement.REQUIRED),
    CoverageDomain("validation / evidence", Requirement.REQUIRED),
    CoverageDomain("current governing decisions", Requirement.REQUIRED),
    CoverageDomain("next action", Requirement.REQUIRED),
    CoverageDomain("production / release restrictions", Requirement.CONDITIONAL),
    CoverageDomain("deployment state", Requirement.CONDITIONAL),
    CoverageDomain("human validation gates", Requirement.CONDITIONAL),
    CoverageDomain("security / destructive-operation constraints", Requirement.CONDITIONAL),
    CoverageDomain("pre-adoption rationale", Requirement.OPTIONAL),
    CoverageDomain("rejected historical approaches", Requirement.OPTIONAL),
    CoverageDomain("complete pre-adoption history", Requirement.OPTIONAL),
)


def _git(project: Path, *args: str) -> str:
    result = subprocess.run(["git", *args], cwd=project, capture_output=True, text=True, check=False)
    if result.returncode:
        raise ProkronError(result.stderr.strip() or "unable to inspect Git repository")
    return result.stdout.strip()


def _git_optional(project: Path, *args: str) -> str | None:
    result = subprocess.run(["git", *args], cwd=project, capture_output=True, text=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else None


def _repository_files(project: Path) -> tuple[PurePosixPath, ...]:
    skipped = {
        ".git",
        ADOPTION_DIR,
        ".venv",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".artifacts",
        "artifacts",
        "build",
        "dist",
    }
    paths = [
        PurePosixPath(path.relative_to(project).as_posix())
        for path in project.rglob("*")
        if path.is_file() and not any(part in skipped for part in path.relative_to(project).parts)
    ]
    return tuple(sorted(paths, key=str))


def _implementation_directory(path: PurePosixPath) -> PurePosixPath | None:
    for index, part in enumerate(path.parts[:-1]):
        if part.lower() in IMPLEMENTATION_DIRS:
            return PurePosixPath(*path.parts[: index + 1])
    return None


def classify_source(path: PurePosixPath) -> Source | None:
    text = path.as_posix()
    name = path.name.lower()
    parts = {part.lower() for part in path.parts}
    stem = path.stem.lower()
    state_prefixes = ("tasks", "state", "intent", "decisions", "adr", "journal", "roadmap", "product-thesis", "implementation-plan")
    archive_parts = {part.lower() for part in path.parts[:-1]}
    archive_name_tokens = set(filter(None, re.split(r"[^a-z0-9]+", stem)))
    is_document = path.suffix.lower() in {".md", ".txt", ".rst", ".adoc"} or (not path.suffix and not name.startswith("."))
    manifests = {
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        "package.json",
        "cargo.toml",
        "go.mod",
        "pom.xml",
        "build.gradle",
        "requirements.txt",
        "composer.json",
    }
    ci_files = {".gitlab-ci.yml", "jenkinsfile", "azure-pipelines.yml", ".travis.yml"}
    deployment_files = {"dockerfile", "docker-compose.yml", "compose.yml"}
    if path.parts and path.parts[0] == ".prokron":
        classification = SourceClassification.DERIVED if name in {"state.md", "task_graph.md"} else SourceClassification.CURRENT_CANONICAL
        return Source(text, 1, classification, "existing Prokron state")
    if archive_parts & ARCHIVE_MARKERS or archive_name_tokens & ARCHIVE_MARKERS:
        return Source(
            text,
            1 if parts & LEGACY_STATE_DIRS else 2,
            SourceClassification.STALE_OR_CONFLICTING,
            "name indicates stale or archived material",
        )
    if _implementation_directory(path) is not None or name in manifests | ci_files | deployment_files or stem in {"deploy", "release"}:
        return Source(text, 3, SourceClassification.IMPLEMENTATION_EVIDENCE, "implementation or build evidence")
    if not is_document:
        return None
    if name in {"state.md", "task_graph.md"} or "dependencies" in name:
        return Source(text, 1, SourceClassification.DERIVED, "state projection; evidence only")
    if name == "journal.md" or name.startswith("changelog") or "history" in name:
        return Source(text, 1, SourceClassification.HISTORICAL, "historical record")
    if parts & LEGACY_STATE_DIRS or stem.startswith(state_prefixes):
        return Source(text, 1, SourceClassification.CURRENT_SUPPORTING, "explicit project-state candidate; authority requires review")
    document_names = ("architecture", "domain-model", "requirements", "specification")
    if (
        name.startswith(("readme", "agents.", "claude."))
        or stem.startswith(document_names)
        or parts & {"docs", "architecture", "specifications"}
    ):
        return Source(text, 2, SourceClassification.CURRENT_SUPPORTING, "project documentation")
    if path.suffix.lower() in {".md", ".txt", ".rst", ".adoc"}:
        return Source(text, 2, SourceClassification.UNKNOWN, "unclassified text source")
    return None


def _classified_sources(paths: tuple[PurePosixPath, ...]) -> tuple[Source, ...]:
    sources: dict[str, Source] = {}
    for path in paths:
        source = classify_source(path)
        if source is None:
            continue
        implementation_directory = _implementation_directory(path)
        if source.classification == SourceClassification.IMPLEMENTATION_EVIDENCE and implementation_directory is not None:
            display = f"{implementation_directory.as_posix()}/"
            source = Source(display, 3, SourceClassification.IMPLEMENTATION_EVIDENCE, "implementation evidence directory")
        sources[source.path] = source
    return tuple(sorted(sources.values(), key=lambda source: (source.priority, source.path)))


def discover(project: Path) -> Discovery:
    if not is_git_repository(project):
        raise ProkronError("Prokron requires a Git repository. Run `git init` first.")
    paths = _repository_files(project)
    sources = _classified_sources(paths)
    status = _git(project, "status", "--porcelain")
    return Discovery(
        branch=_git(project, "branch", "--show-current") or "detached HEAD",
        head=_git_optional(project, "rev-parse", "--short", "HEAD") or "unborn",
        dirty=bool(status),
        recent_commit=_git_optional(project, "log", "-1", "--pretty=%s") or None,
        changed_files=tuple(sorted(line[3:] for line in status.splitlines() if len(line) > 3)),
        recent_files=tuple(
            line
            for line in (_git_optional(project, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD") or "").splitlines()
            if line
        )[:8],
        files=tuple(path.as_posix() for path in paths),
        has_prokron=prokron_dir(project).exists(),
        sources=sources,
    )


def render_discovery(discovery: Discovery) -> str:
    lines = [
        "Prokron Adoption Discovery",
        "",
        "Repository:",
        f"  branch: {discovery.branch}",
        f"  HEAD: {discovery.head}",
        f"  working tree: {'modified' if discovery.dirty else 'clean'}",
        f"  recent commit: {discovery.recent_commit or 'none'}",
        f"  changed files: {', '.join(discovery.changed_files) or 'none'}",
        f"  files: {len(discovery.files)}",
        "",
        f"Existing Prokron state: {'present' if discovery.has_prokron else 'none'}",
    ]
    groups = (
        ("HIGH-PRIORITY STATE SOURCES", 1),
        ("PROJECT DOCUMENTATION", 2),
        ("IMPLEMENTATION EVIDENCE", 3),
    )
    for heading, priority in groups:
        lines.extend(("", heading))
        matches = [source for source in discovery.sources if source.priority == priority]
        lines.extend(f"  {source.path} [{source.classification}]" for source in matches)
        if not matches:
            lines.append("  none")
    legacy = sorted(
        {
            PurePosixPath(*path.parts[: index + 1]).as_posix()
            for value in discovery.files
            for path in (PurePosixPath(value),)
            for index, part in enumerate(path.parts[:-1])
            if part.lower() in LEGACY_STATE_DIRS
        }
    )
    lines.extend(
        ("", "Potential legacy state system:", f"  {', '.join(legacy) if legacy else 'none'}", "", "No project files were modified.")
    )
    return "\n".join(lines) + "\n"


def _source_root(project: Path, value: str | None) -> Path | None:
    if value is None:
        return None
    root = project / value
    try:
        root.resolve().relative_to(project.resolve())
    except ValueError as error:
        raise ProkronError("--from must name a directory inside the repository") from error
    if not root.is_dir() or root.is_symlink():
        raise ProkronError(f"adoption source is not a directory: {value}")
    return root


def _select(project: Path, root: Path | None, name: str) -> tuple[Path | None, str | None]:
    search_root = root or project
    matches = sorted(
        (
            path
            for path in search_root.rglob(name)
            if ADOPTION_DIR not in path.parts and ".git" not in path.parts and ".prokron" not in path.parts and not path.is_symlink()
        ),
        key=lambda path: path.relative_to(project).as_posix(),
    )
    if len(matches) > 1:
        paths = ", ".join(path.relative_to(project).as_posix() for path in matches)
        return None, f"multiple candidate {name} sources require authority confirmation: {paths}"
    return (matches[0], None) if matches else (None, None)


def _read_structured(
    path: Path | None, template: str, parser: Callable[[Path], tuple[Parsed, ...]]
) -> tuple[str, tuple[Parsed, ...], str | None]:
    if path is None:
        return template, (), None
    try:
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            return template, (), None
        parsed = parser(path)
    except (OSError, UnicodeError, ProkronError) as error:
        return template, (), f"{path.name} format is incompatible and was not imported: {error}"
    if not parsed and "## " in text and "```" not in text:
        return template, (), f"{path.name} format is incompatible and was not imported because it is not canonical Prokron state"
    return text.rstrip() + "\n", tuple(parsed), None


SEMANTIC_CONCEPTS = (
    ("architecture", ("architecture", "system design")),
    ("domain-model", ("domain model", "domain-model")),
    ("thesis", ("product thesis", "thesis")),
    ("business-rules", ("business rules", "business-rules")),
    ("constraints", ("constraints",)),
    ("invariants", ("invariants",)),
    ("roadmap", ("roadmap",)),
    ("open-decisions", ("open decisions", "open-decisions")),
    ("implementation-plan", ("implementation plan", "implementation-plan")),
    ("current-work", ("current work", "current-work")),
)


def _concepts(value: str) -> tuple[str, ...]:
    normalized = re.sub(r"[_-]+", " ", value.casefold())
    return tuple(concept for concept, phrases in SEMANTIC_CONCEPTS if any(phrase in normalized for phrase in phrases))


def _source_summary(text: str) -> str:
    for line in text.splitlines():
        value = line.strip()
        if not value or value.startswith(("#", "```", "![", "---")):
            continue
        if re.fullmatch(r"(?:[-*]\s*)?\[[^]]+\]\([^)]+\)(?:\s*[|·]\s*\[[^]]+\]\([^)]+\))*", value):
            continue
        if re.match(r"^[-*]\s*(?:version|status|owner|updated|date):", value, re.IGNORECASE):
            continue
        return value[:240]
    return ""


def _inspect_current_sources(project: Path, discovery: Discovery) -> tuple[InspectedSource, ...]:
    source_by_path = {source.path: source for source in discovery.sources}
    candidates = [
        (source, _concepts(source.path))
        for source in discovery.sources
        if source.classification == SourceClassification.CURRENT_SUPPORTING
        and source.path.endswith((".md", ".txt", ".rst", ".adoc"))
        and _concepts(source.path)
    ]
    order = {concept: index for index, (concept, _) in enumerate(SEMANTIC_CONCEPTS)}

    def rank(item: tuple[Source, tuple[str, ...]]) -> tuple[int, int, str]:
        source, concepts = item
        path = PurePosixPath(source.path)
        noise = 20 if {part.casefold() for part in path.parts} & {"forms", "forms_legal", "legal", "images", "assets"} else 0
        noise += 10 if path.name.casefold().startswith("readme") else 0
        return (noise + min(order[concept] for concept in concepts), len(path.parts), source.path)

    inspected: list[InspectedSource] = []
    read: dict[str, str] = {}

    def inspect(path: str, concepts: tuple[str, ...]) -> None:
        if path in read or len(inspected) >= 6:
            return
        text = (project / path).read_text(encoding="utf-8", errors="replace")[:4096]
        read[path] = text
        summary = _source_summary(text)
        if summary:
            inspected.append(InspectedSource(path, summary, concepts))

    direct = sorted(candidates, key=rank)
    for source, concepts in direct[:4]:
        inspect(source.path, concepts)

    # One local Markdown hop only; linked content competes inside the same six-file budget.
    for origin in tuple(inspected):
        for label, target in re.findall(r"\[([^]]+)]\(([^)]+\.md(?:#[^)]*)?)\)", read[origin.path], re.IGNORECASE):
            linked_concepts = _concepts(f"{label} {target}")
            if not linked_concepts:
                continue
            relative = target.split("#", 1)[0]
            linked = (project / origin.path).parent.joinpath(relative).resolve()
            try:
                linked_path = linked.relative_to(project.resolve()).as_posix()
            except ValueError:
                continue
            linked_source = source_by_path.get(linked_path)
            if (
                linked_source
                and not linked.is_symlink()
                and linked_source.classification in {SourceClassification.CURRENT_SUPPORTING, SourceClassification.UNKNOWN}
            ):
                inspect(linked_path, linked_concepts)

    for source, concepts in direct:
        inspect(source.path, concepts)
    return tuple(inspected)


def _project_purpose(project: Path) -> tuple[str, str | None]:
    readmes = sorted(path for path in project.glob("README*") if path.is_file() and not path.is_symlink())
    if not readmes:
        return "Unknown.", None
    lines = readmes[0].read_text(encoding="utf-8", errors="replace")[:8192].splitlines()
    paragraph = next((line.strip() for line in lines if line.strip() and not line.lstrip().startswith(("#", "[!", "![", "<"))), "")
    return (paragraph, readmes[0].relative_to(project).as_posix()) if paragraph else ("Unknown.", None)


def _structured_assessment(
    domain: CoverageDomain,
    paths: tuple[str, ...],
    explicit_source: bool,
    established_reason: str,
    supported: bool = True,
    unsupported_reason: str = "No usable current-state records were imported for this domain.",
) -> DomainAssessment:
    if paths and supported and explicit_source:
        return DomainAssessment(
            domain.domain,
            domain.requirement,
            AssessmentStatus.ESTABLISHED,
            Confidence.INFERRED_HIGH,
            paths,
            False,
            established_reason,
        )
    return DomainAssessment(
        domain.domain,
        domain.requirement,
        AssessmentStatus.NEEDS_CONFIRMATION,
        Confidence.INFERRED_LOW if paths and supported else Confidence.UNKNOWN,
        paths,
        True,
        "Candidate evidence exists but authority is unconfirmed."
        if paths and supported
        else unsupported_reason,
    )


def assess_domains(
    project: Path,
    discovery: Discovery,
    selected: dict[str, Path | None],
    purpose_source: str | None,
    explicit_source: bool,
    tasks: tuple[Task, ...],
    decisions: tuple[Decision, ...],
    intents: tuple[Intent, ...],
    conflicts: tuple[str, ...],
    inspected: tuple[InspectedSource, ...] = (),
    format_issues: dict[str, str] | None = None,
) -> tuple[DomainAssessment, ...]:
    format_issues = format_issues or {}
    definitions = {item.domain: item for item in COVERAGE_SCHEMA}
    selected_paths = {name: (path.relative_to(project).as_posix(),) if path is not None else () for name, path in selected.items()}
    inspected_paths = tuple(source.path for source in inspected)
    assessments: list[DomainAssessment] = []
    identity = definitions["project identity"]
    assessments.append(
        DomainAssessment(
            identity.domain,
            identity.requirement,
            AssessmentStatus.ESTABLISHED if purpose_source else AssessmentStatus.NEEDS_CONFIRMATION,
            Confidence.INFERRED_HIGH if purpose_source else Confidence.UNKNOWN,
            (purpose_source,) if purpose_source else (),
            purpose_source is None,
            "README purpose text was inspected." if purpose_source else "No repository project identity was inspected.",
        )
    )
    authority = definitions["current authority"]
    structured_authority_paths = tuple(path for paths in selected_paths.values() for path in paths)
    authority_paths = tuple(dict.fromkeys((*structured_authority_paths, *inspected_paths)))
    if conflicts:
        assessments.append(
            DomainAssessment(
                authority.domain,
                authority.requirement,
                AssessmentStatus.CONFLICTING,
                Confidence.CONFLICTING,
                authority_paths,
                True,
                "Candidate sources or canonical relationships conflict.",
            )
        )
    else:
        structured_authority = bool(tasks or decisions or intents)
        assessments.append(
            DomainAssessment(
                authority.domain,
                authority.requirement,
                AssessmentStatus.ESTABLISHED
                if explicit_source and structured_authority
                else AssessmentStatus.NEEDS_CONFIRMATION,
                Confidence.INFERRED_HIGH
                if explicit_source and structured_authority
                else Confidence.INFERRED_LOW
                if authority_paths
                else Confidence.UNKNOWN,
                authority_paths,
                not (explicit_source and structured_authority),
                "--from explicitly selected usable imported state records."
                if explicit_source and structured_authority
                else "Inspected candidate sources do not establish which sources govern current truth."
                if inspected
                else "Current authority requires confirmation; no usable authority evidence was imported.",
            )
        )
    architecture = definitions["current architecture / domain model"]
    architecture_sources = tuple(source.path for source in inspected if set(source.concepts) & {"architecture", "domain-model"})
    architecture_established = len(architecture_sources) == 1
    assessments.append(
        DomainAssessment(
            architecture.domain,
            architecture.requirement,
            AssessmentStatus.ESTABLISHED if architecture_established else AssessmentStatus.NEEDS_CONFIRMATION,
            Confidence.INFERRED_HIGH if architecture_established else Confidence.INFERRED_LOW if architecture_sources else Confidence.UNKNOWN,
            architecture_sources,
            not architecture_established,
            "One semantically named architecture source was inspected within the adoption budget."
            if architecture_established
            else "Bounded inspection found multiple architecture candidates; current authority requires confirmation."
            if architecture_sources
            else "No usable current architecture evidence was inspected.",
        )
    )
    decisions_path = selected_paths["DECISIONS.md"]
    constraints = definitions["constraints / invariants"]
    constraint_sources = decisions_path if decisions else tuple(
        source.path for source in inspected if set(source.concepts) & {"business-rules", "constraints", "invariants"}
    )
    constraints_established = bool(decisions and explicit_source) or len(constraint_sources) == 1
    assessments.append(
        _structured_assessment(
            constraints,
            constraint_sources,
            explicit_source or constraints_established,
            "Imported decisions or one semantically named constraints source establish current constraints.",
            constraints_established,
            "Multiple constraint candidates require authority confirmation." if constraint_sources else "No usable current constraint evidence was inspected.",
        )
    )
    active_tasks = tuple(task for task in tasks if task.status != "DONE")
    imported_active_evidence = (
        (*selected_paths["TASKS.md"], *(task.id for task in active_tasks)) if active_tasks else ()
    ) + ((*selected_paths["INTENTS.md"], *(intent.subject for intent in intents)) if intents else ())
    branch_signal = discovery.branch not in {"main", "master", "trunk", "detached HEAD"}
    plan_sources = tuple(source.path for source in inspected if set(source.concepts) & {"roadmap", "implementation-plan", "current-work"})
    work_signals = tuple(
        [f"Git branch: {discovery.branch}"]
        if branch_signal
        else []
    ) + tuple([f"Recent commit: {discovery.recent_commit}"] if discovery.recent_commit else []) + tuple(
        f"Recent commit file: {path}" for path in discovery.recent_files
    ) + tuple(f"Changed file: {path}" for path in discovery.changed_files[:8]) + plan_sources
    composed_work = branch_signal and bool(discovery.recent_commit) and bool(plan_sources)
    active_format = format_issues.get("INTENTS.md")
    active_reason = (
        "Imported active task or intent records establish current execution state."
        if imported_active_evidence and explicit_source
        else "Branch, recent commit, and an inspected planning source support a high-confidence current-work hypothesis; confirmation is still required."
        if composed_work
        else active_format
        if active_format
        else "Repository metadata suggests possible active work, but no active task or intent was established."
        if work_signals
        else "No active task or intent was imported; current work requires confirmation."
    )
    active_domain = definitions["active work"]
    assessments.append(
        DomainAssessment(
            active_domain.domain,
            active_domain.requirement,
            AssessmentStatus.ESTABLISHED if imported_active_evidence and explicit_source else AssessmentStatus.NEEDS_CONFIRMATION,
            Confidence.INFERRED_HIGH
            if imported_active_evidence and explicit_source
            else Confidence.INFERRED_HIGH
            if composed_work
            else Confidence.INFERRED_LOW
            if imported_active_evidence or work_signals
            else Confidence.UNKNOWN,
            imported_active_evidence or work_signals,
            not (imported_active_evidence and explicit_source),
            active_reason,
        )
    )
    task_evidence = (*selected_paths["TASKS.md"], *(task.id for task in tasks)) if tasks else ()
    planning_evidence = task_evidence or plan_sources
    assessments.append(
        _structured_assessment(
            definitions["tasks / dependencies"],
            planning_evidence,
            explicit_source or bool(plan_sources),
            "Imported tasks or an inspected roadmap/implementation plan establish the current planning surface.",
            bool(tasks or plan_sources),
            format_issues.get("TASKS.md", "No task records or current planning source were inspected; remaining work and dependencies require confirmation."),
        )
    )
    blocker_evidence = task_evidence + ((*selected_paths["INTENTS.md"], *(intent.subject for intent in intents)) if intents else ())
    assessments.append(
        _structured_assessment(
            definitions["blocked / waiting"],
            blocker_evidence,
            explicit_source,
            "Imported task and intent records establish blocker and waiting state.",
            bool(tasks or intents),
            "No usable task or intent records establish whether work is blocked or waiting.",
        )
    )
    validated_tasks = tuple(task for task in tasks if task.validation in VALIDATION_LEVELS)
    validation_evidence = (*selected_paths["TASKS.md"], *(task.id for task in validated_tasks)) if validated_tasks else ()
    assessments.append(
        _structured_assessment(
            definitions["validation / evidence"],
            validation_evidence,
            explicit_source,
            "Imported task records contain usable validation state.",
            bool(validated_tasks),
            "No imported task records contain usable validation state or evidence.",
        )
    )
    assessments.append(
        _structured_assessment(
            definitions["current governing decisions"],
            (*decisions_path, *(decision.id for decision in decisions)) if decisions else (),
            explicit_source,
            "Imported decision records establish current governing decisions.",
            bool(decisions),
            format_issues.get("DECISIONS.md", "No governing decision records were imported; current decisions require confirmation."),
        )
    )
    actionable = eligible_tasks(ProkronState(tasks, decisions, intents, ()))
    next_evidence = (
        (*selected_paths["INTENTS.md"], *(intent.subject for intent in intents if intent.next_action))
        if any(intent.next_action for intent in intents)
        else ()
    ) + ((*selected_paths["TASKS.md"], *(task.id for task in actionable)) if actionable else ())
    assessments.append(
        _structured_assessment(
            definitions["next action"],
            next_evidence,
            explicit_source,
            "An imported active intent or eligible task establishes the next action.",
            bool(next_evidence),
            "No active intent or actionable imported task establishes a safe next action.",
        )
    )

    conditional_specs = (
        (
            "production / release restrictions",
            ("production freeze", "release restriction", "must not release"),
        ),
        (
            "deployment state",
            ("deployment state", "currently deployed", "production environment"),
        ),
        (
            "human validation gates",
            ("requires human approval", "human validation required", "manual review gate"),
        ),
        (
            "security / destructive-operation constraints",
            ("security constraint", "destructive operation", "must not delete", "secret handling"),
        ),
    )
    for domain_name, keywords in conditional_specs:
        domain = definitions[domain_name]
        decision_matches = tuple(
            decision.id
            for decision in decisions
            if any(keyword in f"{decision.title} {decision.context} {decision.decision}".lower() for keyword in keywords)
        )
        task_matches = tuple(
            task.id
            for task in active_tasks
            if any(keyword in f"{task.title} {task.acceptance} {task.evidence}".lower() for keyword in keywords)
        )
        intent_matches = tuple(
            intent.subject
            for intent in intents
            if any(keyword in f"{' '.join(intent.constraints)} {intent.goal} {intent.next_action}".lower() for keyword in keywords)
        )
        inspected_matches = tuple(
            source.path for source in inspected if any(keyword in source.summary.lower() for keyword in keywords)
        )
        surface_evidence = (*decision_matches, *task_matches, *intent_matches, *inspected_matches)
        if not surface_evidence:
            assessments.append(
                DomainAssessment(
                    domain.domain,
                    domain.requirement,
                    AssessmentStatus.NOT_APPLICABLE,
                    Confidence.UNKNOWN,
                    (),
                    False,
                    "No inspected or imported evidence made this conditional domain materially relevant.",
                )
            )
        elif decision_matches and explicit_source:
            assessments.append(
                DomainAssessment(
                    domain.domain,
                    domain.requirement,
                    AssessmentStatus.ESTABLISHED,
                    Confidence.INFERRED_HIGH,
                    (*surface_evidence, *decisions_path, *decision_matches),
                    False,
                    "Relevant governing decision evidence was parsed.",
                )
            )
        else:
            assessments.append(
                DomainAssessment(
                    domain.domain,
                    domain.requirement,
                    AssessmentStatus.NEEDS_CONFIRMATION,
                    Confidence.UNKNOWN,
                    surface_evidence,
                    True,
                    "The domain is relevant, but no governing policy was established from inspected content.",
                )
            )
    historical = tuple(
        source.path
        for source in discovery.sources
        if source.classification in {SourceClassification.HISTORICAL, SourceClassification.STALE_OR_CONFLICTING}
    )
    for domain_name in ("pre-adoption rationale", "rejected historical approaches", "complete pre-adoption history"):
        domain = definitions[domain_name]
        assessments.append(
            DomainAssessment(
                domain.domain,
                domain.requirement,
                AssessmentStatus.DEFERRED,
                Confidence.UNKNOWN,
                historical,
                False,
                "Optional history is preserved as evidence and is not required to establish the adoption boundary.",
            )
        )
    return tuple(assessments)


def generate_interview_prompts(assessments: tuple[DomainAssessment, ...]) -> tuple[InterviewPrompt, ...]:
    prompts: list[InterviewPrompt] = []
    for assessment in assessments:
        if not assessment.blocking:
            continue
        evidence = ", ".join(assessment.evidence)
        context = (
            f"Status={assessment.status}; confidence={assessment.confidence}; "
            f"evidence={evidence or 'not yet identified'}. {assessment.reason}"
        )
        if assessment.domain == "active work":
            question = "Enter `none`, or `TASK_ID | title | owner | dependencies-or-none | current execution point`."
        elif assessment.domain == "tasks / dependencies":
            question = "Enter `none` if no additional tasks exist; otherwise leave blank and edit candidate TASKS.md after staging."
        elif assessment.domain == "blocked / waiting":
            question = "Enter `none`, or `TASK_ID | title | blocking or waiting reason`."
        elif assessment.domain == "validation / evidence":
            question = "Enter `none`, or `UNTESTED|SYNTHETIC|AI_REVIEWED|HUMAN_VERIFIED | evidence summary` for confirmed active work."
        elif assessment.domain == "next action":
            question = "State the exact safe next action, or enter `none` when no work is active."
        elif assessment.domain == "current authority":
            question = (
                f"Does `{assessment.evidence[0]}` govern current project truth? If not, identify the governing source."
                if len(assessment.evidence) == 1
                else f"Which inspected source governs current project truth: {evidence}?"
                if assessment.evidence
                else "Question objective: identify the source that governs current project truth and the evidence for its authority."
            )
        elif assessment.domain == "current architecture / domain model":
            question = (
                f"Core inspected these architecture candidates but could not determine current authority: {evidence}. Identify what governs now."
                if assessment.evidence
                else "Question objective: identify the current architecture/domain model and its governing source."
            )
        elif assessment.requirement == Requirement.CONDITIONAL:
            question = f"Confirm the current truth for {assessment.domain}, or enter `not applicable`:"
        else:
            question = f"Question objective: establish {assessment.domain} with a concrete current source or explicit confirmation."
        prompts.append(InterviewPrompt(assessment.domain, context, question))
    return tuple(prompts)


def _answer_prompts(prompts: tuple[InterviewPrompt, ...]) -> dict[str, str]:
    answers: dict[str, str] = {}
    for prompt in prompts:
        if prompt.domain == "next action" and answers.get("active work", "").casefold() == "none":
            answers[prompt.domain] = "none"
            continue
        try:
            answer = input(f"[{prompt.domain}] {prompt.context}\n{prompt.question}\n> ").strip()
        except EOFError:
            break
        if answer:
            answers[prompt.domain] = answer
    return answers


def _task_markdown(task: Task) -> str:
    return (
        f"## {task.id}: {task.title}\n"
        f"- Status: {task.status}\n- Validation: {task.validation}\n"
        f"- Dependencies: {', '.join(task.dependencies) or 'none'}\n"
        f"- Owner: {task.owner}\n- Claimed: {task.claimed}\n"
        f"- Acceptance: {task.acceptance}\n- Evidence: {task.evidence}\n"
        f"- Governed by: {', '.join(task.governed_by) or 'none'}\n"
    )


def _intent_markdown(intent: Intent) -> str:
    return (
        f"## {intent.subject}\n- Owner: {intent.owner}\n- Updated: {intent.updated}\n"
        f"- Goal: {intent.goal}\n- Current point: {intent.current_point}\n"
        f"- Constraints: {', '.join(intent.constraints) or 'none'}\n"
        f"- Changed files: {', '.join(intent.changed_files) or 'none'}\n"
        f"- Next action: {intent.next_action}\n"
    )


def _confirmed_assessment(assessment: DomainAssessment, answer: str) -> DomainAssessment:
    not_applicable = assessment.requirement == Requirement.CONDITIONAL and answer.casefold() == "not applicable"
    return DomainAssessment(
        assessment.domain,
        assessment.requirement,
        AssessmentStatus.NOT_APPLICABLE if not_applicable else AssessmentStatus.ESTABLISHED,
        Confidence.CONFIRMED_HUMAN,
        (*assessment.evidence, f"developer interview: {answer}"),
        False,
        "Developer confirmed this domain during adoption.",
    )


def materialize_confirmations(
    tasks_text: str,
    intents_text: str,
    tasks: tuple[Task, ...],
    intents: tuple[Intent, ...],
    assessments: tuple[DomainAssessment, ...],
    answers: dict[str, str],
) -> tuple[str, str, tuple[Task, ...], tuple[Intent, ...], tuple[DomainAssessment, ...], tuple[str, ...], tuple[str, ...]]:
    added_tasks: list[Task] = []
    added_intents: list[Intent] = []
    issues: list[str] = []
    by_domain = {assessment.domain: assessment for assessment in assessments}
    special_domains = {"active work", "tasks / dependencies", "blocked / waiting", "validation / evidence", "next action"}
    valid_domains: set[str] = set()
    for domain, answer in answers.items():
        if not answer or domain in special_domains:
            continue
        if answer.casefold() == "not applicable" and by_domain[domain].requirement == Requirement.REQUIRED:
            issues.append(f"{domain} is REQUIRED and cannot be marked not applicable")
        else:
            valid_domains.add(domain)
    existing_ids = {task.id for task in tasks}
    active_answer = answers.get("active work")
    next_answer = answers.get("next action")
    validation_answer = answers.get("validation / evidence")
    validation = "UNTESTED"
    validation_evidence = "Developer confirmation during adoption."
    # ponytail: interactive Core materializes one active and one blocked task; edit candidate Markdown for larger task graphs.
    if validation_answer and validation_answer.casefold() != "none":
        parts = [part.strip() for part in validation_answer.split("|", 1)]
        if len(parts) == 2 and parts[0].upper() in VALIDATION_LEVELS and parts[1]:
            validation, validation_evidence = parts[0].upper(), parts[1]
            valid_domains.add("validation / evidence")
        else:
            issues.append("validation / evidence answer must be `LEVEL | evidence summary` or `none`")
    elif active_answer and active_answer.casefold() == "none":
        valid_domains.add("validation / evidence")
    if active_answer:
        if active_answer.casefold() == "none":
            valid_domains.update(("active work", "next action"))
        else:
            parts = [part.strip() for part in active_answer.split("|", 4)]
            if len(parts) != 5 or not all(parts):
                issues.append("active work answer must be `TASK_ID | title | owner | dependencies-or-none | current execution point`")
            elif not re.fullmatch(r"T-[A-Za-z0-9][A-Za-z0-9-]*", parts[0]) or parts[0] in existing_ids:
                issues.append("active work answer must use a unique valid T- task ID")
            elif not next_answer or next_answer.casefold() == "none":
                issues.append("confirmed active work requires an exact next action")
            else:
                dependencies = (
                    () if parts[3].casefold() in {"none", "-"} else tuple(item.strip() for item in parts[3].split(",") if item.strip())
                )
                task = Task(
                    parts[0],
                    parts[1],
                    dependencies,
                    "WIP",
                    validation,
                    parts[2],
                    date.today().isoformat(),
                    f"Complete the human-confirmed active work: {parts[1]}",
                    validation_evidence,
                    (),
                )
                intent = Intent(
                    task.id,
                    task.owner,
                    date.today().isoformat(),
                    task.acceptance,
                    parts[4],
                    (),
                    (),
                    next_answer,
                )
                added_tasks.append(task)
                added_intents.append(intent)
                existing_ids.add(task.id)
                valid_domains.update(("active work", "next action"))
    blocked_answer = answers.get("blocked / waiting")
    if blocked_answer:
        if blocked_answer.casefold() == "none":
            valid_domains.add("blocked / waiting")
        else:
            parts = [part.strip() for part in blocked_answer.split("|", 2)]
            if len(parts) != 3 or not all(parts):
                issues.append("blocked / waiting answer must be `TASK_ID | title | blocking or waiting reason`")
            elif not re.fullmatch(r"T-[A-Za-z0-9][A-Za-z0-9-]*", parts[0]) or parts[0] in existing_ids:
                issues.append("blocked / waiting answer must use a unique valid T- task ID")
            else:
                task = Task(
                    parts[0],
                    parts[1],
                    (),
                    "BLOCKED",
                    "UNTESTED",
                    "",
                    "",
                    parts[2],
                    "Developer confirmation during adoption.",
                    (),
                )
                added_tasks.append(task)
                existing_ids.add(task.id)
                valid_domains.add("blocked / waiting")
    task_answer = answers.get("tasks / dependencies")
    if task_answer:
        if task_answer.casefold() == "none":
            valid_domains.add("tasks / dependencies")
        else:
            issues.append("additional tasks must be materialized by editing candidate TASKS.md before apply")
    if next_answer and (active_answer is None or active_answer.casefold() == "none"):
        if next_answer.casefold() == "none":
            valid_domains.add("next action")
    if added_tasks and any(task.status == "BLOCKED" for task in added_tasks):
        valid_domains.add("human validation gates")

    updated = tuple(
        _confirmed_assessment(assessment, answers.get(assessment.domain, "confirmed by operational state"))
        if assessment.domain in valid_domains
        else assessment
        for assessment in assessments
    )
    if added_tasks:
        tasks_text = tasks_text.rstrip() + "\n\n" + "\n".join(_task_markdown(task) for task in added_tasks)
    if added_intents:
        intents_text = "# Intents\n\n" + "\n".join(_intent_markdown(intent) for intent in (*intents, *added_intents))
    return (
        tasks_text,
        intents_text,
        (*tasks, *added_tasks),
        (*intents, *added_intents),
        updated,
        tuple(issues),
        tuple(task.id for task in added_tasks),
    )


def _render_assessments(assessments: tuple[DomainAssessment, ...]) -> list[str]:
    lines: list[str] = []
    for assessment in assessments:
        lines.extend(
            (
                f"### {assessment.domain}",
                f"- Requirement: {assessment.requirement}",
                f"- Status: {assessment.status}",
                f"- Confidence: {assessment.confidence}",
                f"- Evidence: {', '.join(assessment.evidence) or 'none'}",
                f"- Blocking: {'yes' if assessment.blocking else 'no'}",
                f"- Reason: {assessment.reason}",
                "",
            )
        )
    return lines


def _render_interview(assessments: tuple[DomainAssessment, ...], prompts: tuple[InterviewPrompt, ...], answers: dict[str, str]) -> str:
    lines = ["# Adoption Interview", "", "## Coverage assessments", "", *_render_assessments(assessments), "## Structured prompts", ""]
    by_domain = {assessment.domain: assessment for assessment in assessments}
    for prompt in prompts:
        assessment = by_domain[prompt.domain]
        confirmed = assessment.confidence == Confidence.CONFIRMED_HUMAN and not assessment.blocking
        materialized = (
            "TASKS.md and INTENTS.md"
            if prompt.domain in {"active work", "next action"}
            else "TASKS.md"
            if prompt.domain in {"tasks / dependencies", "blocked / waiting", "validation / evidence"}
            else "DECISIONS.md and BASELINE.md"
        )
        lines.extend(
            (
                f"### {prompt.domain}",
                f"- Context: {prompt.context}",
                f"- Question: {prompt.question}",
                f"- Answer: {answers.get(prompt.domain, 'pending')}",
                f"- Confirmation date: {date.today().isoformat() if prompt.domain in answers else 'pending'}",
                f"- Confidence: {assessment.confidence}",
                f"- Candidate effect: {materialized if confirmed else 'pending correction or review'}",
                "",
            )
        )
    if not prompts:
        lines.append("- No confirmation prompts remain.\n")
    return "\n".join(lines)


def _source_map(discovery: Discovery) -> str:
    lines = [
        "# Adoption Source Map",
        "",
        "Priority controls retrieval order; it does not establish authority.",
        "",
        "| Source | Priority | Classification | Reason |",
        "|---|---:|---|---|",
    ]
    lines.extend(f"| `{source.path}` | {source.priority} | {source.classification} | {source.reason} |" for source in discovery.sources)
    if not discovery.sources:
        lines.append("| none | - | UNKNOWN | No likely current-state source was found. |")
    return "\n".join([*lines, ""])


def _next_baseline_id(decisions: tuple[object, ...]) -> str:
    ids = {decision.id for decision in decisions if isinstance(decision, Decision)}
    number = 1
    while f"ADR-A{number:03d}" in ids:
        number += 1
    return f"ADR-A{number:03d}"


def stage_adoption(project: Path, from_path: str | None = None, interactive: bool = False) -> AdoptionResult:
    discovery = discover(project)
    if discovery.has_prokron:
        raise ProkronError(".prokron already exists; adoption cannot replace canonical state")
    candidate = project / ADOPTION_DIR
    if candidate.exists():
        raise ProkronError(f"{ADOPTION_DIR} already exists; review or remove the existing candidate first")
    root = _source_root(project, from_path)
    strict_migration = root is not None
    template_root = files("prokron").joinpath("templates")
    selected: dict[str, Path | None] = {}
    conflicts: list[str] = []
    incompatibilities: list[str] = []
    format_issues: dict[str, str] = {}
    for name in ("TASKS.md", "DECISIONS.md", "INTENTS.md"):
        selected[name], conflict = _select(project, root, name)
        if conflict:
            (conflicts if strict_migration else incompatibilities).append(conflict)
    tasks_text, tasks, tasks_error = _read_structured(
        selected["TASKS.md"], template_root.joinpath("TASKS.md").read_text(encoding="utf-8"), parse_tasks
    )
    if tasks_error:
        incompatibilities.append(tasks_error)
        format_issues["TASKS.md"] = tasks_error
    decisions_text, decisions, decisions_error = _read_structured(
        selected["DECISIONS.md"], template_root.joinpath("DECISIONS.md").read_text(encoding="utf-8"), parse_decisions
    )
    if decisions_error:
        incompatibilities.append(decisions_error)
        format_issues["DECISIONS.md"] = decisions_error
    intents_text, intents, intents_error = _read_structured(
        selected["INTENTS.md"], template_root.joinpath("INTENTS.md").read_text(encoding="utf-8"), parse_intents
    )
    if intents_error:
        incompatibilities.append(intents_error)
        format_issues["INTENTS.md"] = intents_error
    usable_selected = {
        "TASKS.md": selected["TASKS.md"] if tasks_error is None and tasks else None,
        "DECISIONS.md": selected["DECISIONS.md"] if decisions_error is None and decisions else None,
        "INTENTS.md": selected["INTENTS.md"] if intents_error is None and intents else None,
    }
    purpose, purpose_source = _project_purpose(project)
    inspected = _inspect_current_sources(project, discovery)
    baseline_id = _next_baseline_id(decisions)
    assessments = assess_domains(
        project,
        discovery,
        usable_selected,
        purpose_source,
        root is not None,
        tasks,
        decisions,
        intents,
        tuple(conflicts),
        inspected,
        format_issues if strict_migration else {},
    )
    prompts = generate_interview_prompts(assessments)
    answers = _answer_prompts(prompts) if interactive else {}
    imported_task_count = len(tasks)
    imported_intent_count = len(intents)
    tasks_text, intents_text, tasks, intents, assessments, confirmation_issues, materialized_ids = materialize_confirmations(
        tasks_text, intents_text, tasks, intents, assessments, answers
    )
    conflicts.extend(confirmation_issues)
    semantic_domains = {
        "project identity",
        "current authority",
        "current architecture / domain model",
        "constraints / invariants",
        "current governing decisions",
        "production / release restrictions",
        "deployment state",
        "human validation gates",
        "security / destructive-operation constraints",
    }
    confirmed_answer_domains = {assessment.domain for assessment in assessments if assessment.confidence == Confidence.CONFIRMED_HUMAN}
    semantic_answers = "; ".join(
        f"{domain}: {answer}" for domain, answer in answers.items() if domain in semantic_domains and domain in confirmed_answer_domains
    )
    decision_text = (
        f"Approve the adoption boundary and these human-confirmed governing semantics: {semantic_answers}."
        if semantic_answers
        else "Approve the facts, provenance, unknowns, conflicts, and limitations recorded in BASELINE.md as the adoption boundary."
    )
    baseline_decision = Decision(
        baseline_id,
        BASELINE_TITLE,
        date.today().isoformat(),
        "PROPOSED",
        "adoption review",
        (),
        (),
        (),
        (),
        materialized_ids,
        "Current project truth needs an explicit boundary without fabricated pre-adoption history.",
        decision_text,
    )
    state_errors = validate(ProkronState(tasks, (*decisions, baseline_decision), intents, ()))
    conflicts.extend(f"candidate canonical state is invalid: {error}" for error in state_errors)
    if state_errors:
        assessments = tuple(
            replace(
                assessment,
                status=AssessmentStatus.CONFLICTING,
                confidence=Confidence.CONFLICTING,
                blocking=True,
                reason="Candidate canonical state failed integrity validation.",
            )
            if assessment.domain == "current authority"
            else assessment
            for assessment in assessments
        )
    unknowns = tuple(
        assessment.domain for assessment in assessments if assessment.blocking and assessment.status == AssessmentStatus.NEEDS_CONFIRMATION
    )
    source_lines = [source.path for source in discovery.sources]
    inspected_lines = ["Git branch, HEAD, and working-tree metadata"]
    if discovery.recent_commit:
        inspected_lines.append(f"Recent commit metadata: {discovery.recent_commit}")
    inspected_lines.extend(f"{source.path} (bounded text inspection)" for source in inspected)
    if purpose_source:
        inspected_lines.append(f"{purpose_source} (bounded purpose paragraph)")
    for name, error in (("TASKS.md", tasks_error), ("DECISIONS.md", decisions_error), ("INTENTS.md", intents_error)):
        selected_path = selected[name]
        if selected_path is not None:
            outcome = "structured parse" if error is None else "structured parse failed"
            inspected_lines.append(f"{selected_path.relative_to(project).as_posix()} ({outcome})")
    confirmed_domains = {assessment.domain for assessment in assessments if assessment.confidence == Confidence.CONFIRMED_HUMAN}
    human_lines = [
        f"- {domain}: {answer} [{Confidence.CONFIRMED_HUMAN}]" for domain, answer in answers.items() if domain in confirmed_domains
    ]
    selected_confidence = Confidence.INFERRED_HIGH if root is not None else Confidence.INFERRED_LOW
    structured_inferences = (
        [f"- Selected structured state files are candidate current truth until apply. [{selected_confidence}]"]
        if tasks or decisions or intents
        else []
    )
    hypothesis_lines = [
        f"- `{source.path}` suggests: {source.summary} [{Confidence.INFERRED_LOW}]"
        for source in inspected
        if source.path != purpose_source
    ]
    if discovery.branch not in {"main", "master", "trunk", "detached HEAD"}:
        planning = tuple(source.path for source in inspected if set(source.concepts) & {"roadmap", "implementation-plan", "current-work"})
        confidence = Confidence.INFERRED_HIGH if discovery.recent_commit and planning else Confidence.INFERRED_LOW
        detail = f", recent commit `{discovery.recent_commit}`, and {', '.join(f'`{path}`' for path in planning)}" if confidence == Confidence.INFERRED_HIGH else ""
        hypothesis_lines.append(
            f"- Current-work signal from branch `{discovery.branch}`{detail} requires confirmation. [{confidence}]"
        )
    if discovery.changed_files:
        hypothesis_lines.append(
            f"- Working-tree changes may indicate active work: {', '.join(discovery.changed_files[:8])}. [{Confidence.INFERRED_LOW}]"
        )
    inferred_lines = structured_inferences + hypothesis_lines or ["- None."]
    purpose_value = answers.get("project identity", purpose)
    purpose_confidence = Confidence.CONFIRMED_HUMAN if "project identity" in confirmed_domains else Confidence.INFERRED_HIGH
    blocking_lines = [
        f"- BLOCKING: {assessment.domain} — {assessment.reason} [{assessment.confidence}]"
        for assessment in assessments
        if assessment.blocking
    ]
    baseline = "\n".join(
        [
            "# Adoption Baseline",
            "",
            f"- Adoption date: {date.today().isoformat()}",
            f"- Baseline decision: {baseline_id}",
            "- Boundary: Pre-adoption history is evidence and may be incomplete; approved state begins Prokron-governed history.",
            "",
            "## Current governing state",
            f"- Project purpose: {purpose_value} [{purpose_confidence}; source: {'developer interview' if 'project identity' in confirmed_domains else purpose_source or 'none'}]",
            f"- Git branch: {discovery.branch} [{Confidence.CONFIRMED_REPOSITORY}; source: Git metadata]",
            f"- Git HEAD: {discovery.head} [{Confidence.CONFIRMED_REPOSITORY}; source: Git metadata]",
            f"- Working tree: {'modified' if discovery.dirty else 'clean'} [{Confidence.CONFIRMED_REPOSITORY}; source: Git status]",
            f"- Imported candidate tasks: {imported_task_count} [{selected_confidence if usable_selected['TASKS.md'] else Confidence.UNKNOWN}; source: {usable_selected['TASKS.md'].relative_to(project).as_posix() if usable_selected['TASKS.md'] else 'none'}]",
            f"- Human-confirmed operational tasks: {len(tasks) - imported_task_count} [{Confidence.CONFIRMED_HUMAN if len(tasks) > imported_task_count else Confidence.UNKNOWN}; source: {'developer interview' if len(tasks) > imported_task_count else 'none'}]",
            f"- Candidate decisions before baseline: {len(decisions)} [{selected_confidence if usable_selected['DECISIONS.md'] else Confidence.UNKNOWN}; source: {usable_selected['DECISIONS.md'].relative_to(project).as_posix() if usable_selected['DECISIONS.md'] else 'none'}]",
            f"- Imported active intents: {imported_intent_count} [{selected_confidence if usable_selected['INTENTS.md'] else Confidence.UNKNOWN}; source: {usable_selected['INTENTS.md'].relative_to(project).as_posix() if usable_selected['INTENTS.md'] else 'none'}]",
            f"- Human-confirmed active intents: {len(intents) - imported_intent_count} [{Confidence.CONFIRMED_HUMAN if len(intents) > imported_intent_count else Confidence.UNKNOWN}; source: {'developer interview' if len(intents) > imported_intent_count else 'none'}]",
            "",
            "## Current-state hypotheses",
            *inferred_lines,
            "",
            "## Current truth confirmed by human",
            *(human_lines or ["- None."]),
            "",
            "## Unresolved unknowns",
            *(blocking_lines or ["- None."]),
            "",
            "## Unresolved conflicts",
            *(f"- BLOCKING: {conflict} [{Confidence.CONFLICTING}]" for conflict in conflicts),
            *([] if conflicts else ["- None."]),
            "",
            "## Migration / format incompatibilities",
            *(f"- {'BLOCKING' if strict_migration else 'INFO'}: {issue} [{Confidence.UNKNOWN}]" for issue in incompatibilities),
            *([] if incompatibilities else ["- None."]),
            "",
            "## Sources discovered",
            *(f"- `{path}`" for path in source_lines),
            *([] if source_lines else ["- None."]),
            "",
            "## Content actually inspected",
            *(f"- {line}" for line in inspected_lines),
            "",
            "## Coverage assessments",
            "",
            *_render_assessments(assessments),
            "## Limitations",
            "- No complete Git-history reconstruction or repository-wide semantic ingestion was performed.",
            "- Filename-classified sources were discovered, not content-inspected, unless listed above.",
            "- Source priority guided retrieval but did not establish authority.",
            "",
        ]
    )
    decision_section = (
        f"## {baseline_id}: {BASELINE_TITLE}\n"
        f"- Date: {date.today().isoformat()}\n- Status: PROPOSED\n- Authority: adoption review\n"
        "- Supersedes: none\n- Amends: none\n- Corrects: none\n- Rejects: none\n"
        f"- Affects: {', '.join(materialized_ids) or 'none'}\n"
        "- Context: Current project truth needs an explicit boundary without fabricated pre-adoption history.\n"
        f"- Decision: {decision_text}\n"
    )
    report = "\n".join(
        [
            "# Adoption Report",
            "",
            "## ADOPTION DATE",
            f"- {date.today().isoformat()}",
            "",
            "## DISCOVERED SOURCES (FILENAME / METADATA ONLY)",
            *(f"- `{path}`" for path in source_lines),
            *([] if source_lines else ["- None."]),
            "",
            "## CONTENT ACTUALLY INSPECTED",
            *(f"- {line}" for line in inspected_lines),
            "",
            "## CURRENT TRUTH CONFIRMED FROM REPOSITORY",
            f"- Git branch and working-tree state. [{Confidence.CONFIRMED_REPOSITORY}]",
            *([f"- Project purpose text from `{purpose_source}`. [{Confidence.INFERRED_HIGH}]"] if purpose_source else ["- None."]),
            "",
            "## CURRENT TRUTH CONFIRMED BY HUMAN",
            *(human_lines or ["- None."]),
            "",
            "## INFERRED FACTS",
            *inferred_lines,
            "",
            "## COVERAGE ASSESSMENTS",
            "",
            *_render_assessments(assessments),
            "",
            "## UNRESOLVED UNKNOWNS",
            *(blocking_lines or ["- None."]),
            "",
            "## CONFLICTING SOURCES",
            *(f"- BLOCKING: {conflict} [{Confidence.CONFLICTING}]" for conflict in conflicts),
            *([] if conflicts else ["- None."]),
            "",
            "## MIGRATION / FORMAT INCOMPATIBILITIES",
            *(f"- {'BLOCKING' if strict_migration else 'INFO'}: {issue} [{Confidence.UNKNOWN}]" for issue in incompatibilities),
            *([] if incompatibilities else ["- None."]),
            "",
            "## HISTORICAL MATERIAL NOT MIGRATED",
            "- Pre-adoption history without a current governing effect was not migrated.",
            "",
            "## LEGACY STATE SOURCES PRESERVED",
            f"- {root.relative_to(project).as_posix() if root else 'All discovered sources remain in place.'}",
            "",
            "## IMPLEMENTATION EVIDENCE DISCOVERED (CONTENT NOT INSPECTED)",
            *(
                f"- Located `{source.path}`; content was not inspected."
                for source in discovery.sources
                if source.classification == SourceClassification.IMPLEMENTATION_EVIDENCE
            ),
            *(
                []
                if any(source.classification == SourceClassification.IMPLEMENTATION_EVIDENCE for source in discovery.sources)
                else ["- None."]
            ),
            "",
            "## ADOPTION LIMITATIONS",
            "- Discovery used filenames and repository metadata; source code was not recursively interpreted.",
            "- Apply is blocked while any `BLOCKING` item remains.",
            "",
        ]
    )
    interview = _render_interview(assessments, prompts, answers)
    candidate.mkdir()
    outputs = {
        "BASELINE.md": baseline,
        "TASKS.md": tasks_text,
        "DECISIONS.md": decisions_text.rstrip() + "\n\n" + decision_section,
        "INTENTS.md": intents_text,
        "SOURCE_MAP.md": _source_map(discovery),
        "ADOPTION_REPORT.md": report,
        "INTERVIEW.md": interview,
        "README.md": template_root.joinpath("README.md").read_text(encoding="utf-8"),
        "JOURNAL.md": template_root.joinpath("JOURNAL.md").read_text(encoding="utf-8"),
    }
    for name, content in outputs.items():
        (candidate / name).write_text(content, encoding="utf-8")
    return AdoptionResult(discovery, tuple(unknowns), tuple(conflicts), tuple(incompatibilities))


def apply_adoption(project: Path) -> None:
    candidate = project / ADOPTION_DIR
    target = prokron_dir(project)
    if target.exists():
        raise ProkronError(".prokron already exists; adoption cannot replace canonical state")
    if not candidate.is_dir() or candidate.is_symlink():
        raise ProkronError(f"{ADOPTION_DIR} is missing; run `prokron adopt` and review the candidate first")
    required = {*CANONICAL_FILES, "BASELINE.md", "SOURCE_MAP.md", "ADOPTION_REPORT.md", "INTERVIEW.md"}
    missing = sorted(name for name in required if not (candidate / name).is_file() or (candidate / name).is_symlink())
    if missing:
        raise ProkronError(f"adoption candidate is incomplete: {', '.join(missing)}")
    report = (candidate / "ADOPTION_REPORT.md").read_text(encoding="utf-8")
    baseline = (candidate / "BASELINE.md").read_text(encoding="utf-8")
    interview = (candidate / "INTERVIEW.md").read_text(encoding="utf-8")
    if "- BLOCKING:" in report or "- BLOCKING:" in baseline or "- Blocking: yes" in interview:
        raise ProkronError("adoption candidate has unresolved blocking unknowns, conflicts, or format incompatibilities")
    state = ProkronState(
        parse_tasks(candidate / "TASKS.md"),
        parse_decisions(candidate / "DECISIONS.md"),
        parse_intents(candidate / "INTENTS.md"),
        parse_journal(candidate / "JOURNAL.md"),
    )
    errors = validate(state)
    if errors:
        raise ProkronError("candidate state is invalid:\n- " + "\n- ".join(errors))
    match = re.search(r"^- Baseline decision: (ADR-[A-Za-z0-9-]+)$", baseline, re.MULTILINE)
    if match is None:
        raise ProkronError("BASELINE.md does not identify the baseline decision")
    for path in [project / name for name in ("AGENTS.md", "CLAUDE.md") if (project / name).exists()] or [project / "AGENTS.md"]:
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        if ("<!-- project-prokron:start -->" in text) != ("<!-- project-prokron:end -->" in text):
            raise ProkronError(f"{path.name}: incomplete managed Prokron block")
    candidate.rename(target)
    update_section_fields(
        target / "DECISIONS.md", DECISION_HEADER, match.group(1), {"status": "ACCEPTED", "authority": "human/explicit-adoption-apply"}
    )
    baseline_decision = next(decision for decision in state.decisions if decision.id == match.group(1))
    for task_id in baseline_decision.affects:
        update_section_fields(target / "TASKS.md", TASK_HEADER, task_id, {"governed_by": match.group(1)})
    journal = target / "JOURNAL.md"
    journal.write_text(
        "# Journal\n\n"
        f"## {datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')} — adoption boundary\n"
        "- Task: adoption\n- Owner: human/explicit-adoption-apply\n"
        "- Did: Promoted the reviewed adoption candidate to canonical Prokron state.\n"
        "- Validation: Candidate canonical files passed Prokron integrity validation.\n"
        "- Learned: Pre-adoption history remains evidence and was not fully reconstructed.\n"
        "- Left mid-air: Adoption complete; normal Prokron lineage begins here.\n"
        "- Next: Follow the approved baseline and current task state.\n",
        encoding="utf-8",
    )
    for path in [project / name for name in ("AGENTS.md", "CLAUDE.md") if (project / name).exists()] or [project / "AGENTS.md"]:
        install_bootstrap(path)
    sync_derived(project)
