"""The shipped sample must open without build tools or third-party Python modules."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SKILL = Path(__file__).resolve().parents[1]/'skills/interior-design'
sys.path.insert(0, str(SKILL/'scripts/_internal'))
from quickstart import available
from open_review import build_viewer, stop


class QuickstartTests(unittest.TestCase):
    def test_demo_serves_with_standard_library_and_no_node_on_path(self):
        with tempfile.TemporaryDirectory() as folder:
            out = Path(folder)/'sample'
            command = [sys.executable, '-S', str(SKILL/'scripts/interior_design.py'),
                       'demo', '--out', str(out), '--no-open']
            env = dict(os.environ, PATH=folder, PYTHONPATH='')
            try:
                result = subprocess.run(command, env=env, capture_output=True, text=True, timeout=15)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('no package downloads', result.stdout)
                self.assertIn('http://127.0.0.1:', result.stdout)
                manifest = json.loads((out/'review/manifest.json').read_text())
                self.assertEqual(len(manifest['variants']), 4)
                self.assertEqual(len(manifest['sheets']), 8)
            finally:
                stop(out/'review')

    def test_viewer_uses_valid_bundle_without_invoking_npm(self):
        with patch('subprocess.run', side_effect=AssertionError('Unexpected build')):
            self.assertEqual(build_viewer(), SKILL/'assets/viewer/prebuilt')

    def test_stale_inputs_and_changed_artifacts_invalidate_bundle(self):
        from quickstart import inputs
        with tempfile.TemporaryDirectory() as folder:
            bundle = Path(folder)
            # Copy only the small viewer bundle, not runtime dependencies.
            import shutil
            shutil.copytree(SKILL/'assets/viewer/prebuilt', bundle, dirs_exist_ok=True)
            self.assertTrue(available(SKILL, bundle, 'viewer'))
            (bundle/'index.html').write_text('changed')
            self.assertFalse(available(SKILL, bundle, 'viewer'))
            with patch('quickstart.inputs', return_value={'changed-source': '0'*64}):
                self.assertFalse(available(SKILL, bundle, 'viewer'))
            self.assertTrue(inputs(SKILL, 'viewer'))
