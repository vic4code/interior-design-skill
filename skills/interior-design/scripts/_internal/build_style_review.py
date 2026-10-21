#!/usr/bin/env python3
"""Join a verified style scene and drawing study into the bundled browser format."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
from PIL import Image
from build_review import safe_file
from output_ownership import verify_inputs_outside, verify_output_directory


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build(study, drawings, out):
    study, drawings = [Path(p).resolve() for p in (study, drawings)]
    out = verify_output_directory(out, expected={'schema_version': '1.0'})
    verify_inputs_outside(out, [study, drawings])
    rendered = json.loads((study/'render-settings.json').read_text())
    issued = json.loads((drawings/'manifest.json').read_text())
    dimensions = json.loads((study/'model_dimensions.json').read_text())
    project = json.loads((drawings/'project.json').read_text())
    for key in ('project.json', 'joinery.json', 'styles.json'):
        if rendered['source_sha256'][key] != issued['sources'][key]:
            raise ValueError('Render and drawing sources differ: '+key)
    if rendered['revision'] != project['project']['revision']:
        raise ValueError('Render and drawing revisions differ')
    if rendered['style'] != issued['style']:
        raise ValueError('Render and drawing styles differ')
    source_files = {name: safe_file(drawings, name) for name in issued['files']}
    for name, sha in issued['files'].items():
        if digest(source_files[name]) != sha:
            raise ValueError('Drawing artifact checksum mismatch: '+name)
    expected = {f['id']: [f[k] for k in ('x','y','width','depth','height')] for f in project['furniture']}
    actual = {f['id']: [f[k] for k in ('x','y','width','depth','height')] for f in dimensions['furniture']}
    if expected != actual:
        raise ValueError('Render/drawing nominal furniture dimensions differ')
    out.mkdir(parents=True, exist_ok=True)
    if (out/'manifest.json').is_file():
        previous = json.loads((out/'manifest.json').read_text())
        for item in previous['files']:
            (out/item['name']).unlink()
        (out/'manifest.json').unlink()
    names = []
    for name in issued['files']:
        target = 'drawings.pdf' if name == 'design-coordination.pdf' else name
        shutil.copyfile(source_files[name], out/target); names.append(target)
    for name in ('scene.glb','render-settings.json','model_dimensions.json'):
        shutil.copyfile(study/name, out/name); names.append(name)
    with Image.open(study/'hero.png') as image:
        clean = Image.new(image.mode,image.size); clean.paste(image); clean.save(out/'render.png')
        size = image.size
    names.append('render.png')
    with (drawings/'issues.csv').open(newline='') as file:
        reviews = [dict(id=row['id'], topic=row['decision'], detail=row['status']) for row in csv.DictReader(file)]
    (out/'review.json').write_text(json.dumps(reviews,ensure_ascii=False,indent=2)+'\n'); names.append('review.json')
    (out/'handoff.md').write_text('# Style review / design coordination\n\nRead the drawing issue register and technical evidence before trade release.\n'); names.append('handoff.md')
    manifest = dict(schema_version='1.0',revision=rendered['revision'],status='coordination_draft',has_model=True,
                    style_name=rendered['style'],render_label=f'{size[0]} × {size[1]} / PNG',
                    plan_label='A101 / A3 · scale on sheet · mm',source_sha256=issued['sources']['project.json'],
                    files=[dict(name=name,bytes=(out/name).stat().st_size,sha256=digest(out/name)) for name in sorted(set(names))])
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return manifest


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--study',type=Path,required=True)
    parser.add_argument('--drawings',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    try:result=build(args.study,args.drawings,args.out)
    except (ValueError,OSError,KeyError) as error:parser.exit(1,f'Style review failed: {error}\n')
    print(f'Built browser review: {len(result["files"])} checksummed files; {result["style_name"]} / {result["revision"]}')


if __name__=='__main__':main()
