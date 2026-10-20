"""View coverage is measured, bounded and honest about missing reference images."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]/'skills/interior-design'
sys.path.insert(0, str(SKILL/'scripts/_internal'))
from view_plan import build, plan, polygon_area


class ViewPlanTests(unittest.TestCase):
    def test_concave_actual_area_controls_view_count_not_bounding_box(self):
        # L-shape: 36 m² bounding rectangle, 11 m² actual floor area.
        shape = [[0, 0], [6000, 0], [6000, 1000], [1000, 1000], [1000, 6000], [0, 6000]]
        self.assertEqual(polygon_area(shape), 11)
        result = plan({'spaces': [{'id': 'L', 'polygon_mm': shape, 'area_m2': 36}]}, '.')
        self.assertEqual(result['spaces'][0]['area_source'], 'polygon_mm-shoelace')
        self.assertEqual(len(result['jobs']), 2)
        self.assertEqual(polygon_area(list(reversed(shape))), 11)
        self.assertEqual(polygon_area([[x*2, y*2] for x, y in shape]), 44)

    def test_area_thresholds_and_explicit_details(self):
        for area, count in [(8, 1), (8.01, 2), (20, 2), (20.01, 3), (40, 3), (40.01, 4), (900, 4)]:
            result = plan([{'id': 'room', 'area_m2': area}], '.')
            self.assertEqual(len(result['jobs']), count)
        result = plan([{'id': 'large', 'area_m2': 70, 'functions': ['客廳', '工作區'], 'features': ['書櫃']}], '.')
        self.assertEqual(len(result['jobs']), 7)
        self.assertEqual(result['jobs'][-1]['role'], 'detail')

    def test_budget_fairly_allocates_rooms_and_reports_deferred_work(self):
        result = plan([{'id': str(i), 'area_m2': 100} for i in range(4)], '.', budget=5)
        self.assertEqual(len(result['jobs']), 5)
        self.assertEqual([job['space'] for job in result['jobs'][:4]], ['0', '1', '2', '3'])
        self.assertEqual(result['deferred_views'], 11)
        self.assertEqual(sum(s['planned_views'] for s in result['spaces']), 5)

    def test_unknown_area_never_invents_dimensions_or_extra_views(self):
        result = plan([{'id': 'unknown', 'features': ['desk'], 'functions': ['work', 'living']}], '.')
        self.assertEqual(len(result['jobs']), 1)
        self.assertIsNone(result['jobs'][0]['area_m2'])
        self.assertEqual(result['jobs'][0]['status'], 'needs-base')
        self.assertEqual(result['measurement_requests'][0]['space'], 'unknown')

    def test_reference_scope_role_existence_and_hash_are_checked(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'front.png').write_bytes(b'base-reference')
            (root/'other.png').write_bytes(b'other-room')
            data = {'spaces': [{'id': 'living', 'area_m2': 25}, {'id': 'bed', 'area_m2': 7}],
                    'existing_views': [
                        {'id': 'wrong-room', 'space': 'bed', 'role': 'reverse', 'base_image': 'other.png'},
                        {'id': 'wrong-role', 'space': 'living', 'role': 'detail', 'base_image': 'other.png'},
                        {'id': 'missing', 'space': 'living', 'role': 'diagonal', 'base_image': 'missing.png'},
                        {'id': 'ready', 'space': 'living', 'role': 'overview', 'base_image': 'front.png'}]}
            source = root/'spaces.json'
            source.write_text(json.dumps(data))
            result = build(source, root/'plan.json')
            ready = [job for job in result['jobs'] if job['status'] == 'pending-image-generation']
            self.assertEqual(len(ready), 1)
            self.assertEqual(ready[0]['reference_id'], 'ready')
            self.assertEqual(ready[0]['base_sha256'], hashlib.sha256(b'base-reference').hexdigest())
            self.assertEqual(len(result['missing_reference_files']), 1)
            self.assertNotIn('image_sha256', ready[0])
            self.assertEqual(json.loads((root/'plan.json').read_text()), result)

    def test_invalid_polygons_inputs_and_budget_fail_explicitly(self):
        for shape in ([[0, 0], [2000, 2000], [0, 2000], [2000, 0]],
                      [[0, 0], [1, 1], [2, 2]], [[0, 0], [True, 1], [1, 0]]):
            with self.assertRaises(ValueError):
                polygon_area(shape)
        for budget in (0, 101, True, 2.5):
            with self.assertRaises(ValueError):
                plan([{'id': 'room'}], '.', budget)
        for data in ([{'id': 'a', 'area_m2': -1}], [{'id': 'a'}, {'id': 'a'}], {'spaces': []}):
            with self.assertRaises(ValueError):
                plan(data, '.')

    def test_facade_cli_is_portable_and_does_not_need_runtime_dependencies(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root/'spaces.json'
            source.write_text(json.dumps({'spaces': [{'id': 'room', 'area_m2': 55}]}))
            result = subprocess.run([sys.executable, str(SKILL/'scripts/interior_design.py'),
                                     'views', '--spaces', str(source), '--out', str(root/'plan.json'),
                                     '--budget', '3'], cwd=root, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads((root/'plan.json').read_text())
            self.assertEqual(len(data['jobs']), 3)
            self.assertEqual(data['deferred_views'], 1)


if __name__ == '__main__':
    unittest.main()
