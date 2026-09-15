from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from .markdown import parse_decisions, parse_intents, parse_journal, parse_tasks
from .models import ProkronError, ProkronState, Task

PROKRON = ".prokron"
CANONICAL_FILES = ("README.md", "TASKS.md", "INTENTS.md", "DECISIONS.md", "JOURNAL.md")
TASK_STATUSES = {"TODO", "WIP", "DONE", "BLOCKED"}
VALIDATION_LEVELS = {"UNTESTED", "SYNTHETIC", "AI_REVIEWED", "HUMAN_VERIFIED"}
DECISION_STATUSES = {"PROPOSED", "ACCEPTED", "REJECTED", "SUPERSEDED"}


def prokron_dir(project: Path) -> Path:
    return project / PROKRON


def load_state(project: Path) -> ProkronState:
    root = prokron_dir(project)
    if not root.is_dir():
        raise ProkronError("Project Prokron is not initialized. Run `prokron init` first.")
    return ProkronState(
        tasks=parse_tasks(root / "TASKS.md"),
        decisions=parse_decisions(root / "DECISIONS.md"),
        intents=parse_intents(root / "INTENTS.md"),
        journal=parse_journal(root / "JOURNAL.md"),
    )


def eligible_tasks(state: ProkronState) -> tuple[Task, ...]:
    by_id = {task.id: task for task in state.tasks}
    return tuple(
        task
        for task in state.tasks
        if task.status == "TODO" and all(by_id.get(dependency) and by_id[dependency].status == "DONE" for dependency in task.dependencies)
    )


def _task_cycle(tasks: tuple[Task, ...]) -> tuple[str, ...]:
    by_id = {task.id: task for task in tasks}
    visiting: list[str] = []
    visited: set[str] = set()

    def visit(task_id: str) -> tuple[str, ...]:
        if task_id in visiting:
            start = visiting.index(task_id)
            return tuple([*visiting[start:], task_id])
        if task_id in visited or task_id not in by_id:
            return ()
        visiting.append(task_id)
        for dependency in sorted(by_id[task_id].dependencies):
            if cycle := visit(dependency):
                return cycle
        visiting.pop()
        visited.add(task_id)
        return ()

    for task_id in sorted(by_id):
        if cycle := visit(task_id):
            return cycle
    return ()


def _decision_cycle(state: ProkronState) -> tuple[str, ...]:
    by_id = {decision.id: decision for decision in state.decisions}
    visiting: list[str] = []
    visited: set[str] = set()

    def visit(decision_id: str) -> tuple[str, ...]:
        if decision_id in visiting:
            start = visiting.index(decision_id)
            return tuple([*visiting[start:], decision_id])
        if decision_id in visited or decision_id not in by_id:
            return ()
        visiting.append(decision_id)
        for target in sorted(by_id[decision_id].supersedes):
            if cycle := visit(target):
                return cycle
        visiting.pop()
        visited.add(decision_id)
        return ()

    for decision_id in sorted(by_id):
        if cycle := visit(decision_id):
            return cycle
    return ()


