import unittest
from pathlib import Path

from prokron.core import validate
from prokron.models import Decision, Intent, ProkronState, Task
from prokron.rendering import render_graph, render_state


def task(
    task_id: str,
    *,
    dependencies: tuple[str, ...] = (),
    status: str = "TODO",
    owner: str = "",
    claimed: str = "",
    governed_by: tuple[str, ...] = (),
) -> Task:
    return Task(task_id, task_id, dependencies, status, "UNTESTED", owner, claimed, "accepted", "evidence" if status == "DONE" else "", governed_by)


def decision(
    decision_id: str,
    *,
    status: str = "ACCEPTED",
    supersedes: tuple[str, ...] = (),
    affects: tuple[str, ...] = (),
) -> Decision:
    return Decision(decision_id, decision_id, "2026-09-15", status, "owner", supersedes, (), (), (), affects, "context", "decision")


def state(
    tasks: tuple[Task, ...] = (),
    decisions: tuple[Decision, ...] = (),
    intents: tuple[Intent, ...] = (),
) -> ProkronState:
    return ProkronState(tasks, decisions, intents, ())


class ValidationTest(unittest.TestCase):
    def test_duplicate_task_id(self) -> None:
        self.assertIn("duplicate task ID: T-001", validate(state((task("T-001"), task("T-001")))))

    def test_broken_dependency(self) -> None:
        self.assertIn("T-002: missing dependency T-404", validate(state((task("T-002", dependencies=("T-404",)),))))

    def test_dependency_cycle(self) -> None:
        errors = validate(state((task("T-001", dependencies=("T-002",)), task("T-002", dependencies=("T-001",)))))
        self.assertIn("dependency cycle: T-001 -> T-002 -> T-001", errors)

    def test_valid_dag(self) -> None:
        self.assertEqual(validate(state((task("T-001", status="DONE"), task("T-002", dependencies=("T-001",))))), [])

    def test_wip_requires_owner_and_claim(self) -> None:
        errors = validate(state((task("T-001", status="WIP"),)))
        self.assertIn("T-001: WIP requires Owner", errors)
        self.assertIn("T-001: WIP requires Claimed", errors)

    def test_invalid_task_values_and_missing_completion_evidence(self) -> None:
        invalid = task("T-001", status="UNKNOWN")
        incomplete = Task("T-002", "T-002", (), "DONE", "UNKNOWN", "owner", "2026-09-15", "", "", ())
        errors = validate(state((invalid, incomplete)))
        self.assertIn("T-001: invalid status UNKNOWN", errors)
        self.assertIn("T-002: invalid validation UNKNOWN", errors)
        self.assertIn("T-002: DONE requires Acceptance", errors)
        self.assertIn("T-002: DONE requires Evidence", errors)

    def test_decision_relationship_resolution(self) -> None:
        decisions = (
            decision("ADR-001", status="SUPERSEDED"),
            decision("ADR-002", supersedes=("ADR-001",), affects=("T-001",)),
        )
        self.assertEqual(validate(state((task("T-001", governed_by=("ADR-002",)),), decisions)), [])

    def test_invalid_decision_target(self) -> None:
        errors = validate(state(decisions=(decision("ADR-002", supersedes=("ADR-404",)),)))
        self.assertIn("ADR-002: supersedes missing decision ADR-404", errors)

    def test_decision_requires_authority_and_valid_status(self) -> None:
        item = Decision("ADR-001", "title", "2026-09-15", "UNKNOWN", "", (), (), (), (), (), "context", "decision")
        errors = validate(state(decisions=(item,)))
        self.assertIn("ADR-001: invalid decision status UNKNOWN", errors)
        self.assertIn("ADR-001: Authority is required", errors)

    def test_decision_supersession_cycle(self) -> None:
        decisions = (
            decision("ADR-001", status="SUPERSEDED", supersedes=("ADR-002",)),
            decision("ADR-002", status="SUPERSEDED", supersedes=("ADR-001",)),
        )
        errors = validate(state(decisions=decisions))
        self.assertIn("decision supersession cycle: ADR-001 -> ADR-002 -> ADR-001", errors)

    def test_stale_active_intent(self) -> None:
        intent = Intent("T-001", "codex", "2026-09-15", "goal", "point", (), (), "next")
        errors = validate(state((task("T-001", status="DONE"),), intents=(intent,)))
        self.assertIn("active intent references completed task T-001", errors)

    def test_graph_and_state_are_deterministic(self) -> None:
        current = state((task("T-001", status="DONE"), task("T-002", dependencies=("T-001",))))
        self.assertEqual(render_graph(current), render_graph(current))
        self.assertEqual(render_state(Path("/tmp/example"), current), render_state(Path("/tmp/example"), current))
        self.assertIn("Eligible now: T-002", render_graph(current))
        blocked = state((task("T-001"), task("T-002", dependencies=("T-001",))))
        self.assertIn("Blocked / waiting: T-002", render_graph(blocked))


if __name__ == "__main__":
    unittest.main()
