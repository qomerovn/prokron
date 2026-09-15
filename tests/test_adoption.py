import subprocess
import tempfile
import unittest
from dataclasses import fields
from pathlib import Path, PurePosixPath

from prokron.adoption import (
    COVERAGE_SCHEMA,
    AssessmentStatus,
    Confidence,
    DomainAssessment,
    Requirement,
    SourceClassification,
    classify_source,
    discover,
    generate_interview_prompts,
    materialize_confirmations,
    render_discovery,
    stage_adoption,
)
from prokron.markdown import parse_decisions, parse_intents, parse_tasks


class AdoptionClassificationTest(unittest.TestCase):
    def test_each_source_classification_is_reachable(self) -> None:
        cases = {
            ".prokron/TASKS.md": SourceClassification.CURRENT_CANONICAL,
            "handoff/TASKS.md": SourceClassification.CURRENT_SUPPORTING,
            "docs/handoff/DECISIONS.md": SourceClassification.CURRENT_SUPPORTING,
            "CHANGELOG.md": SourceClassification.HISTORICAL,
            "handoff/STATE.md": SourceClassification.DERIVED,
            "tests/test_contract.py": SourceClassification.IMPLEMENTATION_EVIDENCE,
            "docs/old-architecture.md": SourceClassification.STALE_OR_CONFLICTING,
            "docs/_archive/architecture.md": SourceClassification.STALE_OR_CONFLICTING,
            "docs/modeling/domain.md": SourceClassification.CURRENT_SUPPORTING,
            "packages/api/tests/test_contract.py": SourceClassification.IMPLEMENTATION_EVIDENCE,
            "NOTES.md": SourceClassification.UNKNOWN,
        }
        for path, expected in cases.items():
            with self.subTest(path=path):
                source = classify_source(PurePosixPath(path))
                self.assertIsNotNone(source)
                assert source is not None
                self.assertEqual(source.classification, expected)

        for path in ("docs/pitch/images/hero.webp", "docs/handoff/TASKS.webp", "docs/.DS_Store"):
            with self.subTest(path=path):
                self.assertIsNone(classify_source(PurePosixPath(path)))

    def test_discovery_filters_artifacts_and_summarizes_nested_implementation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=project, check=True)
            fixture_files = {
                "handoff/TASKS.md": "# Tasks\n",
                "docs/handoff/DECISIONS.md": "# Decisions\n",
                "docs/handoff/INTENTS.md": "# Intents\n",
                "docs/_archive/plan.md": "# Old plan\n",
                "docs/pitch/images/hero.webp": "generated image",
                "docs/.DS_Store": "metadata",
                ".artifacts/release/error-context.md": "generated error context",
                "docs/modeling/domain.md": "# Domain model\n",
                "packages/api/src/service.py": "VALUE = 1\n",
                "packages/api/tests/test_service.py": "assert True\n",
            }
            for relative, content in fixture_files.items():
                path = project / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")

            discovery = discover(project)
            rendered = render_discovery(discovery)
            sources = {source.path: source.classification for source in discovery.sources}

            self.assertIn("handoff/TASKS.md", sources)
            self.assertIn("docs/handoff/DECISIONS.md", sources)
            self.assertIn("docs/handoff/INTENTS.md", sources)
            self.assertEqual(sources["docs/_archive/plan.md"], SourceClassification.STALE_OR_CONFLICTING)
            self.assertEqual(sources["docs/modeling/domain.md"], SourceClassification.CURRENT_SUPPORTING)
            self.assertEqual(sources["packages/api/src/"], SourceClassification.IMPLEMENTATION_EVIDENCE)
            self.assertEqual(sources["packages/api/tests/"], SourceClassification.IMPLEMENTATION_EVIDENCE)
            self.assertNotIn("docs/pitch/images/hero.webp", sources)
            self.assertNotIn("docs/.DS_Store", sources)
            self.assertFalse(any(path.startswith(".artifacts/") for path in discovery.files))
            self.assertIn("Potential legacy state system:\n  docs/handoff, handoff", rendered)

    def test_coverage_schema_and_contextual_prompt_are_structured(self) -> None:
        requirements = {item.domain: item.requirement for item in COVERAGE_SCHEMA}
        self.assertEqual(requirements["project identity"], Requirement.REQUIRED)
        self.assertEqual(
            {domain for domain, requirement in requirements.items() if requirement == Requirement.CONDITIONAL},
            {
                "production / release restrictions",
                "deployment state",
                "human validation gates",
                "security / destructive-operation constraints",
            },
        )
        self.assertEqual(requirements["complete pre-adoption history"], Requirement.OPTIONAL)
        self.assertEqual(
            {field.name for field in fields(DomainAssessment)},
            {"domain", "requirement", "status", "confidence", "evidence", "blocking", "reason"},
        )
        assessment = DomainAssessment(
            "current architecture / domain model",
            Requirement.REQUIRED,
            AssessmentStatus.NEEDS_CONFIRMATION,
            Confidence.INFERRED_LOW,
            ("docs/architecture.md",),
            True,
            "Content was not interpreted.",
        )
        prompt = generate_interview_prompts((assessment,))[0]
        self.assertIn("docs/architecture.md", prompt.context)
        self.assertIn("architecture candidates", prompt.question)
        authority_prompt = generate_interview_prompts(
            (
                DomainAssessment(
                    "current authority",
                    Requirement.REQUIRED,
                    AssessmentStatus.NEEDS_CONFIRMATION,
                    Confidence.INFERRED_LOW,
                    ("docs/thesis.md",),
                    True,
                    "One candidate was inspected.",
                ),
            )
        )[0]
        self.assertIn("Does `docs/thesis.md` govern", authority_prompt.question)
        self.assertNotIn("Which", authority_prompt.question)

        result = materialize_confirmations(
            "# Tasks\n", "# Intents\n\nNo intent in flight.\n", (), (), (assessment,), {assessment.domain: "not applicable"}
        )
        self.assertTrue(result[4][0].blocking)
        self.assertIn("REQUIRED", result[5][0])

    def test_conditional_domains_require_material_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=project, check=True)
            (project / "pyproject.toml").write_text("[project]\nname='fixture'\n", encoding="utf-8")
            (project / ".github" / "workflows").mkdir(parents=True)
            (project / ".github" / "workflows" / "deploy.yml").write_text("name: deploy\n", encoding="utf-8")
            (project / "migrations").mkdir()
            (project / "migrations" / "001.sql").write_text("-- migration\n", encoding="utf-8")
            stage_adoption(project)
            interview = (project / ".prokron-adoption" / "INTERVIEW.md").read_text(encoding="utf-8")
            for domain in (
                "production / release restrictions",
                "deployment state",
                "security / destructive-operation constraints",
            ):
                section = interview.split(f"### {domain}\n", 1)[1].split("### ", 1)[0]
                self.assertIn("- Status: NOT_APPLICABLE", section)
                self.assertIn("- Blocking: no", section)
            for domain in ("pre-adoption rationale", "rejected historical approaches", "complete pre-adoption history"):
                section = interview.split(f"### {domain}\n", 1)[1].split("### ", 1)[0]
                self.assertIn("- Status: DEFERRED", section)
                self.assertIn("- Blocking: no", section)

    def test_malformed_structured_file_does_not_establish_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=project, check=True)
            handoff = project / "handoff"
            handoff.mkdir()
            (handoff / "TASKS.md").write_text("# Tasks\n\n## current work\n- item\n", encoding="utf-8")
            result = stage_adoption(project, "handoff")
            interview = (project / ".prokron-adoption" / "INTERVIEW.md").read_text(encoding="utf-8")
            section = interview.split("### tasks / dependencies\n", 1)[1].split("### ", 1)[0]
            self.assertIn("- Status: NEEDS_CONFIRMATION", section)
            self.assertIn("- Confidence: UNKNOWN", section)
            self.assertIn("- Blocking: yes", section)
            self.assertEqual(result.conflicts, ())
            self.assertEqual(len(result.incompatibilities), 1)
            report = (project / ".prokron-adoption" / "ADOPTION_REPORT.md").read_text(encoding="utf-8")
            self.assertIn("## MIGRATION / FORMAT INCOMPATIBILITIES", report)
            self.assertIn("TASKS.md format is incompatible", report)
            self.assertIn("## CONFLICTING SOURCES\n- None.", report)

    def test_empty_and_malformed_intent_are_not_active_work_or_conflicts(self) -> None:
        for content, incompatible in (("", False), ("# Current handoff\n\nContinue migration.\n", True)):
            with self.subTest(incompatible=incompatible), tempfile.TemporaryDirectory() as temporary:
                project = Path(temporary)
                subprocess.run(["git", "init", "-q"], cwd=project, check=True)
                handoff = project / "handoff"
                handoff.mkdir()
                (handoff / "INTENTS.md").write_text(content, encoding="utf-8")

                result = stage_adoption(project, "handoff")
                report = (project / ".prokron-adoption" / "ADOPTION_REPORT.md").read_text(encoding="utf-8")
                active = report.split("### active work\n", 1)[1].split("### ", 1)[0]
                next_action = report.split("### next action\n", 1)[1].split("### ", 1)[0]

                self.assertIn("- Status: NEEDS_CONFIRMATION", active)
                self.assertNotIn("Imported active task or intent records establish", active)
                self.assertIn("- Status: NEEDS_CONFIRMATION", next_action)
                self.assertIn("- Blocking: yes", next_action)
                self.assertEqual(result.conflicts, ())
                self.assertEqual(bool(result.incompatibilities), incompatible)
                self.assertIn("## CONFLICTING SOURCES\n- None.", report)

    def test_empty_structured_state_does_not_establish_operational_domains(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=project, check=True)
            handoff = project / "handoff"
            handoff.mkdir()
            (handoff / "TASKS.md").write_text("# Tasks\n", encoding="utf-8")
            (handoff / "DECISIONS.md").write_text("# Decisions\n", encoding="utf-8")
            (handoff / "INTENTS.md").write_text("# Intents\n\nNo intent in flight.\n", encoding="utf-8")

            stage_adoption(project, "handoff")
            report = (project / ".prokron-adoption" / "ADOPTION_REPORT.md").read_text(encoding="utf-8")
            for domain in ("active work", "tasks / dependencies", "blocked / waiting", "validation / evidence", "next action"):
                section = report.split(f"### {domain}\n", 1)[1].split("### ", 1)[0]
                self.assertIn("- Status: NEEDS_CONFIRMATION", section)
                self.assertIn("- Blocking: yes", section)
                self.assertNotIn("Imported ", section)

    def test_generic_repository_stages_a_bounded_meaningful_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            subprocess.run(["git", "init", "-q", "-b", "main"], cwd=project, check=True)
            fixture_files = {
                "README.md": "# Widget service\n\nProcesses widgets for partner APIs.\n",
                "docs/architecture.md": "# Architecture\n\nA small HTTP service owns widget processing.\n",
                "docs/roadmap.md": "# Roadmap\n\nCurrent: finish retry-safe widget delivery.\n",
                "src/service.py": "VALUE = 1\n",
                "tests/test_service.py": "assert True\n",
                ".github/workflows/ci.yml": "name: CI\n",
            }
            for relative, content in fixture_files.items():
                path = project / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=project, check=True)
            subprocess.run(
                ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "Add widget service"],
                cwd=project,
                check=True,
            )
            subprocess.run(["git", "checkout", "-qb", "feature/retry-delivery"], cwd=project, check=True)

            result = stage_adoption(project)
            candidate = project / ".prokron-adoption"
            report = (candidate / "ADOPTION_REPORT.md").read_text(encoding="utf-8")
            baseline = (candidate / "BASELINE.md").read_text(encoding="utf-8")

            for source in ("docs/architecture.md", "docs/roadmap.md"):
                self.assertIn(f"{source} (bounded text inspection)", report)
            self.assertIn("README.md (bounded purpose paragraph)", report)
            self.assertNotIn("src/service.py (bounded text inspection)", report)
            self.assertIn("Current-state hypotheses", baseline)
            self.assertIn("finish retry-safe widget delivery", baseline)
            self.assertIn("Git branch: feature/retry-delivery", report)
            self.assertEqual(parse_tasks(candidate / "TASKS.md"), ())
            self.assertEqual(parse_intents(candidate / "INTENTS.md"), ())
            self.assertEqual(len(parse_decisions(candidate / "DECISIONS.md")), 1)
            self.assertIn("active work", result.unknowns)
            self.assertEqual(result.conflicts, ())
            self.assertEqual(result.incompatibilities, ())

    def test_messy_generic_repository_preserves_uncertainty_and_noise_bounds(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=project, check=True)
            fixture_files = {
                "README.md": "# Service\n\nRuns the current service.\n",
                "docs/architecture.md": "# Architecture\n\nThe current design uses services.\n",
                "docs/architecture-v2.md": "# Architecture v2\n\nThe current design uses one process.\n",
                "docs/_archive/architecture.md": "# Old\n\nArchived design.\n",
                "docs/random.md": "# Scratch\n\nUnrelated notes.\n",
                ".artifacts/release/error-context.md": "generated\n",
                "build/generated.md": "generated\n",
                "ops/deploy.sh": "#!/bin/sh\n",
            }
            for relative, content in fixture_files.items():
                path = project / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")

            stage_adoption(project)
            report = (project / ".prokron-adoption" / "ADOPTION_REPORT.md").read_text(encoding="utf-8")
            architecture = report.split("### current architecture / domain model\n", 1)[1].split("### ", 1)[0]
            deployment = report.split("### deployment state\n", 1)[1].split("### ", 1)[0]

            self.assertIn("docs/architecture.md", architecture)
            self.assertIn("docs/architecture-v2.md", architecture)
            self.assertIn("- Status: NEEDS_CONFIRMATION", architecture)
            self.assertNotIn("docs/_archive/architecture.md (bounded text inspection)", report)
            self.assertNotIn("docs/random.md (bounded text inspection)", report)
            self.assertNotIn("error-context.md", report)
            self.assertIn("`ops/deploy.sh`", report)
            self.assertIn("- Status: NOT_APPLICABLE", deployment)

    def test_report_separates_discovery_from_inspection_and_keeps_low_confidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=project, check=True)
            (project / "README.md").write_text("# Fixture\n\nCurrent fixture purpose.\n", encoding="utf-8")
            (project / "src").mkdir()
            (project / "src" / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
            (project / "TASKS.md").write_text("# Tasks\n", encoding="utf-8")
            (project / "DECISIONS.md").write_text("# Decisions\n", encoding="utf-8")
            (project / "INTENTS.md").write_text("# Intents\n\nNo intent in flight.\n", encoding="utf-8")
            stage_adoption(project)
            report = (project / ".prokron-adoption" / "ADOPTION_REPORT.md").read_text(encoding="utf-8")
            discovered = report.split("## DISCOVERED SOURCES (FILENAME / METADATA ONLY)\n", 1)[1].split("## CONTENT ACTUALLY INSPECTED", 1)[
                0
            ]
            inspected = report.split("## CONTENT ACTUALLY INSPECTED\n", 1)[1].split("## CURRENT TRUTH CONFIRMED FROM REPOSITORY", 1)[0]
            self.assertIn("`src/`", discovered)
            self.assertNotIn("src/", inspected)
            self.assertIn("TASKS.md (structured parse)", inspected)
            self.assertNotIn("Selected structured state files are candidate current truth", report)
            self.assertIn("No task records or current planning source were inspected", report)

    def test_generic_legacy_incompatibility_is_informational_but_explicit_source_is_strict(self) -> None:
        for explicit, marker in ((False, "- INFO:"), (True, "- BLOCKING:")):
            with self.subTest(explicit=explicit), tempfile.TemporaryDirectory() as temporary:
                project = Path(temporary)
                subprocess.run(["git", "init", "-q"], cwd=project, check=True)
                (project / "README.md").write_text("# Service\n\nRuns widgets.\n", encoding="utf-8")
                handoff = project / "docs" / "handoff"
                handoff.mkdir(parents=True)
                (handoff / "INTENTS.md").write_text("# Legacy intent\n\nContinue migration.\n", encoding="utf-8")

                result = stage_adoption(project, "docs/handoff" if explicit else None)
                report = (project / ".prokron-adoption" / "ADOPTION_REPORT.md").read_text(encoding="utf-8")
                active = report.split("### active work\n", 1)[1].split("### ", 1)[0]

                self.assertIn(marker, report.split("## MIGRATION / FORMAT INCOMPATIBILITIES\n", 1)[1])
                self.assertNotIn("conflict", result.incompatibilities[0].casefold())
                self.assertEqual(result.conflicts, ())
                if not explicit:
                    self.assertNotIn("format is incompatible", active)

    def test_semantic_ranking_follows_one_markdown_hop_with_a_fixed_budget(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=project, check=True)
            files = {
                "README.md": "# Service\n\nCurrent service.\n",
                "docs/product-thesis.md": "# Product thesis\n\n[Architecture](design/system.md)\n\nOwn the useful present.\n",
                "docs/design/system.md": "# System\n\nThe API and worker form the current system.\n",
                "docs/roadmap.md": "# Roadmap\n\nShip the worker next.\n",
                "docs/business-rules.md": "# Rules\n\nEvery write is idempotent.\n",
                "docs/open-decisions.md": "# Open decisions\n\nStorage remains undecided.\n",
                "docs/implementation-plan.md": "# Plan\n\nBuild API then worker.\n",
                "docs/forms_legal/architecture.md": "# Form architecture\n\nLegal form rendering.\n",
                "docs/nested/README-architecture.md": "# Package\n\nNested package notes.\n",
            }
            for relative, content in files.items():
                path = project / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")

            stage_adoption(project)
            report = (project / ".prokron-adoption" / "ADOPTION_REPORT.md").read_text(encoding="utf-8")
            inspected = report.split("## CONTENT ACTUALLY INSPECTED\n", 1)[1].split(
                "## CURRENT TRUTH CONFIRMED FROM REPOSITORY", 1
            )[0]

            self.assertIn("docs/design/system.md (bounded text inspection)", inspected)
            self.assertNotIn("docs/forms_legal/architecture.md", inspected)
            self.assertNotIn("docs/nested/README-architecture.md", inspected)
            self.assertLessEqual(inspected.count("bounded text inspection"), 6)

    def test_current_authority_is_scoped_and_open_decisions_are_not_governing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=project, check=True)
            files = {
                "README.md": "# Service\n\nRuns widgets.\n",
                "docs/domain-model.md": "# Domain model\n\nDefines the service model.\n",
                "docs/business-rules.md": "# Business rules\n\nWrites are idempotent.\n",
                "docs/roadmap.md": "# Roadmap\n\nSequence delivery work.\n",
                "docs/implementation-plan.md": "# Implementation plan\n\nBuild the worker.\n",
                "docs/open-decisions.md": "# Open decisions\n\nStorage remains unresolved.\n",
            }
            for relative, content in files.items():
                path = project / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")

            stage_adoption(project)
            report = (project / ".prokron-adoption" / "ADOPTION_REPORT.md").read_text(encoding="utf-8")
            authority = report.split("### current authority\n", 1)[1].split("### ", 1)[0]

            self.assertIn("- Status: ESTABLISHED", authority)
            self.assertIn("architecture / domain model: docs/domain-model.md", authority)
            self.assertIn("planning / roadmap: docs/roadmap.md", authority)
            self.assertIn("unresolved decisions surface (non-governing): docs/open-decisions.md", authority)
            self.assertNotIn("Open Decisions as governing authority", authority)

    def test_authority_interview_targets_only_the_ambiguous_scope(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=project, check=True)
            (project / "README.md").write_text("# Service\n\nRuns widgets.\n", encoding="utf-8")
            docs = project / "docs"
            docs.mkdir()
            (docs / "architecture.md").write_text("# Architecture\n\nCurrent service design.\n", encoding="utf-8")
            (docs / "architecture-v2.md").write_text("# Architecture v2\n\nAlternate service design.\n", encoding="utf-8")
            (docs / "roadmap.md").write_text("# Roadmap\n\nSequence delivery.\n", encoding="utf-8")

            stage_adoption(project)
            interview = (project / ".prokron-adoption" / "INTERVIEW.md").read_text(encoding="utf-8")
            prompts = interview.split("## Structured prompts\n", 1)[1]
            authority = prompts.split("### current authority\n", 1)[1].split("### ", 1)[0]

            self.assertIn("AMBIGUOUS architecture / domain model", authority)
            self.assertIn("Resolve authority ownership only for these ambiguous scopes", authority)
            self.assertNotIn("Which inspected source governs current project truth", authority)

    def test_planning_surface_does_not_establish_tasks_or_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=project, check=True)
            (project / "README.md").write_text("# Service\n\nRuns widgets.\n", encoding="utf-8")
            (project / "roadmap.md").write_text("# Roadmap\n\nShip the worker next.\n", encoding="utf-8")
            (project / "implementation-plan.md").write_text("# Plan\n\nBuild the worker.\n", encoding="utf-8")

            stage_adoption(project)
            report = (project / ".prokron-adoption" / "ADOPTION_REPORT.md").read_text(encoding="utf-8")
            tasks = report.split("### tasks / dependencies\n", 1)[1].split("### ", 1)[0]

            self.assertIn("- Status: NEEDS_CONFIRMATION", tasks)
            self.assertIn("- Blocking: yes", tasks)
            self.assertIn("planning surface was inspected", tasks)
            self.assertEqual(parse_tasks(project / ".prokron-adoption" / "TASKS.md"), ())

    def test_git_and_roadmap_compose_high_confidence_without_fabricated_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            subprocess.run(["git", "init", "-q", "-b", "main"], cwd=project, check=True)
            (project / "README.md").write_text("# Service\n\nRuns widgets.\n", encoding="utf-8")
            (project / "roadmap.md").write_text("# Roadmap\n\nDeliver retry handling next.\n", encoding="utf-8")
            subprocess.run(["git", "add", "."], cwd=project, check=True)
            subprocess.run(
                ["git", "-c", "user.name=Test", "-c", "user.email=test@example.com", "commit", "-qm", "Start retries"],
                cwd=project,
                check=True,
            )
            subprocess.run(["git", "checkout", "-qb", "feature/retries"], cwd=project, check=True)

            stage_adoption(project)
            candidate = project / ".prokron-adoption"
            report = (candidate / "ADOPTION_REPORT.md").read_text(encoding="utf-8")
            active = report.split("### active work\n", 1)[1].split("### ", 1)[0]

            self.assertIn("- Confidence: INFERRED_HIGH", active)
            self.assertIn("Recent commit: Start retries", active)
            self.assertEqual(parse_tasks(candidate / "TASKS.md"), ())
            self.assertEqual(parse_intents(candidate / "INTENTS.md"), ())

    def test_generic_agent_instructions_do_not_trigger_human_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = Path(temporary)
            subprocess.run(["git", "init", "-q"], cwd=project, check=True)
            (project / "README.md").write_text("# Service\n\nRuns widgets.\n", encoding="utf-8")
            (project / "AGENTS.md").write_text(
                "Ask a human to review deploy, release, production, migration, and security work.\n", encoding="utf-8"
            )

            stage_adoption(project)
            report = (project / ".prokron-adoption" / "ADOPTION_REPORT.md").read_text(encoding="utf-8")
            for domain in (
                "production / release restrictions",
                "deployment state",
                "human validation gates",
                "security / destructive-operation constraints",
            ):
                section = report.split(f"### {domain}\n", 1)[1].split("### ", 1)[0]
                self.assertIn("- Status: NOT_APPLICABLE", section)


if __name__ == "__main__":
    unittest.main()
