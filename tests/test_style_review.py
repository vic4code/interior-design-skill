"""The browser bridge must reject changed visual-source contracts."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1]/'skills/interior-design/scripts/build_style_review.py'
spec = importlib.util.spec_from_file_location('style_review', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class StyleReviewTests(unittest.TestCase):
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
