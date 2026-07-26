#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
RALPH_CMD="${RALPH_CMD:-pi -ns -p}"
MAX_ITERATIONS="${MAX_ITERATIONS:-40}"
COMPLETION_MARKER="$SCRIPT_DIR/ralph-complete"
README_PATH="$SCRIPT_DIR/README.md"
LOG_DIR="$SCRIPT_DIR/logs"

if [[ ! "$MAX_ITERATIONS" =~ ^[1-9][0-9]*$ ]]; then
  printf 'MAX_ITERATIONS must be a positive integer, got: %s\n' "$MAX_ITERATIONS" >&2
  exit 2
fi

if [[ ! -f "$README_PATH" ]]; then
  printf 'Missing Ralph prompt: %s\n' "$README_PATH" >&2
  exit 2
fi

# RALPH_CMD is intentionally split into a command and simple arguments.
# For complex shell syntax, point RALPH_CMD at a wrapper executable instead.
read -r -a ralph_command <<<"$RALPH_CMD"
if ((${#ralph_command[@]} == 0)); then
  printf 'RALPH_CMD must not be empty\n' >&2
  exit 2
fi

mkdir -p "$LOG_DIR"

if [[ -f "$COMPLETION_MARKER" ]]; then
  printf 'Ralph work is already complete: %s\n' "$COMPLETION_MARKER"
  exit 0
fi

for ((iteration = 1; iteration <= MAX_ITERATIONS; iteration++)); do
  printf '==> Ralph iteration %d/%d\n' "$iteration" "$MAX_ITERATIONS"
  log_path="$LOG_DIR/iteration-$(printf '%03d' "$iteration").log"

  set +e
  "${ralph_command[@]}" "$(cat "$README_PATH")" 2>&1 | tee "$log_path"
  agent_status=${PIPESTATUS[0]}
  set -e

  if ((agent_status != 0)); then
    printf 'Agent command failed with status %d; see %s\n' "$agent_status" "$log_path" >&2
    exit "$agent_status"
  fi

  if [[ -f "$COMPLETION_MARKER" ]]; then
    printf 'Ralph work completed after %d iteration(s).\n' "$iteration"
    exit 0
  fi

done

printf 'Reached MAX_ITERATIONS=%s without %s\n' "$MAX_ITERATIONS" "$COMPLETION_MARKER" >&2
exit 1
