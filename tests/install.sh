#!/bin/sh
set -eu

root=$(CDPATH= cd "$(dirname "$0")/.." && pwd)
fixture=$(mktemp -d "${TMPDIR:-/tmp}/prokron-install.XXXXXX")
trap 'rm -rf "$fixture"' EXIT HUP INT TERM

printf '# Keep agent rules\n' > "$fixture/AGENTS.md"
printf '# Keep Claude rules\n' > "$fixture/CLAUDE.md"
"$root/install.sh" existing "$fixture" > "$fixture/output"

for file in README TASKS TASK_GRAPH DECISIONS STATE INTENT JOURNAL; do
  test -f "$fixture/.prokron/$file.md"
done
test -f "$fixture/.agents/skills/prokron/SKILL.md"
for command in init work decide checkpoint resume; do
  test -f "$fixture/commands/prokron-$command.md"
  test -f "$fixture/.claude/commands/prokron-$command.md"
  test -f "$fixture/.opencode/commands/prokron-$command.md"
done
grep -Fq '# Keep agent rules' "$fixture/AGENTS.md"
grep -Fq '# Keep Claude rules' "$fixture/CLAUDE.md"
grep -Fq 'do not wait for a Prokron command' "$fixture/AGENTS.md"
grep -Fq 'context, token, time, session, rate, or quota limit' "$fixture/AGENTS.md"
grep -Fq 'Record every new work request as a task before implementation' \
  "$fixture/.prokron/README.md"
grep -Fq 'Append an ADR as soon as a material choice is made' \
  "$fixture/.prokron/README.md"
grep -Fq '$prokron init existing' "$fixture/output"
grep -Fq '/prokron-init existing' "$fixture/output"
grep -Fq 'commands/prokron-init.md in existing mode' "$fixture/output"

printf '\nKEEP\n' >> "$fixture/.prokron/TASKS.md"
"$root/install.sh" existing "$fixture" >/dev/null
grep -Fq 'KEEP' "$fixture/.prokron/TASKS.md"
test "$(grep -Fc '<!-- project-prokron:start -->' "$fixture/AGENTS.md")" -eq 1
test "$(grep -Fxc '@AGENTS.md' "$fixture/CLAUDE.md")" -eq 1

"$root/install.sh" new "$fixture" > "$fixture/output-new"
grep -Fq '$prokron init new' "$fixture/output-new"

if "$root/install.sh" invalid "$fixture" >/dev/null 2>&1; then
  exit 1
fi

echo 'installer smoke: pass'
