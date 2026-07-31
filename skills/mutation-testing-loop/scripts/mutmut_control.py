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
from typing import NotRequired, TypedDict, cast

MUTANT_SUFFIX = re.compile(r"__mutmut_\d+$")
REPORT_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
CLASS_SEPARATOR = "ǁ"


class SourceDetails(TypedDict, total=False):
    source_file: str
    source_line: int


class MutationDetails(SourceDetails):
    generated_file: NotRequired[str]
    changes: list[str]


class Mutant(TypedDict):
    name: str
    status: str
    symbol: str
    changes: NotRequired[list[str]]
    generated_file: NotRequired[str]
    source_file: NotRequired[str]
    source_line: NotRequired[int]


class SurvivorGroup(TypedDict):
    symbol: str
    count: int
    mutants: list[Mutant]


class SurvivorReport(TypedDict):
    status_counts: dict[str, int]
    symbol_status_counts: dict[str, dict[str, int]]
    total: int
    survivor_groups: list[SurvivorGroup]


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


def git_root() -> Path | None:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        return None
    return Path(result.stdout.strip()).resolve()


def require_safe_mutants_dir(mutants_dir: Path, fresh: bool) -> None:
    root = git_root()
    expected = (root or Path.cwd().resolve()) / "mutants"
    resolved = mutants_dir.resolve()
    if resolved != expected:
        raise SystemExit(f"mutants directory must be the repository-root generated directory: {expected}")

    if root is not None:
        relative = resolved.relative_to(root)
        tracked = subprocess.run(
            ["git", "ls-files", "--", str(relative)],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        if tracked.returncode or tracked.stdout.strip():
            raise SystemExit(f"refusing to use tracked mutation state at {relative}/")
        ignored = subprocess.run(
            ["git", "check-ignore", "--quiet", "--", str(relative)],
            cwd=root,
            check=False,
        )
        if ignored.returncode != 0:
            raise SystemExit(f"mutation state must be ignored by Git before running: {relative}/")

    if fresh and resolved.exists() and any(resolved.iterdir()):
        generated_markers = (
            resolved / "mutmut-stats.json",
            resolved / "survivors.json",
            resolved / "pyproject.toml",
        )
        if not any(marker.is_file() for marker in generated_markers):
            raise SystemExit(f"refusing to remove {resolved}: no recognized mutmut-generated marker")


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


def definition_locations(tree: ast.AST) -> dict[tuple[str, ...], int]:
    locations: dict[tuple[str, ...], int] = {}

    def visit_body(body: list[ast.stmt], prefix: tuple[str, ...] = ()) -> None:
        for node in body:
            if isinstance(node, ast.ClassDef):
                visit_body(node.body, (*prefix, node.name))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qualified_name = (*prefix, node.name)
                locations[qualified_name] = node.lineno
                visit_body(node.body, qualified_name)

    visit_body(getattr(tree, "body", []))
    return locations


def original_qualified_name(full_name: str) -> tuple[str, ...] | None:
    symbol = MUTANT_SUFFIX.sub("", full_name).rsplit(".", 1)[-1]
    if symbol.startswith(f"x{CLASS_SEPARATOR}"):
        return tuple(symbol[2:].split(CLASS_SEPARATOR))
    if symbol.startswith("x_"):
        return (symbol[2:],)
    return None


def source_details(
    mutants_dir: Path,
    generated_path: Path,
    full_name: str,
    locations: dict[tuple[str, ...], int],
) -> SourceDetails:
    qualified_name = original_qualified_name(full_name)
    if qualified_name is None:
        return {}
    line = locations.get(qualified_name)
    if line is None:
        return {}
    try:
        relative_path = generated_path.relative_to(mutants_dir)
    except ValueError:
        return {}
    return {"source_file": relative_path.as_posix(), "source_line": line}


def generated_diffs(mutants_dir: Path) -> dict[str, MutationDetails]:
    found: dict[str, MutationDetails] = {}
    for metadata_path in sorted(mutants_dir.rglob("*.py.meta")):
        generated_path = Path(str(metadata_path)[: -len(".meta")])
        try:
            tree = ast.parse(generated_path.read_text())
        except (OSError, SyntaxError, UnicodeDecodeError):
            continue
        try:
            relative_path = generated_path.relative_to(mutants_dir)
            original_tree = ast.parse((mutants_dir.parent / relative_path).read_text())
            locations = definition_locations(original_tree)
        except (OSError, SyntaxError, UnicodeDecodeError, ValueError):
            locations = {}
        functions = {
            node.name: node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
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
                "generated_file": str(generated_path),
                "changes": changed_lines(original, mutant),
                **source_details(mutants_dir, generated_path, full_name, locations),
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


def triage_path(mutants_dir: Path, name: str | None) -> Path:
    suffix = f"-{name}" if name else ""
    return mutants_dir / f"triage{suffix}.md"


def fingerprint(mutant: Mutant) -> tuple[str, ...] | None:
    changes = mutant.get("changes")
    if not changes:
        return None
    return tuple(change.strip() for change in changes)


def fingerprint_text(mutant: Mutant) -> str:
    mutation_fingerprint = fingerprint(mutant)
    if mutation_fingerprint is None:
        return "diff unavailable; inspect this group if it is a contender"
    return " → ".join(mutation_fingerprint)


def representative_indexes(length: int, limit: int = 3) -> list[int]:
    if length <= limit:
        return list(range(length))
    return sorted({round(index * (length - 1) / (limit - 1)) for index in range(limit)})


def group_location(group: SurvivorGroup) -> str | None:
    for mutant in group["mutants"]:
        source_file = mutant.get("source_file")
        source_line = mutant.get("source_line")
        if source_file and source_line:
            return f"{source_file}:{source_line}"
    return None


def group_heading(group: SurvivorGroup, level: int) -> str:
    location = group_location(group)
    suffix = f" — {location}" if location else ""
    return f"{'#' * level} {group['symbol']} ({group['count']}){suffix}"


def write_triage(payload: SurvivorReport, path: Path) -> None:
    markdown = [
        "# Survivor-group triage",
        "",
        "Review every group here, then inspect plausible contenders in full.",
        "",
    ]
    for group in payload["survivor_groups"]:
        mutants = group["mutants"]
        markdown.append(group_heading(group, 2))
        markdown.append("")
        unique: list[tuple[str, int]] = []
        counts: Counter[str] = Counter(fingerprint_text(mutant) for mutant in mutants)
        for mutant in mutants:
            text = fingerprint_text(mutant)
            if not any(existing == text for existing, _count in unique):
                unique.append((text, counts[text]))
        for index in representative_indexes(len(unique)):
            text, count = unique[index]
            if len(text) > 300:
                text = text[:297] + "..."
            markdown.append(f"- {count}× `{text}`")
        omitted = len(unique) - len(representative_indexes(len(unique)))
        if omitted:
            markdown.append(
                f"- … {omitted} additional distinct mutation(s); use `inspect` if this group is a contender"
            )
        markdown.append("")
    path.write_text("\n".join(markdown))


def write_reports(mutmut: str, mutants_dir: Path, report_name: str | None = None) -> tuple[list[Mutant], Counter[str]]:
    records = parse_results(mutmut)
    statuses = Counter(record["status"] for record in records)
    diffs = generated_diffs(mutants_dir)
    survivors: list[Mutant] = []
    for record in records:
        if record["status"] != "survived":
            continue
        survivors.append(
            cast(
                Mutant,
                {
                    **record,
                    **diffs.get(record["name"], cast(MutationDetails, {"changes": []})),
                },
            )
        )

    grouped: dict[str, list[Mutant]] = defaultdict(list)
    for survivor in survivors:
        grouped[str(survivor["symbol"])].append(survivor)
    symbol_statuses: dict[str, Counter[str]] = defaultdict(Counter)
    for record in records:
        symbol_statuses[record["symbol"]][record["status"]] += 1

    payload: SurvivorReport = {
        "status_counts": dict(sorted(statuses.items())),
        "symbol_status_counts": {
            symbol: dict(sorted(counts.items())) for symbol, counts in sorted(symbol_statuses.items())
        },
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
        markdown.append(group_heading(group, 3))
        markdown.append("")
        fingerprints = Counter(
            " → ".join(change.strip() for change in mutant.get("changes", []))
            or "diff unavailable; inspect this group with mutmut show if selected"
            for mutant in group["mutants"]
        )
        for fingerprint, count in fingerprints.most_common():
            if len(fingerprint) > 300:
                fingerprint = fingerprint[:297] + "..."
            markdown.append(f"- {count}× `{fingerprint}`")
        markdown.append("")
    report_path(mutants_dir, report_name, "md").write_text("\n".join(markdown))
    write_triage(payload, triage_path(mutants_dir, report_name))
    return survivors, statuses


def print_summary(survivors: list[Mutant], statuses: Counter[str]) -> None:
    total = sum(statuses.values())
    counts = [
        f"total={total}",
        *[f"{key}={value}" for key, value in sorted(statuses.items())],
    ]
    print("Mutation status:", ", ".join(counts))
    groups = Counter(str(item["symbol"]) for item in survivors)
    print(f"Survivor groups: {len(groups)}")


def command_run(args: argparse.Namespace) -> int:
    mutmut = mutmut_command(args.mutmut)
    stem = report_stem(args.report_name)
    mutants_dir = Path(args.mutants_dir)
    require_safe_mutants_dir(mutants_dir, args.fresh)
    if args.fresh and mutants_dir.exists():
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
    print(f"Triage inventory: {triage_path(mutants_dir, args.report_name)}")
    print(f"Complete survivor details: {details_path}")
    return return_code


def command_report(args: argparse.Namespace) -> int:
    mutmut = mutmut_command(args.mutmut)
    survivors, statuses = write_reports(mutmut, Path(args.mutants_dir), args.report_name)
    print_summary(survivors, statuses)
    return 0


def load_report(mutants_dir: Path, name: str | None) -> SurvivorReport:
    path = report_path(mutants_dir, name, "json")
    if not path.is_file():
        raise SystemExit(f"missing {path}; run the report command first")
    return cast(SurvivorReport, json.loads(path.read_text()))


def selected_groups(payload: SurvivorReport, symbols: list[str]) -> list[SurvivorGroup]:
    groups_by_symbol = {group["symbol"]: group for group in payload["survivor_groups"]}
    missing = sorted(set(symbols) - set(groups_by_symbol))
    if missing:
        raise SystemExit("unknown survivor symbol(s): " + ", ".join(missing))
    return [groups_by_symbol[symbol] for symbol in symbols]


def command_inspect(args: argparse.Namespace) -> int:
    groups = selected_groups(load_report(Path(args.mutants_dir), args.report_name), args.symbol)
    for group in groups:
        mutations = group["mutants"]
        fingerprints = Counter(fingerprint_text(mutant) for mutant in mutations)
        mutation_label = "mutation" if len(fingerprints) == 1 else "mutations"
        location = group_location(group)
        location_suffix = f" at {location}" if location else ""
        print(
            f"{group['symbol']} ({group['count']} survivors, "
            f"{len(fingerprints)} distinct {mutation_label}){location_suffix}"
        )
        if args.verbose:
            for mutant in mutations:
                print(f"  {mutant['name']}")
                print(f"    {fingerprint_text(mutant)}")
        else:
            for text, count in fingerprints.items():
                print(f"  {count}× {text}")
    return 0


def command_rerun(args: argparse.Namespace) -> int:
    mutmut = mutmut_command(args.mutmut)
    mutants_dir = Path(args.mutants_dir)
    baseline_groups = selected_groups(load_report(mutants_dir, args.report_name), args.symbol)
    patterns = [f"{symbol}__mutmut_*" for symbol in args.symbol]
    return_code = run_captured([mutmut, "run", *patterns], Path(args.log))

    records = [record for record in parse_results(mutmut) if record["symbol"] in args.symbol]
    diffs = generated_diffs(mutants_dir)
    current: list[Mutant] = [
        cast(
            Mutant,
            {
                **record,
                **diffs.get(record["name"], cast(MutationDetails, {"changes": []})),
            },
        )
        for record in records
    ]
    counts = Counter(str(record["status"]) for record in current)
    print(f"Current mutants in selected symbol(s): {len(current)}")
    print(
        "Mutation status:",
        ", ".join(f"{key}={value}" for key, value in sorted(counts.items())),
    )

    baseline_fingerprints = Counter(
        mutation_fingerprint
        for group in baseline_groups
        for mutant in group["mutants"]
        if (mutation_fingerprint := fingerprint(mutant)) is not None
    )
    current_by_fingerprint: dict[tuple[str, ...], Counter[str]] = defaultdict(Counter)
    for mutant in current:
        mutation_fingerprint = fingerprint(mutant)
        if mutation_fingerprint is not None:
            current_by_fingerprint[mutation_fingerprint][str(mutant["status"])] += 1
    dispositions: Counter[str] = Counter()
    for mutation_fingerprint, baseline_count in baseline_fingerprints.items():
        remaining = baseline_count
        for status, count in sorted(current_by_fingerprint[mutation_fingerprint].items()):
            matched = min(remaining, count)
            dispositions[status] += matched
            remaining -= matched
        dispositions["not generated"] += remaining
    unavailable = sum(fingerprint(mutant) is None for group in baseline_groups for mutant in group["mutants"])
    if unavailable:
        dispositions["diff unavailable"] += unavailable
    print(
        "Baseline survivor fingerprints:",
        ", ".join(f"{key}={value}" for key, value in sorted(dispositions.items())),
    )

    unresolved = [record for record in current if record["status"] != "killed"]
    if unresolved:
        print("Unresolved current mutations:")
        unresolved_fingerprints = Counter((str(record["status"]), fingerprint_text(record)) for record in unresolved)
        for (status, text), count in unresolved_fingerprints.items():
            if len(text) > 300:
                text = text[:297] + "..."
            print(f"  {count}× {status}: {text}")
    if args.verbose:
        print("All current mutants:")
        for record in current:
            print(f"{record['status']:>12}  {record['name']}")
    print(f"Full output: {args.log}")
    return return_code


def survivor_fingerprints(group: SurvivorGroup | None) -> Counter[tuple[str, ...]]:
    if group is None:
        return Counter()
    return Counter(
        mutation_fingerprint
        for mutant in group["mutants"]
        if (mutation_fingerprint := fingerprint(mutant)) is not None
    )


def command_compare(args: argparse.Namespace) -> int:
    mutants_dir = Path(args.mutants_dir)
    before = load_report(mutants_dir, args.before)
    after = load_report(mutants_dir, args.after)
    before_groups = {group["symbol"]: group for group in before["survivor_groups"]}
    after_groups = {group["symbol"]: group for group in after["survivor_groups"]}
    missing = sorted(set(args.symbol) - set(before_groups))
    if missing:
        raise SystemExit("unknown survivor symbol(s) in before report: " + ", ".join(missing))

    print(
        f"Before status: total={before['total']}, "
        + ", ".join(f"{k}={v}" for k, v in sorted(before["status_counts"].items()))
    )
    print(
        f"After status: total={after['total']}, "
        + ", ".join(f"{k}={v}" for k, v in sorted(after["status_counts"].items()))
    )
    for symbol in args.symbol:
        before_group = before_groups[symbol]
        after_group = after_groups.get(symbol)
        before_fingerprints = survivor_fingerprints(before_group)
        after_fingerprints = survivor_fingerprints(after_group)
        persisted = before_fingerprints & after_fingerprints
        added = after_fingerprints - before_fingerprints
        removed = before_fingerprints - after_fingerprints
        unavailable_before = sum(fingerprint(mutant) is None for mutant in before_group["mutants"])
        unavailable_after = sum(fingerprint(mutant) is None for mutant in after_group["mutants"]) if after_group else 0
        print(f"{symbol}:")
        before_statuses = before.get("symbol_status_counts", {}).get(symbol)
        after_statuses = after.get("symbol_status_counts", {}).get(symbol)
        if before_statuses is not None or after_statuses is not None:
            before_text = ", ".join(f"{key}={value}" for key, value in sorted((before_statuses or {}).items()))
            after_text = ", ".join(f"{key}={value}" for key, value in sorted((after_statuses or {}).items()))
            print(f"  all statuses before: {before_text or 'none'}")
            print(f"  all statuses after: {after_text or 'none'}")
        print(
            f"  survivors before={before_group['count']} after={after_group['count'] if after_group else 0}; "
            f"same-diff persisted={sum(persisted.values())}, no-longer-surviving={sum(removed.values())}, "
            f"new-diff={sum(added.values())}, diff-unavailable before={unavailable_before} after={unavailable_after}"
        )
        for label, mutations in (("persisted", persisted), ("new", added)):
            for mutation_fingerprint, count in mutations.items():
                text = " → ".join(mutation_fingerprint)
                if len(text) > 300:
                    text = text[:297] + "..."
                print(f"  {label} {count}× `{text}`")
    return 0


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

    inspect = commands.add_parser("inspect", help="print full details for exact survivor groups")
    inspect.add_argument("--symbol", action="append", required=True)
    inspect.add_argument("--report-name", help="read groups from this named report")
    inspect.add_argument(
        "--verbose",
        action="store_true",
        help="print every mutant name instead of distinct mutation counts",
    )
    inspect.set_defaults(handler=command_inspect)

    rerun = commands.add_parser("rerun", help="rerun all current mutants for one or more exact survivor symbols")
    rerun.add_argument("--symbol", action="append", required=True)
    rerun.add_argument(
        "--report-name",
        help="read selected symbols and baseline fingerprints from this named report",
    )
    rerun.add_argument("--log", default="mutants/mutmut-scoped-run.log")
    rerun.add_argument(
        "--verbose",
        action="store_true",
        help="print every current selected mutant status",
    )
    rerun.set_defaults(handler=command_rerun)

    compare = commands.add_parser("compare", help="compare selected survivor groups across named reports by diff")
    compare.add_argument("--before", required=True, help="before report name")
    compare.add_argument("--after", required=True, help="after report name")
    compare.add_argument("--symbol", action="append", required=True)
    compare.set_defaults(handler=command_compare)
    return result


def main() -> int:
    args = parser().parse_args()
    return int(args.handler(args))


if __name__ == "__main__":
    sys.exit(main())
