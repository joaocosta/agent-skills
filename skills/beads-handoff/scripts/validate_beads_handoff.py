#!/usr/bin/env python3
"""Validate a live Beads handoff exported by `bd show <ids> --json`."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import TypedDict, cast

TASK_HEADINGS = [
    "Outcome and current state",
    "Required reading and anchors",
    "Scope and owned components",
    "Non-goals",
    "Settled decisions and constraints",
    "Dependencies and prerequisites",
    "Implementation direction",
    "Acceptance criteria",
    "Validation",
    "Risks and assumptions",
    "Completion check",
    "Completion boundary and done condition",
    "Next-task handoff",
]
EPIC_HEADINGS = [
    "Outcome and current state",
    "Success criteria",
    "Required reading and anchors",
    "Scope and owned components",
    "Non-goals",
    "Settled decisions and constraints",
    "Work breakdown and dependency DAG",
    "Design coverage",
    "Final validation",
    "Risks and assumptions",
    "Completion boundary and done condition",
    "Execution protocol",
]
HEADING_RE = re.compile(r"^## (.+?)\s*$", re.MULTILINE)
AC_RE = re.compile(r"(?<![A-Za-z0-9])AC[- ]?(\d+)(?![A-Za-z0-9])", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"\{\{.*?\}\}", re.DOTALL)
BLOCKED_BY_RE = re.compile(r"^Blocked by:\s*(.+?)\s*$", re.MULTILINE | re.IGNORECASE)


class Dependency(TypedDict, total=False):
    id: str
    dependency_type: str


class Issue(TypedDict, total=False):
    id: str
    title: str
    description: str
    acceptance_criteria: str
    status: str
    issue_type: str
    parent: str
    spec_id: str
    dependencies: list[Dependency]


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def load_issues(path: Path) -> list[Issue]:
    payload: object = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        envelope = cast("dict[str, object]", payload)
        payload = envelope.get("data", envelope.get("issues"))
    if not isinstance(payload, list):
        raise ValueError("show JSON must be a list of issues or an object with a data/issues list")
    items = cast("list[object]", payload)
    if not all(isinstance(item, dict) for item in items):
        raise ValueError("every item in show JSON must be an issue object")
    return cast("list[Issue]", items)


def ac_ids(text: str) -> set[str]:
    return {f"AC{int(match)}" for match in AC_RE.findall(text)}


def validate_headings(issue: Issue, expected: list[str], errors: list[str]) -> None:
    issue_id = issue.get("id", "<unknown>")
    description = issue.get("description") or ""
    headings = HEADING_RE.findall(description)
    if headings != expected:
        fail(errors, f"{issue_id}: required headings differ or are out of order; got {headings!r}")
    if PLACEHOLDER_RE.search(description):
        fail(errors, f"{issue_id}: unresolved template placeholder")
    if not (issue.get("acceptance_criteria") or "").strip():
        fail(errors, f"{issue_id}: acceptance_criteria is empty")


def declared_blockers(issue: Issue, errors: list[str]) -> set[str]:
    issue_id = issue.get("id", "<unknown>")
    description = issue.get("description") or ""
    matches = BLOCKED_BY_RE.findall(description)
    if len(matches) != 1:
        fail(errors, f"{issue_id}: Dependencies section must contain exactly one `Blocked by:` line")
        return set()
    value = matches[0].strip()
    if value.lower() == "none":
        return set()
    blockers = {item.strip() for item in value.split(",") if item.strip()}
    if not blockers:
        fail(errors, f"{issue_id}: `Blocked by:` must contain IDs or None")
    return blockers


def live_blockers(issue: Issue) -> set[str]:
    blockers: set[str] = set()
    for dependency in issue.get("dependencies") or []:
        dependency_id = dependency.get("id")
        if dependency.get("dependency_type", "blocks") == "blocks" and dependency_id:
            blockers.add(dependency_id)
    return blockers


def source_matches(spec_id: str, source: Path) -> bool:
    normalized_spec = spec_id.replace("\\", "/")
    while normalized_spec.startswith("./"):
        normalized_spec = normalized_spec[2:]
    normalized_source = str(source.resolve()).replace("\\", "/")
    if normalized_spec.startswith("/"):
        return normalized_source == normalized_spec
    return bool(normalized_spec) and normalized_source.endswith("/" + normalized_spec)


def internal_blocking_graph(tasks: list[Issue]) -> dict[str, set[str]]:
    ids = {str(task.get("id")) for task in tasks}
    graph: dict[str, set[str]] = {issue_id: set() for issue_id in ids}
    for task in tasks:
        issue_id = str(task.get("id"))
        for dependency in task.get("dependencies") or []:
            target = str(dependency.get("id"))
            dep_type = dependency.get("dependency_type", "blocks")
            if target in ids and dep_type == "blocks":
                graph[issue_id].add(target)
    return graph


def cycle_in(graph: dict[str, set[str]]) -> list[str] | None:
    visiting: set[str] = set()
    visited: set[str] = set()
    path: list[str] = []

    def visit(node: str) -> list[str] | None:
        if node in visiting:
            start = path.index(node)
            return [*path[start:], node]
        if node in visited:
            return None
        visiting.add(node)
        path.append(node)
        for dependency in graph[node]:
            found = visit(dependency)
            if found:
                return found
        path.pop()
        visiting.remove(node)
        visited.add(node)
        return None

    for node in graph:
        found = visit(node)
        if found:
            return found
    return None


def validate(path: Path, source: Path) -> list[str]:
    errors: list[str] = []
    issues = load_issues(path)
    ids = [str(issue.get("id", "")) for issue in issues]
    if any(not issue_id for issue_id in ids) or len(ids) != len(set(ids)):
        fail(errors, "issues must have unique, nonempty IDs")

    epics = [issue for issue in issues if issue.get("issue_type") == "epic"]
    tasks = [issue for issue in issues if issue.get("issue_type") == "task"]
    unexpected = [issue.get("id") for issue in issues if issue.get("issue_type") not in {"epic", "task"}]
    if unexpected:
        fail(errors, f"unexpected issue types: {unexpected}")

    for issue in issues:
        if issue.get("status") != "open":
            fail(errors, f"{issue.get('id')}: initial status must be open, got {issue.get('status')!r}")

    if not tasks:
        fail(errors, "handoff requires at least one executable task")
    if len(epics) > 1:
        fail(errors, "handoff permits at most one coordination epic")
    if epics:
        if len(tasks) < 2:
            fail(errors, "coordination epic requires at least two executable tasks")
        epic_id = epics[0].get("id")
        epic_description = epics[0].get("description") or ""
        for task in tasks:
            if task.get("parent") != epic_id:
                fail(errors, f"{task.get('id')}: parent is not coordination epic {epic_id}")
            if str(task.get("id")) not in epic_description:
                fail(errors, f"{epic_id}: final breakdown does not reference child {task.get('id')}")
        validate_headings(epics[0], EPIC_HEADINGS, errors)

    for task in tasks:
        validate_headings(task, TASK_HEADINGS, errors)
        declared = declared_blockers(task, errors)
        live = live_blockers(task)
        if declared != live:
            fail(
                errors,
                f"{task.get('id')}: declared blockers {sorted(declared)} "
                f"do not match live blocking edges {sorted(live)}",
            )

    for issue in issues:
        spec_id = str(issue.get("spec_id") or "")
        if not source_matches(spec_id, source):
            fail(errors, f"{issue.get('id')}: spec_id {spec_id!r} does not identify {source}")

    source_text = source.read_text(encoding="utf-8")
    required_acs = ac_ids(source_text)
    if not required_acs:
        fail(errors, "source design contains no acceptance IDs matching AC1 or AC-1")
    executable_text = "\n".join(
        (task.get("description") or "") + "\n" + (task.get("acceptance_criteria") or "") for task in tasks
    )
    missing = sorted(required_acs - ac_ids(executable_text), key=lambda value: int(value[2:]))
    if missing:
        fail(errors, f"acceptance IDs missing from executable tasks: {', '.join(missing)}")

    cycle = cycle_in(internal_blocking_graph(tasks))
    if cycle:
        fail(errors, "internal blocking cycle: " + " -> ".join(cycle))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("show_json", type=Path)
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()

    try:
        errors = validate(args.show_json, args.source)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Validated Beads handoff from {args.source}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
