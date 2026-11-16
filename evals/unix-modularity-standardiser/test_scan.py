import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main

SCANNER = (
    Path(__file__).resolve().parents[2]
    / "unix-modularity-standardiser" / "scripts" / "scan.py"
)


class ScannerGateTests(TestCase):
    def setUp(self):
        workspace = TemporaryDirectory()
        self.addCleanup(workspace.cleanup)
        self.root = Path(workspace.name)
        self.baseline = self.root / "baseline.json"

    def write_source(self, name, code_lines):
        (self.root / name).write_text("run()\n" * code_lines, encoding="utf-8")

    def scan(self, *options):
        return subprocess.run(
            [sys.executable, str(SCANNER), str(self.root), *options],
            capture_output=True,
            text=True,
        )

    def check(self, *options, expected):
        result = self.scan("--check", "--json", *options)
        self.assertEqual(result.returncode, bool(expected), result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual([row["path"] for row in report["blocking_violations"]], expected)
        return report, result.stderr

    def test_audit_and_strict_gate(self):
        self.write_source("at_limit.py", 300)
        (self.root / "view.vue").write_text(
            "<template>\n" + "<div />\n" * 301 + "</template>\n"
            "<script>\n" + "run();\n" * 300 + "// comment\n\n</script>\n",
            encoding="utf-8",
        )
        self.check(expected=[])

        self.write_source("over_limit.py", 301)
        audit = self.scan("--json")
        self.assertEqual(audit.returncode, 0, audit.stderr)
        self.assertNotIn("blocking_violations", json.loads(audit.stdout))
        _, diagnostic = self.check(expected=["over_limit.py"])
        self.assertIn("over_limit.py: 301 code lines (limit 300)", diagnostic)

    def test_baseline_allows_existing_debt_and_rejects_growth_and_new_paths(self):
        self.write_source("legacy.py", 310)
        self.write_source("shrinking.py", 309)
        self.write_source("removed.py", 308)
        audit = self.scan("--json")
        self.assertEqual(audit.returncode, 0, audit.stderr)
        self.baseline.write_text(audit.stdout, encoding="utf-8")
        options = ("--baseline", str(self.baseline))

        self.write_source("shrinking.py", 301)
        (self.root / "removed.py").unlink()
        report, _ = self.check(*options, expected=[])
        self.assertEqual([row["path"] for row in report["violations"]],
                         ["legacy.py", "shrinking.py"])

        self.write_source("legacy.py", 311)
        self.write_source("new.py", 301)
        _, diagnostic = self.check(*options, expected=["legacy.py", "new.py"])
        self.assertIn("baseline 310", diagnostic)

    def test_invalid_baseline_is_a_configuration_error(self):
        self.baseline.write_text('{"gate":"code_lines","threshold":301,"violations":[]}',
                                 encoding="utf-8")
        result = self.scan("--check", "--baseline", str(self.baseline))
        self.assertEqual(result.returncode, 2)
        self.assertIn("same threshold", result.stderr)


if __name__ == "__main__":
    main()
