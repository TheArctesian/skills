import os
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main

REPO = Path(__file__).resolve().parents[2]
SKILL = "unix-modularity-standardiser"


class InstallerTests(TestCase):
    def setUp(self):
        workspace = TemporaryDirectory(prefix="skill installer ")
        self.addCleanup(workspace.cleanup)
        self.home = Path(workspace.name).resolve()
        self.config = self.home / "custom config"
        self.claude = self.home / "custom claude"
        self.deepseek = self.home / "custom deepseek"
        self.env = {
            "PATH": os.environ["PATH"],
            "HOME": str(self.home),
            "XDG_CONFIG_HOME": str(self.config),
            "CLAUDE_CONFIG_DIR": str(self.claude),
            "DSH_AGENTS_HOME": str(self.deepseek),
        }

    def run_install(self, *options):
        result = subprocess.run(
            [str(REPO / "install.sh"), *map(str, options)],
            cwd=self.home,
            env=self.env,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def test_global_paths_and_removal_preserve_other_installs(self):
        paths = dict(line.split("\t") for line in self.run_install("--list").stdout.splitlines())
        expected = {
            "codex": self.home / ".agents/skills",
            "kimi-code-cli": self.home / ".agents/skills",
            "cursor": self.home / ".cursor/skills",
            "claude-code": self.claude / "skills",
            "deepseek-harness": self.deepseek / "skills",
            "opencode": self.config / "opencode/skills",
            "devin": self.config / "devin/skills",
        }
        for agent, root in expected.items():
            self.assertEqual(paths[agent], str(root))
        self.assertEqual(list(self.home.iterdir()), [])

        existing = expected["cursor"] / SKILL
        existing.mkdir(parents=True)
        unrelated = expected["claude-code"] / SKILL
        unrelated.parent.mkdir(parents=True)
        unrelated.symlink_to(self.home / "missing foreign skill")
        personas = list((REPO / "persona-test/agents").glob("persona-*.md"))
        self.assertTrue(personas)

        self.run_install("--remove")
        self.run_install()
        roots = {Path(path) for path in paths.values() if path != "(project only)"}
        sources = [manifest.parent for manifest in REPO.glob("*/SKILL.md")]
        for root in roots:
            for source in sources:
                link = root / source.name
                if link not in (existing, unrelated):
                    self.assertEqual(link.readlink(), source)
        self.assertTrue(all((self.claude / "agents" / p.name).is_symlink() for p in personas))
        self.assertEqual(self.run_install().stdout, "")

        self.run_install("--remove")
        self.assertTrue(existing.is_dir())
        self.assertEqual(unrelated.readlink(), self.home / "missing foreign skill")
        for root in roots:
            for source in sources:
                link = root / source.name
                if link not in (existing, unrelated):
                    self.assertFalse(link.is_symlink())
        self.assertFalse(any((self.claude / "agents" / p.name).is_symlink() for p in personas))

    def test_project_only_destinations(self):
        project = self.home / "my project"
        project.mkdir()
        self.run_install("--project", project)
        for root in (".agents/skills", ".devin/skills", "agent/skills"):
            self.assertEqual((project / root / SKILL).readlink(), REPO / SKILL)
        self.assertFalse(self.claude.exists())
        self.run_install("--project", project, "--remove")
        for root in (".agents/skills", ".devin/skills", "agent/skills"):
            self.assertFalse((project / root / SKILL).is_symlink())


if __name__ == "__main__":
    main()
