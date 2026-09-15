from __future__ import annotations

from dataclasses import dataclass


class ProkronError(ValueError):
    """A user-correctable Prokron state or command error."""


@dataclass(frozen=True)
class Task:
    id: str
    title: str
    dependencies: tuple[str, ...]
    status: str
    validation: str
    owner: str
    claimed: str
    acceptance: str
    evidence: str
    governed_by: tuple[str, ...]


@dataclass(frozen=True)
class Decision:
    id: str
    title: str
    date: str
    status: str
    authority: str
    supersedes: tuple[str, ...]
    amends: tuple[str, ...]
    corrects: tuple[str, ...]
    rejects: tuple[str, ...]
    affects: tuple[str, ...]
    context: str
    decision: str


@dataclass(frozen=True)
class Intent:
    subject: str
    owner: str
    updated: str
    goal: str
    current_point: str
    constraints: tuple[str, ...]
    changed_files: tuple[str, ...]
    next_action: str

    @property
    def task_id(self) -> str | None:
        return self.subject if self.subject.startswith("T-") else None


@dataclass(frozen=True)
class JournalEntry:
    label: str
    task: str
    owner: str
    did: str
    validation: str
    learned: str
    left_mid_air: str
    next_action: str


@dataclass(frozen=True)
class ProkronState:
    tasks: tuple[Task, ...]
    decisions: tuple[Decision, ...]
    intents: tuple[Intent, ...]
    journal: tuple[JournalEntry, ...]