def validate(state: ProkronState) -> list[str]:
    errors: list[str] = []
    task_counts = Counter(task.id for task in state.tasks)
    decision_counts = Counter(decision.id for decision in state.decisions)
    task_by_id = {task.id: task for task in state.tasks}
    decision_by_id = {decision.id: decision for decision in state.decisions}

    for task_id, count in sorted(task_counts.items()):
        if count > 1:
            errors.append(f"duplicate task ID: {task_id}")
    for task in state.tasks:
        if task.status not in TASK_STATUSES:
            errors.append(f"{task.id}: invalid status {task.status}")
        if task.validation not in VALIDATION_LEVELS:
            errors.append(f"{task.id}: invalid validation {task.validation}")
        for dependency in task.dependencies:
            if dependency not in task_by_id:
                errors.append(f"{task.id}: missing dependency {dependency}")
        for decision_id in task.governed_by:
            if decision_id not in decision_by_id:
                errors.append(f"{task.id}: missing governing decision {decision_id}")
            elif decision_by_id[decision_id].status != "ACCEPTED":
                errors.append(f"{task.id}: governed by non-current decision {decision_id}")
        if task.status == "WIP" and not task.owner:
            errors.append(f"{task.id}: WIP requires Owner")
        if task.status == "WIP" and not task.claimed:
            errors.append(f"{task.id}: WIP requires Claimed")
        if task.status == "DONE" and not task.acceptance:
            errors.append(f"{task.id}: DONE requires Acceptance")
        if task.status == "DONE" and not task.evidence:
            errors.append(f"{task.id}: DONE requires Evidence")
    if cycle := _task_cycle(state.tasks):
        errors.append(f"dependency cycle: {' -> '.join(cycle)}")

    for decision_id, count in sorted(decision_counts.items()):
        if count > 1:
            errors.append(f"duplicate decision ID: {decision_id}")
    superseded_by: dict[str, list[str]] = defaultdict(list)
    for decision in state.decisions:
        if decision.status not in DECISION_STATUSES:
            errors.append(f"{decision.id}: invalid decision status {decision.status}")
        if not decision.authority:
            errors.append(f"{decision.id}: Authority is required")
        relationships = {
            "supersedes": decision.supersedes,
            "amends": decision.amends,
            "corrects": decision.corrects,
            "rejects": decision.rejects,
        }
        used_targets: dict[str, str] = {}
        for relationship, targets in relationships.items():
            for target in targets:
                if target == decision.id:
                    errors.append(f"{decision.id}: cannot {relationship} itself")
                elif target not in decision_by_id:
                    errors.append(f"{decision.id}: {relationship} missing decision {target}")
                if target in used_targets:
                    errors.append(f"{decision.id}: {target} appears in both {used_targets[target]} and {relationship}")
                used_targets[target] = relationship
                if relationship == "supersedes":
                    superseded_by[target].append(decision.id)
                    if decision.status not in {"ACCEPTED", "SUPERSEDED"}:
                        errors.append(f"{decision.id}: non-authoritative decision cannot supersede {target}")
        for task_id in decision.affects:
            if task_id not in task_by_id:
                errors.append(f"{decision.id}: affects missing task {task_id}")
    for target, sources in sorted(superseded_by.items()):
        if len(sources) > 1:
            errors.append(f"{target}: multiple superseding decisions: {', '.join(sorted(sources))}")
        if target in decision_by_id and decision_by_id[target].status != "SUPERSEDED":
            errors.append(f"{target}: referenced as superseded but status is {decision_by_id[target].status}")
    for decision in state.decisions:
        if decision.status == "SUPERSEDED" and decision.id not in superseded_by:
            errors.append(f"{decision.id}: SUPERSEDED without a superseding decision")
    if cycle := _decision_cycle(state):
        errors.append(f"decision supersession cycle: {' -> '.join(cycle)}")

    intent_counts = Counter(intent.subject for intent in state.intents)
    for subject, count in sorted(intent_counts.items()):
        if count > 1:
            errors.append(f"duplicate active intent: {subject}")
    for intent in state.intents:
        if not all((intent.owner, intent.updated, intent.goal, intent.current_point, intent.next_action)):
            errors.append(f"{intent.subject}: active intent has empty required fields")
        if intent.task_id:
            intent_task = task_by_id.get(intent.task_id)
            if intent_task is None:
                errors.append(f"active intent references missing task {intent.task_id}")
            elif intent_task.status == "DONE":
                errors.append(f"active intent references completed task {intent.task_id}")
            elif intent_task.status != "WIP":
                errors.append(f"active intent references non-WIP task {intent.task_id}")
            elif intent_task.owner != intent.owner:
                errors.append(f"{intent.task_id}: task owner and intent owner disagree")
    for entry in state.journal:
        if not entry.left_mid_air:
            errors.append(f"journal entry {entry.label}: Left mid-air is required")
    return errors
