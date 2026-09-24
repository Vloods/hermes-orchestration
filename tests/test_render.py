"""Offline contract checks for the renderer; never touch the live home."""
import os
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/render.py"


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

    def test_preview_has_no_side_effects(self):
        result = self.run_render()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PREVIEW CREATE", result.stdout)
        self.assertFalse(self.home.exists())

    def test_apply_fixture_and_model_substitution(self):
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
        self.assertNotIn("api_mode:", config)
        self.assertNotIn("api_mode:", solver)
        self.assertIn("subagent_auto_approve: false", config)
        self.assertIn("# Project orchestration policy", (self.root / "project/.hermes.md").read_text())
        self.assertEqual((self.home / "config.yaml").stat().st_mode & 0o777, 0o600)
        main = yaml.safe_load(config)
        self.assertEqual(len(main["auxiliary"]), 10)
        self.assertEqual(main["delegation"]["max_concurrent_children"], 3)
        self.assertFalse(main["kanban"]["auto_decompose"])

    def test_merge_preserves_unrelated_secrets_and_existing_solver_metadata(self):
        solver = self.home / "profiles/solver"
        solver.mkdir(parents=True)
        original = "model:\n  default: old\n  base_url: https://private.invalid\nplugins:\n  private: token-placeholder\nkanban:\n  custom: 42\n"
        (self.home / "config.yaml").write_text(original)
        (solver / "config.yaml").write_text("model:\n  default: legacy\n  api_mode: custom\nsecrets:\n  untouched: fixture\n")
        (solver / "profile.yaml").write_text("description: My specialist\ncustom: preserved\n")
        preview = self.run_render()
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertEqual((self.home / "config.yaml").read_text(), original)
        self.assertNotIn("token-placeholder", preview.stdout)
        result = self.run_render("--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        main = yaml.safe_load((self.home / "config.yaml").read_text())
        self.assertEqual(main["plugins"]["private"], "token-placeholder")
        self.assertEqual(main["model"]["base_url"], "https://private.invalid")
        self.assertEqual(main["model"]["default"], "gpt-6-astra")
        self.assertEqual(main["kanban"]["custom"], 42)
        merged_solver = yaml.safe_load((solver / "config.yaml").read_text())
        self.assertEqual(merged_solver["secrets"]["untouched"], "fixture")
        self.assertEqual(merged_solver["model"]["api_mode"], "custom")
        self.assertEqual((solver / "profile.yaml").read_text(), "description: My specialist\ncustom: preserved\n")
        for path in (self.home / "config.yaml", solver / "config.yaml"):
            self.assertEqual(path.with_name("config.yaml.backup").stat().st_mode & 0o777, 0o600)
        self.assertEqual((self.home / "config.yaml.backup").read_text(), original)
        again = self.run_render("--apply")
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertFalse((self.home / "config.yaml.backup.1").exists())

    def test_invalid_existing_yaml_preflight_no_partial_write(self):
        self.home.mkdir()
        (self.home / "config.yaml").write_text("model: [invalid\n")
        result = self.run_render("--apply")
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.home / "profiles").exists())
        (self.home / "config.yaml").write_text("a: 1\na: 2\n")
        self.assertEqual(self.run_render("--apply").returncode, 2)
        (self.home / "config.yaml").write_text("model: scalar\n")
        self.assertEqual(self.run_render("--apply").returncode, 2)

    def test_project_policy_conflict_refuses_all_writes(self):
        project = self.root / "project"
        project.mkdir()
        (project / ".hermes.md").write_text("personal rules")
        result = self.run_render("--apply", "--project", project)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.home.exists())

    def test_rejects_relative_root_and_yaml_injection(self):
        self.assertEqual(self.run_render("--provider", "x\nunsafe: true").returncode, 2)
        result = subprocess.run([sys.executable, str(SCRIPT), "--home", "relative", "--apply"],
                                capture_output=True, text=True, cwd=self.root)
        self.assertEqual(result.returncode, 2)
        self.assertFalse((self.root / "relative").exists())

    def test_rejects_symlink_destination_and_ancestor(self):
        self.home.mkdir()
        outside = self.root / "outside"
        outside.write_text("do not touch")
        (self.home / "config.yaml").symlink_to(outside)
        self.assertEqual(self.run_render("--apply").returncode, 2)
        self.assertEqual(outside.read_text(), "do not touch")
        (self.home / "config.yaml").unlink()
        self.home.rmdir()
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

    def test_default_home_resolves_to_ordinary_user_home_preview_only(self):
        result = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True,
                                env={**os.environ, "HOME": str(self.root), "HERMES_HOME": str(self.root / "ignored")})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(str(self.root / ".hermes/config.yaml"), result.stdout)
        self.assertFalse((self.root / ".hermes").exists())

    def test_local_markdown_links_and_citation(self):
        import re
        from urllib.parse import unquote
        for doc in [*ROOT.glob("*.md"), *(ROOT / "docs").glob("*.md")]:
            content = doc.read_text(encoding="utf-8")
            for link in re.findall(r"\]\(([^)]+)\)", content):
                if link.startswith(("https://", "http://", "mailto:")):
                    continue
                target, _, anchor = link.partition("#")
                dest = (doc.parent / unquote(target)).resolve() if target else doc
                self.assertTrue(dest.is_file(), f"{doc}: missing {link}")
                if anchor:
                    headings = re.findall(r"^#+ (.+)$", dest.read_text(encoding="utf-8"), re.M)
                    slugs = [re.sub(r"[^\w -]", "", h.lower()).replace(" ", "-") for h in headings]
                    self.assertIn(anchor, slugs, f"{doc}: missing anchor {link}")
        cite = yaml.safe_load((ROOT / "CITATION.cff").read_text())
        self.assertEqual(cite["cff-version"], "1.2.0")
        self.assertEqual(cite["authors"][0]["name"], "Vloods")
        self.assertEqual(cite["repository-code"], "https://github.com/Vloods/hermes-orchestration")
        self.assertNotIn("doi", cite)

    def test_svg_assets_are_well_formed(self):
        for p in (ROOT / "assets").glob("*.svg"):
            self.assertEqual(ET.parse(p).getroot().tag, "{http://www.w3.org/2000/svg}svg")


if __name__ == "__main__":
    unittest.main()
