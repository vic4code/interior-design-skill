#!/usr/bin/env python3
"""Publish coordinated A3 design studies from the shared room and joinery data.

Millimetres throughout. These are design-development sheets, not an approved
fabrication or electrical design. No render, logo or private project is required.
"""
import argparse
import csv
import hashlib
import html
import json
import math
import re
import textwrap
import unicodedata
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont, CIDEncoding
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.units import mm
from project import validate, dxf
from output_ownership import verify_output_directory, verify_inputs_outside

ROOT = Path(__file__).resolve().parents[2]
INK, MUTED, ACCENT, PALE = '#243345', '#66727c', '#986747', '#ece9e3'
INDEX = [('G000','Drawing register & design basis'),('A101','Dimensioned furniture plan'),
         ('A102','Lighting & power coordination'),('A201','South interior elevation'),
         ('A202','North interior elevation'),('J301','F05 sideboard - general arrangement'),
         ('J401','F05 casework - section & interfaces'),('S001','Schedules, finishes & open decisions')]

def number(n):
    return f'{n:g}'


def pdf_text_font(text):
    """Use the standard Traditional Chinese CID font when Latin is insufficient.

    MSung-Light is a PDF CJK font resource: no machine-specific font path,
    proprietary font file or network download is required.
    """
    if any(ord(c)>255 for c in text):
        if 'MSung-Light' not in pdfmetrics.getRegisteredFontNames():
            font=UnicodeCIDFont('MSung-Light')
            # Some ReportLab versions pair MSung (Adobe-CNS1) with UniGB,
            # which PDF readers reject. Explicitly select the matching CMap.
            font.encodingName='UniCNS-UCS2-H'
            font.encoding=CIDEncoding(font.encodingName)
            pdfmetrics.registerFont(font)
        return 'MSung-Light'
    return 'Helvetica'


def paragraph_lines(text,width):
    """Wrap CJK at ideograph boundaries; preserve existing English wrapping."""
    if not any(unicodedata.east_asian_width(c) in ('W','F') for c in text):
        return textwrap.wrap(text,width)
    lines=[];line='';used=0
    tokens=re.findall(r'-?[A-Za-z0-9]+(?:[._/:\-–][A-Za-z0-9]+)*|.',text,re.DOTALL)
    for token in tokens:
        if token=='\n':
            lines.append(line.rstrip());line='';used=0;continue
        weight=sum(2 if unicodedata.east_asian_width(c) in ('W','F') else 1 for c in token)
        # Keep dimensions, IDs and filenames intact when they fit a line.
        chunks=[token] if weight<=width else list(token)
        for chunk in chunks:
            weight=sum(2 if unicodedata.east_asian_width(c) in ('W','F') else 1 for c in chunk)
            if used+weight>width and line:
                lines.append(line.rstrip());line='';used=0
            if not line and chunk.isspace():continue
            line+=chunk;used+=weight
    if line:lines.append(line.rstrip())
    return lines


def joinery_geometry(project, spec):
    f = next(x for x in project['furniture'] if x['id'] == spec['object_id'])
    w,d,h = [f[k] for k in ('width','depth','height')]
    c,t,b,ph,dt,gap,clear,st = [spec[k] for k in ('carcass_thickness','top_thickness','back_thickness','plinth_height','door_thickness','door_gap','front_clearance','shelf_thickness')]
    bays=spec['bays']
    if not isinstance(bays,int) or bays < 1: raise ValueError('bays must be a positive integer')
    body_depth=d-dt-clear
    v=dict(width=w,depth=d,height=h,body_depth=body_depth,inner_depth=body_depth-b,
           bay_clear=(w-(bays+1)*c)/bays,leaf_width=(w-(bays+1)*gap)/bays,
           base_top=ph+c,top_under=h-t,shelf_top=spec['shelf_top_height'],
           shelf_bottom=spec['shelf_top_height']-st,door_top=h-t-gap,door_bottom=ph+gap,leaf_height=h-t-ph-2*gap)
    if min(v['bay_clear'],v['leaf_width'],v['inner_depth'],v['leaf_height']) <= 0: raise ValueError('Nonpositive joinery clear dimension')
    if not v['base_top'] < v['shelf_bottom'] < v['shelf_top'] < v['top_under']: raise ValueError('Shelf does not fit carcass')
    if min(c,t,b,ph,dt,gap,clear,st)<=0: raise ValueError('Joinery dimensions must be positive')
    for p in spec['service_points']:
        if not 0<=p['x']<=project['room']['width'] or not 0<=p['y']<=project['room']['depth'] or not 0<=p['z']<=project['room']['height']: raise ValueError('Service point outside room')
    return v

