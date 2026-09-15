"""Small agent-facing schema and deterministic operational-state validation."""
from __future__ import annotations

import re
from dataclasses import fields
from datetime import datetime
from typing import Any, TypeVar

from .core import DECISION_STATUSES, TASK_STATUSES, VALIDATION_LEVELS, validate
from .models import Decision, Intent, ProkronError, ProkronState, Task


def obj(properties: dict[str, Any], required: list[str] | None = None) -> dict[str, Any]:
    return {"type": "object", "properties": properties, "required": list(properties) if required is None else required,
            "additionalProperties": False}


def array(items: dict[str, Any]) -> dict[str, Any]:
    return {"type": "array", "items": items}


SINGLE_LINE = r"^(?![\s\S]*[\n\r\v\f\x1c-\x1e\x85\u2028\u2029])[\s\S]*$"
TEXT: dict[str, Any] = {"type": "string", "minLength": 1, "pattern": SINGLE_LINE}
OPTIONAL_TEXT: dict[str, Any] = {"type": "string", "pattern": SINGLE_LINE}
TASK_ID = {**TEXT, "pattern": r"^T-[A-Za-z0-9][A-Za-z0-9-]*$"}
DECISION_ID = {**TEXT, "pattern": r"^ADR-[A-Za-z0-9][A-Za-z0-9-]*$"}
CLAIM = obj({
    "statement": TEXT, "status": {"enum": ["OBSERVED", "INFERRED", "CONFIRMED"]}, "sources": array(TEXT),
    "created_at": TEXT, "confirmed_by": TEXT, "confirmed_at": TEXT,
}, ["statement", "status", "sources"])
DIGEST = {**TEXT, "pattern": "^[a-f0-9]{64}$"}
SNAPSHOT = obj({"head": OPTIONAL_TEXT, "branch": TEXT, "worktree": DIGEST})
CONFIRMATION = obj({"digest": DIGEST, "by": TEXT, "at": TEXT})
TASK = obj({
    "id": TASK_ID, "title": TEXT, "status": {"enum": sorted(TASK_STATUSES)},
    "validation": {"enum": sorted(VALIDATION_LEVELS)}, "dependencies": array(TASK_ID),
    "owner": OPTIONAL_TEXT, "claimed": OPTIONAL_TEXT, "acceptance": TEXT, "evidence": OPTIONAL_TEXT,
    "governed_by": array(DECISION_ID), "provenance": CLAIM,
}, ["id", "title", "status", "acceptance"])
DECISION = obj({
    "id": DECISION_ID, "title": TEXT, "date": TEXT, "status": {"enum": sorted(DECISION_STATUSES)},
    "authority": TEXT, "supersedes": array(DECISION_ID), "amends": array(DECISION_ID), "corrects": array(DECISION_ID),
    "rejects": array(DECISION_ID), "affects": array(TASK_ID), "context": TEXT, "decision": TEXT, "provenance": CLAIM,
}, ["id", "title", "date", "status", "authority", "context", "decision"])
INTENT = obj({
    "subject": {**TEXT, "pattern": r"^(T-[A-Za-z0-9][A-Za-z0-9-]*|maintenance/[a-z0-9][a-z0-9-]*)$"},
    "owner": TEXT, "updated": TEXT, "goal": TEXT, "current_point": TEXT, "constraints": array(TEXT),
    "changed_files": array(TEXT), "next_action": TEXT,
}, ["subject", "owner", "updated", "goal", "current_point", "next_action"])
SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Prokron agent adoption candidate v1",
    **obj({
        "version": {"enum": [1]}, "checkpoint": SNAPSHOT,
        "project": obj({"purpose": CLAIM, "current_state": CLAIM}),
        "authority": array(obj({"scope": TEXT, "source": TEXT, "reason": TEXT})),
        "architecture": obj({"summary": CLAIM, "components": array(CLAIM)}),
        "constraints": array(CLAIM), "active_work": CLAIM,
        "tasks": array(TASK), "intents": array(INTENT), "blockers": array(CLAIM),
        "validation": obj({"known": array(CLAIM), "unknown": array(TEXT)}),
        "decisions": array(DECISION),
        "next_action": obj({"action": TEXT, "reason": TEXT, "depends_on": array(TASK_ID), "task_id": TASK_ID},
                           ["action", "reason", "depends_on"]),
        "unknowns": array(TEXT),
    }),
}


