#!/bin/sh
set -eu

mode=${1:-}
target=${2:-.}

case "$mode" in
  new|existing) ;;
  *)
    echo "Usage: install.sh new|existing [target-directory]" >&2
    exit 2
    ;;
esac

if [ ! -d "$target" ]; then
  echo "Target directory does not exist: $target" >&2
  exit 2
fi

target=$(CDPATH= cd "$target" && pwd)
source_dir=
temp_dir=

for file in AGENTS.md CLAUDE.md; do
  if [ -e "$target/$file" ] && [ ! -f "$target/$file" ]; then
    echo "Cannot install: $target/$file is not a regular file" >&2
    exit 1
  fi
done

case $0 in
  */*)
    candidate=$(CDPATH= cd "$(dirname "$0")" && pwd)
    if [ -f "$candidate/templates/.prokron/README.md" ]; then
      source_dir=$candidate
    fi
    ;;
esac

cleanup() {
  if [ -n "$temp_dir" ]; then
    rm -rf "$temp_dir"
  fi
}
trap cleanup EXIT HUP INT TERM

if [ -z "$source_dir" ]; then
  temp_dir=$(mktemp -d "${TMPDIR:-/tmp}/prokron.XXXXXX")
  command -v tar >/dev/null 2>&1 || { echo "tar is required" >&2; exit 1; }
  if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
    gh api repos/qomerovn/prokron/tarball/main > "$temp_dir/prokron.tar.gz"
  else
    command -v curl >/dev/null 2>&1 || { echo "curl is required" >&2; exit 1; }
    curl -fsSL "https://github.com/qomerovn/prokron/archive/refs/heads/main.tar.gz" \
      -o "$temp_dir/prokron.tar.gz"
  fi
  mkdir "$temp_dir/source"
  tar -xzf "$temp_dir/prokron.tar.gz" -C "$temp_dir/source"
  set -- "$temp_dir/source"/*
  source_dir=$1
fi

if [ ! -f "$source_dir/templates/.prokron/README.md" ]; then
  echo "Downloaded Prokron source is incomplete" >&2
  exit 1
fi

copy_new() {
  source_file=$1
  target_file=$2
  if [ ! -e "$target_file" ]; then
    mkdir -p "$(dirname "$target_file")"
    cp "$source_file" "$target_file"
  fi
}

if [ -e "$target/.prokron" ] && [ ! -d "$target/.prokron" ]; then
  echo "Cannot install: $target/.prokron is not a directory" >&2
  exit 1
fi
if [ ! -d "$target/.prokron" ]; then
  cp -R "$source_dir/templates/.prokron" "$target/.prokron"
fi

for command in init work decide checkpoint resume; do
  copy_new "$source_dir/commands/prokron-$command.md" \
    "$target/commands/prokron-$command.md"
  copy_new "$source_dir/.claude/commands/prokron-$command.md" \
    "$target/.claude/commands/prokron-$command.md"
done
copy_new "$source_dir/.agents/skills/prokron/SKILL.md" \
  "$target/.agents/skills/prokron/SKILL.md"

if [ ! -f "$target/AGENTS.md" ]; then
  cp "$source_dir/AGENTS.md" "$target/AGENTS.md"
elif ! grep -Fq '<!-- project-prokron:start -->' "$target/AGENTS.md"; then
  printf '\n' >> "$target/AGENTS.md"
  cat "$source_dir/AGENTS.md" >> "$target/AGENTS.md"
fi

if [ ! -f "$target/CLAUDE.md" ]; then
  printf '@AGENTS.md\n' > "$target/CLAUDE.md"
elif ! grep -Fxq '@AGENTS.md' "$target/CLAUDE.md"; then
  printf '\n@AGENTS.md\n' >> "$target/CLAUDE.md"
fi

printf 'Prokron installed in %s\n\n' "$target"
printf 'Start in your agent chat:\n'
printf '  Codex:       $prokron init %s\n' "$mode"
printf '  Claude Code: /prokron-init %s\n' "$mode"
