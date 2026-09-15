from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .core import eligible_tasks, load_state, prokron_dir, validate
from .models import Decision, ProkronError, ProkronState, Task


def _blocked_tasks(state: ProkronState) -> tuple[tuple[Task, tuple[str, ...]], ...]:
    by_id = {task.id: task for task in state.tasks}
    blocked: list[tuple[Task, tuple[str, ...]]] = []
    for task in state.tasks:
        incomplete = tuple(dependency for dependency in task.dependencies if dependency not in by_id or by_id[dependency].status != "DONE")
        if task.status == "BLOCKED" or (task.status == "TODO" and incomplete):
            blocked.append((task, incomplete))
    return tuple(blocked)


def render_graph(state: ProkronState) -> str:
    ready_ids = {task.id for task in eligible_tasks(state)}
    blocked_ids = [task.id for task, _ in _blocked_tasks(state)]
    unlocked_by: dict[str, list[str]] = defaultdict(list)
    for task in state.tasks:
        for dependency in task.dependencies:
            unlocked_by[dependency].append(task.id)
    lines = ["# Task Graph", "", "Generated from `TASKS.md`; do not edit manually.", "", "## Summary"]
    for status in ("DONE", "WIP", "TODO", "BLOCKED"):
        ids = [task.id for task in state.tasks if task.status == status]
        lines.append(f"- {status}: {', '.join(ids) if ids else 'none'}")
    lines.append(f"- Eligible now: {', '.join(task.id for task in eligible_tasks(state)) or 'none'}")
    lines.append(f"- Blocked / waiting: {', '.join(blocked_ids) or 'none'}")
    lines.extend(("", "## Tasks"))
    if not state.tasks:
        lines.append("- None")
    for task in state.tasks:
        lines.append(f"- {task.id} [{task.status}] {task.title}")
        lines.append(f"  - depends on: {', '.join(task.dependencies) or 'none'}")
        lines.append(f"  - unlocks: {', '.join(unlocked_by[task.id]) or 'none'}")
        lines.append(f"  - eligible: {'yes' if task.id in ready_ids else 'no'}")
    return "\n".join([*lines, ""])


def render_state(project: Path, state: ProkronState) -> str:
    intents = {intent.task_id: intent for intent in state.intents if intent.task_id}
    ready = eligible_tasks(state)
    blocked = _blocked_tasks(state)
    relevant_ids = {
        decision_id
        for task in (*[task for task in state.tasks if task.status == "WIP"], *ready)
        for decision_id in task.governed_by
    }
    decisions = [decision for decision in state.decisions if decision.id in relevant_ids and decision.status == "ACCEPTED"]
    lines = [
        "# State",
        "",
        "Generated from canonical Prokron files; do not edit manually.",
        "",
        "## Current",
        f"- Project: {project.name}",
        f"- Tasks: {len(state.tasks)}",
        f"- Active intents: {len(state.intents)}",
        "",
        "## In flight",
    ]
    wip = [task for task in state.tasks if task.status == "WIP"]
    if not wip:
        lines.append("- None")
    for task in wip:
        intent = intents.get(task.id)
        lines.append(f"- {task.id}: {task.title} — {task.owner}")
        if intent:
            lines.append(f"  - Current point: {intent.current_point}")
            lines.append(f"  - Next action: {intent.next_action}")
    lines.extend(("", "## Ready"))
    lines.extend(f"- {task.id}: {task.title}" for task in ready)
    if not ready:
        lines.append("- None")
    lines.extend(("", "## Blocked / waiting"))
    for task, dependencies in blocked:
        reason = f"waiting on {', '.join(dependencies)}" if dependencies else "explicitly blocked"
        lines.append(f"- {task.id}: {reason}")
    if not blocked:
        lines.append("- None")
    lines.extend(("", "## Governing decisions"))
    lines.extend(f"- {decision.id}: {decision.title}" for decision in decisions)
    if not decisions:
        lines.append("- None")
    uncertain = [task.id for task in state.tasks if task.status != "DONE" and task.validation == "UNTESTED"]
    lines.extend(("", "## Risks / uncertainty", f"- Untested active or pending work: {', '.join(uncertain) or 'none'}", "", "## Next"))
    next_actions = [intent.next_action for intent in state.intents if intent.next_action]
    if next_actions:
        lines.extend(f"- {action}" for action in next_actions)
    elif ready:
        lines.append(f"- Start {ready[0].id}: {ready[0].title}")
    else:
        lines.append("- No eligible task.")
    return "\n".join([*lines, ""])


