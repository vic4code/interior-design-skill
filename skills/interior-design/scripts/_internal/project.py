#!/usr/bin/env python3
"""Validate one source of truth and produce a reviewable drawing package."""
import argparse
import csv
import hashlib
import html
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys

from jsonschema import Draft202012Validator
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from geometry import WALLS, overlaps, wall_length

ROOT = Path(__file__).resolve().parents[2]
STAMP = 'COORDINATION DRAFT - NOT FOR CONSTRUCTION'


def validate(data):
    def finite(value):
        if isinstance(value, float) and not math.isfinite(value):
            raise ValueError('All numbers must be finite')
        if isinstance(value, dict):
            for v in value.values(): finite(v)
        if isinstance(value, list):
            for v in value: finite(v)
    finite(data)
    schema = json.loads((ROOT / 'assets/project.schema.json').read_text())
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: str(list(e.path)))
    if errors:
        e = errors[0]
        raise ValueError(f'{".".join(map(str,e.path)) or "project"}: {e.message}')
    r = data['room']
    ids = set()
    for obj in data['openings'] + data['furniture']:
        if obj['id'] in ids: raise ValueError(f'Duplicate ID: {obj["id"]}')
        ids.add(obj['id'])
    for o in data['openings']:
        if o['offset']+o['width'] > wall_length(r,o['wall']) or o['sill']+o['height'] > r['height']:
            raise ValueError(f'{o["id"]}: opening extends beyond wall')
        if o['kind'] == 'door' and o['sill'] != 0:
            raise ValueError(f'{o["id"]}: doors must start at finished floor (sill=0)')
    for i, a in enumerate(data['openings']):
        for b in data['openings'][i+1:]:
            if (a['wall'] == b['wall'] and a['offset'] < b['offset']+b['width']
                and b['offset'] < a['offset']+a['width'] and a['sill'] < b['sill']+b['height']
                and b['sill'] < a['sill']+a['height']):
                raise ValueError(f'Overlapping openings: {a["id"]}, {b["id"]}')
    for f in data['furniture']:
        if min(f['width'],f['depth'],f['height']) < 150:
            raise ValueError(f'{f["id"]}: furniture dimensions must be at least 150 mm for this primitive generator')
        if f['x']+f['width'] > r['width'] or f['y']+f['depth'] > r['depth'] or f['height'] > r['height']:
            raise ValueError(f'{f["id"]}: furniture extends beyond room')
    return data


def review(data):
    issues = [
        {'id':'R01','topic':'Field survey','detail':'Confirm all dimensions, wall construction, levels and opening sizes on site.'},
        {'id':'R02','topic':'Door coordination','detail':'Door leaf, frame, swing, hardware and clear opening are not specified; check circulation and accessibility.'},
        {'id':'R03','topic':'Services','detail':'Lighting, circuits, outlets, plumbing, HVAC and ceiling coordination are not designed.'},
        {'id':'R04','topic':'Construction details','detail':'Joinery, fixings, substrates, fire performance and waterproofing details need trade review.'},
        {'id':'R05','topic':'Approval','detail':'Local code, permits, structural changes and professional sign-off are outside this draft.'},
        {'id':'R06','topic':'Quantities','detail':'Net geometric areas only. No waste, reveals, layers, adhesives or purchasing allowances.'}
    ]
    if data['project']['measurement_status'] != 'site_measured_reviewed':
        issues.insert(0, {'id':'R00','topic':'Unverified dimensions','detail':'Dimensions are assumed or not yet reviewed. Do not order or construct from this package.'})
    for i,a in enumerate(data['furniture']):
        for b in data['furniture'][i+1:]:
            if overlaps(a,b): issues.append({'id':f'CLASH-{a["id"]}-{b["id"]}','topic':'Furniture overlap','detail':f'{a["id"]} overlaps {b["id"]} in plan. Resolve before issue.'})
    return issues


