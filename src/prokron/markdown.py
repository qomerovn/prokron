from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .models import Decision, Intent, JournalEntry, ProkronError, Task

TASK_HEADER = re.compile(r"^##\s+(T-[A-Za-z0-9][A-Za-z0-9-]*):\s*(.+?)\s*$")
DECISION_HEADER = re.compile(r"^##\s+(ADR-[A-Za-z0-9][A-Za-z0-9-]*):\s*(.+?)\s*$")
INTENT_HEADER = re.compile(r"^##\s+(T-[A-Za-z0-9][A-Za-z0-9-]*|maintenance/[a-z0-9][a-z0-9-]*)\s*$")
JOURNAL_HEADER = re.compile(r"^##\s+(.+?)\s*$")
FIELD = re.compile(r"^-\s+([A-Za-z][A-Za-z -]*):\s*(.*?)\s*$")


@dataclass(frozen=True)
class Section:
    identifier: str
    title: str
    fields: dict[str, str]
    line: int


def _sections(path: Path, header: re.Pattern[str], kind: str) -> list[Section]:
    if not path.exists():
        raise ProkronError(f"{path.name} is missing")
    sections: list[Section] = []
    current_id: str | None = None
    current_title = ""
    current_line = 0
    fields: dict[str, str] = {}
    in_fence = False

    def finish() -> None:
        nonlocal current_id, current_title, current_line, fields
        if current_id is not None:
            sections.append(Section(current_id, current_title, fields, current_line))
        current_id, current_title, current_line, fields = None, "", 0, {}

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if match := header.match(line):
            finish()
            current_id = match.group(1)
            current_title = match.group(2) if match.lastindex and match.lastindex > 1 else ""
            current_line = line_number
            continue
        if line.startswith("## ") and (line.startswith("## T-") or line.startswith("## ADR-") or kind == "intent"):
            raise ProkronError(f"{path.name}:{line_number}: malformed {kind} heading")
        if current_id is not None and (match := FIELD.match(line)):
            key, value = match.groups()
            normalized = key.lower().replace("-", "_").replace(" ", "_")
            if normalized in fields:
                raise ProkronError(f"{path.name}:{line_number}: duplicate field {key} in {current_id}")
            fields[normalized] = value
    if in_fence:
        raise ProkronError(f"{path.name}: unclosed fenced block")
    finish()
    return sections


def _required(path: Path, section: Section, names: tuple[str, ...]) -> None:
    missing = [name.replace("_", " ").title() for name in names if name not in section.fields]
    if missing:
        raise ProkronError(f"{path.name}:{section.line}: {section.identifier} missing {', '.join(missing)}")


def _refs(value: str) -> tuple[str, ...]:
    if not value or value.lower() in {"none", "-"}:
        return ()
    return tuple(item.strip() for item in value.split(",") if item.strip())


def _iso_date(path: Path, section: Section, key: str) -> str:
    value = section.fields[key]
    if not value:
        return value
    try:
        date.fromisoformat(value)
    except ValueError as error:
        raise ProkronError(f"{path.name}:{section.line}: {section.identifier} has invalid {key.replace('_', ' ')}") from error
    return value


def parse_tasks(path: Path) -> tuple[Task, ...]:
    required = ("status", "validation", "dependencies", "owner", "claimed", "acceptance", "evidence", "governed_by")
    tasks: list[Task] = []
    for section in _sections(path, TASK_HEADER, "task"):
        _required(path, section, required)
        tasks.append(
            Task(
                id=section.identifier,
                title=section.title,
                dependencies=_refs(section.fields["dependencies"]),
                status=section.fields["status"].upper(),
                validation=section.fields["validation"].upper(),
                owner=section.fields["owner"],
                claimed=_iso_date(path, section, "claimed"),
                acceptance=section.fields["acceptance"],
                evidence=section.fields["evidence"],
                governed_by=_refs(section.fields["governed_by"]),
            )
        )
    return tuple(tasks)


