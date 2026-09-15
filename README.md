# Prokron

**Project memory for people and coding agents.**

Prokron keeps project context in a small Markdown chronicle. A new
person or agent can see what matters, why it matters, and what to do next before
reading implementation code.

`TASK_GRAPH.md` shows the path forward. `DECISIONS.md` preserves the reasoning
that shaped it. Four supporting records make each handoff complete:

| Record | Answers |
|---|---|
| `TASKS.md` | What work exists, and when is it done? |
| `TASK_GRAPH.md` | What is in flight, ready, or blocked? |
| `DECISIONS.md` | Why does the project work this way? |
| `STATE.md` | Where is the project now? |
| `INTENT.md` | What single task is active? |
| `JOURNAL.md` | What happened, and what happens next? |

That is the product: six Markdown files plus instructions for the agent already
doing the work. There is no runtime or service to operate.

## Add Prokron to a project

1. Copy [`templates/.prokron`](templates/.prokron) to the project root as
   `.prokron/`.
2. Copy [`commands`](commands) to the project root.
3. Merge the Prokron rules from [`AGENTS.md`](AGENTS.md) into the project's
   agent instructions.
4. Add the adapter for each agent you use:
   - **Codex:** copy [`.agents/skills/prokron`](.agents/skills/prokron).
   - **Claude Code:** copy [`.claude/commands`](.claude/commands) and add
     `@AGENTS.md` to the project's `CLAUDE.md`.

Merge instruction files instead of replacing project-specific guidance.

## Start in one of two modes

### New repository

Run `/prokron-init new` in Claude Code or `$prokron init new` in Codex. The
agent works with the developer to turn the product specification into the first
tasks, dependency graph, decisions, and project state.

### Existing repository

Run `/prokron-init existing` in Claude Code or `$prokron init existing` in
Codex. The chronicle starts empty and records work from that session onward. It
does not invent historical tasks or decisions from the repository.

## Work with the chronicle

| Purpose | Claude Code | Codex |
|---|---|---|
| Start the chronicle | `/prokron-init [mode]` | `$prokron init [mode]` |
| Start or continue one task | `/prokron-work [task]` | `$prokron work [task]` |
| Record a decision | `/prokron-decide` | `$prokron decide` |
| Prepare a handoff | `/prokron-checkpoint` | `$prokron checkpoint` |
| Continue from project memory | `/prokron-resume` | `$prokron resume` |

Agents update the chronicle as project truth changes. Decisions and journal
entries are appended; changed decisions get a new ADR that supersedes the old
one. `INTENT.md` holds at most one active task.

The agent checkpoints before handoff, interruption, context compaction, or a
host warning that the five-hour or seven-day usage limit is near. If the host
does not expose quota status, it checkpoints at meaningful milestones and
before ending the session.

Read the [specification](docs/SPEC.md) for the complete working agreement and
the [chronicle guide](.prokron/README.md) for the read order.

## License

Apache-2.0. See [LICENSE](LICENSE), [NOTICE](NOTICE), and
[TRADEMARKS.md](TRADEMARKS.md).
