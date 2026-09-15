from __future__ import annotations

import argparse
import json
import sys
from importlib.metadata import version
from pathlib import Path

from .adoption import INSTRUCTIONS, adopted_state, apply, confirm, freshness, ingest, recorded_next, resume
from .candidate import SCHEMA
from .core import eligible_tasks, load_state, validate
from .models import ProkronError
from .operations import checkpoint, initialize, start_task
from .rendering import context_pack, derived_errors, render_graph, render_state, sync_derived
from .repository import prepare


def command_init(args: argparse.Namespace) -> int:
    created = initialize(Path.cwd())
    print("Initialized .prokron/" if created else "Prokron already initialized; no canonical files changed.")
    return 0


def command_adopt(args: argparse.Namespace) -> int:
    project = Path.cwd()
    action = args.adopt_action
    if action in (None, "prepare"):
        print(json.dumps({**prepare(project), "instructions": INSTRUCTIONS}, indent=2))
    elif action == "schema":
        print(json.dumps(SCHEMA, indent=2))
    elif action == "ingest":
        digest = ingest(project, Path(args.candidate))
        print(f"Staged .prokron-candidate/candidate.json\nReview digest: {digest}\nHuman confirmation required before apply.")
    elif action == "confirm":
        confirm(project, args.by, args.digest)
        print("Recorded confirmation for the reviewed digest.")
    elif action == "apply":
        apply(project)
        print("Applied the confirmed candidate to .prokron/.")
    return 0


def command_resume(args: argparse.Namespace) -> int:
    result = resume(Path.cwd())
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "CURRENT" else 2


def command_status(args: argparse.Namespace) -> int:
    project = Path.cwd()
    state = load_state(project)
    errors = validate(state)
    if errors:
        raise ProkronError("canonical state is invalid:\n- " + "\n- ".join(errors))
    adopted_state(project)
    sync_derived(project, state)
    print(render_state(project, state), end="")
    return 0


def command_next(args: argparse.Namespace) -> int:
    project = Path.cwd()
    state = load_state(project)
    errors = validate(state)
    if errors:
        raise ProkronError("canonical state is invalid:\n- " + "\n- ".join(errors))
    envelope = freshness(project)
    action = recorded_next(envelope["candidate"], state) if envelope is not None else None
    if action is not None:
        print(json.dumps(action, indent=2))
        return 0
    ready = eligible_tasks(state)
    print("READY")
    if ready:
        for task in ready:
            print(f"{task.id}\t{task.title}")
        print(f"\nRECOMMENDED\n{ready[0].id}\t{ready[0].title}")
    else:
        print("None")
    return 0


def command_graph(args: argparse.Namespace) -> int:
    project = Path.cwd()
    state = load_state(project)
    errors = validate(state)
    if errors:
        raise ProkronError("canonical state is invalid:\n- " + "\n- ".join(errors))
    sync_derived(project, state)
    print(render_graph(state), end="")
    return 0


def command_doctor(args: argparse.Namespace) -> int:
    project = Path.cwd()
    state = load_state(project)
    errors = [*validate(state), *derived_errors(project, state)]
    try:
        freshness(project)
    except ProkronError as health_error:
        errors.append(str(health_error))
    if errors:
        print("Project Prokron: unhealthy")
        for error in errors:
            print(f"x {error}")
        return 1
    print("Project Prokron: healthy")
    print(f"✓ {len(state.tasks)} task(s), {len(state.decisions)} decision(s), {len(state.intents)} active intent(s)")
    return 0


def command_start(args: argparse.Namespace) -> int:
    task = start_task(Path.cwd(), args.task_id, args.owner)
    print(f"Started {task.id}: {task.title}")
    print(context_pack(Path.cwd(), task.id), end="")
    return 0


def command_context(args: argparse.Namespace) -> int:
    print(context_pack(Path.cwd(), args.task_id), end="")
    return 0


def command_checkpoint(args: argparse.Namespace) -> int:
    adopted_state(Path.cwd())
    intent = checkpoint(
        Path.cwd(),
        args.task,
        args.did,
        args.validation,
        args.learned,
        args.left_mid_air,
        args.next,
        tuple(args.changed_file),
    )
    print(f"Checkpointed {intent.subject}. Next: {intent.next_action}")
    return 0


def parser() -> argparse.ArgumentParser:
    command_parser = argparse.ArgumentParser(prog="prokron", description="Repository-native project continuity.")
    command_parser.add_argument("--version", action="version", version=version("project-prokron"))
    subcommands = command_parser.add_subparsers(dest="command", required=True)
    for name, handler in {
        "init": command_init,
        "status": command_status,
        "next": command_next,
        "graph": command_graph,
        "resume": command_resume,
    }.items():
        subcommands.add_parser(name).set_defaults(handler=handler)
    adopt = subcommands.add_parser("adopt", help="Agent-authored current-state adoption")
    adopt.set_defaults(handler=command_adopt, adopt_action=None)
    adoption_commands = adopt.add_subparsers(dest="adopt_action")
    for name in ("prepare", "schema", "apply"):
        adoption_commands.add_parser(name)
    ingest_parser = adoption_commands.add_parser("ingest")
    ingest_parser.add_argument("candidate")
    confirm_parser = adoption_commands.add_parser("confirm")
    confirm_parser.add_argument("--by", required=True, help="Identity of the human who explicitly approved this candidate")
    confirm_parser.add_argument("--digest", required=True, help="Digest of the candidate the human reviewed")
    doctor = subcommands.add_parser("doctor")
    doctor.add_argument("--ci", action="store_true", help="Reserved for CI output policy; exit semantics are already CI-safe.")
    doctor.set_defaults(handler=command_doctor)
    context = subcommands.add_parser("context")
    context.add_argument("task_id", nargs="?")
    context.set_defaults(handler=command_context)
    start = subcommands.add_parser("start")
    start.add_argument("task_id")
    start.add_argument("--owner", required=True)
    start.set_defaults(handler=command_start)
    checkpoint_parser = subcommands.add_parser("checkpoint")
    checkpoint_parser.add_argument("--task")
    checkpoint_parser.add_argument("--did", required=True)
    checkpoint_parser.add_argument("--validation", required=True)
    checkpoint_parser.add_argument("--learned", default="")
    checkpoint_parser.add_argument("--left-mid-air", required=True)
    checkpoint_parser.add_argument("--next", required=True)
    checkpoint_parser.add_argument("--changed-file", action="append", default=[])
    checkpoint_parser.set_defaults(handler=command_checkpoint)
    return command_parser


def main(argv: list[str] | None = None) -> None:
    args = parser().parse_args(argv)
    try:
        raise SystemExit(args.handler(args))
    except (ProkronError, OSError, UnicodeError) as error:
        print(f"prokron: {error}", file=sys.stderr)
        raise SystemExit(2) from error
