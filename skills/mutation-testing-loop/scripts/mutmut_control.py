#!/usr/bin/env python3
"""Run mutmut quietly and produce compact, deterministic survivor artifacts."""

from __future__ import annotations

import argparse
import ast
import difflib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

MUTANT_SUFFIX = re.compile(r"__mutmut_\d+$")
REPORT_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def mutmut_command(value: str) -> str:
    path = shutil.which(value) if "/" not in value else value
    if not path or not Path(path).is_file():
        raise SystemExit(f"mutmut executable not found: {value}")
    return path


def run_captured(command: list[str], log_path: Path) -> int:
    with tempfile.NamedTemporaryFile(prefix="mutmut-", delete=False) as stream:
        temporary_path = Path(stream.name)
        result = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, check=False)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(temporary_path, log_path)
    return result.returncode


def parse_results(mutmut: str) -> list[dict[str, str]]:
    result = subprocess.run(
        [mutmut, "results", "--all", "true"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise SystemExit(result.stderr or result.stdout or "mutmut results failed")
    records: list[dict[str, str]] = []
    for line in result.stdout.splitlines():
        stripped = line.strip()
        if ": " not in stripped:
            continue
        name, status = stripped.rsplit(": ", 1)
        records.append({"name": name, "status": status, "symbol": MUTANT_SUFFIX.sub("", name)})
    return records


def changed_lines(original: ast.AST, mutant: ast.AST) -> list[str]:
    before = ast.unparse(original).splitlines()[1:]
    after = ast.unparse(mutant).splitlines()[1:]
    return [line for line in difflib.ndiff(before, after) if line[:2] in {"- ", "+ "}]


def generated_diffs(mutants_dir: Path) -> dict[str, dict[str, object]]:
    found: dict[str, dict[str, object]] = {}
    for metadata_path in sorted(mutants_dir.rglob("*.py.meta")):
        source_path = Path(str(metadata_path)[: -len(".meta")])
        try:
            tree = ast.parse(source_path.read_text())
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue
        functions = {
            node.name: node
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        metadata = json.loads(metadata_path.read_text())
        for full_name in metadata.get("exit_code_by_key", {}):
            short_name = full_name.rsplit(".", 1)[-1]
            mutant = functions.get(short_name)
            original_name = MUTANT_SUFFIX.sub("__mutmut_orig", short_name)
            original = functions.get(original_name)
            if mutant is None or original is None:
                continue
            found[full_name] = {
                "generated_file": str(source_path),
                "changes": changed_lines(original, mutant),
            }
    return found


def report_stem(name: str | None) -> str:
    if name is None:
        return "survivors"
    if not REPORT_NAME.fullmatch(name):
        raise SystemExit("report name must contain only letters, numbers, '.', '_', or '-'")
    return f"survivors-{name}"


def report_path(mutants_dir: Path, name: str | None, suffix: str) -> Path:
    return mutants_dir / f"{report_stem(name)}.{suffix}"


def write_reports(
    mutmut: str, mutants_dir: Path, report_name: str | None = None
) -> tuple[list[dict[str, object]], Counter[str]]:
    records = parse_results(mutmut)
    statuses = Counter(record["status"] for record in records)
    diffs = generated_diffs(mutants_dir)
    survivors: list[dict[str, object]] = []
    for record in records:
        if record["status"] != "survived":
            continue
        survivors.append({**record, **diffs.get(record["name"], {"changes": []})})

    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for survivor in survivors:
        grouped[str(survivor["symbol"])].append(survivor)

    payload = {
        "status_counts": dict(sorted(statuses.items())),
        "total": len(records),
        "survivor_groups": [
            {
                "symbol": symbol,
                "count": len(items),
                "mutants": items,
            }
            for symbol, items in sorted(grouped.items(), key=lambda pair: (-len(pair[1]), pair[0]))
        ],
    }
    json_path = report_path(mutants_dir, report_name, "json")
    json_path.write_text(json.dumps(payload, indent=2) + "\n")

    markdown = ["# Surviving mutants", "", "## Status summary", ""]
    markdown.extend(f"- {status}: {count}" for status, count in sorted(statuses.items()))
    markdown.extend(["", "## Groups", ""])
    for group in payload["survivor_groups"]:
        markdown.append(f"### {group['symbol']} ({group['count']})")
        markdown.append("")
        fingerprints = Counter(
            " → ".join(str(change).strip() for change in mutant.get("changes", []))
            or "diff unavailable; inspect this group with mutmut show if selected"
            for mutant in group["mutants"]
        )
        for fingerprint, count in fingerprints.most_common():
            if len(fingerprint) > 300:
                fingerprint = fingerprint[:297] + "..."
            markdown.append(f"- {count}× `{fingerprint}`")
        markdown.append("")
    report_path(mutants_dir, report_name, "md").write_text("\n".join(markdown))
    return survivors, statuses


def print_summary(survivors: list[dict[str, object]], statuses: Counter[str]) -> None:
    total = sum(statuses.values())
    counts = [f"total={total}", *[f"{key}={value}" for key, value in sorted(statuses.items())]]
    print("Mutation status:", ", ".join(counts))
    groups = Counter(str(item["symbol"]) for item in survivors)
    print(f"Survivor groups: {len(groups)}")
    for symbol, count in groups.most_common():
        print(f"{count:4}  {symbol}")


def command_run(args: argparse.Namespace) -> int:
    mutmut = mutmut_command(args.mutmut)
    stem = report_stem(args.report_name)
    mutants_dir = Path(args.mutants_dir)
    if args.fresh and mutants_dir.exists():
        if mutants_dir.resolve() == Path.cwd().resolve():
            raise SystemExit("refusing to remove the working directory")
        shutil.rmtree(mutants_dir)
    default_log = f"mutmut-{args.report_name}-run.log" if args.report_name else "mutmut-run.log"
    log_path = Path(args.log) if args.log else mutants_dir / default_log
    return_code = run_captured([mutmut, "run"], log_path)
    if not mutants_dir.is_dir():
        raise SystemExit(f"mutmut did not create {mutants_dir}; inspect {log_path}")
    survivors, statuses = write_reports(mutmut, mutants_dir, args.report_name)
    details_path = mutants_dir / f"{stem}.md"
    print_summary(survivors, statuses)
    print(f"Full output: {log_path}")
    print(f"Survivor details: {details_path}")
    return return_code


def command_report(args: argparse.Namespace) -> int:
    mutmut = mutmut_command(args.mutmut)
    survivors, statuses = write_reports(mutmut, Path(args.mutants_dir), args.report_name)
    print_summary(survivors, statuses)
    return 0


def command_rerun(args: argparse.Namespace) -> int:
    mutmut = mutmut_command(args.mutmut)
    mutants_dir = Path(args.mutants_dir)
    source_report = report_path(mutants_dir, args.report_name, "json")
    if not source_report.is_file():
        raise SystemExit(f"missing {source_report}; run the report command first")
    payload = json.loads(source_report.read_text())
    names = [
        mutant["name"]
        for group in payload["survivor_groups"]
        if group["symbol"] in args.symbol
        for mutant in group["mutants"]
    ]
    missing = sorted(set(args.symbol) - {group["symbol"] for group in payload["survivor_groups"]})
    if missing:
        raise SystemExit("unknown survivor symbol(s): " + ", ".join(missing))
    return_code = run_captured([mutmut, "run", *names], Path(args.log))
    current = {record["name"]: record["status"] for record in parse_results(mutmut)}
    counts = Counter(current.get(name, "missing") for name in names)
    print(f"Selected mutants: {len(names)}")
    print("Mutation status:", ", ".join(f"{key}={value}" for key, value in sorted(counts.items())))
    unresolved = [name for name in names if current.get(name, "missing") != "killed"]
    if unresolved:
        print("Unresolved selected mutants:")
        for name in unresolved:
            print(f"{current.get(name, 'missing'):>12}  {name}")
    if args.verbose:
        print("All selected mutants:")
        for name in names:
            print(f"{current.get(name, 'missing'):>12}  {name}")
    print(f"Full output: {args.log}")
    return return_code


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--mutmut", default=".venv/bin/mutmut")
    result.add_argument("--mutants-dir", default="mutants")
    commands = result.add_subparsers(dest="command", required=True)

    run = commands.add_parser("run", help="run all mutants without streaming progress output")
    run.add_argument("--fresh", action="store_true", help="remove generated mutation state first")
    run.add_argument("--report-name", help="retain reports and the default log under this run name")
    run.add_argument("--log", help="full output path (default derives from --report-name)")
    run.set_defaults(handler=command_run)

    report = commands.add_parser("report", help="regenerate compact survivor artifacts")
    report.add_argument("--report-name", help="write reports under this run name")
    report.set_defaults(handler=command_report)

    rerun = commands.add_parser("rerun", help="rerun survivor mutants for one or more exact symbols")
    rerun.add_argument("--symbol", action="append", required=True)
    rerun.add_argument("--report-name", help="read selected mutants from this named report")
    rerun.add_argument("--log", default="mutants/mutmut-scoped-run.log")
    rerun.add_argument("--verbose", action="store_true", help="print every selected mutant status")
    rerun.set_defaults(handler=command_rerun)
    return result


def main() -> int:
    args = parser().parse_args()
    return int(args.handler(args))


if __name__ == "__main__":
    sys.exit(main())