def parse_decisions(path: Path) -> tuple[Decision, ...]:
    required = (
        "date",
        "status",
        "authority",
        "supersedes",
        "amends",
        "corrects",
        "rejects",
        "affects",
        "context",
        "decision",
    )
    decisions: list[Decision] = []
    for section in _sections(path, DECISION_HEADER, "decision"):
        _required(path, section, required)
        decisions.append(
            Decision(
                id=section.identifier,
                title=section.title,
                date=_iso_date(path, section, "date"),
                status=section.fields["status"].upper(),
                authority=section.fields["authority"],
                supersedes=_refs(section.fields["supersedes"]),
                amends=_refs(section.fields["amends"]),
                corrects=_refs(section.fields["corrects"]),
                rejects=_refs(section.fields["rejects"]),
                affects=_refs(section.fields["affects"]),
                context=section.fields["context"],
                decision=section.fields["decision"],
            )
        )
    return tuple(decisions)


def parse_intents(path: Path) -> tuple[Intent, ...]:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    sections = _sections(path, INTENT_HEADER, "intent")
    empty_marker = "No intent in flight." in text
    if empty_marker and sections:
        raise ProkronError(f"{path.name}: empty-intent marker conflicts with active intent")
    if not sections:
        if empty_marker:
            return ()
        raise ProkronError(f"{path.name}: expected an active intent or `No intent in flight.`")
    required = ("owner", "updated", "goal", "current_point", "constraints", "changed_files", "next_action")
    intents: list[Intent] = []
    for section in sections:
        _required(path, section, required)
        intents.append(
            Intent(
                subject=section.identifier,
                owner=section.fields["owner"],
                updated=_iso_date(path, section, "updated"),
                goal=section.fields["goal"],
                current_point=section.fields["current_point"],
                constraints=_refs(section.fields["constraints"]),
                changed_files=_refs(section.fields["changed_files"]),
                next_action=section.fields["next_action"],
            )
        )
    return tuple(intents)


def parse_journal(path: Path) -> tuple[JournalEntry, ...]:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    sections = _sections(path, JOURNAL_HEADER, "journal")
    sections = [section for section in sections if section.identifier != "Journal"]
    if not sections:
        if "No journal entries." in text:
            return ()
        raise ProkronError(f"{path.name}: expected a journal entry or `No journal entries.`")
    required = ("task", "owner", "did", "validation", "learned", "left_mid_air", "next")
    entries: list[JournalEntry] = []
    for section in sections:
        _required(path, section, required)
        entries.append(
            JournalEntry(
                label=section.identifier,
                task=section.fields["task"],
                owner=section.fields["owner"],
                did=section.fields["did"],
                validation=section.fields["validation"],
                learned=section.fields["learned"],
                left_mid_air=section.fields["left_mid_air"],
                next_action=section.fields["next"],
            )
        )
    return tuple(entries)


def update_section_fields(path: Path, header: re.Pattern[str], identifier: str, updates: dict[str, str]) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    starts = [index for index, line in enumerate(lines) if (match := header.match(line)) and match.group(1) == identifier]
    if len(starts) != 1:
        raise ProkronError(f"expected exactly one {identifier} section, found {len(starts)}")
    start = starts[0]
    end = next((index for index in range(start + 1, len(lines)) if header.match(lines[index])), len(lines))
    section = lines[start:end]
    remaining = {key.lower().replace("_", " "): value for key, value in updates.items()}
    for index, line in enumerate(section):
        if field := FIELD.match(line):
            key = field.group(1).lower().replace("-", " ")
            if key in remaining:
                section[index] = f"- {field.group(1)}: {remaining.pop(key)}"
    if remaining:
        section.extend(f"- {key.title()}: {value}" for key, value in remaining.items())
    path.write_text("\n".join([*lines[:start], *section, *lines[end:]]) + "\n", encoding="utf-8")
