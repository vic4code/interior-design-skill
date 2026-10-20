"""Verify portable installation scope, package completeness and filesystem safety."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SKILL = Path(__file__).resolve().parents[1] / 'skills/interior-design'
SCRIPT = SKILL / 'scripts/_internal/install_skill.py'
spec = importlib.util.spec_from_file_location('install_skill', SCRIPT)
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallSkillTests(unittest.TestCase):
    def test_all_hosts_copy_complete_package_to_project_and_user_scope(self):
        for agent, roots in installer.HOSTS.items():
            for user in (False, True):
                with self.subTest(agent=agent, user=user), tempfile.TemporaryDirectory() as folder:
                    root = Path(folder)
                    with patch.object(Path, 'home', return_value=root):
                        installed = installer.install(agent, user=True) if user else installer.install(agent, project=root)
                    self.assertEqual(installed, root.resolve() / roots[int(user)] / 'interior-design')
                    for resource in ('SKILL.md', 'LICENSE.txt', 'scripts/interior_design.py', 'scripts/_internal/project.py',
                                     'scripts/_internal/install_skill.py', 'assets/example-project.json',
                                     'assets/project.schema.json', 'assets/viewer/package.json'):
                        self.assertTrue((installed / resource).is_file(), resource)
                    self.assertTrue(any((installed / 'references').iterdir()))
                    self.assertFalse(any(p.is_symlink() for p in installed.rglob('*')))
                    self.assertFalse(any(p.name in ('generated', '__pycache__', 'node_modules', '.venv')
                                         for p in installed.rglob('*')))
                    listed = subprocess.run([sys.executable, str(installed / 'scripts/interior_design.py'), 'install', '--list'],
                                            cwd=root, capture_output=True, text=True)
                    self.assertEqual(listed.returncode, 0, listed.stderr)
                    self.assertIn('claude-code:', listed.stdout)

    def test_existing_installation_and_symlink_destinations_remain_untouched(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            installed = installer.install('codex', project=root)
            marker = installed / 'SKILL.md'
            marker.write_text('keep this installation')
            with self.assertRaises(FileExistsError):
                installer.install('codex', project=root)
            self.assertEqual(marker.read_text(), 'keep this installation')
            outside = root / 'outside'
            outside.mkdir()
            (root / '.claude').symlink_to(outside, target_is_directory=True)
            with self.assertRaises(FileExistsError):
                installer.install('claude-code', project=root)
            self.assertEqual(list(outside.iterdir()), [])
            dangling = root / '.cursor/skills/interior-design'
            dangling.parent.mkdir(parents=True)
            dangling.symlink_to(root / 'missing')
            with self.assertRaises(FileExistsError):
                installer.install('cursor', project=root)
            self.assertTrue(dangling.is_symlink())

    def test_runtime_secrets_and_all_source_symlinks_are_excluded(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / 'source'
            source.mkdir()
            (source / 'SKILL.md').write_text('test')
            for name in ('.env', '.env.local', '.DS_Store', 'module.pyc'):
                (source / name).write_text('private')
            for name in ('.venv', '.cache', 'node_modules', 'dist', 'generated', '__pycache__'):
                (source / name).mkdir()
                (source / name / 'private.txt').write_text('private')
            secret = root / 'private.txt'
            secret.write_text('private')
            (source / 'linked-file').symlink_to(secret)
            (source / 'linked-directory').symlink_to(root, target_is_directory=True)
            installed = installer.install('copilot', project=root, source=source)
            self.assertEqual([p.name for p in installed.iterdir()], ['SKILL.md'])

    def test_cli_requires_explicit_host_and_scope(self):
        for args in ([], ['--agent', 'codex'], ['--user'],
                     ['--agent', 'codex', '--user', '--project', '.']):
            with self.subTest(args=args):
                result = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
        result = subprocess.run([sys.executable, str(SCRIPT), '--list'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(len(result.stdout.splitlines()), 4)

    def test_install_rejects_source_recursion_and_invalid_scope(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'SKILL.md').write_text('test')
            with self.assertRaises(ValueError):
                installer.install('codex', project=root, source=root)
            with self.assertRaises(ValueError):
                installer.install('codex')
            with self.assertRaises(ValueError):
                installer.install('codex', project=root, user=True)


if __name__ == '__main__':
    unittest.main()