class Sheet:
    """A3 landscape drawing commands in paper mm; SVG/PDF share the same geometry."""
    def __init__(self, number, title, project, scale=50):
        self.number, self.title, self.items = number, title, []
        self.rect(10,10,400,277)
        self.text(16,20,'INTERIOR / DESIGN STUDIO',5)
        self.text(16,29,f'{number}  {title}',4)
        self.line(10,255,410,255)
        self.text(16,263,STAMP,4,'#9b3f24')
        self.text(16,272,f'Rev {project["project"]["revision"]} | mm | A3 | 1:{scale} at 100% | Model origin SW; +X east, +Y north',2.8)
        self.text(16,280,f'Measurements: {project["project"]["measurement_status"]} | Do not scale this drawing. Verify written dimensions.',2.8)
    def rect(self,x,y,w,h,fill='none',layer='WALL'):
        self.items.append(('rect',(x,y,w,h,fill,layer)))
    def line(self,x1,y1,x2,y2,layer='DIM'):
        self.items.append(('line',(x1,y1,x2,y2,layer)))
    def text(self,x,y,text,size=3,color='#253e36'):
        self.items.append(('text',(x,y,str(text),size,color)))
    def dim(self,x1,y1,x2,y2,label):
        self.line(x1,y1,x2,y2)
        for x,y in ((x1,y1),(x2,y2)): self.line(x-1,y+1,x+1,y-1)
        self.text((x1+x2)/2+1,(y1+y2)/2-2,label,2.7)
    def svg(self):
        parts=['<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 420 297">', '<rect width="420" height="297" fill="white"/>']
        for kind,p in self.items:
            if kind=='rect':
                x,y,w,h,fill,layer=p
                parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="#253e36" stroke-width="0.3"/>')
            elif kind=='line':
                a,b,c,d,layer=p
                parts.append(f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}" stroke="#253e36" stroke-width="0.2"/>')
            else:
                x,y,t,s,c=p
                parts.append(f'<text x="{x}" y="{y}" font-family="sans-serif" font-size="{s}" fill="{c}">{html.escape(t)}</text>')
        return '\n'.join(parts+['</svg>'])
    def pdf(self,c):
        for kind,p in self.items:
            c.setLineWidth(.25*mm)
            c.setStrokeColor(HexColor('#253e36'))
            if kind=='rect':
                x,y,w,h,fill,_=p
                if fill!='none': c.setFillColor(HexColor(fill))
                c.rect(x*mm,(297-y-h)*mm,w*mm,h*mm,stroke=1,fill=int(fill!='none'))
            elif kind=='line':
                a,b,d,e,_=p
                c.line(a*mm,(297-b)*mm,d*mm,(297-e)*mm)
            else:
                x,y,t,s,color=p
                c.setFillColor(HexColor(color)); c.setFont('Helvetica',s*mm)
                c.drawString(x*mm,(297-y)*mm,t)
        c.showPage()


def drawings(data):
    r=data['room']; w,d,h,t=(r[k] for k in ('width','depth','height','wall_thickness'))
    scale=100 if d>8000 else 50
    s=1/scale; ox,oy=35,63
    plan=Sheet('A101','Furniture plan / clear internal dimensions',data,scale)
    plan.rect(ox-t*s,oy-t*s,(w+2*t)*s,(d+2*t)*s,'#eee9de')
    plan.rect(ox,oy,w*s,d*s,'#f6f3ec')
    for o in data['openings']:
        along=o['offset']*s; size=o['width']*s
        if o['wall'] in ('north','south'):
            x,y=ox+along,oy-t*s if o['wall']=='north' else oy+d*s
            plan.rect(x,y,size,t*s,'#ffffff','OPENING'); plan.text(x,y-2,o['id'],2.5)
        else:
            x,y=ox-t*s if o['wall']=='west' else ox+w*s,oy+(d-o['offset']-o['width'])*s
            plan.rect(x,y,t*s,size,'#ffffff','OPENING'); plan.text(x+4,y+3,o['id'],2.5)
    for f in data['furniture']:
        x,y=ox+f['x']*s,oy+(d-f['y']-f['depth'])*s
        plan.rect(x,y,f['width']*s,f['depth']*s,'#ded4c1','FURNITURE')
        plan.text(x+1,y+4,f['id'],2.5)
    plan.dim(ox,oy-14,ox+w*s,oy-14,f'{w:g}')
    plan.dim(ox-18,oy,ox-18,oy+d*s,f'{d:g}')
    plan.text(ox+w*s-7,oy-24,'N ↑',4)
    tx=265
    plan.text(tx,50,'ROOM / QUANTITIES',4)
    plan.text(tx,60,f'Internal: {w:g} x {d:g} x {h:g} mm')
    plan.text(tx,68,f'Floor: {w*d/1e6:.2f} m2 (net)')
    plan.text(tx,76,f'Wall thickness: {t:g} mm (assumed build-up)')
    plan.text(tx,90,'FURNITURE / W x D x H',4)
    for i,f in enumerate(data['furniture'][:10]):
        plan.text(tx,100+i*13,f'{f["id"]}  {f["name"]}',3)
        plan.text(tx,105+i*13,f'{f["width"]:g} x {f["depth"]:g} x {f["height"]:g}',2.6)
    if len(data['furniture'])>10: plan.text(tx,239,'More furniture: see furniture.csv',2.8)
    plan.text(20,234,'Origin = inside southwest corner. Plan: north up. Door gaps show rough positions; swing NOT specified.',3)
    plan.text(20,242,'Furniture outlines are bounding envelopes. Openings are nominal; structural rough openings require review.',3)
    sheets=[plan]
    s=1/50
    for i,wall in enumerate(WALLS):
        length=wall_length(r,wall)
        sh=Sheet(f'A20{i+1}',f'{wall.upper()} wall / datum elevation',data)
        # Datum view, increasing station left-to-right. This is explicit, not a mirrored interior perspective.
        x,y=35,68
        sh.rect(x,y,length*s,h*s,'#f6f3ec')
        holes=sorted([o for o in data['openings'] if o['wall']==wall], key=lambda o:o['offset'])
        stations=sorted({0,length,*(v for o in holes for v in (o['offset'],o['offset']+o['width']))})
        for a,b in zip(stations,stations[1:]): sh.dim(x+a*s,y-12,x+b*s,y-12,f'{b-a:g}')
        sh.dim(x,y-24,x+length*s,y-24,f'{length:g}')
        sh.dim(x-18,y,x-18,y+h*s,f'{h:g}')
        for o in holes:
            a,b=x+o['offset']*s,y+(h-o['sill']-o['height'])*s
            sh.rect(a,b,o['width']*s,o['height']*s,'#ffffff','OPENING')
            sh.text(a+2,b+6,o['id'],3)
        sh.text(265,55,'OPENING SCHEDULE / mm',4)
        for j,o in enumerate(holes):
            sh.text(265,68+j*20,f'{o["id"]}  {o["kind"]}  W{o["width"]:g} x H{o["height"]:g}')
            sh.text(265,75+j*20,f'Station {o["offset"]:g} | sill +{o["sill"]:g}',2.8)
        sh.text(20,222,'DATUM VIEW: stations increase west to east (N/S), south to north (E/W). Not an interior perspective.',3)
        sh.text(20,232,'FFL = 0. Heights above finished floor. Wall face only; furniture, MEP and construction layers not shown.',3)
        sh.text(20,242,'Nominal opening dimensions. Confirm frames, tolerances, lintels and waterproofing with responsible trade.',3)
        sheets.append(sh)
    return sheets


