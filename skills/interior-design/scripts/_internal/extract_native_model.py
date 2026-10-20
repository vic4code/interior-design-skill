#!/usr/bin/env python3
"""Extract evaluated native Blender geometry without modifying the source.

Usage: blender -b model.blend --python extract_native_model.py -- --out inventory.json
All exported coordinates are world-space millimetres. Filters select actual
objects, not a replacement parametric room. Dense omitted geometry is recorded.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import sys


def safe_properties(obj):
    def value(v):
        if isinstance(v,(str,int,float,bool)) or v is None:return v
        if hasattr(v,'to_list'):return value(v.to_list())
        if isinstance(v,(list,tuple)):return [value(x) for x in v[:100]]
        if hasattr(v,'items'):return {str(k):value(x) for k,x in v.items() if not str(k).startswith('_')}
        return str(v)[:500]
    return {str(k):value(obj[k]) for k in obj.keys() if not str(k).startswith('_')}


def feature_edges(triangles,vertices,angle_degrees=25):
    """Retain mesh boundaries and creases; discard coplanar triangulation edges."""
    adjacency={}
    # Imported glTF/OBJ meshes often split every normal/UV seam into new
    # vertices. Weld only coincident coordinates for edge classification.
    canonical={};welded=[]
    for index,point in enumerate(vertices):
        key=tuple(round(v,3) for v in point)
        welded.append(canonical.setdefault(key,index))
    for triangle in triangles:
        a,b,c=[vertices[i] for i in triangle]
        u=[b[k]-a[k] for k in range(3)];v=[c[k]-a[k] for k in range(3)]
        n=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]]
        length=math.sqrt(sum(x*x for x in n))
        if length<=1e-12:continue
        n=[x/length for x in n]
        for i,j in ((triangle[0],triangle[1]),(triangle[1],triangle[2]),(triangle[2],triangle[0])):
            adjacency.setdefault(tuple(sorted((welded[i],welded[j]))),[]).append(n)
    threshold=math.cos(math.radians(angle_degrees));result=[]
    for edge,normals in adjacency.items():
        if len(normals)!=2 or sum(a*b for a,b in zip(*normals))<threshold:result.append(list(edge))
    return result


def main():
    import bpy
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--include',default='.*',help='Object/collection regular expression')
    parser.add_argument('--exclude',default=r'^$',help='Object/collection regular expression')
    parser.add_argument('--max-triangles',type=int,default=500000,help='Per-object budget; omitted meshes remain in evidence register')
    parser.add_argument('--precision',type=int,default=3)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    if not bpy.data.filepath:raise ValueError('Open a saved native file before extracting')
    source=Path(bpy.data.filepath);scene=bpy.context.scene;factor=1000*scene.unit_settings.scale_length
    if factor<=0:raise ValueError('Invalid source unit scale')
    inc=re.compile(args.include,re.I);exc=re.compile(args.exclude,re.I)
    depsgraph=bpy.context.evaluated_depsgraph_get();objects=[];omissions=[]
    instances=sorted([(i.object,i.matrix_world.copy(),tuple(i.persistent_id)) for i in depsgraph.object_instances],key=lambda i:(i[0].original.name,i[2]))
    counts={}
    for evaluated,instance_matrix,persistent_id in instances:
        obj=evaluated.original
        if obj.type not in ('MESH','CURVE','SURFACE','FONT','META'):continue
        collections=sorted(c.name for c in obj.users_collection)
        search=' '.join([obj.name]+collections)
        if not any(inc.search(v) for v in [obj.name]+collections) or any(exc.search(v) for v in [obj.name]+collections):continue
        counts[obj.name]=counts.get(obj.name,0)+1
        name=obj.name if counts[obj.name]==1 else f'{obj.name} [instance {counts[obj.name]}]'
        mesh=evaluated.to_mesh()
        if mesh is None or not len(mesh.vertices):
            evaluated.to_mesh_clear();continue
        try:
            matrix=instance_matrix
            vertices=[[round(c*factor,args.precision) for c in (matrix@v.co)] for v in mesh.vertices]
            bounds=dict(min=[min(v[k] for v in vertices) for k in range(3)],max=[max(v[k] for v in vertices) for k in range(3)])
            mesh.calc_loop_triangles();triangle_count=len(mesh.loop_triangles)
            record=dict(id=f'OBJ{len(objects)+1:05}',name=name,source_name=obj.name,type=obj.type,collections=collections,
                        custom_properties=safe_properties(obj),bbox_mm=bounds,hidden_render=obj.hide_render,
                        material_names=[m.name if m else '' for m in mesh.materials],vertex_count=len(vertices),triangle_count=triangle_count)
            if triangle_count>args.max_triangles:
                record.update(vertices_mm=[],triangles=[],feature_edges=[],geometry_status='omitted_budget')
                omissions.append(dict(id=record['id'],reason='triangle budget exceeded',triangle_count=triangle_count))
            else:
                triangles=[list(t.vertices) for t in mesh.loop_triangles]
                record.update(vertices_mm=vertices,triangles=triangles,feature_edges=feature_edges(triangles,vertices),geometry_status='evaluated_mesh')
            objects.append(record)
        finally:evaluated.to_mesh_clear()
    if not objects:raise ValueError('No geometry matched the selection')
    bounds=dict(min=[min(o['bbox_mm']['min'][k] for o in objects) for k in range(3)],max=[max(o['bbox_mm']['max'][k] for o in objects) for k in range(3)])
    inventory=dict(format='native-model-inventory-v1',source=dict(filename=source.name,sha256=hashlib.sha256(source.read_bytes()).hexdigest()),
                   units=dict(coordinate_unit='mm',source_scale_length=scene.unit_settings.scale_length),axes=dict(x='native X',y='native Y',z='native Z / up'),
                   extractor_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),bounds_mm=bounds,selection=dict(include=args.include,exclude=args.exclude),objects=objects,omissions=omissions,
                   evidence='Evaluated scene geometry only; modeled dimensions are not surveyed measurements or approved fabrication dimensions.')
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(inventory,separators=(',',':'),ensure_ascii=False)+'\n')
    print(f'Extracted {len(objects)} evaluated object records; {len(omissions)} geometry omissions; {args.out.stat().st_size} bytes')

if __name__=='__main__':main()
