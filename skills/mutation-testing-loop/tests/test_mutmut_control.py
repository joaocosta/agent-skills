from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

CONTROLLER_PATH = Path(__file__).parents[1] / "scripts" / "mutmut_control.py"
SPEC = importlib.util.spec_from_file_location("mutmut_control", CONTROLLER_PATH)
assert SPEC and SPEC.loader
controller = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(controller)


class ReportNamingTests(unittest.TestCase):
    def test_named_reports_preserve_distinct_run_artifacts(self) -> None:
        records = [
            {
                "name": "package.x_target__mutmut_1",
                "status": "survived",
                "symbol": "package.x_target",
            },
            {
                "name": "package.x_target__mutmut_2",
                "status": "killed",
                "symbol": "package.x_target",
            },
        ]
        with tempfile.TemporaryDirectory() as directory:
            mutants_dir = Path(directory)
            with (
                patch.object(controller, "parse_results", return_value=records),
                patch.object(controller, "generated_diffs", return_value={}),
            ):
                controller.write_reports("mutmut", mutants_dir, "initial")
                controller.write_reports("mutmut", mutants_dir, "final")

            for name in ("initial", "final"):
                payload = json.loads((mutants_dir / f"survivors-{name}.json").read_text())
                self.assertEqual(payload["status_counts"], {"killed": 1, "survived": 1})
                self.assertEqual(
                    payload["symbol_status_counts"],
                    {"package.x_target": {"killed": 1, "survived": 1}},
                )
                self.assertTrue((mutants_dir / f"survivors-{name}.md").is_file())
                triage = (mutants_dir / f"triage-{name}.md").read_text()
                self.assertIn("package.x_target (1)", triage)

    def test_report_name_rejects_path_traversal(self) -> None:
        with self.assertRaisesRegex(SystemExit, "report name"):
            controller.report_stem("../outside")