class Sheet:
    def __init__(self, code, title, revision, scale='AS SHOWN'):
        self.code,self.title,self.items=code,title,[]
        self.rect(10,10,400,277,stroke=.35)
        self.text(17,20,'INTERIOR / DESIGN DEVELOPMENT',3,ACCENT)
        self.text(17,29,title.upper(),5.1)
        self.text(403,20,code,5,anchor='end')
        self.line(10,35,410,35,.35)
        self.rect(10,264,400,23,stroke=.35)
        for x in (228,308,365): self.line(x,264,x,287,.25)
        self.text(15,270,'GALLERY LIVING / SYNTHETIC STYLE STUDY',2.7)
        self.text(15,276,'DESIGN COORDINATION / TECHNICAL DEVELOPMENT',2.7,ACCENT)
        self.text(15,282,'All dimensions mm. Assumed design measurements. Verify on site.',2.5,MUTED)
        self.text(233,270,'SCALE AT A3',2.4,MUTED); self.text(233,278,scale,3.4)
        self.text(313,270,'REVISION',2.4,MUTED); self.text(313,278,revision,3.4)
        self.text(370,270,'SHEET',2.4,MUTED); self.text(370,280,code,4.3)
    def line(self,x,y,a,b,width=.18,color=INK,dash=False):
        self.items.append(('line',(x,y,a,b,width,color,dash)))
    def rect(self,x,y,w,h,fill='none',stroke=.22,color=INK):
        self.items.append(('rect',(x,y,w,h,fill,stroke,color)))
    def text(self,x,y,t,size=3,color=INK,anchor='start'):
        self.items.append(('text',(x,y,str(t),size,color,anchor)))
    def circle(self,x,y,r,fill='none',width=.2,color=INK):
        self.items.append(('circle',(x,y,r,fill,width,color)))
    def arc(self,x,y,r,start,end,width=.18):
        pts=[(x+r*math.cos(math.radians(a)),y+r*math.sin(math.radians(a))) for a in [start+(end-start)*i/24 for i in range(25)]]
        for a,b in zip(pts,pts[1:]):self.line(*a,*b,width,MUTED,True)
    def paragraph(self,x,y,t,width=62,size=2.8,leading=4.6):
        for row in paragraph_lines(t,width): self.text(x,y,row,size); y+=leading
        return y
    def dimh(self,x1,x2,y,ref,label=None):
        for x in (x1,x2):self.line(x,ref,x,y+2,.1,MUTED)
        self.line(x1,y,x2,y,.13)
        for x in (x1,x2):self.line(x-1,y+1,x+1,y-1,.3)
        self.text((x1+x2)/2,y-1.8,label or number(x2-x1),2.6,anchor='middle')
    def dimv(self,y1,y2,x,ref,label):
        for y in (y1,y2):self.line(ref,y,x-2,y,.1,MUTED)
        self.line(x,y1,x,y2,.13)
        for y in (y1,y2):self.line(x-1,y+1,x+1,y-1,.3)
        self.text(x+2,(y1+y2)/2+.8,label,2.6)
    def tag(self,x,y,label):
        self.circle(x,y,3.2,'#ffffff');self.text(x,y+1,label,2.6,anchor='middle')
    def datum(self,x,y,label):
        self.line(x,y,x+10,y,.25);self.line(x,y,x+2,y-2,.25);self.line(x+2,y-2,x+4,y,.25)
        self.text(x+11,y+1,label,2.6,MUTED)
    def save(self,path,pdf):
        parts=['<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 420 297">','<rect width="420" height="297" fill="#ffffff"/>']
        for typ,p in self.items:
            if typ=='line':
                x,y,a,b,w,c,ds=p
                parts.append(f'<line x1="{x}" y1="{y}" x2="{a}" y2="{b}" stroke="{c}" stroke-width="{w}"'+(' stroke-dasharray="1.5 1"' if ds else '')+'/>')
                pdf.setStrokeColor(HexColor(c));pdf.setLineWidth(w*mm);pdf.setDash([1.5*mm,mm] if ds else []);pdf.line(x*mm,(297-y)*mm,a*mm,(297-b)*mm)
            elif typ=='rect':
                x,y,w,h,fill,sw,c=p
                parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{c}" stroke-width="{sw}"/>')
                pdf.setDash([]);pdf.setLineWidth(sw*mm);pdf.setStrokeColor(HexColor(c))
                if fill!='none':pdf.setFillColor(HexColor(fill))
                pdf.rect(x*mm,(297-y-h)*mm,w*mm,h*mm,fill=int(fill!='none'),stroke=int(sw>0))
            elif typ=='circle':
                x,y,r,fill,sw,c=p
                parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{c}" stroke-width="{sw}"/>')
                pdf.setDash([]);pdf.setLineWidth(sw*mm);pdf.setStrokeColor(HexColor(c))
                if fill!='none':pdf.setFillColor(HexColor(fill))
                pdf.circle(x*mm,(297-y)*mm,r*mm,fill=int(fill!='none'))
            else:
                x,y,t,size,c,anchor=p
                parts.append(f'<text x="{x}" y="{y}" font-family="Arial, sans-serif" font-size="{size}" fill="{c}" text-anchor="{anchor}">{html.escape(t)}</text>')
                pdf.setFillColor(HexColor(c));pdf.setFont(pdf_text_font(t),size*mm)
                fn={'start':pdf.drawString,'middle':pdf.drawCentredString,'end':pdf.drawRightString}[anchor];fn(x*mm,(297-y)*mm,t)
        path.write_text('\n'.join(parts+['</svg>']))
        pdf.showPage()


