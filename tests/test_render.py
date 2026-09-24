"""Offline contract checks for the starter renderer; never touch the live home."""
import os
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "render.py"


class RenderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="hermes-starter-test-",
                                                dir=os.environ.get("HERMES_STARTER_TEST_TMPROOT"))
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.home = self.root / "home"

    def run_render(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), "--home", str(self.home), *map(str, args)],
                              capture_output=True, text=True, env={**os.environ, "HERMES_HOME": str(self.root / "unrelated")})

    def test_dry_run_has_no_side_effects(self):
        result = self.run_render()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("DRY RUN", result.stdout)
        self.assertFalse(self.home.exists())

    def test_apply_sandbox_and_model_substitution(self):
        result = self.run_render("--apply", "--provider", "openrouter", "--primary-model", "vendor/primary",
                                 "--delegate-model", "vendor/delegate", "--aux-model", "vendor/cheap",
                                 "--solver-model", "vendor/solver", "--project", self.root / "project")
        self.assertEqual(result.returncode, 0, result.stderr)
        config = (self.home / "config.yaml").read_text()
        solver = (self.home / "profiles/solver/config.yaml").read_text()
        self.assertIn('default: "vendor/primary"', config)
        self.assertIn('model: "vendor/delegate"', config)
        self.assertIn('model: "vendor/cheap"', config)
        self.assertIn('default: "vendor/solver"', solver)
        self.assertIn('provider: "openrouter"', solver)
        # The runtime chooses transport per provider/model; never pin Codex's wire mode
        # into a substituted solver provider.
        self.assertNotIn("api_mode:", config)
        self.assertNotIn("api_mode:", solver)
        self.assertIn("subagent_auto_approve: false", config)
        self.assertIn("max_spawn_depth: 1", config)
        self.assertIn("# Project orchestration policy", (self.root / "project/.hermes.md").read_text())
        self.assertEqual((self.home / "config.yaml").stat().st_mode & 0o777, 0o600)
        try:
            import yaml
        except ImportError:
            return
        main = yaml.safe_load(config)
        self.assertEqual(len(main["auxiliary"]), 10)
        self.assertEqual(main["delegation"]["max_concurrent_children"], 3)
        self.assertFalse(main["kanban"]["auto_decompose"])

    def test_conflict_preflight_no_partial_write(self):
        self.home.mkdir()
        (self.home / "config.yaml").write_text("original\n")
        result = self.run_render("--apply")
        self.assertEqual(result.returncode, 2)
        self.assertEqual((self.home / "config.yaml").read_text(), "original\n")
        self.assertFalse((self.home / "profiles").exists())

    def test_backup_opt_in(self):
        self.home.mkdir()
        (self.home / "config.yaml").write_text("original\n")
        result = self.run_render("--apply", "--backup-existing")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.home / "config.yaml.backup").read_text(), "original\n")
        self.assertEqual((self.home / "config.yaml.backup").stat().st_mode & 0o777, 0o600)
        self.assertIn("kanban:", (self.home / "config.yaml").read_text())
        result = self.run_render("--apply", "--backup-existing")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.home / "config.yaml.backup.1").exists())

    def test_rejects_relative_root_and_yaml_injection(self):
        self.assertEqual(self.run_render("--provider", "x\nunsafe: true").returncode, 2)
        result = subprocess.run([sys.executable, str(SCRIPT), "--home", "relative", "--apply"],
                                capture_output=True, text=True, cwd=self.root)
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.root / "relative").exists())

    def test_rejects_symlink_destination(self):
        self.home.mkdir()
        outside = self.root / "outside"
        outside.write_text("do not touch")
        (self.home / "config.yaml").symlink_to(outside)
        result = self.run_render("--apply", "--backup-existing")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(outside.read_text(), "do not touch")

    def test_rejects_symlink_ancestor(self):
        actual = self.root / "actual"
        actual.mkdir()
        self.home.symlink_to(actual, target_is_directory=True)
        self.assertEqual(self.run_render("--apply").returncode, 2)
        self.assertEqual(list(actual.iterdir()), [])

    def test_no_credentials_or_local_absolute_paths(self):
        for p in (ROOT / "templates").glob("*.yaml"):
            s = p.read_text()
            self.assertNotIn("api_key", s)
            self.assertNotIn("/Users/", s)
            self.assertNotIn(".env", s)

    def test_svg_assets_are_well_formed(self):
        for p in (ROOT / "assets").glob("*.svg"):
            self.assertEqual(ET.parse(p).getroot().tag, "{http://www.w3.org/2000/svg}svg")


if __name__ == "__main__":
    unittest.main()
