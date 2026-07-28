#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
RALPH_CMD="${RALPH_CMD:-pi -ne -ns -p}"
MAX_ITERATIONS="${MAX_ITERATIONS:-40}"
COMPLETION_MARKER="$SCRIPT_DIR/ralph-complete"
README_PATH="$SCRIPT_DIR/README.md"
PROGRESS_PATH="$SCRIPT_DIR/progress.md"
TASKS_DIR="$SCRIPT_DIR/tasks"
LOG_DIR="$SCRIPT_DIR/logs"
INITIATIVE_NAME="$(basename "$SCRIPT_DIR")"
RALPH_SESSION_PREFIX="${RALPH_SESSION_PREFIX:-ralph:${INITIATIVE_NAME}}"

if [[ ! "$MAX_ITERATIONS" =~ ^[1-9][0-9]*$ ]]; then
  printf 'MAX_ITERATIONS must be a positive integer, got: %s\n' "$MAX_ITERATIONS" >&2
  exit 2
fi

if [[ ! -f "$README_PATH" ]]; then
  printf 'Missing Ralph prompt: %s\n' "$README_PATH" >&2
  exit 2
fi

if [[ ! -f "$PROGRESS_PATH" ]]; then
  printf 'Missing Ralph progress: %s\n' "$PROGRESS_PATH" >&2
  exit 2
fi

next_task_name() {
  local next_task_line
  local task_name

  next_task_line="$(grep -m1 -E '^\*\*Next task:\*\*' "$PROGRESS_PATH" || true)"
  if [[ "$next_task_line" =~ (task-[0-9]{2}-[a-z0-9]+(-[a-z0-9]+)*) ]]; then
    task_name="${BASH_REMATCH[1]}"
  else
    printf 'Cannot determine the next task from %s\n' "$PROGRESS_PATH" >&2
    return 2
  fi

  if [[ ! -f "$TASKS_DIR/$task_name.md" ]]; then
    printf 'Next task file does not exist: %s\n' "$TASKS_DIR/$task_name.md" >&2
    return 2
  fi

  printf '%s\n' "$task_name"
}

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
  iteration_id="$(printf '%03d' "$iteration")"
  task_name="$(next_task_name)"
  log_path="$LOG_DIR/iteration-${iteration_id}.log"
  session_name="${RALPH_SESSION_PREFIX}:${task_name}"

  set +e
  "${ralph_command[@]}" -n "$session_name" "$(cat "$README_PATH")" 2>&1 | tee "$log_path"
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
