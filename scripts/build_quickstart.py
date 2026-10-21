#!/usr/bin/env python3
"""Maintainer: rebuild the offline demo drawings and production browser viewer."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]/'skills/interior-design'
sys.path.insert(0, str(ROOT/'scripts/_internal'))
from build_drawing_studies import build
from output_ownership import write_output_manifest
from quickstart import inputs


def register(directory, kind):
    data = write_output_manifest(directory, 'quickstart-'+kind+'-v1', manifest_name='bundle.json')
    data['inputs'] = inputs(ROOT, kind)
    (directory/'bundle.json').write_text(json.dumps(data, indent=2)+'\n')


def main():
    drawings = ROOT/'assets/review-demo/drawings'
    for style in ('mcm', 'japandi', 'contemporary', 'bauhaus'):
        build(ROOT/'assets/style-studies/project.json', ROOT/'assets/style-studies/joinery.json',
              drawings/style, style=style)
    register(drawings, 'drawings')
    viewer = ROOT/'assets/viewer'
    if not (viewer/'node_modules/.bin/vite').is_file():
        subprocess.run(['npm', 'ci', '--ignore-scripts'], cwd=viewer, check=True)
    subprocess.run(['npm', 'run', 'build', '--', '--outDir', 'prebuilt'], cwd=viewer, check=True)
    # Vite public assets are runtime output, never part of the shipped viewer.
    if (viewer/'prebuilt/generated').exists():
        shutil.rmtree(viewer/'prebuilt/generated')
    shutil.copyfile(viewer/'node_modules/three/LICENSE', viewer/'prebuilt/THREE-LICENSE.txt')
    register(viewer/'prebuilt', 'viewer')


if __name__ == '__main__':
    main()
