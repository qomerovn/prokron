import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]


class ProkronCLITest(unittest.TestCase):
    def run_cli(self, directory: Path, *args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(PROJECT_ROOT / "src")
        return subprocess.run(
            [sys.executable, "-m", "prokron", *args],
            cwd=directory,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
            input=input_text,
        )

    def make_interview_fixture(self, project: Path) -> None:
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=project, check=True)
        files = {
            "README.md": "# Ledger\n\nTracks operational finance.\n",
            "docs/domain-model.md": "# Domain model\n\nDefines the current ledger model.\n",
            "docs/business-rules.md": "# Business rules\n\nEvery posting balances.\n",
            "docs/roadmap.md": "# Roadmap\n\nImplement GRNI reconciliation next.\n",
            "docs/implementation-plan.md": "# Implementation plan\n\nBuild GRNI reconciliation.\n",
            "docs/open-decisions.md": "# Open decisions\n\nTax mapping remains unresolved.\n",
        }
        for relative, content in files.items():
            path = project / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=project, check=True)
        subprocess.run(
            ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "Start GRNI"],
            cwd=project,
            check=True,
        )
        subprocess.run(["git", "checkout", "-qb", "T-M6-02-grni"], cwd=project, check=True)

    def test_version_matches_release(self) -> None:
        result = self.run_cli(PROJECT_ROOT, "--version")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "0.1.1")

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

    def test_adoption_discovers_stages_migrates_and_applies(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=project, check=True)
            (project / "README.md").write_text("# Existing project\n\nMaintains the current deployment contract.\n", encoding="utf-8")
            (project / "AGENTS.md").write_text("# Constraints\n\nPreserve the deployment contract.\n", encoding="utf-8")
            (project / "docs").mkdir()
            (project / "docs" / "architecture.md").write_text("# Current architecture\n", encoding="utf-8")
            (project / "tests").mkdir()
            (project / "tests" / "test_contract.py").write_text("def test_contract():\n    assert True\n", encoding="utf-8")
            handoff = project / "handoff"
            handoff.mkdir()
            (handoff / "TASKS.md").write_text(
                "# Tasks\n\n## T-001: Verify deployment\n"
                "- Status: TODO\n- Validation: UNTESTED\n- Dependencies: none\n- Owner:\n- Claimed:\n"
                "- Acceptance: Deployment contract is verified.\n- Evidence:\n- Governed by: none\n",
                encoding="utf-8",
            )
            (handoff / "DECISIONS.md").write_text("# Decisions\n", encoding="utf-8")
            (handoff / "INTENTS.md").write_text("# Intents\n\nNo intent in flight.\n", encoding="utf-8")

            dry_run = self.run_cli(project, "adopt", "--dry-run")
            self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
            self.assertIn("handoff/TASKS.md [CURRENT_SUPPORTING]", dry_run.stdout)
            self.assertIn("tests/ [IMPLEMENTATION_EVIDENCE]", dry_run.stdout)
            self.assertIn("No project files were modified.", dry_run.stdout)
            self.assertFalse((project / ".prokron-adoption").exists())
            self.assertFalse((project / ".prokron").exists())

            adopted = self.run_cli(
                project,
                "adopt",
                "--from",
                "handoff",
                "--interactive",
                input_text=(
                    "2\nCurrent architecture is documented in docs/architecture.md.\n"
                    "2\nPreserve the deployment contract.\n"
                    "1\n"
                ),
            )
            self.assertEqual(adopted.returncode, 0, adopted.stderr)
            self.assertIn("0 blocking unknown(s), 0 conflict(s)", adopted.stdout)
            candidate = project / ".prokron-adoption"
            self.assertTrue(candidate.is_dir())
            self.assertFalse((project / ".prokron").exists())
            self.assertIn("- Status: PROPOSED", (candidate / "DECISIONS.md").read_text(encoding="utf-8"))
            self.assertTrue((candidate / "INTERVIEW.md").is_file())
            self.assertTrue(handoff.is_dir())

            applied = self.run_cli(project, "adopt", "--apply")
            self.assertEqual(applied.returncode, 0, applied.stderr)
            self.assertFalse(candidate.exists())
            self.assertTrue(handoff.is_dir())
            decisions = (project / ".prokron" / "DECISIONS.md").read_text(encoding="utf-8")
            self.assertIn("## ADR-A001: Adoption baseline", decisions)
            self.assertIn("- Status: ACCEPTED", decisions)
            self.assertIn("adoption boundary", (project / ".prokron" / "JOURNAL.md").read_text(encoding="utf-8"))
            self.assertEqual(self.run_cli(project, "doctor").returncode, 0)

    def test_interactive_adoption_persists_human_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=project, check=True)
            answers = (
                "\n".join(
                    (
                        "2",
                        "Maintains deployment safety.",
                        "2",
                        "Developer confirmation governs adoption.",
                        "2",
                        "A single local service.",
                        "2",
                        "Preserve migration safety.",
                        "1",
                        "T-100",
                        "Resume migration",
                        "dev/owner",
                        "Schema update is half complete.",
                        "1",
                        "1",
                        "2",
                        "focused migration tests pass",
                        "2",
                        "Use migration-safe writes",
                        "Migration writes can corrupt state.",
                        "Use only migration-safe writes.",
                        "1",
                        "Run the focused migration tests.",
                    )
                )
                + "\n"
            )
            adopted = self.run_cli(project, "adopt", "--interactive", input_text=answers)
            self.assertEqual(adopted.returncode, 0, adopted.stderr)
            candidate = project / ".prokron-adoption"
            report = (candidate / "ADOPTION_REPORT.md").read_text(encoding="utf-8")
            self.assertIn("[CONFIRMED_HUMAN]", report)
            self.assertNotIn("- BLOCKING:", report)
            self.assertIn("## T-100: Resume migration", (candidate / "TASKS.md").read_text(encoding="utf-8"))
            self.assertIn("## T-100", (candidate / "INTENTS.md").read_text(encoding="utf-8"))
            baseline = (candidate / "BASELINE.md").read_text(encoding="utf-8")
            self.assertIn("Human-confirmed operational tasks: 1 [CONFIRMED_HUMAN", baseline)
            self.assertEqual(self.run_cli(project, "adopt", "--apply").returncode, 0)
            context = self.run_cli(project, "context", "T-100")
            self.assertIn("Run the focused migration tests.", context.stdout)
            self.assertIn("ADR-A002: Adoption baseline", context.stdout)
            self.assertIn("ADR-A001: Use migration-safe writes", (project / ".prokron" / "DECISIONS.md").read_text(encoding="utf-8"))

    def test_interactive_adoption_resumes_and_materializes_confirmed_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            self.make_interview_fixture(project)

            interrupted = self.run_cli(
                project,
                "adopt",
                "--answer-json",
                '{"domain":"active work","mode":"confirm"}',
            )
            self.assertEqual(interrupted.returncode, 0, interrupted.stderr)
            stored = json.loads((project / ".prokron-adoption" / "ANSWERS.json").read_text(encoding="utf-8"))
            self.assertEqual(stored["answers"]["active work"]["confidence"], "CONFIRMED_HUMAN")
            self.assertEqual(stored["answers"]["active work"]["source"], "adoption interview")
            self.assertIn("confirmation_timestamp", stored["answers"]["active work"])

            resumed = self.run_cli(project, "adopt", "--interactive", input_text="\n")
            self.assertEqual(resumed.returncode, 0, resumed.stderr)
            self.assertIn("1 confirmations already recorded.", resumed.stdout)
            self.assertNotIn("[1/5] Active Work", resumed.stdout)
            self.assertIn("0 blocking confirmations remain.", resumed.stdout)
            self.assertIn("Adoption candidate is ready.", resumed.stdout)
            self.assertIn("Run: prokron adopt --apply", resumed.stdout)

            candidate = project / ".prokron-adoption"
            task_text = (candidate / "TASKS.md").read_text(encoding="utf-8")
            intent_text = (candidate / "INTENTS.md").read_text(encoding="utf-8")
            interview = (candidate / "INTERVIEW.md").read_text(encoding="utf-8")
            self.assertIn("## T-M6-02: GRNI", task_text)
            self.assertIn("- Validation: UNTESTED", task_text)
            self.assertIn("## T-M6-02", intent_text)
            self.assertIn("Implement GRNI reconciliation next.", intent_text)
            self.assertIn("- Source: adoption interview", interview)
            self.assertIn("- Confidence: CONFIRMED_HUMAN", interview)
            report = (candidate / "ADOPTION_REPORT.md").read_text(encoding="utf-8")
            blocked = report.split("### blocked / waiting\n", 1)[1].split("### ", 1)[0]
            self.assertIn("- Status: ESTABLISHED", blocked)
            self.assertIn("- Confidence: CONFIRMED_HUMAN", blocked)
            self.assertNotIn("- BLOCKING:", report)

    def test_interactive_adoption_accepts_grouped_current_state_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            self.make_interview_fixture(project)

            adopted = self.run_cli(project, "adopt", "--interactive", input_text="\n")

            self.assertEqual(adopted.returncode, 0, adopted.stderr)
            self.assertIn("Current-state proposal", adopted.stdout)
            self.assertIn("Accept all supported/inferred values", adopted.stdout)
            self.assertIn("0 blocking confirmations remain.", adopted.stdout)
            candidate = project / ".prokron-adoption"
            task_text = (candidate / "TASKS.md").read_text(encoding="utf-8")
            intent_text = (candidate / "INTENTS.md").read_text(encoding="utf-8")
            self.assertIn("## T-M6-02: GRNI", task_text)
            self.assertIn("- Owner: developer", task_text)
            self.assertNotIn("adoption/interview", task_text)
            self.assertIn("- Current point: Work on branch T-M6-02-grni", intent_text)
            stored = json.loads((candidate / "ANSWERS.json").read_text(encoding="utf-8"))
            self.assertEqual(len(stored["answers"]), 6)
            self.assertEqual({item["confidence"] for item in stored["answers"].values()}, {"CONFIRMED_HUMAN"})

    def test_grouped_edit_preserves_inferred_task_identity_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            self.make_interview_fixture(project)

            adopted = self.run_cli(
                project,
                "adopt",
                "--interactive",
                input_text="2\n1\n\n\n\nImplement the current branch changes.\n",
            )

            self.assertEqual(adopted.returncode, 0, adopted.stderr)
            task_text = (project / ".prokron-adoption" / "TASKS.md").read_text(encoding="utf-8")
            intent_text = (project / ".prokron-adoption" / "INTENTS.md").read_text(encoding="utf-8")
            self.assertIn("## T-M6-02: GRNI", task_text)
            self.assertIn("- Owner: developer", task_text)
            self.assertIn("- Current point: Implement the current branch changes.", intent_text)

    def test_agent_question_and_answer_primitives_recompute_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            self.make_interview_fixture(project)

            questions = self.run_cli(project, "adopt", "--questions-json")
            self.assertEqual(questions.returncode, 0, questions.stderr)
            items = json.loads(questions.stdout)
            self.assertEqual(len(items), 6)
            active = next(item for item in items if item["domain"] == "active work")
            self.assertEqual(active["confidence"], "INFERRED_HIGH")
            self.assertEqual(active["hypothesis"]["task_id"], "T-M6-02")
            self.assertEqual(active["hypothesis"]["owner"], "developer")
            self.assertEqual(active["hypothesis"]["current_point"], "Work on branch T-M6-02-grni")
            self.assertIn("Recent commit: Start GRNI", active["evidence"])
            self.assertIn("allowed_answer_modes", active)

            answered = self.run_cli(
                project,
                "adopt",
                "--answer-json",
                '{"domain":"active work","mode":"confirm"}',
            )
            self.assertEqual(answered.returncode, 0, answered.stderr)
            self.assertIn("5 blocking confirmations remain.", answered.stdout)
            remaining = json.loads(self.run_cli(project, "adopt", "--questions-json").stdout)
            self.assertNotIn("active work", {item["domain"] for item in remaining})

            blocked_apply = self.run_cli(project, "adopt", "--apply")
            self.assertEqual(blocked_apply.returncode, 2)
            self.assertIn("unresolved blocking", blocked_apply.stderr)

    def test_interactive_adoption_fails_clearly_when_input_is_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            self.make_interview_fixture(project)
            result = self.run_cli(project, "adopt", "--interactive", input_text="")
            self.assertEqual(result.returncode, 2)
            self.assertIn("interactive input ended before the interview completed", result.stderr)

    def test_adoption_has_no_provider_runtime_dependency(self) -> None:
        metadata = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8").casefold()
        for provider in ("openai", "anthropic", "gemini"):
            self.assertNotIn(provider, metadata)

    def test_empty_markers_without_final_newlines_are_removed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=project, check=True)
            self.assertEqual(self.run_cli(project, "init").returncode, 0)
            tasks = project / ".prokron" / "TASKS.md"
            tasks.write_text(
                tasks.read_text(encoding="utf-8")
                .replace(
                    "# Tasks\n\nAdd tasks using this exact field vocabulary:\n\n```markdown\n",
                    "# Tasks\n\n",
                )
                .replace("\n```\n", "\n"),
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
