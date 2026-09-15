"""Repository facts only. No filename ranking or content interpretation."""
from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path

from .models import ProkronError

GENERATED = (
    ".prokron", ".prokron-candidate", ".prokron-adoption", ".venv", "node_modules",
    "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".artifacts", "artifacts", "build", "dist",
)
PATHS = (".", *(f":(exclude,glob)**/{name}/**" for name in GENERATED), ":(exclude)AGENTS.md", ":(exclude)CLAUDE.md")


def git(project: Path, *args: str, raw: bool = False) -> str:
    result = subprocess.run(["git", *args], cwd=project, capture_output=True, text=True, check=False)
    if result.returncode:
        raise ProkronError(result.stderr.strip() or "unable to inspect Git repository")
    return result.stdout if raw else result.stdout.strip()


def git_optional(project: Path, *args: str) -> str | None:
    result = subprocess.run(["git", *args], cwd=project, capture_output=True, text=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else None


def repository_root(project: Path) -> None:
    if Path(git(project, "rev-parse", "--show-toplevel")).resolve() != project.resolve():
        raise ProkronError("Run Prokron from the Git repository root")


def checkpoint_facts(project: Path) -> dict[str, str]:
    repository_root(project)
    head = git_optional(project, "rev-parse", "--verify", "HEAD") or ""
    digest = hashlib.sha256()
    digest.update(git(project, "ls-files", "--stage", "-z", "--", *PATHS, raw=True).encode())
    for args in (("diff", "--binary", "--no-ext-diff", "--no-textconv"),
                 ("diff", "--cached", "--binary", "--no-ext-diff", "--no-textconv")):
        digest.update(git(project, *args, "--", *PATHS, raw=True).encode())
    untracked = git(project, "ls-files", "--others", "--exclude-standard", "-z", "--", *PATHS, raw=True)
    for name in sorted(filter(None, untracked.split("\0"))):
        path = project / name
        digest.update(name.encode())
        if path.is_symlink():
            digest.update(os.readlink(path).encode())
        elif path.is_file():
            with path.open("rb") as source:
                digest.update(hashlib.file_digest(source, "sha256").digest())
    # Bootstrap installation must not invalidate the reviewed repository snapshot.
    # Custom instructions outside the managed block still participate in freshness.
    for name in ("AGENTS.md", "CLAUDE.md"):
        path = project / name
        if path.is_symlink():
            raise ProkronError(f"{name}: symlink bootstrap files are not supported")
        content = path.read_text(encoding="utf-8") if path.exists() else ""
        start, end = "<!-- project-prokron:start -->", "<!-- project-prokron:end -->"
        if (start in content) != (end in content) or content.count(start) > 1 or content.count(end) > 1:
            raise ProkronError(f"{name}: incomplete or duplicate managed Prokron block")
        if start in content:
            before, rest = content.split(start, 1)
            _, after = rest.split(end, 1)
            content = before.rstrip() + after.rstrip()
        digest.update(name.encode() + content.rstrip().encode())
    return {
        "head": head,
        "branch": git_optional(project, "symbolic-ref", "--short", "HEAD") or "(detached)",
        "worktree": digest.hexdigest(),
    }


def prepare(project: Path) -> dict[str, object]:
    snapshot = checkpoint_facts(project)
    names = git(project, "ls-files", "--cached", "--others", "--exclude-standard", "-z", raw=True).split("\0")
    names = [name for name in names if name and not any(part in GENERATED for part in Path(name).parts)]
    return {
        "repo_root": str(project.resolve()),
        "checkpoint": snapshot,
        "dirty": bool(git(project, "status", "--porcelain")),
        "recent_commits": (git(project, "log", "-5", "--format=%H %s").splitlines() if snapshot["head"] else []),
        "top_level_tree": sorted({Path(name).parts[0] for name in names}),
        "file_extensions": sorted({Path(name).suffix for name in names if Path(name).suffix}),
        "ignored_paths": git(project, "ls-files", "--others", "--ignored", "--exclude-standard", "--directory", "-z", raw=True).split("\0")[:-1],
        "generated_exclusions": list(GENERATED),
        "existing_prokron": (project / ".prokron").exists(),
    }


def require_fresh(project: Path, recorded: dict[str, str]) -> None:
    current = checkpoint_facts(project)
    if any(recorded[key] != current[key] for key in ("branch", "worktree")):
        raise ProkronError(
            f"STATE_STALE\ncheckpoint: {recorded.get('head') or '(unborn)'}\n"
            f"current_head: {current['head'] or '(unborn)'}\n"
            "Repository branch or working tree content changed. Run /prokron-sync."
        )
