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
--questions-json` and submit human answers through `prokron adopt --answer-json
'<json>'`; do not edit `.prokron-adoption/INTERVIEW.md` directly.