def table(sh,x,y,width,headers,rows,colwidths=None,step=9,size=2.7):
    widths=colwidths or [width/len(headers)]*len(headers)
    sh.rect(x,y,width,8,PALE,0)
    xx=x
    for title,w in zip(headers,widths):sh.text(xx+2,y+5.4,title,2.5);xx+=w
    y+=8
    for row in rows:
        sh.line(x,y+step,x+width,y+step,.1,'#d5d9dc');xx=x
        for value,w in zip(row,widths):sh.text(xx+2,y+5.6,str(value),size);xx+=w
        y+=step
    return y


def plan_geometry(sh,p,services=None):
    r=p['room'];s=1/40;ox,oy=58,69;W,D,T=r['width']*s,r['depth']*s,r['wall_thickness']*s
    sh.rect(ox-T,oy-T,W+2*T,D+2*T,PALE,.55)
    # poche hatching, restrained enough to keep the plan readable
    for i in range(int((W+2*T)/3)):
        xx=ox-T+i*3
        sh.line(xx,oy-T,xx+T,oy,.1,MUTED)
        sh.line(xx,oy+D,xx+T,oy+D+T,.1,MUTED)
    sh.rect(ox,oy,W,D,'#ffffff',.45)
    for o in p['openings']:
        a=o['offset']*s;b=o['width']*s
        if o['wall'] in ('north','south'):
            yy=oy-T if o['wall']=='north' else oy+D
            sh.rect(ox+a,yy,b,T,'#ffffff',.2)
            if o['kind']=='window':
                for off in (T*.32,T*.68):sh.line(ox+a,yy+off,ox+a+b,yy+off,.15)
            else:
                # assumed left hinge, inward leaf; nominal width is not clear opening
                sh.line(ox+a,oy+D,ox+a,oy+D-b,.3);sh.arc(ox+a,oy+D,b,-90,0)
            sh.text(ox+a+b/2,yy+T+5,o['id'],2.8,anchor='middle')
        else:
            yy=oy+D-a-b;xx=ox+W if o['wall']=='east' else ox-T
            sh.rect(xx,yy,T,b,'#ffffff',.2)
            for off in (T*.32,T*.68):sh.line(xx+off,yy,xx+off,yy+b,.15)
            sh.text(xx+T+2,yy+b/2,o['id'],2.8)
    for f in p['furniture']:
        x=ox+f['x']*s;y=oy+D-(f['y']+f['depth'])*s;w=f['width']*s;d=f['depth']*s
        sh.rect(x,y,w,d,'#f5f3ee',.3)
        if f['kind']=='sofa':
            sh.rect(x+2,y+2,w-4,3,PALE,.15)
            for i in range(3):sh.rect(x+2+i*(w-4)/3,y+6,(w-4)/3-1,d-8,'none',.15)
        elif f['kind']=='cabinet':
            for i in range(1,4):sh.line(x+i*w/4,y,x+i*w/4,y+d,.15)
        else:
            for xx in (x+1.4,x+w-2.5):
                for yy in (y+1.4,y+d-2.5):sh.rect(xx,yy,1.1,1.1,PALE,.15)
        sh.tag(x+w/2,y+d/2,f['id'])
    sh.dimh(ox,ox+W,oy-22,oy,str(r['width']))
    north=sorted({0,r['width'],*[v for o in p['openings'] if o['wall']=='north' for v in (o['offset'],o['offset']+o['width'])]})
    for a,b in zip(north,north[1:]):sh.dimh(ox+a*s,ox+b*s,oy-11,oy,number(b-a))
    sh.dimv(oy,oy+D,ox-26,ox,str(r['depth']))
    south=sorted({0,r['width'],*[v for o in p['openings'] if o['wall']=='south' for v in (o['offset'],o['offset']+o['width'])]})
    for a,b in zip(south,south[1:]):sh.dimh(ox+a*s,ox+b*s,oy+D+18,oy+D,number(b-a))
    sh.text(ox+W+12,oy-15,'N',3.4);sh.line(ox+W+13,oy-7,ox+W+13,oy-14,.4);sh.line(ox+W+13,oy-14,ox+W+11,oy-11,.4)
    # cabinet setting-out chain, independent of the opening chain
    cabinet=next(v for v in p['furniture'] if v['id']=='F05')
    stations=sorted({0,r['width'],cabinet['x'],cabinet['x']+cabinet['width']})
    for a,b in zip(stations,stations[1:]):sh.dimh(ox+a*s,ox+b*s,oy+D+35,oy+D,number(b-a))
    sh.text(ox,oy+D+47,'01 / PLAN  1:40     origin: internal SW corner; north up',2.8)
    east=sorted({0,r['depth'],*[v for o in p['openings'] if o['wall']=='east' for v in (o['offset'],o['offset']+o['width'])]})
    for a,b in zip(east,east[1:]):sh.dimv(oy+D-b*s,oy+D-a*s,ox+W+24,ox+W,number(b-a))
    if services:
        for pnt in services:
            x=ox+pnt['x']*s;y=oy+D-pnt['y']*s
            if pnt['system']=='lighting':
                sh.circle(x,y,3.5);sh.line(x-2,y-2,x+2,y+2);sh.line(x-2,y+2,x+2,y-2)
            else:sh.circle(x,y,2);sh.line(x-.7,y-1,x-.7,y+1);sh.line(x+.7,y-1,x+.7,y+1)
            sh.line(x+3,y-3,x+8,y-8,.15,ACCENT);sh.text(x+9,y-8,f"{pnt['id']} / +{pnt['z']} AFF",2.6,ACCENT)
    return ox,oy,s


