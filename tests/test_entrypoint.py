"""The installed entry point delivers a browser package without repository runtime files."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1] / 'skills/interior-design'


class EntryPointTests(unittest.TestCase):
    def test_portable_demo_delivers_four_same_space_presentations_models_and_drawing_sets_without_blender(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            installed = root / 'installed/interior-design'
            shutil.copytree(SKILL, installed, ignore=shutil.ignore_patterns(
                '.venv', '.cache', '__pycache__', 'node_modules', 'dist', 'generated'))
            working = root / 'user-project'
            working.mkdir()
            out = working / 'delivery'
            result = subprocess.run([sys.executable, str(installed / 'scripts/interior_design.py'),
                                     'demo', '--out', str(out), '--no-serve'], cwd=working,
                                    capture_output=True, text=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((out/'review/manifest.json').read_text())
            self.assertEqual(len(manifest['sheets']), 8)
            self.assertEqual(manifest['presentation']['kind'], 'completion-simulation')
            self.assertIsNotNone(manifest['presentation']['base_image'])
            self.assertEqual([entry['id'] for entry in manifest['variants']], ['mcm', 'japandi', 'contemporary', 'bauhaus'])
            self.assertTrue(manifest['model'])
            geometries = set()
            bases = set()
            for variant in manifest['variants']:
                child_root = out/'review'/Path(variant['manifest']).parent
                child = json.loads((out/'review'/variant['manifest']).read_text())
                self.assertEqual(len(child['sheets']), 8)
                self.assertTrue((child_root/child['model']).is_file())
                self.assertTrue((out/'drawings'/variant['id']/'design-coordination.pdf').is_file())
                geometries.add(hashlib.sha256((child_root/'project.json').read_bytes()).hexdigest())
                bases.add(hashlib.sha256((child_root/child['presentation']['base_image']).read_bytes()).hexdigest())
                provenance = json.loads((child_root/child['presentation']['provenance']).read_text())
                self.assertEqual(hashlib.sha256((child_root/child['presentation']['image']).read_bytes()).hexdigest(), provenance['image_sha256'])
                if variant['id'] == 'mcm':
                    from PIL import Image
                    lighting_views = [view for view in child['presentations'] if view['id'].startswith('lighting-')]
                    self.assertEqual({view['id'] for view in lighting_views}, {'lighting-day-off', 'lighting-day-on', 'lighting-night-on'})
                    sizes = set()
                    lighting_bases = set()
                    for view in lighting_views:
                        evidence = json.loads((child_root/view['provenance']).read_text())
                        image = child_root/view['image']
                        self.assertEqual(hashlib.sha256(image.read_bytes()).hexdigest(), evidence['image_sha256'])
                        base_sha = hashlib.sha256((child_root/view['base_image']).read_bytes()).hexdigest()
                        self.assertEqual(base_sha, evidence['base_sha256'])
                        lighting_bases.add(base_sha)
                        with Image.open(image) as decoded:
                            sizes.add(decoded.size)
                    self.assertEqual(sizes, {(1448, 1086)})
                    self.assertEqual(len(lighting_bases), 1)
            self.assertEqual(len(geometries), 1)
            self.assertEqual(len(bases), 1)
            for entry in manifest['files']:
                path = out/'review'/entry['name']
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), entry['sha256'])


if __name__ == '__main__':
    unittest.main()