def dxf(data):
    """ASCII DXF in model-space mm, explicit INSUNITS=4, basic editable entities."""
    lines=['0','SECTION','2','HEADER','9','$INSUNITS','70','4','0','ENDSEC','0','SECTION','2','ENTITIES']
    def line(x,y,a,b,layer):
        lines.extend(map(str,['0','LINE','8',layer,'10',x,'20',y,'30',0,'11',a,'21',b,'31',0]))
    def rect(x,y,w,h,layer):
        for a,b,c,d in [(x,y,x+w,y),(x+w,y,x+w,y+h),(x+w,y+h,x,y+h),(x,y+h,x,y)]: line(a,b,c,d,layer)
    def text(x,y,label,layer='NOTES'):
        lines.extend(map(str,['0','TEXT','8',layer,'10',x,'20',y,'30',0,'40',100,'1',label]))
    r=data['room']; w,d,t=(r[k] for k in ('width','depth','wall_thickness'))
    # Split wall outlines at door/window stations. Opening boxes live on their own layer.
    for wall in WALLS:
        holes=sorted([o for o in data['openings'] if o['wall']==wall],key=lambda o:o['offset'])
        intervals=[]; prev=0
        for o in holes:
            if o['offset']>prev: intervals.append((prev,o['offset']))
            prev=max(prev,o['offset']+o['width'])
        if prev<wall_length(r,wall): intervals.append((prev,wall_length(r,wall)))
        def segment(a,b,layer):
            if wall in ('south','north'): rect(a,-t if wall=='south' else d,b-a,t,layer)
            else: rect(-t if wall=='west' else w,a,t,b-a,layer)
        for a,b in intervals: segment(a,b,'WALL')
        for o in holes: segment(o['offset'],o['offset']+o['width'],'OPENING')
    for f in data['furniture']:
        rect(f['x'],f['y'],f['width'],f['depth'],'FURNITURE');text(f['x']+30,f['y']+120,f['id'],'LABEL')
    line(0,-600,w,-600,'DIM');text(w/2,-550,f'{w:g} mm')
    line(-600,0,-600,d,'DIM');text(-1000,d/2,f'{d:g} mm')
    text(0,d+900,STAMP); text(0,d+650,f'Rev {data["project"]["revision"]} / mm / internal origin SW')
    lines.extend(['0','ENDSEC','0','EOF'])
    return '\n'.join(lines)+'\n'


