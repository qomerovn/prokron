import tempfile
import unittest
from pathlib import Path

from prokron.markdown import parse_intents, parse_tasks
from prokron.models import ProkronError

VALID_TASK = """# Tasks

## T-001: Parse canonical tasks
- Status: TODO
- Validation: UNTESTED
- Dependencies: none
- Owner:
- Claimed:
- Acceptance: The task parses.
- Evidence:
- Governed by: ADR-001
"""


class ParsingTest(unittest.TestCase):
    def test_valid_task_parsing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "TASKS.md"
            path.write_text(VALID_TASK, encoding="utf-8")
            task = parse_tasks(path)[0]
            self.assertEqual(task.id, "T-001")
            self.assertEqual(task.governed_by, ("ADR-001",))

    def test_malformed_task_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "TASKS.md"
            path.write_text(VALID_TASK.replace("- Governed by: ADR-001\n", ""), encoding="utf-8")
            with self.assertRaisesRegex(ProkronError, "missing Governed By"):
                parse_tasks(path)

    def test_explicit_no_active_intent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "INTENTS.md"
            path.write_text("# Intents\n\nNo intent in flight.\n", encoding="utf-8")
            self.assertEqual(parse_intents(path), ())

    def test_structural_errors_are_rejected(self) -> None:
        cases = {
            "malformed task heading": VALID_TASK.replace("## T-001:", "## T-:"),
            "duplicate field": VALID_TASK.replace("- Status: TODO\n", "- Status: TODO\n- Status: DONE\n"),
            "unclosed fenced block": "# Tasks\n\n```markdown\n" + VALID_TASK,
            "invalid claimed date": VALID_TASK.replace("- Claimed:\n", "- Claimed: 2026-99-99\n"),
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "TASKS.md"
            for label, content in cases.items():
                with self.subTest(label=label):
                    path.write_text(content, encoding="utf-8")
                    with self.assertRaises(ProkronError):
                        parse_tasks(path)

    def test_empty_intent_marker_cannot_coexist_with_an_intent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "INTENTS.md"
            path.write_text(
                "# Intents\n\nNo intent in flight.\n\n"
                "## T-001\n"
                "- Owner: test/owner\n"
                "- Updated: 2026-09-15\n"
                "- Goal: Test parsing.\n"
                "- Current point: Started.\n"
                "- Constraints: none\n"
                "- Changed files: none\n"
                "- Next action: Continue.\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ProkronError, "conflicts with active intent"):
                parse_intents(path)

    def test_missing_or_unmarked_intent_file_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "INTENTS.md"
            with self.assertRaisesRegex(ProkronError, "is missing"):
                parse_intents(path)
            path.write_text("# Intents\n", encoding="utf-8")
            with self.assertRaisesRegex(ProkronError, "expected an active intent"):
                parse_intents(path)


if __name__ == "__main__":
    unittest.main()
