import copy
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from prokron.adoption import apply, candidate_digest, confirm, freshness, ingest, resume
from prokron.candidate import SCHEMA, validate_candidate
from prokron.models import ProkronError
from prokron.operations import install_bootstrap
from prokron.repository import checkpoint_facts, prepare

PROJECT_ROOT = Path(__file__).parents[1]


class AgentAdoptionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.project = Path(self.temporary.name)
        self.git("init", "-q", "-b", "main")
        (self.project / "src").mkdir()
        (self.project / "src/main.py").write_text("print('receipt import')\n")
        self.git("add", ".")
        self.commit("Initial importer")
        self.candidate = json.loads((PROJECT_ROOT / "examples/brownfield-candidate.json").read_text())
        self.candidate["checkpoint"] = checkpoint_facts(self.project)
        self.input = self.project / ".prokron-candidate/input.json"
        self.input.parent.mkdir()

    def git(self, *args: str) -> str:
        return subprocess.run(["git", *args], cwd=self.project, check=True, capture_output=True, text=True).stdout

    def commit(self, message: str) -> None:
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", message)

    def cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, "-m", "prokron", *args], cwd=self.project,
                              env={**os.environ, "PYTHONPATH": str(PROJECT_ROOT / "src")},
                              capture_output=True, text=True)

    def stage(self) -> str:
        self.input.write_text(json.dumps(self.candidate))
        return ingest(self.project, self.input)

    def adopt(self) -> None:
        confirm(self.project, "human/operator", self.stage())
        apply(self.project)

    def test_brownfield_adoption_and_fresh_process_resume(self) -> None:
        self.assertFalse((self.project / ".prokron").exists())
        self.assertEqual(list(self.project.glob("*.md")), [])
        self.input.write_text(json.dumps(self.candidate))
        for args in (("adopt", "ingest", str(self.input)),
                     ("adopt", "confirm", "--by", "human/operator", "--digest", candidate_digest(self.candidate)),
                     ("adopt", "apply"), ("doctor",)):
            result = self.cli(*args)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        # A separate CLI process has no memory of ingest, confirmation or agent A.
        result = self.cli("resume")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        pack = json.loads(result.stdout)
        self.assertEqual(pack["status"], "CURRENT")
        state = pack["operational_state"]
        self.assertEqual(state["tasks"][1]["dependencies"], ["T-1"])
        self.assertEqual(state["tasks"][2]["status"], "BLOCKED")
        self.assertEqual(state["decisions"][1]["supersedes"], ["ADR-1"])
        self.assertEqual(state["decisions"][1]["affects"], ["T-2"])
        self.assertEqual(state["intents"][0]["goal"], "Reject duplicate receipt rows.")
        self.assertEqual(pack["adoption_baseline"]["candidate"], self.candidate)
        self.assertEqual(pack["next_action"]["action"], self.candidate["next_action"]["action"])
        self.assertEqual(json.loads(self.cli("next").stdout), pack["next_action"])
        self.assertIn("Production deployment details are unknown.", result.stdout)
        self.assertIn("Duplicate behavior has not been exercised.", result.stdout)
        self.assertIn("Preserve existing receipt identifiers.", result.stdout)
        self.assertEqual(self.cli("adopt", "apply").returncode, 2)

    def test_primary_path_never_calls_or_imports_heuristic_engine(self) -> None:
        with patch("prokron.fallback.adoption.discover", side_effect=AssertionError("semantic inference")), \
             patch("prokron.fallback.adoption.stage_adoption", side_effect=AssertionError("semantic inference")):
            facts = prepare(self.project)
            self.assertNotIn("architecture_file", facts)
            self.assertNotIn("current_task", facts)
            self.assertNotIn("next_action", facts)
            self.adopt()
            self.assertEqual(resume(self.project)["status"], "CURRENT")
        result = subprocess.run([sys.executable, "-c", "import prokron.cli, sys; "
                                 "assert not any(n.startswith('prokron.fallback') for n in sys.modules)"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("hypothesis", self.cli("adopt", "schema").stdout)

    def test_read_paths_do_not_repeat_publication_round_trip(self) -> None:
        self.adopt()
        with patch("prokron.adoption._round_trip", side_effect=AssertionError("publication validation")):
            self.assertIsNotNone(freshness(self.project))
            self.assertEqual(resume(self.project)["status"], "CURRENT")

    def test_invalid_candidates_fail_before_staging(self) -> None:
        changes = [
            lambda c: c.update(version=True),
            lambda c: c.update(unexpected="field"),
            lambda c: c["project"]["purpose"].update(status="CERTAIN"),
            lambda c: c["project"]["purpose"].update(sources=[]),
            lambda c: c["project"]["purpose"].update(status="CONFIRMED"),
            lambda c: c["tasks"][1].update(dependencies=["T-missing"]),
            lambda c: c["tasks"][0].update(dependencies=["T-2"]),
            lambda c: c["tasks"].append(copy.deepcopy(c["tasks"][0])),
            lambda c: c["tasks"][1].update(governed_by=["ADR-1"]),
            lambda c: c["intents"][0].update(owner="someone-else"),
            lambda c: c["intents"][0].update(changed_files=["a,b"]),
            lambda c: c["tasks"][1].update(claimed="not a date"),
            lambda c: c["next_action"].update(depends_on=["T-missing"]),
            lambda c: c["tasks"][1].update(title="Hello\n## T-injected: Surprise"),
            lambda c: c["project"]["purpose"].update(statement="Hello\u2028## Injected"),
            lambda c: c["decisions"][1].update(supersedes=["ADR-2"]),
        ]
        original = copy.deepcopy(self.candidate)
        for change in changes:
            self.candidate = copy.deepcopy(original)
            change(self.candidate)
            with self.subTest(candidate=self.candidate), self.assertRaises(ProkronError):
                self.stage()
            self.assertFalse((self.project / ".prokron").exists())
            self.assertFalse((self.input.parent / "candidate.json").exists())

    def test_unknowns_and_claim_provenance_survive_confirmation(self) -> None:
        self.candidate["constraints"][0].update(status="CONFIRMED", confirmed_by="human/operator",
                                               confirmed_at="2026-09-16T10:00:00Z", created_at="2026-09-16T09:00:00Z")
        self.adopt()
        stored = json.loads((self.project / ".prokron/ADOPTION.json").read_text())
        self.assertEqual(stored["candidate"], self.candidate)
        self.assertEqual(stored["candidate"]["active_work"]["status"], "INFERRED")
        self.assertEqual(stored["confirmation"]["by"], "human/operator")

    def test_confirmation_digest_corrections_and_apply_guards(self) -> None:
        digest = self.stage()
        with self.assertRaisesRegex(ProkronError, "confirmation"):
            apply(self.project)
        with self.assertRaisesRegex(ProkronError, "digest"):
            confirm(self.project, "human/operator", "0" * 64)
        with self.assertRaisesRegex(ProkronError, "confirmation.by"):
            confirm(self.project, "human/operator\u2028## forged", digest)
        confirm(self.project, "human/operator", digest)
        staged = self.input.parent / "candidate.json"
        envelope = json.loads(staged.read_text())
        envelope["candidate"]["unknowns"].append("Correction after review")
        staged.write_text(json.dumps(envelope))
        with self.assertRaisesRegex(ProkronError, "changed after confirmation"):
            apply(self.project)
        self.stage()
        with self.assertRaisesRegex(ProkronError, "confirmation"):
            apply(self.project)
        self.assertFalse((self.project / ".prokron").exists())

    def test_moving_repository_rejects_ingest_confirm_and_apply(self) -> None:
        self.stage()
        source = self.project / "src/main.py"
        source.write_text("print('changed')\n")
        with self.assertRaisesRegex(ProkronError, "STATE_STALE"):
            self.stage()
        with self.assertRaisesRegex(ProkronError, "STATE_STALE"):
            confirm(self.project, "human/operator", candidate_digest(self.candidate))
        self.candidate["checkpoint"] = checkpoint_facts(self.project)
        confirm(self.project, "human/operator", self.stage())
        source.write_text("print('changed again')\n")
        with self.assertRaisesRegex(ProkronError, "STATE_STALE"):
            apply(self.project)

    def test_next_stale_for_dirty_changes_and_new_head_checkpoint_restores(self) -> None:
        self.adopt()
        (self.project / "src/main.py").write_text("print('duplicate check')\n")
        self.assertIn("STATE_STALE", self.cli("next").stderr)
        self.assertEqual(json.loads(self.cli("resume").stdout)["status"], "STATE_STALE")
        result = self.cli("checkpoint", "--task", "T-2", "--did", "Added duplicate check.",
                          "--validation", "Regression passed.", "--left-mid-air", "Review pending.",
                          "--next", "Review duplicate handling.")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(self.cli("next").stdout)["action"], "Review duplicate handling.")
        self.git("add", "src/main.py")
        self.commit("Add duplicate check")
        self.assertIn("STATE_STALE", self.cli("next").stderr)
        self.assertEqual(self.cli("doctor").returncode, 1)

    def test_committing_adoption_state_keeps_snapshot_fresh(self) -> None:
        self.adopt()
        self.git("add", ".prokron", "AGENTS.md")
        self.commit("Adopt Prokron")
        self.assertEqual(resume(self.project)["status"], "CURRENT")
        self.assertEqual(self.cli("doctor").returncode, 0)

    def test_empty_work_can_resume_without_fabricated_task_or_intent(self) -> None:
        self.candidate.update(tasks=[], intents=[], decisions=[], blockers=[])
        self.candidate["next_action"] = {"action": "Ask the operator which import to extend.", "reason": "Priority unknown.", "depends_on": []}
        self.adopt()
        self.assertEqual(json.loads(self.cli("resume").stdout)["operational_state"]["tasks"], [])
        self.assertEqual(self.cli("next").returncode, 0)

    def test_recorded_action_obeys_current_dependencies_and_blockers(self) -> None:
        self.adopt()
        path = self.project / ".prokron/TASKS.md"
        before = path.read_text()
        for after in (before.replace("- Status: DONE", "- Status: TODO", 1), before.replace("- Status: WIP", "- Status: BLOCKED", 1)):
            path.write_text(after)
            # BLOCKED work cannot retain a WIP intent.
            (self.project / ".prokron/INTENTS.md").write_text("# Intents\n\nNo intent in flight.\n")
            result = self.cli("next")
            self.assertEqual(result.returncode, 2, result.stdout)
            self.assertIn("NEXT_ACTION_BLOCKED", result.stderr)

    def test_staging_symlinks_and_partial_bootstrap_fail_without_publication(self) -> None:
        digest = self.stage()
        confirm(self.project, "human/operator", digest)
        (self.project / "AGENTS.md").write_text("<!-- project-prokron:start -->\n")
        with self.assertRaisesRegex(ProkronError, "managed Prokron block"):
            apply(self.project)
        self.assertFalse((self.project / ".prokron").exists())
        (self.project / "AGENTS.md").unlink()
        staged = self.input.parent / "candidate.json"
        staged.unlink()
        staged.symlink_to(self.input)
        with self.assertRaisesRegex(ProkronError, "symlink"):
            apply(self.project)

    def test_apply_rolls_back_bootstrap_if_publication_fails(self) -> None:
        confirm(self.project, "human/operator", self.stage())
        with patch.object(Path, "rename", side_effect=OSError("publication failed")), self.assertRaises(OSError):
            apply(self.project)
        self.assertFalse((self.project / ".prokron").exists())
        self.assertFalse((self.project / "AGENTS.md").exists())
        apply(self.project)
        self.assertEqual(self.cli("doctor").returncode, 0)

    def test_apply_does_not_overwrite_a_concurrent_bootstrap_edit(self) -> None:
        confirm(self.project, "human/operator", self.stage())
        bootstrap = self.project / "AGENTS.md"

        def fail_after_edit(*_: object) -> None:
            bootstrap.write_text("# Concurrent edit\n")
            raise OSError("publication failed")

        with patch.object(Path, "rename", side_effect=fail_after_edit), self.assertRaises(OSError):
            apply(self.project)
        self.assertEqual(bootstrap.read_text(), "# Concurrent edit\n")

    def test_apply_rolls_back_to_content_seen_during_install(self) -> None:
        confirm(self.project, "human/operator", self.stage())
        bootstrap = self.project / "AGENTS.md"

        def edit_then_install(path: Path) -> tuple[bytes | None, bytes] | None:
            bootstrap.write_text("# Concurrent edit\n")
            return install_bootstrap(path)

        with patch("prokron.adoption.install_bootstrap", side_effect=edit_then_install), \
             self.assertRaisesRegex(ProkronError, "STATE_STALE"):
            apply(self.project)
        self.assertEqual(bootstrap.read_text(), "# Concurrent edit\n")

    def test_bootstrap_install_preserves_existing_bytes(self) -> None:
        bootstrap = self.project / "AGENTS.md"
        original = b"# Windows instructions\r\n\r\nKeep receipt IDs.\r\n"
        bootstrap.write_bytes(original)
        installed = install_bootstrap(bootstrap)
        self.assertIsNotNone(installed)
        self.assertTrue(bootstrap.read_bytes().startswith(original))
        self.assertEqual(installed, (original, bootstrap.read_bytes()))

    def test_apply_loser_preserves_winner_bootstrap(self) -> None:
        confirm(self.project, "human/operator", self.stage())

        def publish_elsewhere(*_: object) -> None:
            (self.project / ".prokron").mkdir()
            raise FileExistsError("published concurrently")

        with patch.object(Path, "rename", side_effect=publish_elsewhere), self.assertRaises(FileExistsError):
            apply(self.project)
        self.assertIn("<!-- project-prokron:start -->", (self.project / "AGENTS.md").read_text())

    def test_prepare_ignores_generated_content_and_detects_untracked_changes(self) -> None:
        before = checkpoint_facts(self.project)
        (self.project / "node_modules").mkdir()
        (self.project / "node_modules/generated.js").write_text("ignored")
        self.assertEqual(before, checkpoint_facts(self.project))
        (self.project / "src/new.py").write_text("one")
        changed = checkpoint_facts(self.project)
        self.assertNotEqual(before, changed)
        (self.project / "src/new.py").write_text("two")
        self.assertNotEqual(changed, checkpoint_facts(self.project))
        unusual = self.project / " leading-space.py"
        unusual.write_text("one")
        changed = checkpoint_facts(self.project)
        unusual.write_text("two")
        self.assertNotEqual(changed, checkpoint_facts(self.project))

    def test_schema_validates_minimal_task_defaults(self) -> None:
        state = validate_candidate(self.candidate)
        self.assertEqual(state.tasks[1].validation, "UNTESTED")
        self.assertEqual(state.decisions[0].supersedes, ())
        pattern = SCHEMA["properties"]["project"]["properties"]["purpose"]["properties"]["statement"]["pattern"]
        self.assertIsNone(re.fullmatch(pattern, "Hello\u2028## Injected"))
        self.assertIsNone(re.search(pattern, "Hello\n"))

    def test_live_next_action_moves_to_new_task_after_checkpoint(self) -> None:
        self.adopt()
        root = self.project / ".prokron"
        tasks = (root / "TASKS.md").read_text().replace("- Status: WIP", "- Status: DONE", 1)
        tasks = tasks.replace("- Evidence: \n- Governed by: ADR-2", "- Evidence: Duplicate regression passed.\n- Governed by: ADR-2")
        tasks = tasks.replace("- Status: BLOCKED", "- Status: TODO", 1)
        (root / "TASKS.md").write_text(tasks)
        (root / "INTENTS.md").write_text("# Intents\n\nNo intent in flight.\n")
        result = self.cli("start", "T-3", "--owner", "agent-b")
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.cli("next")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["task_id"], "T-3")
        self.assertEqual(json.loads(result.stdout)["action"], "Implement T-3.")

    def test_maintenance_intent_does_not_emit_a_task_id(self) -> None:
        self.candidate.update(tasks=[], decisions=[], blockers=[])
        self.candidate["intents"] = [{
            "subject": "maintenance/dependencies", "owner": "agent-a", "updated": "2026-09-16",
            "goal": "Refresh dependencies.", "current_point": "Ready.", "next_action": "Update locked versions.",
        }]
        self.candidate["next_action"] = {"action": "Update locked versions.", "reason": "Recorded intent.", "depends_on": []}
        self.adopt()
        action = json.loads(self.cli("next").stdout)
        self.assertEqual(action["action"], "Update locked versions.")
        self.assertNotIn("task_id", action)

    def test_prepare_is_read_only_and_unborn_repository_can_adopt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            subprocess.run(["git", "init", "-q", "-b", "main"], cwd=project, check=True)
            facts = prepare(project)
            self.assertEqual(facts["checkpoint"]["head"], "")
            self.assertEqual(list(project.iterdir()), [project / ".git"])
            candidate = copy.deepcopy(self.candidate)
            candidate["checkpoint"] = facts["checkpoint"]
            self.input.write_text(json.dumps(candidate))
            digest = ingest(project, self.input)
            confirm(project, "human/operator", digest)
            apply(project)
            self.assertEqual(resume(project)["status"], "CURRENT")

    def test_custom_bootstrap_survives_apply_and_changes_invalidate_freshness(self) -> None:
        path = self.project / "AGENTS.md"
        path.write_text("# Custom instructions\n\nKeep receipt IDs.\n")
        self.candidate["checkpoint"] = checkpoint_facts(self.project)
        self.adopt()
        self.assertTrue(path.read_text().startswith("# Custom instructions\n\nKeep receipt IDs.\n"))
        self.assertEqual(self.cli("next").returncode, 0)
        path.write_text(path.read_text().replace("Keep receipt IDs.", "Change receipt IDs."))
        self.assertIn("STATE_STALE", self.cli("next").stderr)


if __name__ == "__main__":
    unittest.main()
