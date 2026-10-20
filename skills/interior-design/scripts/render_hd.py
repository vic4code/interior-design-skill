"""Render an existing .blend at an explicit resolution, without altering its source."""
import argparse
from pathlib import Path
import sys
import bpy

parser=argparse.ArgumentParser()
parser.add_argument('--width',type=int,default=3840);parser.add_argument('--height',type=int,default=2880)
parser.add_argument('--samples',type=int,default=128);parser.add_argument('--out',type=Path,required=True)
args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
if not (256 <= args.width <= 8192 and 256 <= args.height <= 8192 and 1 <= args.samples <= 4096):
    parser.error('Resolution must be 256..8192 and samples 1..4096')
args.out.parent.mkdir(parents=True,exist_ok=True)
scene=bpy.context.scene;scene.render.resolution_x=args.width;scene.render.resolution_y=args.height;scene.render.resolution_percentage=100
scene.render.engine='CYCLES';scene.cycles.samples=args.samples;scene.cycles.use_denoising=bool(getattr(__import__('_cycles'),'with_openimagedenoise',False))
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(args.out.resolve())
bpy.ops.render.render(write_still=True)