def sync_derived(project: Path, state: ProkronState | None = None) -> ProkronState:
    state = state or load_state(project)
    root = prokron_dir(project)
    (root / "TASK_GRAPH.md").write_text(render_graph(state), encoding="utf-8")
    (root / "STATE.md").write_text(render_state(project, state), encoding="utf-8")
    return state


def derived_errors(project: Path, state: ProkronState) -> list[str]:
    root = prokron_dir(project)
    expected = {"TASK_GRAPH.md": render_graph(state), "STATE.md": render_state(project, state)}
    return [
        f"{name} is stale; run `prokron status`"
        for name, content in expected.items()
        if not (root / name).exists() or (root / name).read_text(encoding="utf-8") != content
    ]


def _related_decisions(state: ProkronState, task: Task) -> tuple[Decision, ...]:
    direct = set(task.governed_by)
    direct.update(decision.id for decision in state.decisions if task.id in decision.affects)
    changed = True
    while changed:
        changed = False
        for decision in state.decisions:
            targets = (*decision.supersedes, *decision.amends, *decision.corrects, *decision.rejects)
            if decision.id in direct or any(target in direct for target in targets):
                before = len(direct)
                direct.add(decision.id)
                direct.update(targets)
                changed = changed or len(direct) != before
    return tuple(decision for decision in state.decisions if decision.id in direct)


def context_pack(project: Path, task_id: str | None = None) -> str:
    state = load_state(project)
    errors = validate(state)
    if errors:
        raise ProkronError("canonical state is invalid:\n- " + "\n- ".join(errors))
    if task_id is None:
        candidates = [intent.task_id for intent in state.intents if intent.task_id]
        candidates = candidates or [task.id for task in eligible_tasks(state)]
        if len(candidates) != 1:
            raise ProkronError("Specify a task ID when context is not unambiguous")
        task_id = candidates[0]
    matches = [task for task in state.tasks if task.id == task_id]
    if len(matches) != 1:
        raise ProkronError(f"expected exactly one task {task_id}, found {len(matches)}")
    task = matches[0]
    by_id = {item.id: item for item in state.tasks}
    dependencies = [by_id[item] for item in task.dependencies if item in by_id]
    neighbors = [item for item in state.tasks if task.id in item.dependencies]
    intent = next((item for item in state.intents if item.task_id == task.id), None)
    decisions = _related_decisions(state, task)
    lines = [
        f"# Context: {task.id}",
        "",
        f"- Project: {project.name}",
        "",
        "## Task",
        f"- Title: {task.title}",
        f"- Status: {task.status}",
        f"- Validation: {task.validation}",
        f"- Acceptance: {task.acceptance}",
        f"- Evidence: {task.evidence or 'none'}",
        "",
        "## Dependencies",
        *(f"- {item.id}: {item.status} — {item.title}" for item in dependencies),
    ]
    if not dependencies:
        lines.append("- None")
    lines.extend(("", "## Immediate downstream work"))
    lines.extend(f"- {item.id}: {item.status} — {item.title}" for item in neighbors)
    if not neighbors:
        lines.append("- None")
    lines.extend(("", "## Active intent"))
    if intent:
        lines.extend(
            (
                f"- Owner: {intent.owner}",
                f"- Goal: {intent.goal}",
                f"- Current point: {intent.current_point}",
                f"- Constraints: {', '.join(intent.constraints) or 'none'}",
                f"- Changed files: {', '.join(intent.changed_files) or 'none'}",
                f"- Next action: {intent.next_action}",
            )
        )
    else:
        lines.append("- None")
    lines.extend(("", "## Governing decisions"))
    for decision in decisions:
        lines.extend((f"### {decision.id}: {decision.title}", f"- Status: {decision.status}", f"- Decision: {decision.decision}"))
    if not decisions:
        lines.append("- None")
    return "\n".join([*lines, ""])
