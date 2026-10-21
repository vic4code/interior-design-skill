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
    def invoke(self, *arguments, cwd=None):
        return subprocess.run([sys.executable, str(SKILL/'scripts/interior_design.py'),
                               *map(str, arguments)], cwd=cwd, capture_output=True,
                              text=True, timeout=60)

    def snapshot(self, root):
        return {p.relative_to(root).as_posix():p.read_bytes()
                for p in root.rglob('*') if p.is_file()}

    def test_demo_and_native_reject_unmanaged_whole_output_before_any_child_writes(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            inventory=root/'inventory.json'; inventory.write_text('input must not be read yet')
            config=root/'config.json'; config.write_text('{}')
            for command in ('demo', 'native'):
                with self.subTest(command=command):
                    out=root/command
                    (out/'drawings/mcm').mkdir(parents=True)
                    (out/'drawings/mcm/project.json').write_bytes(b'authored source project')
                    (out/'author.blend').write_bytes(b'authored Blender source')
                    before=self.snapshot(out)
                    args=[command, '--out', out, '--no-serve']
                    if command == 'native': args += ['--inventory', inventory, '--config', config]
                    result=self.invoke(*args)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn('unmanaged nonempty output', result.stderr)
                    self.assertEqual(self.snapshot(out), before)

    def test_native_owned_output_rebuilds_and_preserves_authored_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); inventory=root/'inventory.json'; config=root/'config.json'; out=root/'delivery'
            vertices=[[0,0,0],[1000,0,0],[1000,1000,0],[0,1000,0],
                      [0,0,1000],[1000,0,1000],[1000,1000,1000],[0,1000,1000]]
            triangles=[[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],
                       [1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]]
            sys.path.insert(0, str(SKILL/'scripts/_internal'))
            from extract_native_model import feature_edges
            obj=dict(id='OBJ00001',name='Synthetic cabinet',bbox_mm=dict(min=[0,0,0],max=[1000,1000,1000]),
                     vertices_mm=vertices,triangles=triangles,feature_edges=feature_edges(triangles,vertices),
                     geometry_status='evaluated_mesh')
            inventory.write_text(json.dumps(dict(format='native-model-inventory-v1',units=dict(coordinate_unit='mm'),
                                                source=dict(filename='example.blend',sha256='0'*64),objects=[obj])))
            config.write_text(json.dumps(dict(views=[dict(kind='section',axis='y',offset_mm=500,title='Cabinet section')])))
            inputs={p:p.read_bytes() for p in (inventory,config)}
            args=['native', '--inventory', inventory, '--config', config, '--out', out, '--no-serve']
            for _ in range(2):
                result=self.invoke(*args)
                self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
            self.assertEqual(json.loads((out/'manifest.json').read_text())['format'], 'native-output-v1')
            (out/'drawings/M001.svg').write_bytes(b'author revised section')
            before=self.snapshot(out)
            result=self.invoke(*args)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('modified output artifact',result.stderr)
            self.assertEqual(self.snapshot(out),before)
            for path,data in inputs.items():self.assertEqual(path.read_bytes(),data)

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
            self.assertEqual(json.loads((out/'manifest.json').read_text())['format'], 'demo-output-v1')
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
            rerun = subprocess.run([sys.executable, str(installed/'scripts/interior_design.py'),
                                    'demo', '--out', str(out), '--no-serve'], cwd=working,
                                   capture_output=True, text=True, timeout=60)
            self.assertEqual(rerun.returncode, 0, rerun.stdout+rerun.stderr)
            (out/'drawings/mcm/author.blend').write_bytes(b'author native scene')
            before=self.snapshot(out)
            rerun = subprocess.run([sys.executable, str(installed/'scripts/interior_design.py'),
                                    'demo', '--out', str(out), '--no-serve'], cwd=working,
                                   capture_output=True, text=True, timeout=60)
            self.assertNotEqual(rerun.returncode, 0)
            self.assertIn('unregistered artifacts', rerun.stderr)
            self.assertEqual(self.snapshot(out),before)


if __name__ == '__main__':
    unittest.main()