def validate_schema(value: Any, schema: dict[str, Any], path: str) -> None:
    """Validate only the JSON Schema vocabulary used by the published schema."""
    kind = schema.get("type")
    expected = {"object": dict, "array": list, "string": str}
    if kind and not isinstance(value, expected[kind]):
        raise ProkronError(f"{path}: expected {kind}")
    if "enum" in schema and not any(type(value) is type(item) and value == item for item in schema["enum"]):
        raise ProkronError(f"{path}: expected one of {schema['enum']}")
    if kind == "object":
        missing = set(schema["required"]) - value.keys()
        extra = value.keys() - schema["properties"].keys()
        if missing or extra:
            raise ProkronError(f"{path}: missing fields {sorted(missing)}; unsupported fields {sorted(extra)}")
        for key, item in value.items():
            validate_schema(item, schema["properties"][key], f"{path}.{key}")
        if "statement" in value and "status" in value:
            if value["status"] == "OBSERVED" and not value["sources"]:
                raise ProkronError(f"{path}: OBSERVED requires sources")
            if value["status"] == "CONFIRMED" and not all(value.get(key) for key in ("confirmed_by", "confirmed_at")):
                raise ProkronError(f"{path}: CONFIRMED requires confirmed_by and confirmed_at")
            for key in ("created_at", "confirmed_at"):
                if key in value:
                    try:
                        datetime.fromisoformat(value[key])
                    except ValueError as error:
                        raise ProkronError(f"{path}.{key}: expected ISO timestamp") from error
    elif kind == "array":
        for index, item in enumerate(value):
            validate_schema(item, schema["items"], f"{path}[{index}]")
    elif kind == "string":
        if len(value.strip()) < schema.get("minLength", 0) or not re.fullmatch(schema["pattern"], value):
            raise ProkronError(f"{path}: invalid or empty single-line text")


Record = TypeVar("Record", Task, Decision, Intent)


def _records(model: type[Record], entries: list[dict[str, Any]], tuple_fields: set[str]) -> tuple[Record, ...]:
    records: list[Record] = []
    for entry in entries:
        values: dict[str, Any] = {
            field.name: tuple(entry.get(field.name, [])) if field.name in tuple_fields
            else entry.get(field.name, "UNTESTED" if field.name == "validation" else "")
            for field in fields(model)
        }
        records.append(model(**values))
    return tuple(records)


def validate_candidate(candidate: Any) -> ProkronState:
    validate_schema(candidate, SCHEMA, "candidate")
    state = ProkronState(
        tasks=_records(Task, candidate["tasks"], {"dependencies", "governed_by"}),
        decisions=_records(Decision, candidate["decisions"], {"supersedes", "amends", "corrects", "rejects", "affects"}),
        intents=_records(Intent, candidate["intents"], {"constraints", "changed_files"}),
        journal=(),
    )
    errors = validate(state)
    by_id = {task.id: task for task in state.tasks}
    action = candidate["next_action"]
    for task_id in action["depends_on"] + ([action["task_id"]] if "task_id" in action else []):
        if task_id not in by_id:
            errors.append(f"next_action: missing task {task_id}")
    target = by_id.get(action.get("task_id"))
    if target and target.status == "DONE":
        errors.append("next_action: target task is already DONE")
    if errors:
        raise ProkronError("candidate state is invalid:\n- " + "\n- ".join(errors))
    return state
