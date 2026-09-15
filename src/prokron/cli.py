from __future__ import annotations

import argparse
import sys
from importlib.metadata import version
from pathlib import Path

from .adoption import apply_adoption, discover, render_discovery, stage_adoption
from .core import eligible_tasks, load_state, validate
from .models import ProkronError
from .operations import checkpoint, initialize, start_task
from .rendering import context_pack, derived_errors, render_graph, render_state, sync_derived


def command_init(args: argparse.Namespace) -> int:
    created = initialize(Path.cwd())
    print("Initialized .prokron/" if created else "Prokron already initialized; no canonical files changed.")
    return 0


def command_adopt(args: argparse.Namespace) -> int:
    project = Path.cwd()
    if args.apply and (args.interactive or args.from_path):
        raise ProkronError("--apply cannot be combined with --interactive or --from")
    if args.dry_run and args.interactive:
        raise ProkronError("--dry-run cannot be combined with --interactive")
    if args.dry_run:
        print(render_discovery(discover(project)), end="")
        return 0
    if args.apply:
        apply_adoption(project)
        print("Applied the reviewed adoption baseline to .prokron/.")
        return 0
    result = stage_adoption(project, args.from_path, args.interactive)
    print(
        f"Staged adoption candidate in .prokron-adoption/ "
        f"({len(result.unknowns)} blocking unknown(s), {len(result.conflicts)} conflict(s), "
        f"{len(result.incompatibilities)} migration incompatibility(s))."
    )
    print("Review the candidate, resolve every BLOCKING item, then run `prokron adopt --apply`.")
    return 0


def command_status(args: argparse.Namespace) -> int:
    project = Path.cwd()
    state = load_state(project)
    errors = validate(state)
    if errors:
        raise ProkronError("canonical state is invalid:\n- " + "\n- ".join(errors))
    sync_derived(project, state)
    print(render_state(project, state), end="")
    return 0


def command_next(args: argparse.Namespace) -> int:
    state = load_state(Path.cwd())
    errors = validate(state)
    if errors:
        raise ProkronError("canonical state is invalid:\n- " + "\n- ".join(errors))
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
    }.items():
        subcommands.add_parser(name).set_defaults(handler=handler)
    adopt = subcommands.add_parser("adopt")
    mode = adopt.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Discover candidate sources without modifying project files.")
    mode.add_argument("--apply", action="store_true", help="Promote a reviewed, unblocked candidate into .prokron/.")
    adopt.add_argument("--from", dest="from_path", help="Prefer structured legacy state from this repository directory.")
    adopt.add_argument("--interactive", action="store_true", help="Ask only questions needed to close required current-state gaps.")
    adopt.set_defaults(handler=command_adopt)
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
    except ProkronError as error:
        print(f"prokron: {error}", file=sys.stderr)
        raise SystemExit(2) from error
