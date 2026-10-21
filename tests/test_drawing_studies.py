"""Contract checks for shared dimensions, issued-sheet extents and provenance."""
import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]/'skills/interior-design'
sys.path.insert(0,str(ROOT/'scripts/_internal'))
from build_drawing_studies import build, joinery_geometry, make_sheets

class DrawingStudyTests(unittest.TestCase):
    def setUp(self):
        self.project=json.loads((ROOT/'assets/style-studies/project.json').read_text())
        self.project['project'].setdefault('brief','Synthetic gallery living design study.')
        self.joinery=json.loads((ROOT/'assets/style-studies/joinery.json').read_text())
        self.style=json.loads((ROOT/'assets/style-studies/styles.json').read_text())['mcm']

    def test_joinery_stacks_close_and_update_from_source(self):
        for width,depth,height,bays in [(2200,450,750,4),(2600,500,900,5)]:
            p=copy.deepcopy(self.project);j=copy.deepcopy(self.joinery)
            f=next(f for f in p['furniture'] if f['id']==j['object_id'])
            f.update(width=width,depth=depth,height=height);j['bays']=bays
            g=joinery_geometry(p,j)
            self.assertAlmostEqual(g['bay_clear']*bays+(bays+1)*j['carcass_thickness'],width)
            self.assertAlmostEqual(g['leaf_width']*bays+(bays+1)*j['door_gap'],width)
            self.assertEqual(g['inner_depth']+j['back_thickness']+j['front_clearance']+j['door_thickness'],depth)
            self.assertEqual(g['base_top']+g['shelf_bottom']-g['base_top']+j['shelf_thickness']+g['top_under']-g['shelf_top']+j['top_thickness'],height)

    def test_invalid_shelf_and_service_positions_are_rejected(self):
        for spec in [dict(self.joinery,shelf_top_height=40),dict(self.joinery,bays=0),dict(self.joinery,back_thickness=500)]:
            with self.assertRaises(ValueError):joinery_geometry(self.project,spec)
        j=copy.deepcopy(self.joinery);j['service_points'][0]['z']=6000
        with self.assertRaises(ValueError):joinery_geometry(self.project,j)

    def test_issued_geometry_and_text_remain_on_a3_sheet(self):
        for sh in make_sheets(self.project,self.joinery,self.style):
            for kind,p in sh.items:
                if kind=='text':
                    x,y,text,size,color,anchor=p
                    self.assertTrue(10<=x<=410 and 10<=y<=287,(sh.code,p))
                    # Helvetica width from the actual PDF font, including right/centre anchors.
                    from reportlab.pdfbase.pdfmetrics import stringWidth
                    w=stringWidth(text,'Helvetica',size)
                    left=x-({'start':0,'middle':w/2,'end':w}[anchor])
                    self.assertGreaterEqual(left,10,(sh.code,text))
                    self.assertLessEqual(left+w,410,(sh.code,text))
                elif kind=='rect':
                    x,y,w,h,*_=p
                    self.assertTrue(x>=10 and y>=10 and x+w<=410 and y+h<=287,(sh.code,p))
                elif kind=='line':
                    x,y,a,b,*_=p
                    self.assertTrue(min(x,a)>=10 and max(x,a)<=410 and min(y,b)>=10 and max(y,b)<=287,(sh.code,p))

    def test_manifest_covers_actual_outputs_and_sources(self):
        with tempfile.TemporaryDirectory() as td:
            base=Path(td);source=base/'input.json';source.write_text(json.dumps(self.project));out=base/'issued'
            build(source,ROOT/'assets/style-studies/joinery.json',out)
            manifest=json.loads((out/'manifest.json').read_text())
            self.assertEqual(set(manifest['files']),{f.name for f in out.iterdir()}-{'manifest.json'})
            for name,digest in manifest['files'].items():
                self.assertEqual(digest,hashlib.sha256((out/name).read_bytes()).hexdigest())
            self.assertEqual(manifest['sources']['project.json'],hashlib.sha256(source.read_bytes()).hexdigest())
            self.assertNotIn(str(base),json.dumps(manifest))
            svgs=list(out.glob('*.svg'));self.assertEqual(len(svgs),8)
            for svg in svgs:
                root=ET.parse(svg).getroot();self.assertEqual(root.attrib['viewBox'],'0 0 420 297')
            self.assertGreater((out/'design-coordination.pdf').stat().st_size,15000)

    def test_existing_project_files_are_not_overwritten(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'project';out.mkdir()
            (out/'author.blend').write_bytes(b'original model')
            (out/'A101.svg').write_bytes(b'original drawing')
            before={p.name:p.read_bytes() for p in out.iterdir()}
            with self.assertRaises(ValueError):
                build(ROOT/'assets/style-studies/project.json',ROOT/'assets/style-studies/joinery.json',out)
            self.assertEqual(before,{p.name:p.read_bytes() for p in out.iterdir()})

    def test_reduced_sheet_scope_does_not_leave_obsolete_owned_drawings(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'issued'
            project=ROOT/'assets/style-studies/project.json';joinery=ROOT/'assets/style-studies/joinery.json'
            build(project,joinery,out)
            selected=make_sheets(self.project,self.joinery,self.style)[:1]
            with patch('build_drawing_studies.make_sheets',return_value=selected):
                build(project,joinery,out)
                self.assertEqual({path.name for path in out.glob('*.svg')},{selected[0].code+'.svg'})
                manifest=json.loads((out/'manifest.json').read_text())
                self.assertEqual(set(manifest['files']),{path.name for path in out.iterdir()}-{'manifest.json'})
                build(project,joinery,out)
                self.assertEqual(manifest['files'],json.loads((out/'manifest.json').read_text())['files'])

    def test_owned_output_rebuilds_but_changes_unknown_files_and_symlinks_are_preserved(self):
        for alteration in ('none','modified','unknown','symlink'):
            with self.subTest(alteration=alteration),tempfile.TemporaryDirectory() as td:
                base=Path(td);out=base/'issued'
                build(ROOT/'assets/style-studies/project.json',ROOT/'assets/style-studies/joinery.json',out)
                original=json.loads((out/'manifest.json').read_text())['files']
                if alteration=='modified':(out/'A101.svg').write_bytes(b'edited drawing')
                if alteration=='unknown':(out/'author.blend').write_bytes(b'original model')
                if alteration=='symlink':
                    target=base/'original.svg';target.write_bytes(b'original external drawing')
                    (out/'A101.svg').unlink();(out/'A101.svg').symlink_to(target)
                before={p.name:p.read_bytes() for p in out.iterdir()}
                if alteration=='none':
                    build(ROOT/'assets/style-studies/project.json',ROOT/'assets/style-studies/joinery.json',out)
                    self.assertEqual(original,json.loads((out/'manifest.json').read_text())['files'])
                else:
                    with self.assertRaises(ValueError):
                        build(ROOT/'assets/style-studies/project.json',ROOT/'assets/style-studies/joinery.json',out)
                    self.assertEqual(before,{p.name:p.read_bytes() for p in out.iterdir()})
                    if alteration=='symlink':self.assertEqual(target.read_bytes(),b'original external drawing')

    def test_project_and_joinery_inputs_inside_output_are_rejected(self):
        for inside in ('project','joinery'):
            with self.subTest(inside=inside),tempfile.TemporaryDirectory() as td:
                base=Path(td);out=base/'issued';out.mkdir()
                project=(out if inside=='project' else base)/'project.json'
                joinery=(out if inside=='joinery' else base)/'joinery.json'
                project.write_text(json.dumps(self.project));joinery.write_text(json.dumps(self.joinery))
                before={p.name:p.read_bytes() for p in out.iterdir()}
                with self.assertRaises(ValueError):build(project,joinery,out)
                self.assertEqual(before,{p.name:p.read_bytes() for p in out.iterdir()})

if __name__=='__main__':unittest.main()
