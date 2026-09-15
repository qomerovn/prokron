"""Agent-authored adoption. This module never imports the optional heuristic engine."""
from __future__ import annotations

import hashlib
import json
import tempfile
from dataclasses import asdict
from datetime import UTC, datetime
from importlib.resources import files
from pathlib import Path
from typing import Any

from .candidate import CONFIRMATION, SNAPSHOT, TEXT, validate_candidate, validate_schema
from .core import load_state, validate
from .models import ProkronError, ProkronState
from .operations import install_bootstrap
from .persistence import read_json, write_json
from .rendering import baseline_markdown, decision_markdown, intent_markdown, render_graph, render_state, task_markdown
from .repository import require_fresh

STAGING = ".prokron-candidate"
INSTRUCTIONS = """The coding agent inspects the repository with native tools, interprets its
current state, and asks the human only material unresolved questions. Run
`prokron adopt schema`; copy prepare.checkpoint into the candidate. Supply
current state, scoped authority, architecture, constraints, work, tasks,
dependencies, blockers, validation, decisions, exact next action and unknowns.
Use OBSERVED / INFERRED / CONFIRMED claims with provenance; preserve uncertainty.
Write the candidate outside the repository or inside .prokron-candidate/.
Run `prokron adopt ingest <file>` and show the staged candidate to the human.
After explicit human approval, run `prokron adopt confirm --by <human> --digest
<reviewed digest>`, then `prokron adopt apply`. Corrections require re-ingest and
renewed confirmation. Core never generates semantic questions or conclusions.
"""


