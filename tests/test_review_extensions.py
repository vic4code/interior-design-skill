"""Sandbox browser contract checks for spatial, image and MEP evidence."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'skills/interior-design/scripts/_internal'))
from build_review import build, digest


class ReviewExtensions(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root/'source'; self.source.mkdir()
        self.out = self.root/'out'

    def register(self, files):
        for name, data in files.items():
            (self.source/name).write_text(json.dumps(data) if isinstance(data, (list, dict)) else data)
        (self.source/'manifest.json').write_text(json.dumps(dict(files={name:digest(self.source/name) for name in files})))

    def structured(self, mep=False):
        files = {'project.json':dict(project=dict(name='One space', revision='R01'), room=dict(width=6000, depth=4800), furniture=[dict(id='F01', name='Desk', x=1000,y=700,width=1200,depth=600)], openings=[dict(wall='south',kind='door',offset=700,width=900)]), 'A101.svg':'<svg xmlns="http://www.w3.org/2000/svg"><text y="29">Dimensioned furniture sheet</text></svg>'}
        if mep: files['A102.svg']='<svg xmlns="http://www.w3.org/2000/svg"><text y="29">Lighting and electrical intent</text></svg>'
        self.register(files)

    def test_layout_is_distinct_and_uses_original_furniture_location(self):
        self.structured()
        result=build(self.source,self.out)
        self.assertEqual(result['layout']['kind'], 'furniture-layout')
        self.assertNotEqual((self.out/'layout.svg').read_bytes(),(self.out/'A101.svg').read_bytes())
        root=ET.parse(self.out/'layout.svg').getroot()
        rects=[n for n in root.iter() if n.tag.endswith('rect')]
        self.assertTrue(any(n.get('x')=='1000' and n.get('y')=='3500' and n.get('width')=='1200' for n in rects))
        self.assertNotIn('Dimensioned furniture sheet',(self.out/'layout.svg').read_text())
        self.assertEqual(result['mep'],[])

    def test_mep_only_with_actual_registered_sheet_or_checksummed_attachment(self):
        self.structured(mep=True)
        self.assertEqual(build(self.source,self.out)['mep'][0]['kind'],'lighting-electrical-intent')
        external=self.root/'hvac.svg';external.write_bytes(b'<svg xmlns="http://www.w3.org/2000/svg"/>')
        metadata=self.root/'metadata.json'
        item=dict(id='M201',title='Mechanical reference',source='hvac.svg',kind='hvac',status='pending-specialist-review',reference='Supplied consultant reference',sha256=digest(external))
        metadata.write_text(json.dumps(dict(mep=[item])))
        result=build(self.source,self.out,metadata=metadata)
        self.assertEqual(result['mep'][1]['status'],'pending-specialist-review')
        external.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'MEP attachment checksum'):
            build(self.source,self.out,metadata=metadata)

    def test_native_uses_irregular_mesh_lines_and_excludes_title_dimensions(self):
        svg='<svg xmlns="http://www.w3.org/2000/svg"><text>Private title</text><line x1="40" y1="65" x2="80" y2="65" stroke-width="0.38"/><line x1="80" y1="65" x2="55" y2="92" stroke-width="0.1"/><line x1="55" y1="92" x2="40" y2="65" stroke-width="0.38"/><line x1="40" y1="50" x2="80" y2="50" stroke-width="0.18"/></svg>'
        self.register({'selection.json':dict(project='Irregular home'),'views.json':[dict(sheet='N101',title='Native plan',kind='plan',scale=75)],'N101.svg':svg})
        result=build(self.source,self.out)
        self.assertEqual(result['layout']['kind'],'native-plan-extract')
        root=ET.parse(self.out/'layout.svg').getroot()
        self.assertEqual(len(list(root)),3)
        self.assertFalse(any(n.tag.endswith('rect') for n in root.iter()))
        self.assertNotIn('Private title',(self.out/'layout.svg').read_text())

    def test_real_pdf_pages_have_png_previews_and_original_download_hash(self):
        from reportlab.pdfgen import canvas
        from PIL import Image
        self.structured()
        pdf=self.root/'engineering.pdf'
        writer=canvas.Canvas(str(pdf),pagesize=(420,297))
        for title in ('Lighting arrangement', 'Power outlet arrangement'):
            writer.drawString(50,200,title);writer.line(30,30,300,200);writer.showPage()
        writer.save()
        metadata=self.root/'metadata.json'
        metadata.write_text(json.dumps(dict(mep=[dict(id='E201',title='Electrical drawings',source=pdf.name,sha256=digest(pdf),kind='electrical',status='pending-consultant-review')])) )
        result=build(self.source,self.out,metadata=metadata)
        self.assertEqual(len(result['mep']),2)
        for number,entry in enumerate(result['mep'],1):
            self.assertEqual(entry['id'],f'E201-p{number:03d}')
            self.assertEqual(entry['source_page'],number)
            self.assertEqual(entry['status'],'pending-consultant-review')
            self.assertEqual(entry['original_file'],'mep/E201.pdf')
            with Image.open(self.out/entry['file']) as preview:
                self.assertEqual(preview.format,'PNG')
                self.assertLessEqual(max(preview.size),2048)
                self.assertLess(min(pair[0] for pair in preview.convert('RGB').getextrema()),255)
        self.assertNotEqual(digest(self.out/result['mep'][0]['file']),digest(self.out/result['mep'][1]['file']))
        self.assertEqual(digest(self.out/'mep/E201.pdf'),digest(pdf))
        registered={entry['name']:entry['sha256'] for entry in result['files']}
        for entry in result['mep']:
            self.assertEqual(registered[entry['file']],digest(self.out/entry['file']))
        self.assertEqual(registered['mep/E201.pdf'],digest(pdf))
        previous=(self.out/'manifest.json').read_bytes()
        pdf.write_bytes(b'invalid PDF')
        config=json.loads(metadata.read_text());config['mep'][0]['sha256']=digest(pdf)
        metadata.write_text(json.dumps(config))
        with self.assertRaisesRegex(ValueError,'Cannot open MEP PDF'):
            build(self.source,self.out,metadata=metadata)
        self.assertEqual((self.out/'manifest.json').read_bytes(),previous)

    def test_pdf_filled_form_is_visible_in_preview(self):
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        from PIL import Image
        from pdf_preview import render_pdf_pages
        import pypdfium2 as pdfium
        pdf=self.root/'form.pdf'
        writer=canvas.Canvas(str(pdf),pagesize=(420,297))
        writer.acroForm.textfield(name='approval',value='CONSULTANT REVIEW PENDING',x=50,y=100,width=300,height=35,textColor=colors.black,borderWidth=0,fillColor=colors.white)
        writer.showPage();writer.save()
        names=render_pdf_pages(pdf,self.root/'previews')
        with Image.open(self.root/'previews'/names[0]) as preview:
            self.assertLess(min(pair[0] for pair in preview.convert('RGB').getextrema()),200)
        with pdfium.PdfDocument(str(pdf)) as document:
            document.init_forms()
            page=document[0];bitmap=page.render(scale=2,may_draw_forms=False,draw_annots=False)
            baseline=bitmap.to_pil()
            self.assertEqual(min(pair[0] for pair in baseline.convert('RGB').getextrema()),255)
            baseline.close();bitmap.close();page.close()

    def test_pdf_page_limit_and_invalid_pdf_fail_explicitly(self):
        from reportlab.pdfgen import canvas
        from unittest.mock import patch
        from pdf_preview import render_pdf_pages
        pdf=self.root/'many.pdf'
        writer=canvas.Canvas(str(pdf))
        for index in range(2):writer.drawString(30,30,str(index));writer.showPage()
        writer.save()
        with patch('pdf_preview.MAX_PAGES',1):
            with self.assertRaisesRegex(ValueError,'pages'):
                render_pdf_pages(pdf,self.root/'previews')
        self.assertFalse((self.root/'previews').exists())
        with patch('pdf_preview.MAX_TOTAL_PIXELS',1):
            with self.assertRaisesRegex(ValueError,'pixel preview budget'):
                render_pdf_pages(pdf,self.root/'previews')
        self.assertFalse((self.root/'previews').exists())
        with patch.dict(sys.modules, {'pypdfium2': None}):
            with self.assertRaisesRegex(ValueError,'PDF previews require pypdfium2'):
                render_pdf_pages(pdf,self.root/'previews')
        pdf.write_bytes(b'invalid PDF')
        with self.assertRaisesRegex(ValueError,'Cannot open MEP PDF'):
            render_pdf_pages(pdf,self.root/'previews')

    def test_additional_view_keeps_status_and_requires_real_base_provenance(self):
        self.structured()
        image=self.root/'view.jpg';image.write_bytes(b'generated view')
        base=self.root/'base.png';base.write_bytes(b'actual camera')
        provenance=self.root/'view.json';provenance.write_text(json.dumps(dict(mode='completion-simulation',review_status='pending',image_sha256=digest(image),base_sha256=digest(base))))
        metadata=self.root/'metadata.json';metadata.write_text(json.dumps(dict(presentations=[dict(id='reading',title='Reading angle',space='Living',image='view.jpg',base_image='base.png',provenance='view.json')])))
        result=build(self.source,self.out,metadata=metadata)
        entry=result['presentations'][0]
        self.assertEqual((entry['kind'],entry['review_status']),('completion-simulation','pending'))
        self.assertEqual(digest(self.out/entry['base_image']),digest(base))
        image.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'Additional presentation checksum'):
            build(self.source,self.out,metadata=metadata)


if __name__=='__main__':unittest.main()
