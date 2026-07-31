from __future__ import annotations

import contextlib
import importlib.util
import io
import json
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
                self.assertTrue((mutants_dir / f"survivors-{name}.md").is_file())

    def test_report_name_rejects_path_traversal(self) -> None:
        with self.assertRaisesRegex(SystemExit, "report name"):
            controller.report_stem("../outside")


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
                {"name": "package.x_target__mutmut_1", "status": "killed"},
                {"name": "package.x_target__mutmut_2", "status": "killed"},
            ]
            output = io.StringIO()
            with (
                patch.object(controller, "run_captured", return_value=0),
                patch.object(controller, "parse_results", return_value=current),
                contextlib.redirect_stdout(output),
            ):
                result = controller.command_rerun(args)

            self.assertEqual(result, 0)
            self.assertIn("Mutation status: killed=2", output.getvalue())
            self.assertNotIn("__mutmut_1", output.getvalue())
            self.assertNotIn("Unresolved selected mutants", output.getvalue())

    def test_unresolved_mutants_remain_visible(self) -> None:
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
            current = [{"name": "package.x_target__mutmut_1", "status": "survived"}]
            output = io.StringIO()
            with (
                patch.object(controller, "run_captured", return_value=0),
                patch.object(controller, "parse_results", return_value=current),
                contextlib.redirect_stdout(output),
            ):
                controller.command_rerun(args)

            self.assertIn("Unresolved selected mutants", output.getvalue())
            self.assertIn("package.x_target__mutmut_1", output.getvalue())


if __name__ == "__main__":
    unittest.main()