def make_sheets(p,j,style):
    rev=p['project']['revision'];r=p['room'];g=joinery_geometry(p,j)
    sheets=[]
    def new(code,scale):
        sh=Sheet(code,dict(INDEX)[code],rev,scale);sheets.append(sh);return sh
    sh=new('G000','DRAWING REGISTER')
    sh.text(20,53,'A ROOM, FROM INTENT TO BUILDABLE QUESTIONS.',5.5)
    sh.paragraph(20,64,'A coordinated design-development set: shared geometry, dimensioned plans, interior elevations and casework interfaces. This study makes design decisions visible before detailed trade coordination.',105,3.2,5.8)
    table(sh,20,91,230,['SHEET','DELIVERABLE','SCALE'],[(a,b,{'A101':'1:40','A102':'1:40','A201':'1:30','A202':'1:30','J301':'1:20','J401':'1:5'}.get(a,'NTS')) for a,b in INDEX],[24,178,28],11)
    sh.text(270,97,'ISSUE BASIS / S01',3.6,ACCENT)
    yy=108
    for n in [f"Internal room {r['width']} x {r['depth']} x {r['height']} mm.",f"Wall thickness {r['wall_thickness']} mm is an assumed envelope.",'All opening sizes and locations are design assumptions; survey before setting out.',f"Finish study: {style['name']}. Geometry is common to all style variants.",'Elevation arrows reference interior views: south is east-left, north is west-left.','Door hinge and inward swing are proposed. Nominal 900 leaf is not a certified clear opening.','Trade release requires the specific decisions in S001 and hardware review in J401.']:
        yy=sh.paragraph(270,yy,n,43,2.9,4.8)+6
    sh.text(20,214,'COORDINATION WORKFLOW',3.5,ACCENT)
    for x,num,title,note in [(20,'01','CONFIRM','Survey / dimensions'),(118,'02','COORDINATE','Trades / equipment'),(216,'03','DETAIL','Hardware / interfaces'),(314,'04','RELEASE','Local professional review')]:
        sh.text(x,229,num,7,MUTED);sh.text(x+18,224,title,3.1);sh.text(x+18,231,note,2.6)
    sh=new('A101','1:40')
    plan_geometry(sh,p)
    sh.text(254,52,'LAYOUT / SETTING-OUT',3.6,ACCENT)
    table(sh,254,61,145,['ID','WIDTH x DEPTH x HEIGHT'],[(f['id'],f"{f['width']} x {f['depth']} x {f['height']}") for f in p['furniture']],[22,123],10)
    y=133
    for f in p['furniture']:
        sh.text(256,y,f"{f['id']}  {f['name']}",2.9);sh.text(256,y+5,f"SW origin: X {f['x']} / Y {f['y']}",2.6,MUTED);y+=14
    sh.paragraph(256,211,'Furniture outlines are nominal envelopes. F05 is developed on J301/J401. No egress, accessibility or operational clearance approval is implied.',49,2.8)
    sh.text(58,248,'Key: heavy line = cut wall; fine line = furniture; dashed arc = proposed door swing.',2.7,MUTED)
    sh=new('A102','1:40')
    plan_geometry(sh,p,j['service_points'])
    sh.text(254,52,'SERVICE POINT PROPOSAL',3.6,ACCENT)
    table(sh,254,62,145,['ID','X / Y','AFF'],[(v['id'],f"{v['x']} / {v['y']}",v['z']) for v in j['service_points']],[20,86,39],12)
    y=118
    for text in ['AFF = above finished floor. XY positions reference inside SW corner.','L01: pendant design position. Ceiling anchor and suspension require product/substrate selection.','P01: desk power proposal at north wall; confirm plugs, cable paths and equipment access.','P02: power proposal above F05; coordinate finish, faceplate and cable route.','No circuits, loads, protective devices or concealed routes have been designed in this set. Electrical trade must develop these against the actual installation.']:
        y=sh.paragraph(256,y,text,49,2.8,4.8)+8
    # interior elevations, drawn in actual viewing direction
    for code,wall in [('A201','south'),('A202','north')]:
        sh=new(code,'1:30');s=1/30;ox=42;fy=176;ww=r['width']*s;hh=r['height']*s
        sh.rect(ox,fy-hh,ww,hh,'#faf9f6',.4);sh.line(ox-5,fy,ox+ww+5,fy,.55)
        def ex(a,w=0):return ox+((r['width']-a-w) if wall=='south' else a)*s
        for o in [v for v in p['openings'] if v['wall']==wall]:
            x=ex(o['offset'],o['width']);y=fy-(o['sill']+o['height'])*s
            sh.rect(x,y,o['width']*s,o['height']*s,'#ffffff',.4)
            if o['kind']=='window':
                sh.rect(x+1,y+1,o['width']*s-2,o['height']*s-2,'none',.18);sh.line(x+o['width']*s/2,y,x+o['width']*s/2,fy-o['sill']*s,.22)
            sh.text(x+o['width']*s/2,y-3,o['id'],3,anchor='middle')
            if o['kind']=='door':sh.circle(x+o['width']*s-3,fy-o['height']*s*.48,.65)
        fs=[v for v in p['furniture'] if (v['id']=='F05' if wall=='south' else v['id'] in ('F01','F03','F04'))]
        for f in fs:
            x=ex(f['x'],f['width']);y=fy-f['height']*s;w=f['width']*s;h=f['height']*s
            sh.rect(x,y,w,h,'#ede8df',.25)
            if f['kind']=='cabinet':
                for k in range(1,j['bays']):sh.line(x+k*w/j['bays'],y,x+k*w/j['bays'],fy-j['plinth_height']*s,.15)
                sh.line(x,fy-j['plinth_height']*s,x+w,fy-j['plinth_height']*s,.2)
            elif f['kind']=='table':sh.line(x,y+2,x+w,y+2,.2);sh.rect(x,y+2,1.5,h-2);sh.rect(x+w-1.5,y+2,1.5,h-2)
            elif f['kind']=='sofa':
                sh.rect(x+2,y+2,w-4,h*.38,'none',.15)
                sh.line(x,y+h*.64,x+w,y+h*.64,.2)
                for k in (1,2):sh.line(x+k*w/3,y+h*.4,x+k*w/3,y+h*.64,.15)
                sh.rect(x+2,fy-4,1.7,4,'#ffffff',.15);sh.rect(x+w-3.7,fy-4,1.7,4,'#ffffff',.15)
            elif f['kind']=='chair':sh.line(x,y+h*.5,x+w,y+h*.5,.2)
            label_y=fy+7+(8 if f['id']=='F04' else 0)
            sh.line(x+w/2,fy+1,x+w/2,label_y-3,.12,MUTED)
            sh.text(x+w/2,label_y,f['id']+(' / projection' if wall=='north' else ''),2.6,anchor='middle')
        sh.dimh(ox,ox+ww,fy-hh-18,fy-hh,str(r['width']))
        holes=[v for v in p['openings'] if v['wall']==wall]
        stations=sorted({0,r['width'],*[a for v in holes for a in (v['offset'],v['offset']+v['width'])]})
        for a,b in zip(stations,stations[1:]):
            x1,x2=sorted((ex(a),ex(b)));sh.dimh(x1,x2,fy-hh-8,fy-hh,number(b-a))
        sh.dimv(fy-hh,fy,ox-18,ox,str(r['height']))
        if wall=='north':
            o=next(v for v in p['openings'] if v['wall']==wall)
            sh.dimv(fy-o['sill']*s,fy,ox+ww+7,ox+ww,str(o['sill']))
            sh.dimv(fy-(o['sill']+o['height'])*s,fy-o['sill']*s,ox+ww+7,ox+ww,str(o['height']))
        else:
            f=next(v for v in fs if v['id']=='F05');sh.dimv(fy-f['height']*s,fy,ox+ww+7,ox+ww,str(f['height']))
            door=next(v for v in holes if v['kind']=='door')
            sh.dimv(fy-door['height']*s,fy,ox+ww+21,ox+ww,str(door['height']))
        sh.datum(ox+ww+22,fy,'+0 FFL');sh.datum(ox+ww+22,fy-hh,f"+{r['height']} ceiling")
        sh.text(42,211,f"01 / {wall.upper()} INTERIOR ELEVATION   1:30",3.5,ACCENT)
        sh.paragraph(42,223,'View faces '+wall+'. Horizontal screen direction: '+('east to west.' if wall=='south' else 'west to east. Furniture projected in elevation; distance from wall remains as A101.')+' Window sizes are nominal; frame, reveal and glazing specifications require supplier coordination.',105,2.9)
    sh=new('J301','1:20')
    f=next(v for v in p['furniture'] if v['id']==j['object_id']);s=1/20;x=38;y=113;w=g['width']*s;h=g['height']*s;d=g['depth']*s
    sh.text(38,49,'F05 / CUSTOM LOW SIDEBOARD',4,ACCENT)
    sh.rect(x,y-h,w,h,PALE,.35);sh.line(x,y-j['plinth_height']*s,x+w,y-j['plinth_height']*s,.25);sh.line(x,y-h+j['top_thickness']*s,x+w,y-h+j['top_thickness']*s,.25)
    for i in range(j['bays']):
        xx=x+(j['door_gap']+i*(g['leaf_width']+j['door_gap']))*s
        sh.rect(xx,y-g['door_top']*s,g['leaf_width']*s,g['leaf_height']*s,'none',.18)
        sh.line(xx+g['leaf_width']*s-2,y-20,xx+g['leaf_width']*s-2,y-16,.3)
    sh.dimh(x,x+w,y-h-13,y-h,str(g['width']));sh.dimv(y-h,y,x-13,x,str(g['height']));sh.text(x,y+10,'01 / FRONT ELEVATION   1:20',2.9)
    yy=159;sh.rect(x,yy,w,d,PALE,.35)
    sh.line(x,yy+d-(j['door_thickness']+j['front_clearance'])*s,x+w,yy+d-(j['door_thickness']+j['front_clearance'])*s,.18)
    sh.dimv(yy,yy+d,x-13,x,str(g['depth']));sh.text(x,yy+d+10,'02 / PLAN   1:20',2.9)
    xx=183;sh.rect(xx,y-h,d,h,PALE,.35);sh.line(xx,y-j['plinth_height']*s,xx+d,y-j['plinth_height']*s,.25);sh.dimh(xx,xx+d,y-h-13,y-h,str(g['depth']));sh.text(xx,y+10,'03 / SIDE  1:20',2.9)
    sh.text(250,50,'CONSTRUCTION INTENT',3.5,ACCENT)
    y0=62
    for txt in [f"Overall W {g['width']} / D {g['depth']} / H {g['height']}.",f"{j['bays']} bays, clear width {number(g['bay_clear'])} each between {j['carcass_thickness']} mm dividers.",f"{j['bays']} overlay leaves: {number(g['leaf_width'])} wide each; {j['door_gap']} mm perimeter/inter-leaf design gaps.",f"Depth stack: {j['door_thickness']} door + {j['front_clearance']} gap + {g['body_depth']} body = {g['depth']}.",f"Body internal depth: {g['body_depth']} - {j['back_thickness']} back = {g['inner_depth']}.",f"Door height {g['leaf_height']} is provisional: top +{g['door_top']} / bottom +{g['door_bottom']}. Select hinges before overlay/drilling release.",'Section, shelf datum and unresolved fixing interfaces: J401. Finish sample: S001.']:
        y0=sh.paragraph(250,y0,txt,49,2.9,5)+8
    sh.text(38,226,'FINISH',3,ACCENT);sh.paragraph(38,234,f"{style['name']}: {j['finish']}. Grain direction, edge treatment and sheen require an approved physical sample.",109,2.8)
    sh=new('J401','1:5 / 1:15')
    # longitudinal side section. Rear at x=48, front at x=138.
    s=.2;x=48;fy=218;top=fy-g['height']*s;body=g['body_depth']*s;back=j['back_thickness']*s
    sh.text(28,49,'01 / VERTICAL DEPTH SECTION   1:5',3.3,ACCENT)
    sh.rect(x,top,g['depth']*s,j['top_thickness']*s,PALE,.45)
    sh.rect(x,top+j['top_thickness']*s,back,(g['top_under']-j['plinth_height'])*s,PALE,.35)
    sh.rect(x,fy-g['base_top']*s,body,j['carcass_thickness']*s,PALE,.4)
    sh.rect(x+back,fy-g['shelf_top']*s,g['inner_depth']*s,j['shelf_thickness']*s,PALE,.4)
    sh.rect(x+12,fy-j['plinth_height']*s,body-18,j['plinth_height']*s,PALE,.4)
    sh.rect(x+(g['body_depth']+j['front_clearance'])*s,fy-g['door_top']*s,j['door_thickness']*s,g['leaf_height']*s,PALE,.4)
    sh.line(x-10,fy,x+g['depth']*s+10,fy,.5)
    sh.dimh(x,x+g['depth']*s,top-11,top,str(g['depth']))
    sh.dimv(top,fy,x-16,x,str(g['height']))
    ys=[(z,number(z)) for z in (0,j['plinth_height'],g['base_top'],g['shelf_bottom'],g['shelf_top'],g['top_under'],g['height'])]
    # distinct leaders rather than overlapping 18/20 mm text at 1:5
    for z,label in ys:
        yy=fy-z*s;end_y=yy
        if z==g['height']:end_y-=4
        if z==g['base_top']:end_y-=3
        if z==g['shelf_top']:end_y-=3
        sh.line(x+g['depth']*s+2,yy,158,end_y,.12,MUTED);sh.text(160,end_y+1,'+'+label,2.6)
    sh.text(28,246,'Rear / wall side',2.8);sh.text(105,246,'Front / door side',2.8)
    sh.text(205,49,'02 / CARCASS WIDTH STACK',3.3,ACCENT)
    # width diagram at 1:20, dimension chain values all derived
    xx=205;yy=67;ss=1/15;ww=g['width']*ss;sh.rect(xx,yy,ww,21,PALE,.4)
    pos=0
    for i in range(j['bays']+1):
        sh.rect(xx+pos*ss,yy,j['carcass_thickness']*ss,21,INK,.2)
        if i<j['bays']:
            sh.text(xx+(pos+j['carcass_thickness']+g['bay_clear']/2)*ss,yy+12,number(g['bay_clear']),2.7,anchor='middle')
        pos+=j['carcass_thickness']+g['bay_clear']
    sh.dimh(xx,xx+ww,yy+33,yy+21,str(g['width']))
    sh.text(205,114,f"{j['bays']} x {number(g['bay_clear'])} clear + {j['bays']+1} x {j['carcass_thickness']} panels = {g['width']}",2.9)
    sh.text(205,121,'Width diagram 1:15; written dimensions govern.',2.6,MUTED)
    yy=137
    notes=[f"A / TOP {j['top_thickness']} mm. Underside +{g['top_under']}. Edge/overhang requires sample approval.",f"B / SHELF {j['shelf_thickness']} mm. Top +{g['shelf_top']}; bottom +{g['shelf_bottom']}. Clear below {g['shelf_bottom']-g['base_top']} / above {g['top_under']-g['shelf_top']}.",f"C / BASE {j['carcass_thickness']} mm over {j['plinth_height']} mm plinth. Plinth setback shown as design intent; leveling method unresolved.",f"D / BACK {j['back_thickness']} mm, full-back depth concept. Joint/rebate and rear service penetrations unresolved.",f"E / FRONT {j['door_thickness']} mm + {j['front_clearance']} mm front gap. No hinge cups, screw pattern or opening angle selected.",'F / WALL FIXING: confirm substrate, anchorage and loading. No fixing capacity or hardware approval is asserted.']
    for txt in notes:yy=sh.paragraph(205,yy,txt,64,2.7,4.4)+5
    sh=new('S001','SCHEDULES / NTS')
    sh.text(20,49,'FURNITURE & OPENINGS',3.6,ACCENT)
    table(sh,20,57,218,['ID','ITEM','W x D x H / mm'],[(f['id'],f['name'],f"{f['width']} x {f['depth']} x {f['height']}") for f in p['furniture']],[18,105,95],10)
    table(sh,20,122,218,['ID','WALL / OFFSET','W x H / SILL'],[(o['id'],f"{o['wall']} / {o['offset']}",f"{o['width']} x {o['height']} / {o['sill']}") for o in p['openings']],[18,105,95],10)
    sh.text(20,177,'FINISH INTENT / '+style['name'].upper(),3.3,ACCENT)
    for idx,(key,value) in enumerate(style['palette'].items()):
        sh.rect(20,185+idx*9,7,5,value,.1);sh.text(32,189+idx*9,f"{key.upper()} / {value}",2.8)
    sh.text(255,49,'DECISIONS BEFORE TRADE RELEASE',3.5,ACCENT)
    yy=61
    for tag,txt in issues():
        sh.text(255,yy,tag,3,ACCENT);yy=sh.paragraph(272,yy,txt,45,2.8,4.5)+9
    sh.paragraph(255,230,'Evidence: shared project.json + joinery.json; manifest includes source and output SHA-256 hashes. No surveyed or engineer-approved measurements.',48,2.6)
    return sheets


