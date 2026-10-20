"""Verify current generated artifact integrity, resolution and GLB structure."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import xml.etree.ElementTree as ET
from PIL import Image


def verify(out):
    manifest=json.loads((out/'manifest.json').read_text());data=json.loads((out/'project.json').read_text())
    assert manifest['revision']==data['project']['revision'],'Revision mismatch'
    for item in manifest['files']:
        p=out/item['name']
        assert p.stat().st_size==item['bytes'],item['name']+' size mismatch'
        assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],item['name']+' checksum mismatch'
    assert (out/'drawings.pdf').read_bytes().startswith(b'%PDF-')
    for name in ['A101','A201','A202','A203','A204']:
        ET.parse(out/(name+'.svg'))
    if manifest['has_model']:
        with Image.open(out/'render.png') as im:
            assert im.size==(1920,1440),im.size
            # A blank image isn't a successful render.
            extrema=im.convert('RGB').getextrema()
            assert max(high-low for low,high in extrema)>40,'Blank render'
        raw=(out/'scene.glb').read_bytes();magic,version,length=struct.unpack_from('<4sII',raw)
        assert (magic,version,length)==(b'glTF',2,len(raw))
        count,kind=struct.unpack_from('<I4s',raw,12);assert kind==b'JSON'
        gltf=json.loads(raw[20:20+count]);names=[n.get('name','') for n in gltf['nodes']]
        assert any(n.startswith('wall_north') for n in names)
        for f in data['furniture']:assert any(n.startswith('furniture_'+f['id']) for n in names),f['id']
        assert (out/'scene.blend').read_bytes().startswith(b'BLENDER') or (out/'scene.blend').stat().st_size>10000
        settings=json.loads((out/'render-settings.json').read_text());assert settings['resolution']==[1920,1440]
    print(f'Verified {len(manifest["files"])} checksummed artifacts; revision {manifest["revision"]}; model={manifest["has_model"]}')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('directory',type=Path);args=parser.parse_args();verify(args.directory)