def write_csv(path,fields,rows):
    with path.open('w',encoding='utf-8-sig',newline='') as file:
        writer=csv.DictWriter(file,fieldnames=fields);writer.writeheader()
        for row in rows:
            safe={key: ("'"+value if isinstance(value,str) and value.lstrip().startswith(('=','+','-','@')) else value) for key,value in row.items()}
            writer.writerow(safe)


def build(source,out,blender=False):
    data=validate(json.loads(source.read_text()))
    out=out.resolve();out.mkdir(parents=True,exist_ok=True)
    if source.resolve().is_relative_to(out): raise ValueError('Source project must be outside output directory')
    # Clear known optional artifacts on every successful rebuild; never show stale models.
    for name in ('scene.glb','scene.blend','render.png','scene.blend1','render-settings.json','manifest.json'):
        (out/name).unlink(missing_ok=True)
    (out/'project.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    sheets=drawings(data)
    pdf=canvas.Canvas(str(out/'drawings.pdf'),pagesize=(420*mm,297*mm))
    pdf.setTitle('Interior coordination drawings - '+data['project']['revision'])
    for sh in sheets:
        (out/f'{sh.number}.svg').write_text(sh.svg());sh.pdf(pdf)
    pdf.save();(out/'plan.dxf').write_text(dxf(data))
    write_csv(out/'furniture.csv',['id','name','kind','x','y','width','depth','height','color','material'],data['furniture'])
    write_csv(out/'openings.csv',['id','kind','wall','offset','width','height','sill'],data['openings'])
    r=data['room'];floor=r['width']*r['depth']/1e6
    walls=(2*(r['width']+r['depth'])*r['height']-sum(o['width']*o['height'] for o in data['openings']))/1e6
    write_csv(out/'materials.csv',['surface','finish','net_area_m2','basis'],[
        {'surface':'floor','finish':data['finishes']['floor']['name'],'net_area_m2':round(floor,3),'basis':'Net geometry; excludes waste, skirting and build-up'},
        {'surface':'wall','finish':data['finishes']['wall']['name'],'net_area_m2':round(walls,3),'basis':'One interior face; openings deducted; no reveals or waste'}])
    issues=review(data);(out/'review.json').write_text(json.dumps(issues,indent=2))
    (out/'handoff.md').write_text('# Coordination package / 工程協調草圖\n\n**NOT FOR CONSTRUCTION — 不可直接施工或下單。**\n\n'
        +'Project: '+data['project']['name']+' / '+data['project']['revision']+'\n\n'
        +'詳細圖面說明見已安裝 skill 的 references/drawing-handoff.zh-TW.md。尺寸單位 mm，模型單位 m；PDF 為 A3，100% 列印；比例請看各張圖框（通常 1:50，深房間平面 1:100）。優先以標註尺寸為準，不量螢幕截圖。\n\n'
        +'現階段只有單房幾何、家具包絡、門窗名義尺寸及牆面立面。未設計水電、天花、消防、防水與施工節點；沒有聲稱滿足任何建築法規。\n\n'
        +'## Outstanding review\n\n'+'\n'.join(f'- {i["id"]} / {i["topic"]}: {i["detail"]}' for i in issues)+'\n')
    if blender:
        binary=shutil.which('blender')
        if not binary: raise ValueError('Blender 4.3+ is required for --blender; install Blender or omit this flag for drawings only')
        subprocess.run([binary,'--background','--threads','4','--python-exit-code','1','--python',str(ROOT/'scripts/_internal/blender_scene.py'),'--',str(out/'project.json'),str(out)],check=True)
    files=['project.json','drawings.pdf','A101.svg',*[f'A20{i}.svg' for i in range(1,5)],'plan.dxf','furniture.csv','openings.csv','materials.csv','review.json','handoff.md']
    if blender: files+=['scene.glb','scene.blend','render.png','render-settings.json']
    manifest={'schema_version':'1.0','revision':data['project']['revision'],'status':'coordination_draft','has_model':blender,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'files':[]}
    for name in files:
        p=out/name
        if not p.is_file() or not p.stat().st_size: raise ValueError(f'Missing or empty output: {name}')
        manifest['files'].append({'name':name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(f'Built {len(files)} files: {out}; {len(issues)} unresolved review items; {STAMP}')
    return manifest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['validate','build']);parser.add_argument('source',type=Path)
    parser.add_argument('--out',type=Path,default=Path('output'));parser.add_argument('--blender',action='store_true')
    args=parser.parse_args()
    try:
        if args.command=='validate': validate(json.loads(args.source.read_text()));print('Valid project (not construction approval)')
        else: build(args.source,args.out,args.blender)
    except (ValueError,OSError,subprocess.CalledProcessError) as error:
        print(f'Error: {error}',file=sys.stderr);return 1
    return 0


if __name__=='__main__': sys.exit(main())
