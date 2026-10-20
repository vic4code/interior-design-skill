#!/usr/bin/env python3
"""Draw model-derived coordination views from extract_native_model.py inventory.

A selection configuration may add views with kind plan/elevation/section,
include/exclude regular expressions, axis x/y/z and offset_mm for actual cuts.
Optional typed annotations and verified face-to-face dimension chains preserve
their source basis. Neither model envelopes nor room labels approve fabrication.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import textwrap
from build_drawing_studies import Sheet, INK, MUTED, ACCENT, PALE, table, number
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

AXES={'x':0,'y':1,'z':2}


def bounds(objects):
    if not objects:raise ValueError('Selection matched no objects')
    return dict(min=[min(o['bbox_mm']['min'][k] for o in objects) for k in range(3)],max=[max(o['bbox_mm']['max'][k] for o in objects) for k in range(3)])


def select(objects,include='.*',exclude=r'^$'):
    inc=re.compile(include,re.I);exc=re.compile(exclude,re.I)
    return [o for o in objects if any(inc.search(v) for v in [o['name']]+o.get('collections',[])) and not any(exc.search(v) for v in [o['name']]+o.get('collections',[]))]


def section_segments(obj,axis,offset,tolerance=.01):
    """Intersect evaluated mesh triangles with a real world-coordinate plane."""
    vertices=obj.get('vertices_mm',[]);result=[];seen=set()
    for triangle in obj.get('triangles',[]):
        points=[vertices[i] for i in triangle];intersections=[]
        distances=[p[axis]-offset for p in points]
        if all(abs(d)<=tolerance for d in distances):continue  # coplanar face, not a section boundary
        for a,b,da,db in zip(points,points[1:]+points[:1],distances,distances[1:]+distances[:1]):
            if abs(da)<=tolerance:intersections.append(a)
            if da*db < -tolerance*tolerance:
                t=da/(da-db);intersections.append([a[k]+t*(b[k]-a[k]) for k in range(3)])
        unique={tuple(round(v,3) for v in p):p for p in intersections}
        pts=list(unique.values())
        if len(pts)==2:
            key=tuple(sorted(tuple(round(v,2) for v in p) for p in pts))
            if key not in seen:seen.add(key);result.append(pts)
    return result



def planar_station_evidence(objects,axis,coordinate,region=None,tolerance=.15):
    """Locate a real planar triangle face at a measured axis station.

    A vertex at the requested coordinate is insufficient. The entire triangle
    must lie at that station, with its normal perpendicular to the station
    plane (within 0.1 degree). An optional world-space bbox clips candidate
    faces to the selected annotation region. This verifies plane positions;
    it does not infer that the space between them is a functional clearance.
    """
    def area_vector(poly):
        if len(poly)<3:return [0,0,0]
        result=[0,0,0];origin=poly[0]
        for index in range(1,len(poly)-1):
            a=[poly[index][k]-origin[k] for k in range(3)]
            b=[poly[index+1][k]-origin[k] for k in range(3)]
            cross=[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
            result=[x+y for x,y in zip(result,cross)]
        return result
    def clipped(poly):
        if region is None:return poly
        for k in range(3):
            for boundary,sign in ((region['min'][k],1),(region['max'][k],-1)):
                result=[]
                for a,b in zip(poly,poly[1:]+poly[:1]):
                    da=(a[k]-boundary)*sign;db=(b[k]-boundary)*sign
                    if da>=0:result.append(a)
                    if (da<0<=db) or (db<0<=da):
                        ratio=da/(da-db);result.append([a[j]+ratio*(b[j]-a[j]) for j in range(3)])
                poly=result
                if len(poly)<3:return []
        return poly
    for obj in objects:
        vertices=obj.get('vertices_mm',[])
        for index,tri in enumerate(obj.get('triangles',[])):
            points=[vertices[i] for i in tri]
            if not all(abs(p[axis]-coordinate)<=tolerance for p in points):continue
            normal=area_vector(points);length=math.sqrt(sum(v*v for v in normal))
            if length<=1e-8:continue
            alignment=abs(normal[axis])/length
            if alignment<math.cos(math.radians(.1)):continue
            polygon=clipped(points)
            if math.sqrt(sum(v*v for v in area_vector(polygon)))<=1e-8:continue
            return dict(object_id=obj['id'],triangle_index=index,station_mm=coordinate,
                        axis='XYZ'[axis],normal_alignment=alignment,region_mm=region)
    return None


def projected_segments(obj,cut_axis=None,cut_offset=None):
    vertices=obj.get('vertices_mm',[]);segments=[]
    for a,b in obj.get('feature_edges',[]):
        p,q=vertices[a],vertices[b]
        if cut_axis is not None:
            da=p[cut_axis]-cut_offset;db=q[cut_axis]-cut_offset
            if da>0 and db>0:continue
            if da*db<0:
                ratio=da/(da-db);cross=[p[k]+ratio*(q[k]-p[k]) for k in range(3)]
                if da>0:p=cross
                else:q=cross
        segments.append((p,q))
    return segments


class NativeSheet(Sheet):
    def __init__(self,code,title,project,revision,scale,chinese=False):
        self.code,self.title,self.items=code,title,[]
        self.rect(10,10,400,277,stroke=.35)
        self.text(17,20,('原生模型／設計與施工介面協調' if chinese else 'NATIVE MODEL / DESIGN COORDINATION'),3,ACCENT)
        self.text(17,29,title.upper()[:77],4.6)
        self.text(403,20,code,4.5,anchor='end');self.line(10,35,410,35,.35)
        self.rect(10,264,400,23,stroke=.35)
        for x in (236,315,365):self.line(x,264,x,287,.25)
        self.text(15,270,project[:90],2.7)
        self.text(15,276,('模型實際幾何擷取／現場與工種尚待覆核' if chinese else 'MODEL-DERIVED / SITE AND TRADE VERIFICATION PENDING'),2.6,ACCENT)
        self.text(15,282,('單位 mm；標註值為模型證據，製作前須覆核現場、五金與接合。' if chinese else 'Units mm. Written values are model evidence; no fabrication approval.'),2.5,MUTED)
        self.text(241,270,('A3 列印比例' if chinese else 'SCALE AT A3'),2.4,MUTED);self.text(241,279,scale,3.4)
        self.text(320,270,('版次' if chinese else 'REVISION'),2.4,MUTED);self.text(320,279,revision,3.4)
        self.text(370,270,('圖號' if chinese else 'SHEET'),2.4,MUTED);self.text(370,280,code,4.2)


def view_axes(view):
    axis=AXES[view.get('axis','z' if view['kind']=='plan' else 'y')]
    return axis,([0,1] if axis==2 else ([0,2] if axis==1 else [1,2]))


def expand_dimension_chains(view):
    """Expand configured chains into the same verified-face path as key dimensions."""
    result=list(view.get('dimensions',[]))
    for chain in view.get('dimension_chains',[]):
        if not chain.get('basis'):raise ValueError('Dimension chains require a source basis')
        axis=AXES[chain['axis']];stations=chain['stations_mm']
        if len(stations)<2 or any(not isinstance(v,(int,float)) or not math.isfinite(v) for v in stations) or any(b<=a for a,b in zip(stations,stations[1:])):
            raise ValueError('Dimension-chain stations must be finite and increasing')
        anchor=chain['at_mm']
        if len(anchor)!=3 or any(not isinstance(v,(int,float)) or not math.isfinite(v) for v in anchor):raise ValueError('Dimension chain requires a finite world-space anchor')
        for i,(a,b) in enumerate(zip(stations,stations[1:]),1):
            start=list(anchor);end=list(anchor);start[axis]=a;end[axis]=b
            item={k:v for k,v in chain.items() if k not in ('stations_mm','at_mm')}
            item.update(id=chain['id']+'.'+str(i),start_mm=start,end_mm=end,display_id=False)
            result.append(item)
    ids=[d['id'] for d in result]
    if len(set(ids))!=len(ids):raise ValueError('Duplicate dimension IDs in view')
    return result


def draw_annotations(sh,view,config,xy,bbox):
    """Draw explicit sourced annotations, never infer a building or product claim."""
    rows=[];known_sheets={v.get('sheet',f'M{i:03}') for i,v in enumerate(config.get('views',[]),1)}
    for item in view.get('annotations',[]):
        kind=item.get('kind')
        if kind not in ('room','text','leader','sectionmark','opening','material'):raise ValueError('Unsupported annotation kind')
        if not item.get('basis'):raise ValueError('Annotations require a source basis')
        point=item.get('at_mm',[])
        if len(point)!=3 or any(not isinstance(v,(int,float)) or not math.isfinite(v) for v in point):raise ValueError('Annotation requires finite world-space coordinates')
        if any(point[k]<bbox['min'][k]-1 or point[k]>bbox['max'][k]+1 for k in range(3)):raise ValueError('Annotation anchor lies outside selected geometry')
        if item.get('reference_sheet') and item['reference_sheet'] not in known_sheets:raise ValueError('Annotation references an unknown drawing sheet')
        x,y=xy(point);label=item.get('text','');code=item.get('id','')
        if kind=='room':
            width=item.get('paper_width_mm',26)
            sh.rect(x-width/2,y-6,width,12,'#ffffff',.12,'#b9c1c2')
            sh.text(x,y-1,code,2.4,ACCENT,anchor='middle');sh.text(x,y+3.5,label,3.0,INK,anchor='middle')
        elif kind in ('opening','material'):
            offset=item.get('paper_offset_mm',[0,-7]);xx,yy=x+offset[0],y+offset[1]
            sh.line(x,y,xx,yy,.18,ACCENT);sh.rect(xx-6,yy-2.8,12,5.6,'#ffffff',.2,ACCENT);sh.text(xx,yy+1,code,2.5,ACCENT,anchor='middle')
        elif kind=='sectionmark':
            xx,yy=x+item.get('paper_offset_mm',[0,-9])[0],y+item.get('paper_offset_mm',[0,-9])[1]
            sh.line(x,y,xx,yy,.25,ACCENT);sh.circle(xx,yy,5,'#ffffff',.25,ACCENT)
            sh.line(xx-4.7,yy,xx+4.7,yy,.18,ACCENT);sh.text(xx,yy-1.1,code,2.4,ACCENT,anchor='middle');sh.text(xx,yy+3.2,item['reference_sheet'],2,ACCENT,anchor='middle')
        elif kind=='leader':
            offset=item.get('paper_offset_mm',[10,-10]);xx,yy=x+offset[0],y+offset[1]
            sh.circle(x,y,.7,ACCENT,0,ACCENT);sh.line(x,y,xx,yy,.2,ACCENT)
            sh.paragraph(xx,yy-2,(code+' '+label).strip(),item.get('wrap',30),2.6,4)
        else:
            sh.paragraph(x,y,(code+' '+label).strip(),item.get('wrap',36),item.get('size',2.8),4)
        rows.append(dict(item,view_sheet=view.get('sheet')))
    return rows


def draw_view(inventory,view,code,config,issue_rows):
    objects=select(inventory['objects'],view.get('include','.*'),view.get('exclude',r'^$'))
    bbox=bounds(objects);axis,(haxis,vaxis)=view_axes(view)
    if view['kind']=='plan':
        plan_cut=view.get('offset_mm',bbox['min'][2]+1200)
        objects=[o for o in objects if o['bbox_mm']['min'][2]<=plan_cut]
        bbox=bounds(objects)
    extents=[bbox['max'][k]-bbox['min'][k] for k in range(3)]
    need=max(extents[haxis]/250,extents[vaxis]/154)
    scale=view.get('scale') or next((s for s in (5,10,20,25,30,40,50,75,100,150,200,500) if s>=need),math.ceil(need/100)*100)
    area=view.get('drawing_area_mm',[275,165])
    if len(area)!=2 or not 0<area[0]<=285 or not 0<area[1]<=200:raise ValueError('Invalid drawing area')
    if scale<=0 or extents[haxis]/scale>area[0] or extents[vaxis]/scale>area[1]:raise ValueError(f'{code}: requested scale does not fit sheet')
    chinese=config.get('language')=='zh-TW'
    sh=NativeSheet(code,view['title'],config.get('project','Native model coordination'),config.get('revision','N01'),f'1:{number(scale)}',chinese=chinese)
    ox,oy=view.get('drawing_origin_mm',[35,65]);w=extents[haxis]/scale;h=extents[vaxis]/scale
    if not (15<=ox and 40<=oy and ox+w<=315 and oy+h<=257):raise ValueError('Drawing bounds exceed printable view area')
    flip=view.get('flip_horizontal',False)
    def xy(p):
        x=(bbox['max'][haxis]-p[haxis] if flip else p[haxis]-bbox['min'][haxis])/scale
        y=(bbox['max'][vaxis]-p[vaxis])/scale
        return ox+x,oy+y
    cut=view.get('offset_mm',sum((bbox['min'][axis],bbox['max'][axis]))/2)
    if view['kind']=='plan':cut=view.get('offset_mm',bbox['min'][2]+1200)
    projection_count=section_count=0;omitted=[];marks=[]
    for obj in objects:
        missing=obj.get('geometry_status')!='evaluated_mesh'
        if missing:
            omitted.append(obj['id']);continue
        segments=[]
        if view['kind']!='section':
            segments=projected_segments(obj,axis if view['kind']=='plan' else None,cut if view['kind']=='plan' else None)
        if len(segments)>view.get('max_projected_edges_per_object',12000):
            omitted.append(obj['id']+' projection');segments=[]
        seen=set()
        for p,q in segments:
            a,b=xy(p),xy(q)
            if math.dist(a,b)<.12:continue
            key=tuple(sorted(tuple(round(v/.08) for v in t) for t in (a,b)))
            if key in seen:continue
            seen.add(key);sh.line(*a,*b,.10,'#9a9fa3');projection_count+=1
        if view['kind'] in ('plan','section'):
            for p,q in section_segments(obj,axis,cut):
                a,b=xy(p),xy(q)
                if math.dist(a,b)<.04:continue
                sh.line(*a,*b,.38,INK);section_count+=1
        if view.get('tag_objects',False) and obj.get('geometry_status')=='evaluated_mesh':
            center=[(a+b)/2 for a,b in zip(obj['bbox_mm']['min'],obj['bbox_mm']['max'])]
            x,y=xy(center);marks.append((x,y,obj['id']))
    for x,y,label in marks:
        # source register carries complete object names; callouts stay compact
        sh.text(x,y,label,2.1,ACCENT,anchor='middle')
    sh.dimh(ox,ox+w,oy-15,oy,number(round(extents[haxis],1)))
    sh.dimv(oy,oy+h,ox-14,ox,number(round(extents[vaxis],1)))
    dimension_objects=select(objects,view.get('dimension_include',r'^$'))
    stations=sorted({bbox['min'][haxis],bbox['max'][haxis],*[v for o in dimension_objects for v in (o['bbox_mm']['min'][haxis],o['bbox_mm']['max'][haxis])]})
    filtered=[]
    for v in stations:
        if not filtered or v-filtered[-1]>.5:filtered.append(v)
    stations=filtered
    if 2<len(stations)<=14 and not view.get('dimensions') and all((b-a)/scale>=6 for a,b in zip(stations,stations[1:])):
        for a,b in zip(stations,stations[1:]):
            x1=(bbox['max'][haxis]-b if flip else a-bbox['min'][haxis])/scale+ox
            x2=x1+(b-a)/scale
            sh.dimh(x1,x2,oy+h+12,oy+h,number(round(b-a,1)))
    dimension_evidence=[]
    for dim in expand_dimension_chains(view):
        dim_axis=AXES[dim['axis']]
        if dim_axis not in (haxis,vaxis):raise ValueError('Annotated dimension axis is normal to the view')
        evidence_objects=select(objects,dim.get('source_include','.*'))
        start,end=dim['start_mm'],dim['end_mm']
        matched_faces=[planar_station_evidence(evidence_objects,dim_axis,point[dim_axis],dim.get('evidence_region_mm')) for point in (start,end)]
        if not all(matched_faces):
            raise ValueError(f"{code}/{dim['id']}: station lacks selected planar-face evidence perpendicular to measurement axis")
        a,b=xy(start),xy(end);value=abs(end[dim_axis]-start[dim_axis]);label=(dim['id']+' / ' if dim.get('display_id',True) else '')+number(round(value,2))
        offset=dim.get('paper_offset_mm',10)
        if dim.get('schedule_only'):
            pass
        elif dim_axis==haxis:
            left,right=sorted((a[0],b[0]));reference=(a[1]+b[1])/2
            sh.dimh(left,right,reference+offset,reference,label)
        else:
            top,bottom=sorted((a[1],b[1]));reference=(a[0]+b[0])/2
            sh.dimv(top,bottom,reference+offset,reference,label)
        dimension_evidence.append(dict(id=dim['id'],value_mm=value,axis=dim['axis'],start_mm=start,end_mm=end,basis=dim.get('basis','evaluated mesh face plane separation'),source_object_ids=[o['id'] for o in evidence_objects],matched_faces=matched_faces,verification='each station matches a selected planar triangle face perpendicular to the measurement axis (0.1 degree / 0.15 mm tolerance); functional clearances are not inferred'))
    annotation_rows=draw_annotations(sh,view,config,xy,bbox)
    sh.text(323,51,'圖面依據與判讀' if chinese else 'DRAWING EVIDENCE',3.4,ACCENT)
    yy=61
    notes=[f"{len(objects)} selected native objects.",f"Projected feature edges: {projection_count}.",f"Actual cut segments: {section_count}.",f"Model plane: {'XYZ'[axis]} = {number(round(cut,1))} mm." if view['kind'] in ('plan','section') else 'Projection of actual evaluated geometry.',f"View horizontal: {'XYZ'[haxis]}; vertical: {'XYZ'[vaxis]}."+(' Horizontal reversed.' if flip else ''),'Heavy lines: actual triangle/plane intersections. Fine grey: projected mesh feature edges; no hidden-line removal.','Overall dimensions/chains are model envelopes. Keyed D dimensions separately verify selected mesh face-plane separations; see dimension-evidence.csv. Hardware and fabrication release remain unresolved.']
    if chinese:
        notes=[f"本圖選用 {len(objects)} 個原生模型物件。",f"投影特徵線 {projection_count} 段；實際剖切線 {section_count} 段。",f"剖切位置：{'XYZ'[axis]} = {number(round(cut,1))} mm。" if view['kind'] in ('plan','section') else '由實際模型網格投影，保留原有構件。',f"圖面水平軸 {'XYZ'[haxis]}；垂直軸 {'XYZ'[vaxis]}。"+('水平觀看方向反轉。' if flip else ''),'粗線為網格與剖切面的實際交線；細灰線為投影特徵線，未執行遮蔽線消除。','外框尺寸與尺寸鏈表示模型外廓；D 編號另核對實際網格面間距，詳 dimension-evidence.csv。接合、五金及製作放行仍須工種覆核。']
    if view.get('note'):notes.append(view['note'])
    if omitted:
        notes.append(f'有 {len(omitted)} 項網格或投影省略，詳 issues.csv；未補畫虛構細節。' if chinese else f'{len(omitted)} mesh/projection omissions. See issues.csv; no substitute details invented.')
        issue_rows.append(dict(id=f'G{len(issue_rows)+1:03}',scope=code,question='Geometry/projection omitted: '+', '.join(omitted),status='open'))
    for text in notes:yy=sh.paragraph(323,yy,text,43,2.8,4.8)+7
    if not view.get('omit_footer_note'):
        sh.text(35,242,'構件與尺寸證據對照' if chinese else 'GEOMETRY REGISTER',2.8,ACCENT)
        sh.text(35,248,'物件編號、原始名稱、材質與模型尺寸詳 source-register.csv；關鍵尺寸與取值面詳 dimension-evidence.csv。' if chinese else 'Object IDs, full native names, material assignments and modeled extents: source-register.csv',2.6,MUTED)
    return sh,objects,dict(sheet=code,title=view['title'],kind=view['kind'],axis='XYZ'[axis],plane_mm=cut if view['kind'] in ('plan','section') else None,scale=scale,object_ids=[o['id'] for o in objects],bounds_mm=bbox,projected_segments=projection_count,cut_segments=section_count,dimensions=dimension_evidence,annotations=annotation_rows)


def csv_write(path,fields,rows):
    with path.open('w',newline='') as file:
        writer=csv.DictWriter(file,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows)


def supplementary_sheets(config,records,inventory,issues):
    """Optional issue-linked drawing register and schedules from explicit annotations."""
    if not config.get('include_register'):return [],[],[a for record in records for a in record.get('annotations',[])],[]
    chinese=config.get('language')=='zh-TW';project=config.get('project','Native model coordination');revision=config.get('revision','N01')
    annotations=[a for record in records for a in record.get('annotations',[])]
    rooms=[a for a in annotations if a['kind']=='room'];openings=[a for a in annotations if a['kind']=='opening']
    materials=[]
    for item in config.get('materials',[]):
        if not item.get('basis'):raise ValueError('Material schedules require a source basis')
        objects=select(inventory['objects'],item['source_include'])
        if not objects:raise ValueError('Material definition matches no native object: '+item['id'])
        assignments=sorted({m for o in objects for m in o.get('material_names',[])})
        materials.append(dict(item,model_materials=' | '.join(assignments),source_object_ids=' | '.join(o['id'] for o in objects),status=item.get('status','model appearance; specification unconfirmed')))
    supplements=[]
    def new(code,title):
        sheet=NativeSheet(code,title,project,revision,'NTS',chinese)
        supplements.append(sheet);return sheet
    register_code=config.get('register_sheet','N000')
    sh=new(register_code,'圖紙目錄・圖例與交付界面' if chinese else 'DRAWING REGISTER / EVIDENCE AND RELEASE')
    register_entries=[dict(sheet=register_code,title=sh.title,kind='register',scale=None)]+records
    if config.get('include_schedules'):
        register_entries += [dict(sheet='N501',title='空間與開口定位表' if chinese else 'ROOM AND OPENING LOCATION SCHEDULE',kind='schedule',scale=None),dict(sheet='N502',title='材質索引與待決施工界面' if chinese else 'MATERIAL INDEX AND OUTSTANDING TRADE INTERFACES',kind='schedule',scale=None)]
    sh.text(18,47,'本次圖紙目錄' if chinese else 'ISSUED SHEET REGISTER',3.8,ACCENT)
    table(sh,18,54,235,['圖號','圖名／用途','A3 比例'] if chinese else ['SHEET','TITLE / PURPOSE','A3 SCALE'],[[r['sheet'],r['title'],f"1:{number(r['scale'])}" if isinstance(r.get('scale'),(int,float)) else 'NTS'] for r in register_entries],[23,181,31],step=9,size=2.7)
    sh.text(271,47,'交付依據與線型' if chinese else 'EVIDENCE AND LINEWORK',3.8,ACCENT)
    yy=57
    notes=['粗黑線＝原生網格與指定剖切平面的交線。','細灰線＝原生網格特徵線投影；非完整消隱圖。','D／P 編號尺寸：兩端均核對模型真實平面；詳尺寸證據表。','R＝使用區域標籤；W／O＝開口定位；圓形索引連結立面／剖面圖。','圖面尺寸單位 mm，圖框標示 A3 列印比例；禁止從螢幕量測下料。','此版可供工種討論、核尺寸及介面對照；現場、產品五金、接合與固定須完成覆核，尚非施工核准版。'] if chinese else ['Heavy black: actual evaluated mesh / section-plane intersections.','Fine grey: projected native feature edges; no complete hidden-line removal.','Keyed D/P dimensions match actual planar faces at both stations; see dimension-evidence.csv.','R: use-zone label; W/O: opening locator; circular references link actual detail sheets.','Units mm. A3 scale stated per sheet. Do not measure screen images for fabrication.','Coordination issue: site, products, joints and fixings remain subject to trade verification.']
    for note in notes:yy=sh.paragraph(271,yy,note,62,2.8,4.6)+6
    sh.text(18,205,'來源可追溯檔案' if chinese else 'TRACEABLE EVIDENCE',3.4,ACCENT)
    sh.paragraph(18,214,'source-evidence.json / dimension-evidence.csv / annotation-register.csv / sheet-register.csv',110,2.7,5)
    sh.paragraph(18,226,('來源模型 SHA256：' if chinese else 'Source model SHA256: ')+inventory['source']['sha256'],130,2.5,5)
    if config.get('include_schedules'):
        sh=new('N501','空間與開口定位表' if chinese else 'ROOM AND OPENING LOCATION SCHEDULE')
        sh.text(18,47,'空間使用索引（非面積／現場證明）' if chinese else 'USE-ZONE INDEX / NOT SURVEYED AREAS',3.5,ACCENT)
        table(sh,18,55,180,['編號','空間使用','定位圖'] if chinese else ['ID','USE','VIEW'],[[r.get('id',''),r.get('text',''),r.get('view_sheet','')] for r in rooms],[20,130,30],step=10,size=2.8)
        sh.text(214,47,'門窗與開口定位（尺寸見證據表）' if chinese else 'OPENING LOCATORS / SEE DIMENSION EVIDENCE',3.5,ACCENT)
        table(sh,214,55,188,['編號','描述','模型名義寬 mm'] if chinese else ['ID','DESCRIPTION','MODEL WIDTH mm'],[[r.get('id',''),r.get('text',''),r.get('width_mm','待核')] for r in openings],[20,125,43],step=10,size=2.6)
        sh.paragraph(18,220,'標籤與用途依既有設計及模型定位；不推算現場淨面積。開口標註須另核框、扇、五金、完成面及實際淨通行寬。' if chinese else 'Use labels reflect the existing design and native model locations; no surveyed areas are inferred. Verify frames, leaves, hardware, finishes and clear passage separately.',170,2.9,5)
        sh.paragraph(18,242,'逐項來源依據：annotation-register.csv；圖面位置及文字保留於 selection.json。' if chinese else 'Per-item sources: annotation-register.csv; exact coordinates and wording: selection.json.',170,2.6,4)
        sh=new('N502','材質索引與待決施工界面' if chinese else 'MATERIAL INDEX AND OUTSTANDING TRADE INTERFACES')
        sh.text(18,47,'原生模型材質索引（非產品規格）' if chinese else 'NATIVE MATERIAL INDEX / NOT A PRODUCT SPECIFICATION',3.5,ACCENT)
        yy=55
        for material in materials:
            sh.rect(18,yy,235,21,'none',.13,'#b9c1c2');sh.text(21,yy+5,material['id']+'  '+material.get('name',''),3,ACCENT)
            sh.paragraph(21,yy+10,material['model_materials'],115,2.4,3.8)
            yy+=23
            if yy>235:break
        sh.text(269,47,'製作前待決／負責工種' if chinese else 'PRE-FABRICATION ISSUES / RESPONSIBILITY',3.5,ACCENT)
        yy=57
        for issue in issues[:10]:
            yy=sh.paragraph(269,yy,issue['id']+' / '+issue['question'],64,2.8,4.5)+6
        sh.text(18,246,'完整材質來源與狀態見 material-register.csv；待決事項見 issues.csv。' if chinese else 'Complete source assignments/status: material-register.csv. Outstanding items: issues.csv.',2.6,MUTED)
    added=[]
    for sheet in supplements:
        added.append(dict(sheet=sheet.code,title=sheet.title,kind='register' if sheet.code==register_code else 'schedule',scale=None,object_ids=[],dimensions=[],annotations=[]))
    return supplements,added,annotations,materials


def build(inventory_path,out,config_path=None):
    inventory_path=Path(inventory_path);inventory=json.loads(inventory_path.read_text())
    if inventory.get('format')!='native-model-inventory-v1' or inventory.get('units',{}).get('coordinate_unit')!='mm':raise ValueError('Expected native-model-inventory-v1, world-space mm')
    if len({o['id'] for o in inventory['objects']})!=len(inventory['objects']):raise ValueError('Duplicate object IDs')
    config=json.loads(Path(config_path).read_text()) if config_path else {}
    views=config.get('views',[dict(kind='plan',title='Model-derived coordination plan',axis='z')])
    if not views:raise ValueError('At least one view is required')
    issues=[dict(id='E001',scope='all',question='Confirm native scene unit scale against one independently measured site dimension.',status='open'),dict(id='E002',scope='all',question='Verify site substrate, wall build-ups, opening clear sizes, services, fixing loads and selected hardware before trade release.',status='open'),dict(id='E003',scope='all',question='Mesh surfaces and object envelopes do not establish joinery panels, joints, rebates, clearances or certified product dimensions.',status='open')]
    if config.get('language')=='zh-TW':
        for issue,question in zip(issues,['請以至少一處獨立現場量測尺寸核對原生模型單位與縮放。','製作前核對現場基底、牆體構造、開口淨尺寸、服務設備、固定荷重與實選五金。','網格與外框尺寸不自動成立為板件、接合、溝槽、操作淨空或產品認證尺寸；D 編號面間距另附證據。']):issue['question']=question
    for question in config.get('questions',[]):issues.append(dict(id=f'E{len(issues)+1:03}',scope='project',question=question,status='open'))
    sheets=[];register={};view_register=[]
    for index,view in enumerate(views,1):
        sh,objects,record=draw_view(inventory,view,view.get('sheet',f'M{index:03}'),config,issues)
        sheets.append(sh);view_register.append(record)
        register.update({o['id']:o for o in objects})
    supplementary,extra_records,annotations,materials=supplementary_sheets(config,view_register,inventory,issues)
    if supplementary:
        sheets=[supplementary[0]]+sheets+supplementary[1:]
        view_register=[extra_records[0]]+view_register+extra_records[1:]
    codes=[sheet.code for sheet in sheets]
    if len(set(codes))!=len(codes) or any(not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,25}',code) for code in codes):raise ValueError('Sheet IDs must be unique safe filenames')
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    pdf=canvas.Canvas(str(out/'native-coordination.pdf'),pagesize=(420*mm,297*mm),pageCompression=1,invariant=1)
    pdf.setTitle(config.get('project','Native model coordination'));pdf.setAuthor('Interior Design Skill')
    for sh in sheets:sh.save(out/(sh.code+'.svg'),pdf)
    pdf.save()
    rows=[]
    for o in register.values():
        bbox=o['bbox_mm'];size=[round(b-a,3) for a,b in zip(bbox['min'],bbox['max'])]
        rows.append(dict(id=o['id'],native_name=o['name'],collections=' | '.join(o.get('collections',[])),materials=' | '.join(o.get('material_names',[])),x_min=bbox['min'][0],y_min=bbox['min'][1],z_min=bbox['min'][2],x_extent=size[0],y_extent=size[1],z_extent=size[2],geometry_status=o['geometry_status'],dimension_basis='evaluated world-axis envelope; not fabrication size'))
    csv_write(out/'source-register.csv',['id','native_name','collections','materials','x_min','y_min','z_min','x_extent','y_extent','z_extent','geometry_status','dimension_basis'],rows)
    csv_write(out/'issues.csv',['id','scope','question','status'],issues)
    dimension_rows=[dict(sheet=view['sheet'],id=d['id'],value_mm=d['value_mm'],axis=d['axis'],start_mm=json.dumps(d['start_mm']),end_mm=json.dumps(d['end_mm']),basis=d['basis'],source_object_ids=' | '.join(d['source_object_ids']),matched_faces=json.dumps(d['matched_faces'],ensure_ascii=False),verification=d['verification']) for view in view_register for d in view['dimensions']]
    csv_write(out/'dimension-evidence.csv',['sheet','id','value_mm','axis','start_mm','end_mm','basis','source_object_ids','matched_faces','verification'],dimension_rows)
    csv_write(out/'sheet-register.csv',['sheet','title','kind','scale'],view_register)
    csv_write(out/'annotation-register.csv',['view_sheet','kind','id','text','at_mm','basis','reference_sheet','width_mm'],annotations)
    csv_write(out/'material-register.csv',['id','name','model_materials','source_object_ids','basis','status'],materials)
    (out/'selection.json').write_text(json.dumps(config,indent=2)+'\n')
    (out/'views.json').write_text(json.dumps(view_register,indent=2)+'\n')
    evidence=dict(source=inventory['source'],extractor_sha256=inventory.get('extractor_sha256'),units=inventory['units'],selection=inventory.get('selection'),geometry_omissions=inventory.get('omissions',[]),basis=inventory.get('evidence'))
    (out/'source-evidence.json').write_text(json.dumps(evidence,indent=2)+'\n')
    files=[out/(s.code+'.svg') for s in sheets]+[out/n for n in ('native-coordination.pdf','source-register.csv','issues.csv','dimension-evidence.csv','selection.json','views.json','source-evidence.json','sheet-register.csv','annotation-register.csv','material-register.csv')]
    sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
    sources=dict(inventory=sha(inventory_path),native_file=inventory['source']['sha256'],generator=sha(__file__),drawing_renderer=sha(Path(__file__).with_name('build_drawing_studies.py')))
    if config_path:sources['selection_config']=sha(config_path)
    (out/'manifest.json').write_text(json.dumps(dict(format='native-handoff-v1',source_hashes=sources,files={f.name:sha(f) for f in files}),indent=2)+'\n')
    return view_register


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--config',type=Path)
    args=parser.parse_args();views=build(args.inventory,args.out,args.config)
    print(f'Generated {len(views)} model-derived coordination views; PDF, SVG, source register, issues and manifest in {args.out}')

if __name__=='__main__':main()
