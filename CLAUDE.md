## Skill routing

When the user's request matches an available skill, invoke it via the Skill tool. When in doubt, invoke the skill.

Key routing rules:
- Product ideas/brainstorming → invoke /office-hours
- Strategy/scope → invoke /plan-ceo-review
- Architecture → invoke /plan-eng-review
- Design system/plan review → invoke /design-consultation or /plan-design-review
- Full review pipeline → invoke /autoplan
- Bugs/errors → invoke /investigate
- QA/testing site behavior → invoke /qa or /qa-only
- Code review/diff check → invoke /review
- Visual polish → invoke /design-review
- Ship/deploy/PR → invoke /ship or /land-and-deploy
- Save progress → invoke /context-save
- Resume context → invoke /context-restore
- Author a backlog-ready spec/issue → invoke /spec

<!-- project-prokron:start -->

## Project Prokron

This repository uses `.prokron/` as persistent project coordination state.

Before implementation:

1. Read `.prokron/README.md`.
2. Inspect `.prokron/TASK_GRAPH.md`.
3. Locate the relevant task in `.prokron/TASKS.md`.
4. Read `.prokron/INTENTS.md` if work is active.
5. Read only the governing specification, decisions, and code required for that task.

Do not reconstruct current project truth from chat history.

<!-- project-prokron:end -->
