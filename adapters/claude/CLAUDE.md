# Project Prokron — Claude adapter

Before substantial work, run `prokron status` and `prokron context`.
Start eligible work with `prokron start <task> --owner <owner>` and run
`prokron checkpoint` before stopping or changing models. Treat `.prokron/`
as project authority and never infer current truth from conversation history.

For existing-project adoption, use `prokron adopt --questions-json` to retrieve
unresolved items, synthesize one concise current-state review, ask the human
conversationally, then translate the response into one or more `prokron adopt
--answer-json '<json>'` calls. Core validates and persists every answer; never
edit `.prokron-adoption/INTERVIEW.md` directly.