class MutantsDirectorySafetyTests(unittest.TestCase):
    def initialize_repository(self, root: Path, ignore: bool = True) -> None:
        subprocess.run(["git", "init", "--quiet", str(root)], check=True)
        if ignore:
            (root / ".gitignore").write_text("mutants/\n")

    def test_accepts_ignored_generated_state_at_repository_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.initialize_repository(root)
            mutants_dir = root / "mutants"
            mutants_dir.mkdir()
            (mutants_dir / "mutmut-stats.json").write_text("{}")

            with patch.object(controller, "git_root", return_value=root):
                controller.require_safe_mutants_dir(mutants_dir, fresh=True)

    def test_rejects_fresh_removal_without_generated_marker(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.initialize_repository(root)
            mutants_dir = root / "mutants"
            mutants_dir.mkdir()
            (mutants_dir / "user-data.txt").write_text("keep me")

            with (
                patch.object(controller, "git_root", return_value=root),
                self.assertRaisesRegex(SystemExit, "no recognized mutmut-generated marker"),
            ):
                controller.require_safe_mutants_dir(mutants_dir, fresh=True)

    def test_rejects_unignored_mutation_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.initialize_repository(root, ignore=False)

            with (
                patch.object(controller, "git_root", return_value=root),
                self.assertRaisesRegex(SystemExit, "must be ignored by Git"),
            ):
                controller.require_safe_mutants_dir(root / "mutants", fresh=False)

    def test_rejects_tracked_contents_under_ignored_mutation_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.initialize_repository(root)
            mutants_dir = root / "mutants"
            mutants_dir.mkdir()
            (mutants_dir / "tracked.txt").write_text("tracked")
            subprocess.run(
                ["git", "add", "--force", "mutants/tracked.txt"],
                cwd=root,
                check=True,
            )

            with (
                patch.object(controller, "git_root", return_value=root),
                self.assertRaisesRegex(SystemExit, "tracked mutation state"),
            ):
                controller.require_safe_mutants_dir(mutants_dir, fresh=False)


class GeneratedDiffTests(unittest.TestCase):
    def test_reports_original_source_location(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            original_path = root / "src/package/module.py"
            generated_path = root / "mutants/src/package/module.py"
            original_path.parent.mkdir(parents=True)
            generated_path.parent.mkdir(parents=True)
            original_path.write_text("\ndef target():\n    return 1\n")
            generated_path.write_text(
                "def x_target__mutmut_orig():\n    return 1\n\ndef x_target__mutmut_1():\n    return 2\n"
            )
            generated_path.with_suffix(".py.meta").write_text(
                json.dumps(
                    {
                        "exit_code_by_key": {
                            "package.module.x_target__mutmut_1": 0,
                        }
                    }
                )
            )

            details = controller.generated_diffs(root / "mutants")

        self.assertEqual(
            details["package.module.x_target__mutmut_1"]["source_file"],
            "src/package/module.py",
        )
        self.assertEqual(details["package.module.x_target__mutmut_1"]["source_line"], 2)


class InspectOutputTests(unittest.TestCase):
    def test_default_output_collapses_duplicate_fingerprints(self) -> None:
        report = {
            "survivor_groups": [
                {
                    "symbol": "package.x_target",
                    "count": 2,
                    "mutants": [
                        {
                            "name": "package.x_target__mutmut_1",
                            "changes": ["- a", "+ b"],
                            "source_file": "src/package.py",
                            "source_line": 10,
                        },
                        {
                            "name": "package.x_target__mutmut_2",
                            "changes": ["- a", "+ b"],
                        },
                    ],
                }
            ]
        }
        with tempfile.TemporaryDirectory() as directory:
            mutants_dir = Path(directory)
            (mutants_dir / "survivors-initial.json").write_text(json.dumps(report))
            args = Namespace(
                mutants_dir=str(mutants_dir),
                report_name="initial",
                symbol=["package.x_target"],
                verbose=False,
            )
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                controller.command_inspect(args)

        self.assertIn("2 survivors, 1 distinct mutation", output.getvalue())
        self.assertIn("at src/package.py:10", output.getvalue())
        self.assertIn("2× - a → + b", output.getvalue())
        self.assertNotIn("__mutmut_1", output.getvalue())


class ScopedRerunOutputTests(unittest.TestCase):
    def test_default_output_omits_repetitive_killed_mutant_names(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            mutants_dir = Path(directory)
            executable = mutants_dir / "mutmut"
            executable.touch()
            report = {
                "survivor_groups": [
                    {
                        "symbol": "package.x_target",
                        "mutants": [
                            {"name": "package.x_target__mutmut_1"},
                            {"name": "package.x_target__mutmut_2"},
                        ],
                    }
                ]
            }
            (mutants_dir / "survivors-initial.json").write_text(json.dumps(report))
            args = Namespace(
                mutmut=str(executable),
                mutants_dir=str(mutants_dir),
                report_name="initial",
                symbol=["package.x_target"],
                log=str(mutants_dir / "scoped.log"),
                verbose=False,
            )
            current = [
                {
                    "name": "package.x_target__mutmut_1",
                    "status": "killed",
                    "symbol": "package.x_target",
                },
                {
                    "name": "package.x_target__mutmut_2",
                    "status": "killed",
                    "symbol": "package.x_target",
                },
            ]
            output = io.StringIO()
            with (
                patch.object(controller, "run_captured", return_value=0) as run_captured,
                patch.object(controller, "parse_results", return_value=current),
                contextlib.redirect_stdout(output),
            ):
                result = controller.command_rerun(args)

            self.assertEqual(result, 0)
            run_captured.assert_called_once_with(
                [str(executable), "run", "package.x_target__mutmut_*"],
                mutants_dir / "scoped.log",
            )
            self.assertIn("Mutation status: killed=2", output.getvalue())
            self.assertNotIn("__mutmut_1", output.getvalue())
            self.assertNotIn("Unresolved current mutations", output.getvalue())

    def test_unresolved_mutations_are_grouped_by_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            mutants_dir = Path(directory)
            executable = mutants_dir / "mutmut"
            executable.touch()
            report = {
                "survivor_groups": [
                    {
                        "symbol": "package.x_target",
                        "mutants": [{"name": "package.x_target__mutmut_1"}],
                    }
                ]
            }
            (mutants_dir / "survivors-initial.json").write_text(json.dumps(report))
            args = Namespace(
                mutmut=str(executable),
                mutants_dir=str(mutants_dir),
                report_name="initial",
                symbol=["package.x_target"],
                log=str(mutants_dir / "scoped.log"),
                verbose=False,
            )
            current = [
                {
                    "name": "package.x_target__mutmut_1",
                    "status": "survived",
                    "symbol": "package.x_target",
                }
            ]
            output = io.StringIO()
            with (
                patch.object(controller, "run_captured", return_value=0),
                patch.object(controller, "parse_results", return_value=current),
                patch.object(
                    controller,
                    "generated_diffs",
                    return_value={"package.x_target__mutmut_1": {"changes": ["- old", "+ new"]}},
                ),
                contextlib.redirect_stdout(output),
            ):
                controller.command_rerun(args)

            self.assertIn("Unresolved current mutations", output.getvalue())
            self.assertIn("1× survived: - old → + new", output.getvalue())
            self.assertNotIn("package.x_target__mutmut_1", output.getvalue())


class CompactTriageTests(unittest.TestCase):
    def test_triage_samples_large_groups_but_retains_every_group(self) -> None:
        groups = [
            {
                "symbol": "package.x_large",
                "count": 5,
                "mutants": [
                    {
                        "name": f"package.x_large__mutmut_{index}",
                        "changes": [f"- old {index}", f"+ new {index}"],
                        "source_file": "src/package.py",
                        "source_line": 20,
                    }
                    for index in range(5)
                ],
            },
            {
                "symbol": "package.x_small",
                "count": 1,
                "mutants": [{"name": "package.x_small__mutmut_1", "changes": ["- a", "+ b"]}],
            },
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "triage.md"
            controller.write_triage({"survivor_groups": groups}, path)
            text = path.read_text()

        self.assertIn("package.x_large (5) — src/package.py:20", text)
        self.assertIn("package.x_small (1)", text)
        self.assertIn("2 additional distinct mutation(s)", text)
        self.assertNotIn("old 1", text)


class CompareReportsTests(unittest.TestCase):
    def test_compare_uses_diffs_instead_of_unstable_mutant_ids(self) -> None:
        before = {
            "total": 3,
            "status_counts": {"survived": 2, "timeout": 1},
            "symbol_status_counts": {"package.x_target": {"survived": 2, "timeout": 1}},
            "survivor_groups": [
                {
                    "symbol": "package.x_target",
                    "count": 2,
                    "mutants": [
                        {
                            "name": "package.x_target__mutmut_1",
                            "changes": ["- a", "+ b"],
                        },
                        {
                            "name": "package.x_target__mutmut_2",
                            "changes": ["- c", "+ d"],
                        },
                    ],
                }
            ],
        }
        after = {
            "total": 3,
            "status_counts": {"killed": 1, "survived": 2},
            "symbol_status_counts": {"package.x_target": {"killed": 1, "survived": 2}},
            "survivor_groups": [
                {
                    "symbol": "package.x_target",
                    "count": 2,
                    "mutants": [
                        {
                            "name": "package.x_target__mutmut_9",
                            "changes": ["- a", "+ b"],
                        },
                        {
                            "name": "package.x_target__mutmut_10",
                            "changes": ["- e", "+ f"],
                        },
                    ],
                }
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            mutants_dir = Path(directory)
            (mutants_dir / "survivors-initial.json").write_text(json.dumps(before))
            (mutants_dir / "survivors-final.json").write_text(json.dumps(after))
            args = Namespace(
                mutants_dir=str(mutants_dir),
                before="initial",
                after="final",
                symbol=["package.x_target"],
            )
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                controller.command_compare(args)

        self.assertIn("all statuses before: survived=2, timeout=1", output.getvalue())
        self.assertIn("all statuses after: killed=1, survived=2", output.getvalue())
        self.assertIn("same-diff persisted=1", output.getvalue())
        self.assertIn("no-longer-surviving=1", output.getvalue())
        self.assertIn("new-diff=1", output.getvalue())


if __name__ == "__main__":
    unittest.main()
