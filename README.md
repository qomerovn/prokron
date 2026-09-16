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
Codex, Claude Code, and OpenCode adapters. It preserves existing `.prokron/`
records and project instructions, restores missing files, then prints the
agent-chat command to initialize a fresh chronicle or resume an existing one.

From a downloaded or cloned Prokron checkout, installation also works offline:

```sh
sh ./install.sh existing /path/to/your/project
```

Once this repository is public, anonymous installation will be available with:

```sh
curl -fsSL https://raw.githubusercontent.com/qomerovn/prokron/main/install.sh | sh -s -- existing
```

Use `new` instead of `existing` for a new project. Anonymous delivery cannot be
verified while the repository is private.

### Updating an installation

Reinstalling adds missing files; it **does not upgrade existing guidance**. It
prints a reminder when guidance is retained. From a current Prokron checkout,
review and merge changes to `commands/`, `.claude/commands/`,
`.opencode/commands/`, `.agents/skills/prokron/SKILL.md`, and
`templates/.prokron/README.md` (installed as `.prokron/README.md`). Merge the
Prokron block in `AGENTS.md`, keeping surrounding project rules.

Keep customizations and all six chronicle records. Do not copy empty templates
over project history. Repeated initialization also preserves history and resumes.

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

Installed rules instruct agents to maintain the chronicle automatically, without
requiring slash commands. Every new work request becomes a
task before implementation. Every material choice becomes an ADR as soon as it
is made or acted on; changed decisions get a new ADR that supersedes the old
one. `INTENT.md` always identifies the single active task and exact work point.

The agent checkpoints before handoff, interruption, compaction, or any known or
estimated context, token, time, session, rate, or quota limit. If the host does
not expose a meter, it checkpoints after meaningful milestones, before
long-running work, and before ending the session.

These are instructions the working agent must follow, not a background monitor.
Prokron cannot detect hidden five-hour or seven-day quota counters or guarantee
a final write after an abrupt cutoff. Milestone checkpoints limit how much work
can be missing from the handoff.

Run `sh tests/install.sh` in this checkout to check installation and preservation.
This does not test model compliance or real quota warnings. Use the
[handoff pilot](docs/SPEC.md#handoff-pilot) to verify those workflows with your host.

Read the [specification](docs/SPEC.md) for the complete working agreement and
the [chronicle guide](.prokron/README.md) for the read order.

## License

Apache-2.0. See [LICENSE](LICENSE), [NOTICE](NOTICE), and
[TRADEMARKS.md](TRADEMARKS.md).
