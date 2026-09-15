# Prokron

Prokron is a way for developers and coding agents to keep a project understandable
between working sessions. It is Markdown and agent instructions, with no runtime.

The project chronicle lives in `.prokron/`:

| File | Answers |
|---|---|
| `TASKS.md` | What work exists? |
| `TASK_GRAPH.md` | What can happen next? |
| `DECISIONS.md` | Why is the project shaped this way? |
| `STATE.md` | Where is the project now? |
| `INTENT.md` | What single task is being worked on? |
| `JOURNAL.md` | What happened during each session? |

Together, the task graph and decision lineage are the project’s execution and
reasoning spine. A new person or agent should understand the project from the
chronicle before reading implementation code.

## Two ways to start

1. **New repository:** the agent works with the developer to turn the product
   specification into tasks and a task graph. Decisions, state, intent, and the
   journal grow as work proceeds.
2. **Existing repository:** begin with an empty chronicle. Do not reconstruct old
   history. Record project truth and decisions from the first Prokron session onward.

Copy [`templates/.prokron`](templates/.prokron) and [`commands`](commands) into
the project, then merge the relevant agent configuration:

- [`AGENTS.md`](AGENTS.md) and [`.agents/skills/prokron`](.agents/skills/prokron)
  provide the rules and `$prokron` workflow for Codex.
- [`CLAUDE.md`](CLAUDE.md) and [`.claude/commands`](.claude/commands) provide the
  same rules and slash commands for Claude Code.

## Workflows

| Workflow | Purpose |
|---|---|
| `/prokron-init` | Start the chronicle in a new or existing repository |
| `/prokron-work` | Select or continue one task |
| `/prokron-decide` | Append or supersede an ADR |
| `/prokron-checkpoint` | Prepare a clean handoff |
| `/prokron-resume` | Continue from the chronicle alone |

The agent updates the chronicle during work and checkpoints automatically when
its host reports an approaching session, context, five-hour, or seven-day usage
limit. Hosts that do not expose quota telemetry still checkpoint at meaningful
milestones and before the session ends.

See the [product specification](docs/SPEC.md) and
[`.prokron/README.md`](.prokron/README.md) for the complete protocol.

## License

Apache-2.0. See [LICENSE](LICENSE), [NOTICE](NOTICE), and [TRADEMARKS.md](TRADEMARKS.md).