def candidate_digest(candidate: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(candidate, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _stage(project: Path) -> Path:
    root = project / STAGING
    if root.is_symlink():
        raise ProkronError(f"{STAGING}: symlink staging directories are not supported")
    return root / "candidate.json"


def _new_project(project: Path) -> None:
    target = project / ".prokron"
    if target.exists() or target.is_symlink():
        raise ProkronError(".prokron already exists; adoption cannot replace canonical state")


def _write_operational(root: Path, state: ProkronState) -> None:
    (root / "TASKS.md").write_text("# Tasks\n\n" + "\n".join(map(task_markdown, state.tasks)), encoding="utf-8")
    (root / "DECISIONS.md").write_text("# Decisions\n\n" + "\n".join(map(decision_markdown, state.decisions)), encoding="utf-8")
    (root / "INTENTS.md").write_text("# Intents\n\n" + ("\n".join(map(intent_markdown, state.intents)) or "No intent in flight.\n"), encoding="utf-8")
    (root / "JOURNAL.md").write_text("# Journal\n\nNo journal entries.\n", encoding="utf-8")


def _round_trip(state: ProkronState) -> None:
    # Exercise the existing parsers before accepting JSON into Markdown authority.
    with tempfile.TemporaryDirectory(prefix="prokron-validate-") as directory:
        project = Path(directory)
        root = project / ".prokron"
        root.mkdir()
        _write_operational(root, state)
        if load_state(project) != state:
            raise ProkronError("candidate cannot round-trip through canonical Markdown; check commas, whitespace and fences")


def ingest(project: Path, path: Path) -> str:
    _new_project(project)
    target = _stage(project)
    candidate = read_json(path)
    _round_trip(validate_candidate(candidate))
    require_fresh(project, candidate["checkpoint"])
    target.parent.mkdir(exist_ok=True)
    write_json(target, {"candidate": candidate, "confirmation": None})
    return candidate_digest(candidate)


def _read_envelope(path: Path, confirmed: bool = False) -> tuple[dict[str, Any], ProkronState]:
    envelope = read_json(path)
    if not isinstance(envelope, dict) or set(envelope) != {"candidate", "confirmation"}:
        raise ProkronError("invalid adoption envelope")
    state = validate_candidate(envelope["candidate"])
    confirmation = envelope["confirmation"]
    if confirmed or confirmation is not None:
        if confirmation is None:
            raise ProkronError("candidate requires explicit human confirmation before apply")
        validate_schema(confirmation, CONFIRMATION, "confirmation")
        if confirmation["digest"] != candidate_digest(envelope["candidate"]):
            raise ProkronError("candidate changed after confirmation; re-ingest and confirm the corrected candidate")
    return envelope, state


def confirm(project: Path, by: str, digest: str) -> None:
    _new_project(project)
    envelope, _ = _read_envelope(_stage(project))
    require_fresh(project, envelope["candidate"]["checkpoint"])
    by = by.strip()
    validate_schema(by, TEXT, "confirmation.by")
    if candidate_digest(envelope["candidate"]) != digest:
        raise ProkronError("reviewed digest does not match the staged candidate")
    envelope["confirmation"] = {"digest": digest, "by": by, "at": datetime.now(UTC).isoformat()}
    write_json(_stage(project), envelope)


def apply(project: Path) -> None:
    _new_project(project)
    envelope, state = _read_envelope(_stage(project), confirmed=True)
    candidate = envelope["candidate"]
    require_fresh(project, candidate["checkpoint"])
    _round_trip(state)
    targets = [project / name for name in ("AGENTS.md", "CLAUDE.md") if (project / name).exists()] or [project / "AGENTS.md"]
    installed: dict[Path, tuple[bytes | None, bytes]] = {}
    # Build and validate the whole directory before its single publication rename.
    with tempfile.TemporaryDirectory(prefix="apply-", dir=_stage(project).parent) as directory:
        root = Path(directory) / ".prokron"
        root.mkdir()
        _write_operational(root, state)
        (root / "README.md").write_text(files("prokron").joinpath("templates/README.md").read_text(encoding="utf-8"), encoding="utf-8")
        (root / "BASELINE.md").write_text(baseline_markdown(candidate), encoding="utf-8")
        write_json(root / "ADOPTION.json", envelope)
        write_json(root / "CHECKPOINT.json", candidate["checkpoint"])
        (root / "TASK_GRAPH.md").write_text(render_graph(state), encoding="utf-8")
        (root / "STATE.md").write_text(render_state(project, state), encoding="utf-8")
        confirmation = envelope["confirmation"]
        (root / "JOURNAL.md").write_text(
            f"# Journal\n\n## {confirmation['at']} — adoption boundary\n"
            f"- Task: adoption\n- Owner: {confirmation['by']}\n"
            f"- Did: Applied human-reviewed candidate {confirmation['digest']}.\n"
            "- Validation: Schema, graph and Markdown round-trip checks passed.\n"
            "- Learned: Uncertainty and provenance preserved in ADOPTION.json.\n"
            "- Left mid-air: Adoption complete.\n"
            f"- Next: {candidate['next_action']['action']}\n", encoding="utf-8",
        )
        errors = validate(load_state(Path(directory)))
        if errors:
            raise ProkronError("invalid staged state: " + "; ".join(errors))
        try:
            for path in targets:
                if content := install_bootstrap(path):
                    installed[path] = content
            require_fresh(project, candidate["checkpoint"])
            _new_project(project)
            root.rename(project / ".prokron")
        except (OSError, ProkronError):
            if not (project / ".prokron").exists():
                for path, (before, after) in installed.items():
                    if path.is_symlink():
                        continue
                    try:
                        current = path.read_bytes() if path.exists() else None
                    except OSError:
                        continue
                    if current == after:
                        if before is None:
                            path.unlink(missing_ok=True)
                        else:
                            path.write_bytes(before)
            raise


def adopted_state(project: Path) -> dict[str, Any] | None:
    root = project / ".prokron"
    if root.is_symlink():
        raise ProkronError("symlink canonical directories are not supported")
    if not (root / "ADOPTION.json").exists():
        if (root / "CHECKPOINT.json").exists():
            raise ProkronError("ADOPTION.json is missing for checkpointed agent adoption")
        return None
    envelope, _ = _read_envelope(root / "ADOPTION.json", confirmed=True)
    return envelope


def _check_checkpoint(project: Path) -> None:
    recorded = read_json(project / ".prokron/CHECKPOINT.json")
    validate_schema(recorded, SNAPSHOT, "checkpoint")
    require_fresh(project, recorded)


def freshness(project: Path) -> dict[str, Any] | None:
    envelope = adopted_state(project)
    if envelope is not None:
        _check_checkpoint(project)
    return envelope


def recorded_next(candidate: dict[str, Any], state: ProkronState) -> dict[str, Any]:
    action = dict(candidate["next_action"])
    tasks = {task.id: task for task in state.tasks}
    target = action.get("task_id")
    # An explicit live checkpoint takes precedence over the initial adoption action.
    intents = [intent for intent in state.intents if intent.subject == target] if target else list(state.intents)
    if not intents and len(state.intents) == 1:
        intents = list(state.intents)
    if len(intents) > 1:
        raise ProkronError("NEXT_ACTION_AMBIGUOUS: multiple active intents; record a task-specific next action")
    if len(intents) == 1:
        if intents[0].task_id != target:
            action["depends_on"] = []
            action["reason"] = "Recorded in the current active intent."
        target = intents[0].task_id
        action["action"] = intents[0].next_action
        if target:
            action["task_id"] = target
        else:
            action.pop("task_id", None)
    dependencies = set(action["depends_on"])
    if target:
        if target not in tasks or tasks[target].status == "DONE":
            raise ProkronError("NEXT_ACTION_UNAVAILABLE: recorded task is missing or DONE; run /prokron-sync")
        dependencies.update(tasks[target].dependencies)
        if tasks[target].status == "BLOCKED":
            raise ProkronError(f"NEXT_ACTION_BLOCKED: {target} is BLOCKED")
    waiting = sorted(item for item in dependencies if item not in tasks or tasks[item].status != "DONE")
    if waiting:
        raise ProkronError("NEXT_ACTION_BLOCKED: waiting on " + ", ".join(waiting))
    return action


def resume(project: Path) -> dict[str, Any]:
    state = load_state(project)
    errors = validate(state)
    if errors:
        raise ProkronError("canonical state is invalid: " + "; ".join(errors))
    envelope = adopted_state(project)
    result: dict[str, Any] = {"status": "CURRENT", "operational_state": asdict(state)}
    if envelope is not None:
        result["adoption_baseline"] = envelope
        try:
            _check_checkpoint(project)
            result["next_action"] = recorded_next(envelope["candidate"], state)
        except ProkronError as error:
            if not str(error).startswith(("STATE_STALE", "NEXT_ACTION_")):
                raise
            result["status"] = str(error).split(":", 1)[0].splitlines()[0]
            result["condition"] = str(error)
    else:
        result["next_action"] = [intent.next_action for intent in state.intents]
    return result
