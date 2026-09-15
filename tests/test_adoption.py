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
        self.assertIn("found but did not interpret", prompt.question)

        result = materialize_confirmations(
            "# Tasks\n", "# Intents\n\nNo intent in flight.\n", (), (), (assessment,), {assessment.domain: "not applicable"}
        )
        self.assertTrue(result[4][0].blocking)
        self.assertIn("REQUIRED", result[5][0])

    def test_conditional_domains_and_optional_history_block_correctly(self) -> None:
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
                self.assertIn("- Requirement: CONDITIONAL", section)
                self.assertIn("- Blocking: yes", section)
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
            stage_adoption(project, "handoff")
            interview = (project / ".prokron-adoption" / "INTERVIEW.md").read_text(encoding="utf-8")
            section = interview.split("### tasks / dependencies\n", 1)[1].split("### ", 1)[0]
            self.assertIn("- Status: NEEDS_CONFIRMATION", section)
            self.assertIn("- Confidence: UNKNOWN", section)
            self.assertIn("- Blocking: yes", section)

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
            self.assertIn("candidate current truth until apply. [INFERRED_LOW]", report)


if __name__ == "__main__":
    unittest.main()
