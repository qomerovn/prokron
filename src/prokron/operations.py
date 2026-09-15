from __future__ import annotations

import subprocess
from datetime import UTC, date, datetime
from importlib.resources import files
from pathlib import Path

from .core import CANONICAL_FILES, PROKRON, eligible_tasks, load_state, prokron_dir, validate
from .markdown import INTENT_HEADER, TASK_HEADER, update_section_fields
from .models import Intent, ProkronError, Task
from .persistence import write_json
from .rendering import sync_derived
from .repository import checkpoint_facts

BOOTSTRAP_START = "<!-- project-prokron:start -->"
BOOTSTRAP_END = "<!-- project-prokron:end -->"
BOOTSTRAP_BLOCK = f"""{BOOTSTRAP_START}

## Project Prokron

This repository uses `.prokron/` as persistent project coordination state.

Before implementation:

1. Read `.prokron/README.md`.
2. Read `.prokron/BASELINE.md` if an adoption baseline exists.
3. Inspect `.prokron/TASK_GRAPH.md`.
4. Locate the relevant task in `.prokron/TASKS.md`.
5. Read `.prokron/INTENTS.md` if work is active.
6. Read only the governing specification, decisions, and code required for that task.

Do not reconstruct current project truth from chat history.

{BOOTSTRAP_END}
"""


def is_git_repository(project: Path) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=project,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def install_bootstrap(path: Path) -> tuple[bytes | None, bytes] | None:
    try:
        before = path.read_bytes()
    except FileNotFoundError:
        before = None
    original = before or b""
    text = original.decode()
    has_start, has_end = BOOTSTRAP_START in text, BOOTSTRAP_END in text
    if has_start != has_end:
        raise ProkronError(f"{path.name}: incomplete managed Prokron block")
    if has_start:
        return None
    separator = b"" if not original else b"\n" if original.endswith(b"\n") else b"\n\n"
    updated = original + separator + BOOTSTRAP_BLOCK.encode()
    path.write_bytes(updated)
    return before, updated


def initialize(project: Path) -> bool:
    if not is_git_repository(project):
        raise ProkronError("Prokron requires a Git repository. Run `git init` first.")
    root = prokron_dir(project)
    created = not root.exists()
    if created:
        root.mkdir()
        template_root = files("prokron").joinpath("templates")
        for name in CANONICAL_FILES:
            (root / name).write_text(template_root.joinpath(name).read_text(encoding="utf-8"), encoding="utf-8")
    elif not root.is_dir():
        raise ProkronError(f"{PROKRON} exists but is not a directory")
    state = load_state(project)
    errors = validate(state)
    if errors:
        raise ProkronError("canonical state is invalid:\n- " + "\n- ".join(errors))
    candidates = [project / name for name in ("AGENTS.md", "CLAUDE.md") if (project / name).exists()]
    if not candidates:
        candidates = [project / "AGENTS.md"]
    for path in candidates:
        install_bootstrap(path)
    sync_derived(project, state)
    return created


def start_task(project: Path, task_id: str, owner: str) -> Task:
    state = load_state(project)
    errors = validate(state)
    if errors:
        raise ProkronError("canonical state is invalid:\n- " + "\n- ".join(errors))
    matches = [task for task in state.tasks if task.id == task_id]
    if len(matches) != 1:
        raise ProkronError(f"expected exactly one task {task_id}, found {len(matches)}")
    task = matches[0]
    if task.status != "TODO":
        raise ProkronError(f"{task.id} is {task.status}, not TODO")
    ready_ids = {item.id for item in eligible_tasks(state)}
    if task.id not in ready_ids:
        by_id = {item.id: item for item in state.tasks}
        incomplete = [dependency for dependency in task.dependencies if by_id[dependency].status != "DONE"]
        raise ProkronError(f"{task.id} is blocked by {', '.join(incomplete)}")
    owner = _command_text("Owner", owner)
    intent_path = prokron_dir(project) / "INTENTS.md"
    intent_text = intent_path.read_text(encoding="utf-8")
    intent = (
        f"## {task.id}\n"
        f"- Owner: {owner}\n"
        f"- Updated: {date.today().isoformat()}\n"
        f"- Goal: {task.acceptance}\n"
        "- Current point: Task claimed; implementation not started.\n"
        "- Constraints: none\n"
        "- Changed files: none\n"
        f"- Next action: Implement {task.id}.\n"
    )
    intent_text = "\n".join(line for line in intent_text.splitlines() if line != "No intent in flight.")
    intent_path.write_text(intent_text.rstrip() + "\n\n" + intent, encoding="utf-8")
    update_section_fields(
        prokron_dir(project) / "TASKS.md",
        TASK_HEADER,
        task.id,
        {"status": "WIP", "owner": owner, "claimed": date.today().isoformat()},
    )
    sync_derived(project)
    return task


def checkpoint(
    project: Path,
    task_id: str | None,
    did: str,
    validation_text: str,
    learned: str,
    left_mid_air: str,
    next_action: str,
    changed_files: tuple[str, ...],
) -> Intent:
    state = load_state(project)
    errors = validate(state)
    if errors:
        raise ProkronError("canonical state is invalid:\n- " + "\n- ".join(errors))
    did = _command_text("Did", did)
    validation_text = _command_text("Validation", validation_text)
    learned = _command_text("Learned", learned, allow_empty=True)
    left_mid_air = _command_text("Left mid-air", left_mid_air)
    next_action = _command_text("Next", next_action)
    changed_files = tuple(_command_text("Changed file", item) for item in changed_files)
    intents = [intent for intent in state.intents if task_id is None or intent.subject == task_id]
    if len(intents) != 1:
        raise ProkronError("Checkpoint requires one matching active intent; specify --task when needed")
    intent = intents[0]
    snapshot = checkpoint_facts(project) if (prokron_dir(project) / "ADOPTION.json").exists() else None
    update_section_fields(
        prokron_dir(project) / "INTENTS.md",
        INTENT_HEADER,
        intent.subject,
        {
            "updated": date.today().isoformat(),
            "current_point": left_mid_air,
            "changed_files": ", ".join(changed_files or intent.changed_files) or "none",
            "next_action": next_action,
        },
    )
    journal_path = prokron_dir(project) / "JOURNAL.md"
    journal = "\n".join(line for line in journal_path.read_text(encoding="utf-8").splitlines() if line != "No journal entries.").rstrip()
    label = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    entry = (
        f"## {label} — {intent.subject}\n"
        f"- Task: {intent.subject}\n"
        f"- Owner: {intent.owner}\n"
        f"- Did: {did}\n"
        f"- Validation: {validation_text}\n"
        f"- Learned: {learned or 'Nothing new.'}\n"
        f"- Left mid-air: {left_mid_air}\n"
        f"- Next: {next_action}\n"
    )
    journal_path.write_text(journal + "\n\n" + entry, encoding="utf-8")
    updated = load_state(project)
    errors = validate(updated)
    if errors:
        raise ProkronError("checkpoint produced invalid state:\n- " + "\n- ".join(errors))
    sync_derived(project, updated)
    if snapshot is not None:
        write_json(prokron_dir(project) / "CHECKPOINT.json", snapshot)
    return next(item for item in updated.intents if item.subject == intent.subject)


def _command_text(name: str, value: str, allow_empty: bool = False) -> str:
    value = value.strip()
    if not value and not allow_empty:
        raise ProkronError(f"{name} cannot be empty")
    if "\n" in value or "\r" in value:
        raise ProkronError(f"{name} must fit on one Markdown line")
    if name == "Changed file" and "," in value:
        raise ProkronError("Changed file cannot contain a comma")
    return value
