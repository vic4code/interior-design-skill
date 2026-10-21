"""Run with Blender 4.3+: blender -b --python-exit-code 1 --python ... -- project.json out."""
import json
import math
from pathlib import Path
import sys
import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
from geometry import wall_panels


def material(name,color):
    rgb=tuple(int(color[i:i+2],16)/255 for i in (1,3,5))
    m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);m.use_nodes=True
    bsdf=m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value=(*rgb,1);bsdf.inputs['Roughness'].default_value=.65
    return m


def box(name,center,size,mat,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=tuple(v/1000 for v in center))
    obj=bpy.context.object;obj.name=name;obj.dimensions=tuple(v/1000 for v in size)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    obj.data.materials.append(mat)
    if bevel:
        mod=obj.modifiers.new('Soft edges','BEVEL');mod.width=bevel/1000;mod.segments=3
        obj.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return obj


def furniture(f):
    x,y,w,d,h=(f[k] for k in ('x','y','width','depth','height'))
    m=material(f['id']+' / '+f['material'],f['color']);name='furniture_'+f['id']
    dark=material(f['id']+' legs','#473e34')
    def part(label,c,s,mat=m,b=10): return box(name+'_'+label,c,s,mat,b)
    if f['kind']=='cabinet':
        part('body',(x+w/2,y+d/2,h/2),(w,d,h))
        for station in (.25,.5,.75): part('joint',(x+w*station,y-1,h/2),(3,2,h-30),dark,0)
    elif f['kind']=='sofa':
        part('base',(x+w/2,y+d/2,h*.2625),(w-10,d-10,h*.375))
        part('back',(x+w/2,y+d-d*.11,(h+h*.3875)/2),(w*.84,d*.22,h*.6125))
        for a in (w*.04,w*.96):part('arm',(x+a,y+d/2,h*.55),(w*.08,d,h*.525))
        for a in (.25,.75):part('cushion',(x+w*.08+w*.84*a,y+d*.4,h*.5),(w*.415,d*.72,h*.1625),m,30)
    else:
        top= h if f['kind']=='table' else h*.55
        part('top',(x+w/2,y+d/2,top-35),(w,d,70),m,20)
        for a in (60,w-60):
            for b in (60,d-60):part('leg',(x+a,y+b,(top-70)/2),(35,35,top-70),dark,4)
        if f['kind']=='chair':part('back',(x+w/2,y+d-35,(h+top)/2),(w,70,h-top),m,20)


def main():
    args=sys.argv[sys.argv.index('--')+1:];source,out=Path(args[0]),Path(args[1])
    if out.is_symlink():
        raise ValueError('Output cannot be a symlink')
    out=out.resolve()
    for name in ('scene.glb','scene.blend','render.png','render-settings.json'):
        target=out/name
        if target.exists() or target.is_symlink():
            raise ValueError('Render output already exists; choose a new directory: '+name)
    data=json.loads(source.read_text());r=data['room']
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
    wall=material('Warm wall',data['finishes']['wall']['color']);floor=material('Oak floor',data['finishes']['floor']['color'])
    trim=material('Window frame','#6b6658')
    # A procedural oak grain, entirely local and licence-free.
    nodes=floor.node_tree.nodes;links=floor.node_tree.links
    tex=nodes.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=5;tex.inputs['Detail'].default_value=2
    coords=nodes.new('ShaderNodeTexCoord');mapping=nodes.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(3,65,3)
    ramp=nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.19,.10,.045,1);ramp.color_ramp.elements[1].color=(.65,.43,.22,1)
    links.new(coords.outputs['Generated'],mapping.inputs[0]);links.new(mapping.outputs[0],tex.inputs['Vector']);links.new(tex.outputs['Fac'],ramp.inputs[0]);links.new(ramp.outputs[0],nodes.get('Principled BSDF').inputs['Base Color'])
    box('floor',(r['width']/2,r['depth']/2,-60),(r['width']+2*r['wall_thickness'],r['depth']+2*r['wall_thickness'],120),floor,8)
    cut=[]
    for wallname,c,s in wall_panels(data):
        obj=box('wall_'+wallname,c,s,wall)
        if wallname in ('south','east','corner'):cut.append(obj)
    for o in data['openings']:
        if o['kind']!='window' or min(o['width'],o['height'])<=100:continue
        u=o['offset'];w=o['width'];z=o['sill'];h=o['height'];t=r['wall_thickness']
        def at(station,height):
            if o['wall'] in ('south','north'):return (station,-t/2 if o['wall']=='south' else r['depth']+t/2,height)
            return (-t/2 if o['wall']=='west' else r['width']+t/2,station,height)
        for station,height,span,rise in [(u+25,z+h/2,50,h),(u+w-25,z+h/2,50,h),(u+w/2,z+25,w-100,50),(u+w/2,z+h-25,w-100,50),(u+w/2,z+h/2,35,h-100)]:
            size=(span,t,rise) if o['wall'] in ('south','north') else (t,span,rise)
            obj=box('opening_'+o['wall']+'_'+o['id']+'_frame',at(station,height),size,trim,4)
            if o['wall'] in ('south','east'):cut.append(obj)
        # No opaque glass plane: holes admit real light; frame only, glazing remains unspecified.
    for f in data['furniture']:furniture(f)
    rug=material('Woven rug','#d7cbb4')
    box('decor_rug',(r['width']*.3,r['depth']*13/24,4),(r['width']*.5,r['depth']*23/48,8),rug,3)
    # Export geometry only; lighting/camera belong to the editable .blend.
    bpy.ops.export_scene.gltf(filepath=str(out/'scene.glb'),export_format='GLB',export_cameras=False,export_lights=False)
    scene.world.color=(.35,.35,.35);scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.78,.84,1,1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.5
    for name,loc,power,size in [('Softbox',(2,-1,6),1300,5),('Window',(3,6,4),900,4)]:
        bpy.ops.object.light_add(type='AREA',location=loc);light=bpy.context.object;light.name=name;light.data.energy=power;light.data.shape='DISK';light.data.size=size
        light.rotation_euler=(Vector((r['width']/2000,r['depth']/2000,0))-light.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.light_add(type='SUN',location=(0,0,6));bpy.context.object.data.energy=1.8;bpy.context.object.rotation_euler=(math.radians(28),math.radians(-25),math.radians(-25));bpy.context.object.data.angle=.15
    center=Vector((r['width']/2000,r['depth']/2000,.7));span=max(r['width'],r['depth'])/1000
    bpy.ops.object.camera_add(location=center+Vector((span*.88,-span*1.08,span*.86)))
    camera=bpy.context.object;camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=span*1.48;scene.camera=camera
    scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.device='CPU'
    import _cycles
    denoising=bool(getattr(_cycles,"with_openimagedenoise",False))
    scene.cycles.use_denoising=denoising
    if not denoising:
        scene.cycles.samples=128
        print("OpenImageDenoise unavailable: using 128 samples without denoising")
    scene.render.resolution_x=1920;scene.render.resolution_y=1440;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.filepath=str(out/'render.png')
    for obj in cut:obj.hide_render=True
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'))
    bpy.ops.render.render(write_still=True)
    (out/'render-settings.json').write_text(json.dumps({'engine':'CYCLES','resolution':[1920,1440],'samples':scene.cycles.samples,'denoising':denoising,'view':'cutaway'},indent=2))
    print('Blender export complete: metres; GLB Y-up; 1920x1440 cutaway render. Walls remain in GLB; render cutaway saved in .blend.')


if __name__=='__main__':main()
