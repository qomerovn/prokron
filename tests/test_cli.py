import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]


class ProkronCLITest(unittest.TestCase):
    def run_cli(self, directory: Path, *args: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(PROJECT_ROOT / "src")
        return subprocess.run(
            [sys.executable, "-m", "prokron", *args],
            cwd=directory,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_init_is_idempotent_and_preserves_bootstrap_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=project, check=True)
            agents = project / "AGENTS.md"
            agents.write_text("# Custom instructions\n\nKeep this text.\n", encoding="utf-8")
            self.assertEqual(self.run_cli(project, "init").returncode, 0)
            tasks_before = (project / ".prokron" / "TASKS.md").read_text(encoding="utf-8")
            repeated = self.run_cli(project, "init")
            self.assertEqual(repeated.returncode, 0, repeated.stderr)
            self.assertEqual((project / ".prokron" / "TASKS.md").read_text(encoding="utf-8"), tasks_before)
            instructions = agents.read_text(encoding="utf-8")
            self.assertIn("Keep this text.", instructions)
            self.assertEqual(instructions.count("<!-- project-prokron:start -->"), 1)
            self.assertEqual(self.run_cli(project, "doctor").returncode, 0)

    def test_realistic_fixture_end_to_end_and_checkpoint(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary) / "greenfield"
            shutil.copytree(PROJECT_ROOT / "examples" / "greenfield", project)
            subprocess.run(["git", "init", "-q"], cwd=project, check=True)
            self.assertEqual(self.run_cli(project, "status").returncode, 0)
            self.assertEqual(self.run_cli(project, "doctor").returncode, 0)
            state_path = project / ".prokron" / "STATE.md"
            state_path.write_text(state_path.read_text(encoding="utf-8") + "stale\n", encoding="utf-8")
            self.assertEqual(self.run_cli(project, "doctor").returncode, 1)
            graph = self.run_cli(project, "graph")
            self.assertEqual(graph.returncode, 0, graph.stderr)
            self.assertIn("Eligible now: T-003", graph.stdout)
            next_result = self.run_cli(project, "next")
            self.assertIn("T-003\tWrite reviewer guidance", next_result.stdout)
            context = self.run_cli(project, "context", "T-002")
            self.assertIn("ADR-002: Use four explicit approval states", context.stdout)
            self.assertIn("T-004: TODO", context.stdout)
            self.assertNotIn("T-003: TODO", context.stdout)
            for task_id in ("T-002", "T-004", "T-404"):
                with self.subTest(task_id=task_id):
                    self.assertEqual(self.run_cli(project, "start", task_id, "--owner", "test/owner").returncode, 2)
            intent_path = project / ".prokron" / "INTENTS.md"
            intent_before = intent_path.read_text(encoding="utf-8")
            rejected = self.run_cli(
                project,
                "checkpoint",
                "--task",
                "T-002",
                "--did",
                "",
                "--validation",
                "Not run.",
                "--left-mid-air",
                "Still working.",
                "--next",
                "Continue.",
            )
            self.assertEqual(rejected.returncode, 2)
            self.assertEqual(intent_path.read_text(encoding="utf-8"), intent_before)
            comma_path = self.run_cli(
                project,
                "checkpoint",
                "--task",
                "T-002",
                "--did",
                "Checked input.",
                "--validation",
                "Not run.",
                "--left-mid-air",
                "Still working.",
                "--next",
                "Continue.",
                "--changed-file",
                "src/a.py,src/b.py",
            )
            self.assertEqual(comma_path.returncode, 2)
            self.assertEqual(intent_path.read_text(encoding="utf-8"), intent_before)
            journal_path = project / ".prokron" / "JOURNAL.md"
            journal_before = journal_path.read_text(encoding="utf-8")
            checkpoint = self.run_cli(
                project,
                "checkpoint",
                "--task",
                "T-002",
                "--did",
                "Added invalid-transition checks.",
                "--validation",
                "Workflow tests pass.",
                "--left-mid-air",
                "Ready for review; not human-verified.",
                "--next",
                "Ask a reviewer to verify the transition contract.",
                "--changed-file",
                "tests/test_workflow.py",
            )
            self.assertEqual(checkpoint.returncode, 0, checkpoint.stderr)
            journal = journal_path.read_text(encoding="utf-8")
            self.assertTrue(journal.startswith(journal_before))
            self.assertIn("- Left mid-air: Ready for review; not human-verified.", journal)
            intent_after = intent_path.read_text(encoding="utf-8")
            self.assertIn("- Current point: Ready for review; not human-verified.", intent_after)
            self.assertIn("- Next action: Ask a reviewer to verify the transition contract.", intent_after)
            self.assertEqual(self.run_cli(project, "doctor").returncode, 0)

    def test_init_rejects_an_incomplete_managed_block(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=project, check=True)
            (project / "AGENTS.md").write_text("<!-- project-prokron:start -->\n", encoding="utf-8")
            result = self.run_cli(project, "init")
            self.assertEqual(result.returncode, 2)
            self.assertIn("incomplete managed Prokron block", result.stderr)

    def test_adopt_initializes_without_inventing_history(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=project, check=True)
            (project / "README.md").write_text("# Existing project\n", encoding="utf-8")
            adopted = self.run_cli(project, "adopt")
            self.assertEqual(adopted.returncode, 0, adopted.stderr)
            self.assertIn("without inferring missing history", adopted.stdout)
            journal = (project / ".prokron" / "JOURNAL.md").read_text(encoding="utf-8")
            self.assertIn("Existing history was not inferred", journal)
            self.assertEqual(self.run_cli(project, "doctor").returncode, 0)

    def test_empty_markers_without_final_newlines_are_removed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=project, check=True)
            self.assertEqual(self.run_cli(project, "init").returncode, 0)
            tasks = project / ".prokron" / "TASKS.md"
            tasks.write_text(
                tasks.read_text(encoding="utf-8").replace(
                    "# Tasks\n\nAdd tasks using this exact field vocabulary:\n\n```markdown\n",
                    "# Tasks\n\n",
                ).replace("\n```\n", "\n"),
                encoding="utf-8",
            )
            intents = project / ".prokron" / "INTENTS.md"
            journal = project / ".prokron" / "JOURNAL.md"
            intents.write_text("# Intents\n\nNo intent in flight.", encoding="utf-8")
            journal.write_text("# Journal\n\nNo journal entries.", encoding="utf-8")
            self.assertEqual(self.run_cli(project, "start", "T-001", "--owner", "test/owner").returncode, 0)
            checkpoint = self.run_cli(
                project,
                "checkpoint",
                "--did",
                "No journal entries.",
                "--validation",
                "Regression test.",
                "--left-mid-air",
                "Done.",
                "--next",
                "Review.",
            )
            self.assertEqual(checkpoint.returncode, 0, checkpoint.stderr)
            self.assertEqual(
                self.run_cli(
                    project,
                    "checkpoint",
                    "--did",
                    "Added another entry.",
                    "--validation",
                    "Regression test.",
                    "--left-mid-air",
                    "Done.",
                    "--next",
                    "Review.",
                ).returncode,
                0,
            )
            self.assertNotIn("No intent in flight.", intents.read_text(encoding="utf-8"))
            self.assertIn("- Did: No journal entries.", journal.read_text(encoding="utf-8"))
            self.assertEqual(self.run_cli(project, "doctor").returncode, 0)

    def test_empty_project_has_no_next_task_or_context(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=project, check=True)
            self.assertEqual(self.run_cli(project, "init").returncode, 0)
            self.assertIn("READY\nNone", self.run_cli(project, "next").stdout)
            self.assertIn("No eligible task.", self.run_cli(project, "status").stdout)
            context = self.run_cli(project, "context")
            self.assertEqual(context.returncode, 2)
            self.assertIn("not unambiguous", context.stderr)

    def test_checkpoint_rejects_missing_intent_and_multiline_input(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=project, check=True)
            self.assertEqual(self.run_cli(project, "init").returncode, 0)
            missing = self.run_cli(
                project,
                "checkpoint",
                "--did",
                "Nothing.",
                "--validation",
                "Not run.",
                "--left-mid-air",
                "Idle.",
                "--next",
                "Create a task.",
            )
            self.assertEqual(missing.returncode, 2)

            fixture = Path(temporary) / "greenfield"
            shutil.copytree(PROJECT_ROOT / "examples" / "greenfield", fixture)
            multiline = self.run_cli(
                fixture,
                "checkpoint",
                "--did",
                "first line\nsecond line",
                "--validation",
                "Not run.",
                "--left-mid-air",
                "Still working.",
                "--next",
                "Continue.",
            )
            self.assertEqual(multiline.returncode, 2)
            self.assertIn("one Markdown line", multiline.stderr)

    def test_adapters_delegate_to_the_cli(self) -> None:
        for relative_path in (
            "adapters/codex/AGENTS.md",
            "adapters/claude/CLAUDE.md",
            "adapters/generic/README.md",
        ):
            content = (PROJECT_ROOT / relative_path).read_text(encoding="utf-8")
            self.assertIn("prokron", content)


if __name__ == "__main__":
    unittest.main()
