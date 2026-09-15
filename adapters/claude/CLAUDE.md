# Project Prokron — Claude adapter

Before substantial work, run `prokron status` and `prokron context`.
Start eligible work with `prokron start <task> --owner <owner>` and run
`prokron checkpoint` before stopping or changing models. Treat `.prokron/`
as project authority and never infer current truth from conversation history.

For existing-project adoption, use `prokron adopt --questions-json` to retrieve
unresolved items and `prokron adopt --answer-json '<json>'` to submit human
answers; never edit `.prokron-adoption/INTERVIEW.md` directly.
