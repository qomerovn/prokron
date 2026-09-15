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

## Install with one command

Run one of these from the root of the project that will use Prokron:

```sh
# New repository
gh api -H 'Accept: application/vnd.github.raw+json' 'repos/qomerovn/prokron/contents/install.sh?ref=main' | sh -s -- new

# Existing repository
gh api -H 'Accept: application/vnd.github.raw+json' 'repos/qomerovn/prokron/contents/install.sh?ref=main' | sh -s -- existing
```

The private repository requires an authenticated [GitHub CLI](https://cli.github.com/).
The installer adds the chronicle, workflows, generic agent instructions, and
Codex, Claude Code, and OpenCode adapters. It preserves an existing `.prokron/`
directory and existing project instructions, then prints the agent-chat command
that starts the selected mode.

## Models and agent hosts

GLM, MiniMax, Mistral, and Grok are models or model providers. Prokron configures
the **agent host** running the model, so its project memory stays the same when
the model changes.

- **OpenCode:** the installer adds `.opencode/commands/` and `AGENTS.md`.
  OpenCode supports multiple providers through `/connect` and `/models`; after
  selecting any model, run `/prokron-init new` or `/prokron-init existing`.
- **Any host that loads [`AGENTS.md`](https://agents.md/):** the Prokron rules load with the project.
  Ask the agent to follow the relevant file in `commands/`.
- **Any other capable coding agent:** start with: `Read AGENTS.md, then follow
  commands/prokron-init.md in existing mode.` Change `existing` to `new` when
  starting from a product specification.

Prokron does not store provider credentials or pin a model. See OpenCode's
[provider setup](https://opencode.ai/docs/providers),
[project instructions](https://opencode.ai/docs/rules/), and
[custom commands](https://opencode.ai/docs/commands/).

## Start in one of two modes

### New repository

Run `/prokron-init new` in Claude Code or OpenCode, or `$prokron init new` in
Codex. The agent works with the developer to turn the product specification into
the first tasks, dependency graph, decisions, and project state.

### Existing repository

Run `/prokron-init existing` in Claude Code or OpenCode, or `$prokron init
existing` in Codex. The chronicle starts empty and records work from that
session onward. It does not invent historical tasks or decisions from the
repository.

## Work with the chronicle

| Purpose | Claude Code / OpenCode | Codex |
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
