# /prokron-work

Read `.prokron/README.md`, `STATE.md`, and `TASK_GRAPH.md`. Select the requested
task, or one ready task if none was named. If the requested work has no task yet,
create it before implementation without waiting for a Prokron command. Read that
task and its governing ADRs, then inspect only the specification and code needed
for the task.

Mark it `WIP`, record the owner and claim date, and set `INTENT.md` to that one
task before implementation. Keep intent at the exact execution point, especially
before a long-running step. When a material choice is made, accepted, or acted
on, append its ADR immediately and link affected tasks. As truth changes, update
the task, graph, state, and journal rather than postponing record keeping.