def issues():
    return [('I01','Site survey: verify room, wall build-up, all openings and finished datums.'),('I02','Door supplier: confirm handing, frame, actual leaf and clear opening; check use and circulation.'),('I03','Electrical trade: develop circuiting, loads, protection, routes and mounting details for proposed points.'),('I04','Joiner: select hinges, overlays, door heights, drilling, shelf supports and joints before shop drawings.'),('I05','Site/joiner: establish wall substrate, anchors, load criteria, plinth leveling and restraints.'),('I06','Designer/client: approve veneer/lacquer, grain, edge samples, sheen and all selected fixtures.')]


def write_csv(path,fields,rows):
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows)

def build(project_path,joinery_path,out,style='mcm'):
    verify_inputs_outside(out,[project_path,joinery_path])
    out=verify_output_directory(out,expected={'format':'drawing-studies-v1'})
    previous_files=set(json.loads((out/'manifest.json').read_text())['files']) if (out/'manifest.json').is_file() else set()
    p=json.loads(Path(project_path).read_text());j=json.loads(Path(joinery_path).read_text())
    validate(p);g=joinery_geometry(p,j)
    styles=json.loads((ROOT/'assets/style-studies/styles.json').read_text())
    if style not in styles:raise ValueError(f'Unknown style {style}')
    sheets=make_sheets(p,j,styles[style]);out.mkdir(parents=True,exist_ok=True)
    pdf=canvas.Canvas(str(out/'design-coordination.pdf'),pagesize=(420*mm,297*mm),pageCompression=1,invariant=1)
    pdf.setTitle('Gallery Living - design coordination');pdf.setAuthor('Interior Design Skill')
    for sh in sheets:sh.save(out/(sh.code+'.svg'),pdf)
    pdf.save()
    (out/'project.json').write_text(json.dumps(p,indent=2)+'\n');(out/'joinery.json').write_text(json.dumps(j,indent=2)+'\n')
    (out/'plan.dxf').write_text(dxf(p))
    write_csv(out/'furniture.csv',['id','name','x','y','width','depth','height','material'],p['furniture'])
    write_csv(out/'openings.csv',['id','kind','wall','offset','width','height','sill'],p['openings'])
    write_csv(out/'materials.csv',['finish','color','status'],[dict(finish=k,color=v,status='design palette; physical sample pending') for k,v in styles[style]['palette'].items()])
    write_csv(out/'joinery.csv',['parameter','value','units'],[dict(parameter=k,value=v,units='mm') for k,v in g.items()])
    write_csv(out/'issues.csv',['id','decision','status'],[dict(id=k,decision=v,status='open') for k,v in issues()])
    files=[out/(s.code+'.svg') for s in sheets]+[out/n for n in ['design-coordination.pdf','project.json','joinery.json','plan.dxf','furniture.csv','materials.csv','openings.csv','joinery.csv','issues.csv']]
    digest=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
    sources={name:digest(path) for name,path in [('project.json',project_path),('joinery.json',joinery_path),('styles.json',ROOT/'assets/style-studies/styles.json'),('build_drawing_studies.py',__file__)]}
    # All old registrations were verified before writing; prune obsolete sheets
    # only once every replacement artifact has been produced successfully.
    for name in previous_files-{f.name for f in files}:(out/name).unlink()
    (out/'manifest.json').write_text(json.dumps(dict(format='drawing-studies-v1',units='mm',style=style,status='design coordination / technical development',sources=sources,files={f.name:digest(f) for f in files}),indent=2)+'\n')
    return sheets


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',type=Path,default=ROOT/'assets/style-studies/project.json')
    parser.add_argument('--joinery',type=Path,default=ROOT/'assets/style-studies/joinery.json')
    parser.add_argument('--out',type=Path,default=Path('output/drawing-studies'))
    parser.add_argument('--style',default='mcm')
    args=parser.parse_args();sheets=build(args.project,args.joinery,args.out,args.style)
    print(f'Generated {len(sheets)} coordinated A3 sheets, PDF, DXF, schedules and hash manifest in {args.out}')

if __name__=='__main__':main()
