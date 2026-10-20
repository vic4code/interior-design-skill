"""Exercise the installed skill without any parent-repository runtime files."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1] / 'skills/interior-design'


class InstalledSkillTests(unittest.TestCase):
    def test_copied_skill_builds_from_an_unrelated_directory(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            installed = root / 'installed/interior-design'
            shutil.copytree(SKILL, installed, ignore=shutil.ignore_patterns(
                '.venv', '.cache', '__pycache__', 'node_modules', 'dist', 'generated'))
            working = root / 'user-project'
            working.mkdir()
            output = working / 'review'
            result = subprocess.run([
                sys.executable, str(installed / 'scripts/project.py'), 'build',
                str(installed / 'assets/example-project.json'), '--out', str(output)
            ], cwd=working, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((output / 'manifest.json').read_text())
            self.assertEqual(manifest['revision'], 'P01')
            self.assertFalse(manifest['has_model'])
            self.assertEqual(len(manifest['files']), 13)
            verified = subprocess.run([
                sys.executable, str(installed / 'scripts/verify_outputs.py'), str(output)
            ], cwd=working, capture_output=True, text=True)
            self.assertEqual(verified.returncode, 0, verified.stderr)


if __name__ == '__main__':
    unittest.main()
