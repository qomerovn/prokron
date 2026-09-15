# Project Prokron — generic adapter

Any agent that can read repository files and invoke a shell can use Prokron:

```text
prokron status
prokron next
prokron context <task>
prokron start <task> --owner <owner>
prokron checkpoint --did ... --validation ... --left-mid-air ... --next ...
```

The CLI is the only executable interface. `.prokron/` remains authoritative.

During adoption, retrieve structured questions with `prokron adopt
--questions-json`, synthesize one concise current-state review, ask the human
conversationally, and translate the response into one or more `prokron adopt
--answer-json '<json>'` calls. Core validates and persists every answer; do not
edit `.prokron-adoption/INTERVIEW.md` directly.
