"""The browser bridge must reject changed visual-source contracts."""
import importlib.util
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from PIL import Image

SCRIPT = Path(__file__).resolve().parents[1]/'skills/interior-design/scripts/_internal/build_style_review.py'
sys.path.insert(0, str(SCRIPT.parent))
spec = importlib.util.spec_from_file_location('style_review', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class StyleReviewTests(unittest.TestCase):
    def fixture(self, root):
        from build_drawing_studies import build
        study, drawings = root/'study', root/'drawings'
        study.mkdir()
        fixture = SCRIPT.parents[2]/'assets/style-studies'
        build(fixture/'project.json', fixture/'joinery.json', drawings, 'mcm')
        issued = json.loads((drawings/'manifest.json').read_text())
        project = json.loads((drawings/'project.json').read_text())
        rendered = dict(source_sha256=issued['sources'], style='mcm', revision=project['project']['revision'])
        (study/'render-settings.json').write_text(json.dumps(rendered))
        (study/'model_dimensions.json').write_text(json.dumps({'furniture': project['furniture']}))
        (study/'scene.glb').write_bytes(b'test generated geometry')
        Image.new('RGB', (64, 48), '#6a5b40').save(study/'hero.png')
        return study, drawings

    def snapshot(self, root):
        return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob('*') if p.is_file()}

    def test_unmanaged_and_modified_output_are_preserved(self):
        for mode in ('unmanaged', 'extra-file', 'modified-artifact'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as folder:
                root=Path(folder); study, drawings=self.fixture(root); out=root/'review'
                if mode=='unmanaged':
                    out.mkdir(); (out/'scene.blend').write_bytes(b'authored source')
                else:
                    module.build(study, drawings, out)
                    (out/('private-notes.txt' if mode=='extra-file' else 'scene.glb')).write_bytes(b'authored change')
                before=self.snapshot(out)
                with self.assertRaises(ValueError): module.build(study, drawings, out)
                self.assertEqual(self.snapshot(out),before)

    def test_verified_review_can_be_rebuilt_without_losing_source_inputs(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); study, drawings=self.fixture(root); source_before=self.snapshot(root)
            out=root/'review'; first=module.build(study,drawings,out); second=module.build(study,drawings,out)
            self.assertEqual(first['files'],second['files'])
            for relative,data in source_before.items():self.assertEqual((root/relative).read_bytes(),data)

    def test_nested_sources_and_traversal_are_rejected_before_mutation(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); study, drawings=self.fixture(root); before=self.snapshot(root)
            with self.assertRaises(ValueError):module.build(study,drawings,root)
            self.assertEqual(self.snapshot(root),before)
            manifest_path=drawings/'manifest.json'; manifest=json.loads(manifest_path.read_text())
            outside=root/'authored.txt';outside.write_bytes(b'authored source')
            manifest['files']['../authored.txt']=hashlib.sha256(outside.read_bytes()).hexdigest()
            manifest_path.write_text(json.dumps(manifest)); before=self.snapshot(root)
            with self.assertRaisesRegex(ValueError, 'Unsafe artifact'):module.build(study,drawings,root/'review')
            self.assertEqual(self.snapshot(root),before)

    def test_same_style_name_with_changed_palette_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            study, drawings = root/'study', root/'drawings'
            study.mkdir(); drawings.mkdir()
            common = {'project.json':'project', 'joinery.json':'joinery', 'styles.json':'original'}
            rendered = {'source_sha256':dict(common, **{'styles.json':'changed'})}
            (study/'render-settings.json').write_text(json.dumps(rendered))
            (study/'model_dimensions.json').write_text('{}')
            (drawings/'manifest.json').write_text(json.dumps({'sources':common}))
            (drawings/'project.json').write_text('{}')
            with self.assertRaisesRegex(ValueError, 'styles.json'):
                module.build(study, drawings, root/'review')
            self.assertFalse((root/'review').exists())
