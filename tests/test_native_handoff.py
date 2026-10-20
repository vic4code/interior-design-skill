"""Native geometry evidence tests, independent of Blender installation."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]/'skills/interior-design'
sys.path.insert(0,str(ROOT/'scripts'))
from extract_native_model import feature_edges
from build_native_handoff import section_segments,build,draw_view,planar_station_evidence


def box():
    vertices=[[0,0,0],[1000,0,0],[1000,1000,0],[0,1000,0],[0,0,1000],[1000,0,1000],[1000,1000,1000],[0,1000,1000]]
    triangles=[[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]]
    return dict(id='OBJ00001',name='Example cabinet mesh',bbox_mm=dict(min=[0,0,0],max=[1000,1000,1000]),vertices_mm=vertices,triangles=triangles,feature_edges=feature_edges(triangles,vertices),geometry_status='evaluated_mesh')


class NativeHandoffTests(unittest.TestCase):
    def test_triangle_slice_matches_real_box_perimeter_on_all_axes(self):
        import math
        obj=box()
        for axis in (0,1,2):
            lines=section_segments(obj,axis,375)
            self.assertTrue(lines)
            for a,b in lines:self.assertAlmostEqual(a[axis],375);self.assertAlmostEqual(b[axis],375)
            self.assertAlmostEqual(sum(math.dist(a,b) for a,b in lines),4000)
            self.assertEqual(section_segments(obj,axis,1100),[])

    def test_feature_edges_remove_internal_coplanar_triangulation(self):
        obj=box();self.assertEqual(len(obj['feature_edges']),12)
        edge_lengths=[]
        import math
        for a,b in obj['feature_edges']:edge_lengths.append(math.dist(obj['vertices_mm'][a],obj['vertices_mm'][b]))
        self.assertEqual(set(edge_lengths),{1000})

    def test_imported_split_vertices_do_not_create_fake_diagonal_edges(self):
        original=box();vertices=[];triangles=[]
        for tri in original['triangles']:
            triangles.append(list(range(len(vertices),len(vertices)+3)))
            vertices.extend(original['vertices_mm'][i] for i in tri)
        self.assertEqual(len(feature_edges(triangles,vertices)),12)

    def test_keyed_dimension_requires_actual_mesh_plane_evidence(self):
        obj=box();view=dict(kind='section',axis='y',offset_mm=500,title='Verified dimensions',dimensions=[dict(id='D01',axis='x',start_mm=[0,500,500],end_mm=[1000,500,500])])
        sh,objects,record=draw_view(dict(objects=[obj]),view,'M001',{},[])
        self.assertEqual(record['dimensions'][0]['value_mm'],1000)
        view['dimensions'][0]['end_mm'][0]=800
        with self.assertRaises(ValueError):draw_view(dict(objects=[obj]),view,'M001',{},[])

    def test_sloped_triangles_do_not_prove_axis_aligned_face_stations(self):
        obj=dict(id='OBJ1',vertices_mm=[[0,0,0],[1000,0,100],[0,1000,1000]],triangles=[[0,1,2]])
        # All target coordinates occur as vertices, but no planar station exists.
        for coordinate in (0,100,1000):
            self.assertIsNone(planar_station_evidence([obj],2,coordinate))
        obj=box()
        self.assertIsNotNone(planar_station_evidence([obj],0,0,dict(min=[-1,250,250],max=[1,750,750])))
        self.assertIsNone(planar_station_evidence([obj],0,0,dict(min=[-1,1500,1500],max=[1,2000,2000])))
        match=planar_station_evidence([obj],0,0)
        self.assertEqual(match['object_id'],obj['id'])
        self.assertAlmostEqual(match['normal_alignment'],1)

    def test_native_output_evidence_and_hashes_are_traceable(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);source=base/'inventory.json';out=base/'out'
            obj=box();inventory=dict(format='native-model-inventory-v1',units=dict(coordinate_unit='mm',source_scale_length=1),source=dict(filename='example.blend',sha256='0'*64),objects=[obj])
            source.write_text(json.dumps(inventory));config=base/'selection.json'
            config.write_text(json.dumps(dict(views=[dict(kind='section',axis='y',offset_mm=375,title='Actual evaluated cut')])))
            records=build(source,out,config)
            self.assertGreater(records[0]['cut_segments'],0)
            self.assertEqual(records[0]['projected_segments'],0)
            self.assertEqual(records[0]['plane_mm'],375)
            manifest=json.loads((out/'manifest.json').read_text())
            self.assertNotIn(str(base),json.dumps(manifest))
            self.assertEqual(set(manifest['files']),{p.name for p in out.iterdir()}-{'manifest.json'})
            for name,digest in manifest['files'].items():self.assertEqual(digest,hashlib.sha256((out/name).read_bytes()).hexdigest())
            self.assertEqual(manifest['source_hashes']['inventory'],hashlib.sha256(source.read_bytes()).hexdigest())

    def test_traditional_chinese_pdf_uses_unicode_font_and_wraps_by_display_width(self):
        from build_drawing_studies import paragraph_lines
        import shutil
        import subprocess
        import unicodedata
        title='原生模型施工協調圖'
        self.assertTrue(any('670' in line for line in paragraph_lines('高度閉合：32 + 18 + 264 + 18 + 320 + 18 = 670。',43)))
        text='板件尺寸與施工界面須依現場覆核，詳 dimension-evidence.csv。'
        for line in paragraph_lines(text,22):
            self.assertLessEqual(sum(2 if unicodedata.east_asian_width(c) in ('W','F') else 1 for c in line),22)
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);source=base/'inventory.json';out=base/'out';config=base/'config.json'
            source.write_text(json.dumps(dict(format='native-model-inventory-v1',units=dict(coordinate_unit='mm'),source=dict(filename='example.blend',sha256='0'*64),objects=[box()])))
            config.write_text(json.dumps(dict(language='zh-TW',project='測試住宅',views=[dict(kind='section',axis='y',title=title,note=text)])))
            build(source,out,config)
            pdf=(out/'native-coordination.pdf').read_bytes()
            self.assertIn(b'MSung-Light',pdf);self.assertIn(b'UniCNS-UCS2-H',pdf)
            if shutil.which('pdftotext'):
                extracted=subprocess.check_output(['pdftotext',str(out/'native-coordination.pdf'),'-']).decode('utf-8')
                self.assertIn(title,''.join(extracted.split()))
                self.assertIn('現場覆核',''.join(extracted.split()))

    def test_mesh_omissions_never_become_invented_section_details(self):
        obj=box();obj.update(vertices_mm=[],triangles=[],feature_edges=[],geometry_status='omitted_budget')
        issues=[]
        sh,objects,record=draw_view(dict(objects=[obj]),dict(kind='section',axis='y',title='Missing mesh'), 'M001',{},issues)
        self.assertEqual(record['cut_segments'],0);self.assertEqual(record['projected_segments'],0)
        self.assertTrue(any('omitted' in issue['question'].lower() for issue in issues))
        with self.assertRaises(ValueError):draw_view(dict(objects=[obj]),dict(kind='plan',title='Too large',scale=.01),'M001',{},[])

if __name__=='__main__':unittest.main()
