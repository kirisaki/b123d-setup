"""Exercise the installed CLI and its no-overwrite contract."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class CLITest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "b123d_setup", *map(str, args)],
            cwd=self.root, capture_output=True, text=True,
        )

    def test_generate_nested_project_with_spaces_and_vscode(self):
        target = self.root / "nested" / "My Part"
        result = self.run_cli(target, "--with-vscode")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(str(target), result.stdout)
        self.assertIn('name = "my-part"', (target / "pyproject.toml").read_text())
        self.assertFalse((target / ".venv").exists())
        self.assertFalse((target / "uv.lock").exists())
        for source in target.rglob("*.py"):
            compile(source.read_text(), str(source), "exec")
        launch = json.loads((target / ".vscode/launch.json").read_text())
        self.assertEqual(launch["configurations"][1]["module"], "scripts.export_all")

    def test_legacy_name_accepts_empty_directory(self):
        target = self.root / "empty"
        target.mkdir()
        result = self.run_cli("--name", target)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((target / "main.py").is_file())
        self.assertFalse((target / ".vscode").exists())

    def test_nonempty_directory_is_unchanged(self):
        target = self.root / "existing"
        target.mkdir()
        sentinel = target / ".keep"
        sentinel.write_text("user content")
        result = self.run_cli(target)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(list(target.iterdir()), [sentinel])
        self.assertEqual(sentinel.read_text(), "user content")

    def test_existing_file_is_unchanged(self):
        target = self.root / "file"
        target.write_text("user content")
        result = self.run_cli(target)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(target.read_text(), "user content")

    @unittest.skipIf(os.name == "nt", "symlink creation may require privileges")
    def test_nonempty_symlink_target_is_unchanged(self):
        real = self.root / "real"
        real.mkdir()
        (real / "keep").write_text("user content")
        link = self.root / "link"
        link.symlink_to(real, target_is_directory=True)
        self.assertEqual(self.run_cli(link).returncode, 1)
        self.assertEqual([p.name for p in real.iterdir()], ["keep"])

    def test_invalid_arguments_do_not_create_files(self):
        for arguments in ([], [""], ["one", "--name", "two"]):
            with self.subTest(arguments=arguments):
                self.assertEqual(self.run_cli(*arguments).returncode, 2)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_unicode_directory_produces_valid_fallback_name(self):
        target = self.root / "部品"
        result = self.run_cli(target)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('name = "cad-project"', (target / "pyproject.toml").read_text())

    def test_help_and_version(self):
        self.assertEqual(self.run_cli("--help").returncode, 0)
        result = self.run_cli("--version")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "0.1.0")


if __name__ == "__main__":
    unittest.main()
