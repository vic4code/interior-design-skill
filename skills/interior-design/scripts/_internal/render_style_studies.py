#!/usr/bin/env python3
"""Render original, editable furniture studies from the shared coordination fixture.

Run with Blender, not system Python. No external assets or network are required.
All dimensions in the source fixture and published bounds are millimetres.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import sys

# Blender's --python runner does not consistently add the script directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from output_ownership import require_empty_output, verify_inputs_outside

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
PARENT = None
M = {}
STYLE = ''
RNG = random.Random(26)


def rgb(value):
    values = [int(value[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return tuple(v / 12.92 if v < .04045 else ((v + .055) / 1.055) ** 2.4 for v in values)


def material(name, color, rough=.55, metal=0, texture=None):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*rgb(color), 1)
    mat.use_nodes = True
    tree = mat.node_tree
    bs = tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*rgb(color), 1)
    bs.inputs['Roughness'].default_value = rough
    bs.inputs['Metallic'].default_value = metal
    if texture:
        tex = tree.nodes.new('ShaderNodeTexNoise')
        tex.inputs['Scale'].default_value = 140 if texture == 'fabric' else 4
        tex.inputs['Detail'].default_value = 3
        coord = tree.nodes.new('ShaderNodeTexCoord')
        mapping = tree.nodes.new('ShaderNodeVectorMath')
        mapping.operation = 'MULTIPLY'
        mapping.inputs[1].default_value = (1.5, 70, 70) if texture == 'wood' else (1, 1, 1)
        tree.links.new(coord.outputs['Generated'], mapping.inputs[0])
        tree.links.new(mapping.outputs[0], tex.inputs['Vector'])
        bump = tree.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = .16 if texture == 'fabric' else .12
        bump.inputs['Distance'].default_value = .008 if texture == 'wood' else .002
        tree.links.new(tex.outputs['Fac'], bump.inputs['Height'])
        tree.links.new(bump.outputs['Normal'], bs.inputs['Normal'])
        ramp = tree.nodes.new('ShaderNodeValToRGB')
        c = rgb(color)
        ramp.color_ramp.elements[0].color = (*[v * .72 for v in c], 1)
        ramp.color_ramp.elements[1].color = (*[min(v * 1.13, 1) for v in c], 1)
        tree.links.new(tex.outputs['Fac'], ramp.inputs[0])
        tree.links.new(ramp.outputs[0], bs.inputs['Base Color'])
    return mat


def finish(obj, name, mat, parent=True):
    obj.name = name
    if mat:
        obj.data.materials.append(mat)
    if parent and PARENT:
        obj.parent = PARENT
    return obj


def box(name, loc, size, mat, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = finish(bpy.context.object, name, mat)
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new('Soft manufactured edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 5
        obj.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj


def cyl(name, loc, radius, depth, mat, radius2=None):
    if radius2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=40, radius=radius, depth=depth, location=loc)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=radius, radius2=radius2, depth=depth, location=loc)
    obj = finish(bpy.context.object, name, mat)
    bevel = obj.modifiers.new('Edge glint', 'BEVEL')
    bevel.width = .004
    bevel.segments = 3
    obj.modifiers.new('Normals', 'WEIGHTED_NORMAL')
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj


def rod(name, start, end, radius, mat, top=None):
    a, b = Vector(start), Vector(end)
    o = cyl(name, (a + b) / 2, radius, (b - a).length, mat, top)
    o.rotation_euler = (b - a).to_track_quat('Z', 'Y').to_euler()
    return o


def sphere(name, loc, size, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=1, location=loc)
    o = finish(bpy.context.object, name, mat)
    o.scale = size
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def curve(name, points, radius, mat):
    data = bpy.data.curves.new(name, 'CURVE')
    data.dimensions = '3D'
    data.bevel_depth = radius
    data.bevel_resolution = 3
    s = data.splines.new('POLY')
    s.points.add(len(points) - 1)
    for p, v in zip(s.points, points):
        p.co = (*v, 1)
    ob = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(ob)
    finish(ob, name, mat)
    return ob


def vase(x, y, z, scale=1):
    cyl('Ceramic vessel body', (x,y,z+.09*scale), .065*scale,.18*scale,M['ceramic'], .048*scale)
    cyl('Ceramic vessel neck', (x,y,z+.20*scale),.028*scale,.06*scale,M['ceramic'])
    cyl('Vessel open mouth', (x,y,z+.232*scale),.022*scale,.002,M['dark'])
    for k in range(3):
        tip=(x+(.09*k-.08)*scale,y+.025*k,z+(.54+.06*k)*scale)
        rod('Botanical stem',(x,y,z+.21*scale),tip,.002,M['wood'])
        sphere('Sculptural foliage',tip,(.085*scale,.018*scale,.035*scale),M['leaf'])


def books(x,y,z,axis='horizontal'):
    for i,c in enumerate(('paper','accent','wood')):
        if axis=='horizontal':
            o=box('Original design monograph',(x+.01*i,y,z+.014+i*.026),(.27-i*.015,.19,.025),M[c],.003)
            o.rotation_euler[2]=.10*i
        else:
            box('Bound volume',(x+i*.036,y,z+.13),(.030,.17,.26-(i%2)*.025),M[c],.002)


def artwork(x,y,z,w,h,wall='north'):
    # Each panel is an original geometric relief, not a reproduction.
    if wall=='north':
        base=box('Original geometric art / timber frame',(x,y,z),(w,.035,h),M['wood'],.01)
        box('Cotton art ground',(x,y-.025,z),(w-.045,.018,h-.045),M['paper'])
        for i in range(3):
            xo=x+(i-1)*w*.24
            shape=box('Original painted block',(xo,y-.041,z+(.14 if i%2 else -.10)),(w*.18,.012,h*(.42 if i%2 else .60)),M[['accent','wood','leaf'][i]],.005)
        o=cyl('Original painted disk',(x+w*.19,y-.052,z+h*.24),w*.14,.012,M['yellow'])
        o.rotation_euler[0]=math.pi/2
    else:
        box('Original relief frame',(x,y,z),(w,.03,h),M['wood'],.01)


def sofa(f):
    x,y,w,d,h=[f[k]/1000 for k in ('x','y','width','depth','height')]
    if STYLE=='japandi':
        box('Solid oak platform',(x+w/2,y+d/2,.19),(w,d,.12),M['wood'],.025)
        for xx in (x+.16,x+w-.16):
            for yy in (y+.15,y+d-.15): box('Recessed oak foot',(xx,yy,.08),(.15,.15,.16),M['wood'],.015)
    elif STYLE=='bauhaus':
        for xx in (x+.035,x+w-.035):
            curve('Continuous tubular sofa frame',[(xx,y+.022,.022),(xx,y+d-.022,.022),(xx,y+d-.08,.71),(xx,y+.12,.71),(xx,y+.12,.56)],.022,M['metal'])
        for yy in (y+.12,y+d-.08):
            rod('Chrome seat-bearing stretcher',(x+.03,yy,.282),(x+w-.03,yy,.282),.018,M['metal'])
        for xx in (x+.035,x+w-.035):
            rod('Chrome seat-bearing side rail',(xx,y+.12,.282),(xx,y+d-.08,.282),.018,M['metal'])
    elif STYLE=='mcm':
        box('Exposed walnut seat frame',(x+w/2,y+d/2,.265),(w-.03,d,.12),M['wood'],.015)
        for xx in (x+.12,x+w-.12):
            for yy in (y+.12,y+d-.14):
                rod('Splayed tapered walnut leg',(xx+(-.04 if xx<x+w/2 else .04),yy-.03,.003),(xx,yy,.26),.021,M['wood'],.035)
        for xx in (x+.045,x+w-.045):
            box('Sculpted walnut arm',(xx,y+d/2,.58),(.09,d-.12,.075),M['wood'],.03)
            rod('Arm support',(xx,y+.18,.3),(xx,y+.18,.56),.018,M['wood'])
    else:
        box('Continuous upholstered base',(x+w/2,y+d/2,.25),(w,d,.34),M['fabric'],.13)
        for xx in (x+.25,x+w-.25):
            for yy in (y+.18,y+d-.18):box('Recessed concealed foot',(xx,yy,.045),(.10,.10,.09),M['dark'],.008)
        for xx in (x+.13,x+w-.13):
            box('Rounded upholstered arm',(xx,y+d/2,.52),(.26,d,.56),M['fabric'],.12)
    margin=.12 if STYLE!='contemporary' else .27
    for i in range(3):
        cw=(w-2*margin)/3
        xx=x+margin+cw*(i+.5)
        box('Individual upholstered seat cushion',(xx,y+d*.39,.40),(cw-.012,d*.66,.20),M['fabric'],.065 if STYLE!='bauhaus' else .028)
        ob=box('Upholstered back cushion',(xx,y+d*.84,.614),(cw-.012,.22,.35),M['fabric'],.07 if STYLE!='bauhaus' else .035)
        ob.rotation_euler[0]=-.10
        # Subtle piped seam on cushion front, completely within fixture envelope.
        curve('Cushion welt',[(xx-cw*.43,y+.065,.43),(xx+cw*.43,y+.065,.43)],.0023,M['seam'])
    for i in range(2):
        xx=x+(.35 if i==0 else w-.35)
        ob=box('Loose woven cushion',(xx,y+.66,.61),(.37,.17,.35),M['accent' if i==0 else 'paperfabric'],.075)
        ob.rotation_euler[1]=(-.17 if i==0 else .13)


def table(f,desk=False):
    global PARENT
    x,y,w,d,h=[f[k]/1000 for k in ('x','y','width','depth','height')]
    stone=STYLE=='contemporary' and not desk
    top=.06 if stone else .035
    box('Stone slab' if stone else 'Timber top',(x+w/2,y+d/2,h-top/2),(w,d,top),M['stone' if stone else 'wood'],.065 if stone else .025)
    if stone:
        for xx in (x+.29,x+w-.29): cyl('Stone drum pedestal',(xx,y+d/2,(h-top)/2),.18,h-top,M['stone'])
    elif STYLE=='japandi' and not desk:
        for xx in (x+.15,x+w-.15):box('Solid slab leg',(xx,y+d/2,(h-top)/2),(.10,d-.12,h-top),M['wood'],.015)
    else:
        for xx in (x+.09,x+w-.09):
            for yy in (y+.09,y+d-.09):
                rod('Tubular leg' if STYLE=='bauhaus' else 'Tapered table leg',(xx,yy,.003),(xx,yy,h-top),.016 if STYLE=='bauhaus' else .022,M['metal' if STYLE=='bauhaus' else 'wood'],None if STYLE=='bauhaus' else .036)
    if desk:
        box('Desk drawer',(x+w*.72,y+.28,h-.10),(.53,.48,.12),M['wood'],.012)
        box('Drawer pull',(x+w*.72,y+.033,h-.10),(.16,.018,.012),M['metal'],.004)
        furniture_parent=PARENT;PARENT=None
        books(x+.26,y+.39,h)
        box('Writing pad',(x+.80,y+.27,h+.006),(.49,.34,.009),M['dark'],.015)
        box('Closed notebook',(x+.79,y+.29,h+.022),(.24,.18,.025),M['paper'],.003)
        lamp(x+w-.17,y+d-.19,h,.46)
        PARENT=furniture_parent
    else:
        furniture_parent=PARENT;PARENT=None
        books(x+w*.33,y+d*.51,h)
        cyl('Serving tray',(x+w*.74,y+d*.49,h+.012),.13,.024,M['metal'])
        cyl('Ceramic cup',(x+w*.74,y+d*.49,h+.07),.038,.09,M['ceramic'])
        PARENT=furniture_parent


def chair(f):
    x,y,w,d,h=[f[k]/1000 for k in ('x','y','width','depth','height')]
    for xx in (x+.055,x+w-.055):
        if STYLE=='bauhaus':
            curve('Cantilever tubular chair frame',[(xx,y+.03,.017),(xx,y+d-.03,.017),(xx,y+d-.03,.43),(xx,y+.03,.43),(xx,y+.03,h-.03)],.017,M['metal'])
        else:
            for yy in (y+.07,y+d-.07):rod('Chair leg',(xx,yy,.003),(xx,yy,.43),.018,M['wood'],.026)
    box('Padded seat',(x+w/2,y+d/2,.445),(w-.035,d-.035,.09),M['fabric'],.045)
    box('Curved timber chair back',(x+w/2,y+.045,.70),(w-.02,.07,.24),M['wood' if STYLE in ('mcm','japandi') else 'fabric'],.06)
    if STYLE!='bauhaus':
        for xx in (x+.055,x+w-.055):rod('Back upright',(xx,y+.06,.43),(xx,y+.045,.76),.017,M['wood'])


def cabinet(f,j):
    global PARENT
    x,y,w,d,h=[f[k]/1000 for k in ('x','y','width','depth','height')]
    t=j['carcass_thickness']/1000; top=j['top_thickness']/1000; pl=j['plinth_height']/1000
    back=j['back_thickness']/1000; door=j['door_thickness']/1000; gap=j['door_gap']/1000
    clear=j['front_clearance']/1000; st=j['shelf_thickness']/1000
    box('Top panel 20mm',(x+w/2,y+d/2,h-top/2),(w,d,top),M['wood'],.002)
    body_depth=d-door-clear
    # Match J401: rear setback 60mm; total setback 90mm in the 429mm body.
    plinth_depth=body_depth-.090
    box('Recessed plinth',(x+w/2,y+.060+plinth_depth/2,pl/2),(w-.10,plinth_depth,pl),M['dark'])
    box('Bottom panel 18mm',(x+w/2,y+body_depth/2,pl+t/2),(w,body_depth,t),M['wood'],.001)
    for xx in (x+t/2,x+w-t/2):box('Carcass side 18mm',(xx,y+body_depth/2,(pl+h-top)/2),(t,body_depth,h-top-pl),M['wood'],.001)
    box('Back panel 9mm',(x+w/2,y+back/2,(pl+h-top)/2),(w-2*t,back,h-top-pl),M['wood'])
    bw=(w-2*t-(j['bays']-1)*t)/j['bays']
    for k in range(j['bays']):
        bx=x+t+k*(bw+t)
        if k:box('Vertical divider 18mm',(bx-t/2,y+(d-door-clear)/2,(pl+h-top)/2),(t,d-door-clear,h-top-pl),M['wood'])
        box('Shelf 18mm',(bx+bw/2,y+(body_depth+back)/2,j['shelf_top_height']/1000-st/2),(bw,d-door-clear-back,st),M['wood'])
        # Closed front leaves hide shelving yet retain all parts in editable native scene.
        dw=(w-gap*(j['bays']+1))/j['bays']
        xx=x+gap+k*(dw+gap)+dw/2
        face=M['wood'] if STYLE!='bauhaus' or k!=2 else M['accent']
        box('Door leaf / 3mm reveals',(xx,y+d-door/2,(pl+h-top)/2),(dw,door,h-top-pl-gap*2),face,.0015)
        box('Slim door pull',(xx+dw*.30,y+d+.008,(pl+h-top)/2+.11),(.014,.016,.12),M['metal'],.004)
    furniture_parent=PARENT;PARENT=None
    books(x+.35,y+.22,h)
    vase(x+w-.37,y+.22,h,1.15)
    lamp(x+w*.54,y+.20,h,.52)
    PARENT=furniture_parent


def lamp(x,y,z,height):
    cyl('Lamp foot',(x,y,z+.018),.095,.036,M['metal'])
    rod('Lamp stem',(x,y,z+.02),(x,y,z+height-.12),.011,M['metal'])
    if STYLE=='japandi':
        sphere('Paper lantern shade',(x,y,z+height-.11),(.17,.17,.17),M['paper'])
        for i in range(7):
            zz=z+height-.24+i*.04
            rr=math.sqrt(max(.001,.17**2-(zz-(z+height-.11))**2))
            points=[(x+rr*math.cos(a*math.tau/48),y+rr*math.sin(a*math.tau/48),zz) for a in range(49)]
            curve('Paper lantern rib',points,.0015,M['seam'])
    else:
        cyl('Sculptural lamp shade',(x,y,z+height-.08),.15,.16,M['accent' if STYLE=='bauhaus' else 'ceramic'],.10)
    light('Warm practical',(x,y,z+height-.15),24,'POINT',(1,.72,.43),.1)


def light(name,loc,power,kind='AREA',color=(1,.9,.76),size=3,target=None):
    data=bpy.data.lights.new(name,kind);data.energy=power;data.color=color
    if kind=='AREA':data.shape='DISK';data.size=size
    else:data.shadow_soft_size=size
    o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.location=loc
    if target:o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    return o


def architecture(p):
    W,D,H=[p['room'][k]/1000 for k in ('width','depth','height')]
    box('Continuous subfloor',(W/2,D/2,-.035),(W+.3,D+.3,.06),M['wood'])
    # 180 mm oak boards, 1.1 mm fine shadow joints, staggered lengths.
    for row in range(math.ceil(D/.18)):
        yy=min(.18,D-row*.18)
        xx=-1.2 if row%2 else -2.1
        while xx<W:
            start=max(xx,0);end=min(xx+2.1,W)
            if end>start:box('Oak floorboard',( (start+end)/2,row*.18+yy/2,-.001),(end-start-.0011,yy-.0011,.012),M['floor'],.0006)
            xx+=2.1
    openings=p['openings']
    for side,length in [('north',W),('south',W),('east',D),('west',D)]:
        ops=sorted([o for o in openings if o['wall']==side],key=lambda o:o['offset'])
        def wallbit(a,b,z,hh):
            if b-a<.001 or hh<.001:return
            if side in ('north','south'):loc=((a+b)/2,D+.075 if side=='north' else -.075,z+hh/2);size=(b-a,.15,hh)
            else:loc=(W+.075 if side=='east' else -.075,(a+b)/2,z+hh/2);size=(.15,b-a,hh)
            box(side+' plaster wall',loc,size,M['wall'])
        cursor=0
        for o in ops:
            a=o['offset']/1000;b=a+o['width']/1000;s=o['sill']/1000;h=o['height']/1000
            wallbit(cursor,a,0,H);wallbit(a,b,0,s);wallbit(a,b,s+h,H-s-h);cursor=b
            if o['kind']=='window':
                for pos in (a+.022,(a+b)/2,b-.022):
                    if side=='north':box('Window vertical frame',(pos,D+.06,s+h/2),(.035,.10,h),M['metal'])
                    else:box('Window vertical frame',(W+.06,pos,s+h/2),(.10,.035,h),M['metal'])
                for zz in (s+.02,s+h-.02):
                    if side=='north':box('Window horizontal frame',((a+b)/2,D+.06,zz),(b-a,.10,.035),M['metal'])
                    else:box('Window horizontal frame',(W+.06,(a+b)/2,zz),(.10,b-a,.035),M['metal'])
                if side=='north':
                    box('Deep window sill',((a+b)/2,D-.04,s-.025),(b-a+.12,.26,.045),M['stone'],.006)
                    for edge in (a-.12,b+.12):
                        for q in range(9):
                            cyl('Folded linen drapery',(edge+(q-4)*.038,D-.12,1.43),.035,2.7,M['curtain'])
                # Open apertures admit actual world/daylight; no opaque fake glazing.
            else:
                box('Flush timber door',((a+b)/2,-.07,h/2),(b-a-.025,.045,h-.015),M['wood'],.003)
        wallbit(cursor,length,0,H)
        if side in ('north','south'):box('Painted baseboard',(W/2,D-.008 if side=='north' else .008,.04),(W,.018,.08),M['wall'])
        else:box('Painted baseboard',(W-.008 if side=='east' else .008,D/2,.04),(.018,D,.08),M['wall'])
    box('Plaster ceiling',(W/2,D/2,H+.07),(W+.3,D+.3,.14),M['wall'])
    # A large matte exterior bounce plane reads as an understated garden backdrop.
    box('Exterior backdrop',(W/2,D+3,2.5),(14,.1,7),M['outside'])
    for tree_index, tx in enumerate((.8, 2.6, 4.7, 7.2)):
        ty=D+1.6+(tree_index%2)*.6
        rod('Exterior garden stem',(tx,ty,0),(tx+.12,ty,3.9),.035,M['wood'])
        for branch in range(11):
            aa=branch*2.4;zz=1.0+branch*.24
            end=(tx+math.cos(aa)*.42,ty+math.sin(aa)*.25,zz)
            rod('Exterior garden branch',(tx,ty,zz-.15),end,.012,M['wood'])
            leaf=sphere('Exterior garden foliage',end,(.33,.17,.19),M['leaf']);leaf.rotation_euler[2]=aa
    light('North daylight',(2.8,5.15,2.5),650,'AREA',(.81,.89,1),3.4,(2.4,1.5,.4))
    light('East daylight',(6.35,3.3,2.1),420,'AREA',(1,.88,.71),2.5,(2.5,2.8,.5))
    light('Soft room bounce',(2.5,.5,2.65),150,'AREA',(1,.94,.83),4,(3,3,1))
    sun=bpy.data.lights.new('Afternoon sun','SUN');sun.energy=1.5;sun.angle=.10
    ob=bpy.data.objects.new('Afternoon sun',sun);bpy.context.collection.objects.link(ob);ob.rotation_euler=(math.radians(32),math.radians(-25),math.radians(-125))


def stage():
    box('Bound wool area rug',(1.96,2.51,.018),(2.85,2.70,.014),M['rug'],.025)
    if STYLE=='bauhaus':
        for i in range(4):box('Geometric woven rug stripe',(1.0+i*.12,2.51,.026),(.035,2.54,.002),M['dark'])
    elif STYLE=='mcm':
        for i in range(3):box('Woven border line',(1.96,.0+1.25+i*.025,.026),(2.65,.008,.002),M['accent'])
    artwork(.74,4.76,1.78,.79,1.01)
    # Original smaller composition above the sideboard for the second deliverable view.
    box('Sideboard art frame',(4.35,.022,1.64),(1.14,.035,1.05),M['wood'],.009)
    box('Sideboard art linen',(4.35,.045,1.64),(1.10,.012,1.01),M['paper'])
    for i in range(3):
        box('Original abstract vertical stroke',(4.04+i*.27,.058,1.60+(.10 if i==1 else 0)),(.16,.012,.55),M[['accent','leaf','wood'][i]],.015)
    cyl('Planter',( .38,4.27,.19),.17,.38,M['ceramic'],.21)
    for i in range(11):
        a=i*2.4;zz=.75+(i%4)*.18;r=.22+(i%3)*.065
        end=(.38+math.cos(a)*r,4.27+math.sin(a)*r,zz)
        rod('Plant stem',(.38,4.27,.27),end,.006,M['leaf'])
        leaf=sphere('Broad botanical leaf',end,(.18,.075,.035),M['leaf']);leaf.rotation_euler=(.3,i*.2,a)
    # Pendant is kept above the sight line, making the room legible without a cutaway.
    rod('Pendant suspension',(3,2.4,2.8),(3,2.4,2.51),.003,M['dark'])
    if STYLE=='japandi':sphere('Large paper pendant',(3,2.4,2.45),(.25,.25,.20),M['paper'])
    else:cyl('Pendant shade',(3,2.4,2.50),.24,.15,M['accent' if STYLE=='bauhaus' else 'ceramic'],.10)


def camera(name,loc,target,lens):
    data=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o)
    o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();data.lens=lens;data.clip_start=.03
    return o


def main():
    global PARENT,M,STYLE
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--style',choices=['all','mcm','japandi','contemporary','bauhaus'],default='all')
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--project',type=Path,default=ROOT/'assets/style-studies/project.json')
    parser.add_argument('--styles',type=Path,default=ROOT/'assets/style-studies/styles.json')
    parser.add_argument('--joinery',type=Path,default=ROOT/'assets/style-studies/joinery.json')
    parser.add_argument('--width',type=int,default=1600)
    parser.add_argument('--samples',type=int,default=48)
    parser.add_argument('--device',choices=['cpu','metal'],default='cpu',help='Portable CPU default; Metal uses available Apple GPU with CPU fallback')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    args.out = require_empty_output(args.out)
    verify_inputs_outside(args.out, [args.project, args.styles, args.joinery])
    # Factory UI avoids serializing user workspace state into distributable native scenes.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for screen in bpy.data.screens:
        for area in screen.areas:
            for space in area.spaces:
                if space.type=='FILE_BROWSER' and space.params:
                    # Blender stores fixed-size buffers: overwrite trailing bytes as well
                    # as the visible path before assigning a portable directory.
                    space.params.directory=b'/'*1023
                    space.params.directory=b'//'
    p=json.loads(args.project.read_text());styles=json.loads(args.styles.read_text());j=json.loads(args.joinery.read_text())
    hashes={name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in [('project.json',args.project),('styles.json',args.styles),('joinery.json',args.joinery),('render_style_studies.py',Path(__file__))]}
    actual_device='CPU'
    if args.device=='metal':
        try:
            preferences=bpy.context.preferences.addons['cycles'].preferences
            preferences.compute_device_type='METAL'
            preferences.get_devices()
            available=[device for device in preferences.devices if device.type=='METAL']
            if available:
                for device in preferences.devices:device.use=device.type=='METAL'
                actual_device='Metal / '+', '.join(device.name for device in available)
            else:print('Metal unavailable; using portable CPU renderer',flush=True)
        except (TypeError,RuntimeError) as error:
            print('Metal unavailable; using portable CPU renderer:',error,flush=True)
    for STYLE in (list(styles) if args.style=='all' else [args.style]):
        out=args.out/STYLE if args.style=='all' else args.out;out.mkdir(parents=True,exist_ok=True)
        bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
        PARENT=None;pal=styles[STYLE]['palette']
        M={k:material(k,v,.25 if k=='metal' else .55,.88 if k=='metal' else 0,'wood' if k=='wood' else 'fabric' if k=='rug' else None) for k,v in pal.items()}
        M.update({'fabric':material('Woven linen' if STYLE!='bauhaus' else 'Black leather',pal['upholstery'],.39 if STYLE=='bauhaus' else .78,texture='fabric'),
            'seam':material('Upholstery piping',pal['upholstery'],.8), 'floor':material('Natural oak floor','#aa855b' if STYLE=='mcm' else '#b5a081',.48,texture='wood'),
            'wall':material('Fine mineral plaster',pal['wall'],.85,texture='plaster'),
            'paper':material('Warm paper','#ece3ce',.8),'paperfabric':material('Natural cushion','#d4c5a7',.86,texture='fabric'),
            'ceramic':material('Matte glazed ceramic','#d6c8ad',.32),'dark':material('Blackened detail','#242524',.48),
            'yellow':material('Ochre artwork','#bca13c',.7),'leaf':material('Muted foliage','#56614a',.7),
            'curtain':material('Linen drapery','#d9cdb7',.9,texture='fabric'),'stone':material('Honed warm limestone','#baaf9b',.54,texture='plaster'),
            'outside':material('Soft garden backdrop','#aab6a2',1)})
        architecture(p);stage()
        for f in p['furniture']:
            PARENT=bpy.data.objects.new('furniture_'+f['id'],None);bpy.context.collection.objects.link(PARENT)
            PARENT['fixture_id']=f['id'];PARENT['design_bounds_mm']=json.dumps({k:f[k] for k in ('x','y','width','depth','height')});PARENT['style']=STYLE
            if f['id']=='F01':sofa(f)
            elif f['id'] in ('F02','F03'):table(f,f['id']=='F03')
            elif f['id']=='F04':chair(f)
            else:cabinet(f,j)
        PARENT=None
        hero=camera('Hero / architectural interior',(.42,.43,1.60),(2.85,3.90,1.05),22)
        detail=camera('Joinery / crafted detail',(2.02,3.72,1.48),(4.45,.41,.98),38)
        scene=bpy.context.scene;scene.camera=hero;scene.render.engine='CYCLES';scene.cycles.device='GPU' if actual_device.startswith('Metal') else 'CPU';scene.cycles.samples=args.samples;scene.cycles.use_denoising=True
        scene.render.resolution_x=args.width;scene.render.resolution_y=round(args.width*.75);scene.render.resolution_percentage=100
        if scene.world is None:scene.world=bpy.data.worlds.new('Neutral daylight world')
        scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.72,.80,1,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.35
        scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.15
        scene.render.image_settings.file_format='PNG'
        # Save portable paths only; all materials and geometry are generated in this file.
        scene.render.filepath='//hero.png'
        bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'))
        scene.render.filepath=str(out/'hero.png');bpy.ops.render.render(write_still=True)
        scene.camera=detail;scene.render.resolution_x=min(args.width,1280);scene.render.resolution_y=round(min(args.width,1280)*.75)
        scene.render.filepath=str(out/'detail.png');bpy.ops.render.render(write_still=True)
        scene.camera=hero
        # Export mesh geometry and ID-bearing parent nodes without unsupported lights/cameras.
        bpy.ops.object.select_all(action='DESELECT')
        for ob in scene.objects:
            if ob.type in ('MESH','CURVE','EMPTY') and not ob.name.startswith('Exterior ') and ob.name!='Plaster ceiling':ob.select_set(True)
        # Procedural ColorRamp/Bump graphs are not supported by core glTF.
        # Export the explicitly authored linear albedo as a portable PBR fallback.
        # Native scene was saved before this export-only material simplification.
        for mat in bpy.data.materials:
            if not mat.use_nodes:
                continue
            bs = next((node for node in mat.node_tree.nodes if node.type == 'BSDF_PRINCIPLED'), None)
            if bs is None:
                continue
            for socket_name in ('Base Color', 'Normal'):
                for link in list(bs.inputs[socket_name].links):
                    mat.node_tree.links.remove(link)
            bs.inputs['Base Color'].default_value = mat.diffuse_color
        bpy.ops.export_scene.gltf(filepath=str(out/'scene.glb'),export_format='GLB',use_selection=True,export_cameras=False,export_lights=False,export_extras=True,export_apply=True)
        bpy.context.view_layer.update()
        geometry_bounds={}
        depsgraph=bpy.context.evaluated_depsgraph_get()
        for furniture in p['furniture']:
            parent=bpy.data.objects['furniture_'+furniture['id']]
            points=[]
            for child in parent.children_recursive:
                if child.type not in ('MESH','CURVE'):continue
                evaluated=child.evaluated_get(depsgraph)
                mesh=evaluated.to_mesh()
                points.extend(evaluated.matrix_world @ vertex.co for vertex in mesh.vertices)
                evaluated.to_mesh_clear()
            geometry_bounds[furniture['id']]={'min':[round(min(v[i] for v in points)*1000,2) for i in range(3)],'max':[round(max(v[i] for v in points)*1000,2) for i in range(3)]}
        dimensions={'geometry_bounds_mm':geometry_bounds,'bounds_note':'Furniture coordinates are nominal design envelopes; measured bounds include geometry and projecting pulls. Accessories are separate.','units':'mm','revision':p['project']['revision'],'style':STYLE,'room':p['room'],'furniture':[{k:f[k] for k in ('id','x','y','width','depth','height')} for f in p['furniture']],'joinery':j}
        (out/'model_dimensions.json').write_text(json.dumps(dimensions,indent=2)+'\n')
        settings={'revision':p['project']['revision'],'style':STYLE,'renderer':'Cycles '+actual_device,'requested_device':args.device,'glb_exclusions':['Exterior render staging','Plaster ceiling (native scene retained complete)'],'blender':bpy.app.version_string,'samples':args.samples,'width':args.width,'view_transform':'AgX','exposure':.15,'source_sha256':hashes,'asset_origin':'Original procedural geometry, materials, and geometric artwork; no external assets','measurement_basis':'Synthetic design study; design coordination only','cameras':{o.name:{'position_m':list(o.location),'rotation_rad':list(o.rotation_euler),'lens_mm':o.data.lens} for o in (hero,detail)}}
        (out/'render-settings.json').write_text(json.dumps(settings,indent=2)+'\n')
        print('STYLE_STUDY_COMPLETE',STYLE,flush=True)


if __name__=='__main__':
    main()
