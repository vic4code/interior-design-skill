import copy
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]/'skills/interior-design'
sys.path.insert(0,str(ROOT/'scripts'))
from project import build, validate, review
from geometry import wall_panels


class ProjectTests(unittest.TestCase):
    def setUp(self): self.data=json.loads((ROOT/'assets/example-project.json').read_text())
    def test_rejects_bad_contract_and_geometry(self):
        cases=[]
        a=copy.deepcopy(self.data);a['room']['width']='6000';cases.append(a)
        a=copy.deepcopy(self.data);a['room']['height']=float('nan');cases.append(a)
        a=copy.deepcopy(self.data);a['openings'][0]['offset']=5900;cases.append(a)
        a=copy.deepcopy(self.data);a['openings'][0]['sill']=100;cases.append(a)
        a=copy.deepcopy(self.data);a['openings'].append(dict(a['openings'][0],id='D02'));cases.append(a)
        a=copy.deepcopy(self.data);a['furniture'][0]['id']='D01';cases.append(a)
        a=copy.deepcopy(self.data);a['furniture'][0]['x']=5900;cases.append(a)
        a=copy.deepcopy(self.data);a['project']['status']='approved';cases.append(a)
        for case in cases:
            with self.subTest(case=case),self.assertRaises(ValueError): validate(case)
    def test_openings_are_real_voids_with_correct_net_volume(self):
        validate(self.data)
        for wall in ('north','south','west','east'):
            r=self.data['room'];length=r['width'] if wall in ('north','south') else r['depth']
            holes=[o for o in self.data['openings'] if o['wall']==wall]
            expected=(length*r['height']-sum(o['width']*o['height'] for o in holes))*r['wall_thickness']
            solids=[(c,s) for name,c,s in wall_panels(self.data) if name==wall]
            self.assertAlmostEqual(sum(s[0]*s[1]*s[2] for c,s in solids),expected)
            for c,s in solids:
                u=c[0] if wall in ('north','south') else c[1]
                for hole in holes:
                    self.assertFalse(hole['offset']<u<hole['offset']+hole['width'] and hole['sill']<c[2]<hole['sill']+hole['height'])
    def test_clashes_remain_explicit_review_issues(self):
        self.data['furniture'][1]['x']=800;self.data['furniture'][1]['y']=3300
        validate(self.data)
        self.assertTrue(any(i['id'].startswith('CLASH-') for i in review(self.data)))
    def test_package_units_quantities_revision_and_stale_artifacts(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/'package';out.mkdir();(out/'scene.glb').write_bytes(b'stale')
            manifest=build(ROOT/'assets/example-project.json',out)
            self.assertFalse((out/'scene.glb').exists());self.assertFalse(manifest['has_model'])
            self.assertEqual(manifest['revision'],'P01')
            for item in manifest['files']:
                self.assertEqual(hashlib.sha256((out/item['name']).read_bytes()).hexdigest(),item['sha256'])
            for name in ['A101','A201','A202','A203','A204']:
                svg=ET.fromstring((out/(name+'.svg')).read_text())
                self.assertEqual(svg.attrib['width'],'420mm');self.assertEqual(svg.attrib['height'],'297mm')
                self.assertIn('NOT FOR CONSTRUCTION',ET.tostring(svg,encoding='unicode'))
                self.assertIn('P01',ET.tostring(svg,encoding='unicode'))
            with (out/'materials.csv').open(encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
            self.assertAlmostEqual(float(rows[0]['net_area_m2']),28.8)
            self.assertAlmostEqual(float(rows[1]['net_area_m2']),52.71)
            self.assertIn('$INSUNITS\n70\n4', (out/'plan.dxf').read_text())
            self.assertTrue((out/'drawings.pdf').read_bytes().startswith(b'%PDF-'))
    def test_large_room_plan_fits_sheet_and_csv_is_not_formula(self):
        from project import drawings, write_csv
        self.data['room']['depth']=10000
        validate(self.data)
        sh=drawings(self.data)[0]
        self.assertIn('1:100 at 100%',sh.svg())
        for kind,values in sh.items:
            if kind=='rect':
                x,y,w,h,*_=values
                self.assertLessEqual(x+w,410)
                self.assertLessEqual(y+h,287)
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'table.csv';write_csv(p,['name'],[{'name':'=1+1'}])
            with p.open(encoding='utf-8-sig') as f:row=next(csv.DictReader(f))
            self.assertEqual(row['name'],"'=1+1")
    def test_invalid_cli_fails_without_success_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'bad.json';p.write_text('{}');out=Path(temp)/'out'
            result=subprocess.run([sys.executable,str(ROOT/'scripts/project.py'),'build',str(p),'--out',str(out)],capture_output=True)
            self.assertNotEqual(result.returncode,0);self.assertFalse((out/'manifest.json').exists())
    def test_text_cannot_break_svg_markup(self):
        self.data['furniture'][0]['name']='<script>& bad'
        from project import drawings
        for sheet in drawings(self.data):ET.fromstring(sheet.svg())
        self.assertIn('&lt;script&gt;&amp; bad',drawings(self.data)[0].svg())


if __name__=='__main__':unittest.main()
