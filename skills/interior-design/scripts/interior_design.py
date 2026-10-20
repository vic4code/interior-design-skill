#!/usr/bin/env python3
"""One entry point: assemble drawings, image-generation presentation, and a browser review.

Generate presentation images with your agent's image tool before packaging a real
project. The bundled demo includes a reviewed synthetic example; no Blender or
image API is needed to try it. All geometry measurements remain in the drawings.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
INTERNAL = ROOT / 'scripts/_internal'
sys.path.insert(0, str(INTERNAL))


def run_helper(name, arguments):
    subprocess.run([sys.executable, str(INTERNAL / (name + '.py')), *map(str, arguments)], check=True)


def finish(review, args):
    print(f'Review package: {review}')
    if not args.no_serve:
        from open_review import launch
        print(launch(review, args.viewer, open_browser=not args.no_open)['url'])


def presentation_arguments(parser):
    parser.add_argument('--image', type=Path, help='Actual image-generation result, paired with provenance.')
    parser.add_argument('--base-image', type=Path, help='Geometry/camera reference used by image generation.')
    parser.add_argument('--provenance', type=Path, help='Image/base checksums, mode, and review status JSON.')
    parser.add_argument('--model', type=Path, help='Optional lightweight GLB for spatial inspection.')
    parser.add_argument('--metadata', type=Path, help='Optional project display metadata JSON.')


def browser_arguments(parser):
    parser.add_argument('--no-open', action='store_true', help='Serve without opening the browser.')
    parser.add_argument('--no-serve', action='store_true', help='Package only; no Node or browser required.')
    parser.add_argument('--viewer', type=Path, help='Optional prebuilt viewer directory.')


def package_review(drawings, out, args):
    from build_review import build
    build(drawings, out, presentation=args.image, base_image=args.base_image,
          provenance=args.provenance, model=args.model, metadata=args.metadata)
    finish(out, args)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    views = commands.add_parser('views', help='Plan image-generation views from actual room areas and reference cameras.')
    views.add_argument('--spaces', type=Path, required=True, help='Spaces, optional polygons/zones, and existing reference image JSON.')
    views.add_argument('--out', type=Path, required=True, help='Write planned jobs; this command never generates images.')
    views.add_argument('--budget', type=int, default=12, help='Maximum planned image jobs across all spaces (default: 12).')
    demo = commands.add_parser('demo', help='Try a complete eight-sheet sample and conditioned presentation.')
    demo.add_argument('--out', required=True, type=Path)
    browser_arguments(demo)
    review = commands.add_parser('review', help='Package existing drawings and presentation; open the browser.')
    source = review.add_mutually_exclusive_group(required=True)
    source.add_argument('--drawings', type=Path)
    source.add_argument('--variants', type=Path, help='Same-space variant configuration JSON.')
    source.add_argument('--existing', type=Path, help='Open an already assembled review package.')
    review.add_argument('--out', type=Path)
    review.add_argument('--stop', action='store_true', help='Stop the browser server for --existing.')
    presentation_arguments(review)
    browser_arguments(review)
    native = commands.add_parser('native', help='Extract existing Blender geometry, draw, package, and open.')
    source = native.add_mutually_exclusive_group(required=True)
    source.add_argument('--blend', type=Path)
    source.add_argument('--inventory', type=Path, help='Reuse a previously extracted geometry inventory.')
    native.add_argument('--config', type=Path, required=True, help='Views, dimensions and explicit annotations JSON.')
    native.add_argument('--out', type=Path, required=True)
    native.add_argument('--blender', default='blender', help='Blender executable, only required with --blend.')
    presentation_arguments(native)
    browser_arguments(native)
    # Advanced actions retain their established arguments behind the same entry point.
    for name, description in [('install', 'Copy the complete skill into an agent host.'),
                              ('project', 'Validate/build a starter project JSON.'),
                              ('verify', 'Verify a starter output package.'),
                              ('render', 'Optional procedural Blender style study (requires Blender).')]:
        commands.add_parser(name, help=description, add_help=False)
    if len(sys.argv) > 1 and sys.argv[1] in ('install', 'project', 'verify', 'render'):
        command = sys.argv[1]
        helper = dict(install='install_skill', project='project', verify='verify_outputs', render='render_style_studies')[command]
        if command == 'render':
            binary = shutil.which('blender')
            if not binary:
                parser.error('Blender is required only for procedural rendering; use image generation for presentation.')
            subprocess.run([binary, '--background', '--threads', '4', '--python-exit-code', '1',
                            '--python', str(INTERNAL/(helper+'.py')), '--', *sys.argv[2:]], check=True)
        else:
            run_helper(helper, sys.argv[2:])
        return
    args = parser.parse_args()
    if args.command == 'views':
        from view_plan import build
        result = build(args.spaces, args.out, budget=args.budget)
        print(f"Planned {len(result['jobs'])} image views: {args.out}")
        print('Use the agent image-generation tool for each ready job; missing references remain needs-base.')
    elif args.command == 'demo':
        from build_drawing_studies import build
        assets = ROOT / 'assets'
        sample = assets/'review-demo'
        styles = [('mcm', 'Mid-century Modern', '#956c47'), ('japandi', 'Japandi', '#c9bb9d'),
                  ('contemporary', 'Contemporary', '#8b847b'), ('bauhaus', 'Bauhaus', '#bd3831')]
        required = [sample/'base.jpg']
        required += [sample/'variants'/ident/name for ident, _, _ in styles
                     for name in ('presentation.jpg', 'image-provenance.json', 'space.glb')]
        if not all(path.is_file() for path in required):
            parser.error('The complete skill must include a shared demo base and four presentation/provenance/GLB variants.')
        output = args.out.resolve()
        entries = []
        for ident, label, swatch in styles:
            drawings = output/'drawings'/ident
            build(assets/'style-studies/project.json', assets/'style-studies/joinery.json', drawings, style=ident)
            variant = sample/'variants'/ident
            entries.append(dict(id=ident, label=label, swatch=swatch, source=str(drawings),
                                presentation=str(variant/'presentation.jpg'), base_image=str(sample/'base.jpg'),
                                provenance=str(variant/'image-provenance.json'), model=str(variant/'space.glb')))
            if ident == 'mcm':
                entries[-1]['metadata'] = str(sample/'lighting/metadata.json')
        output.mkdir(parents=True, exist_ok=True)
        config = output/'variants-config.json'
        config.write_text(json.dumps(dict(variants=entries), indent=2)+'\n', encoding='utf-8')
        from build_review import build_variants
        build_variants(config, output/'review')
        finish(output/'review', args)
    elif args.command == 'review':
        if args.existing:
            if args.stop:
                from open_review import stop
                print('Viewer stopped.' if stop(args.existing.resolve()) else 'No running viewer for this package.')
            else:
                finish(args.existing.resolve(), args)
        else:
            if not args.out:
                parser.error('review --drawings or --variants requires --out')
            if args.stop:
                parser.error('--stop requires --existing')
            if args.variants:
                if any((args.image, args.base_image, args.provenance, args.model, args.metadata)):
                    parser.error('Put per-variant presentation options in --variants configuration')
                from build_review import build_variants
                build_variants(args.variants, args.out.resolve())
                finish(args.out.resolve(), args)
            else:
                package_review(args.drawings, args.out.resolve(), args)
    elif args.command == 'native':
        output = args.out.resolve()
        inventory = args.inventory
        if args.blend:
            binary = shutil.which(args.blender)
            if not binary:
                parser.error('Blender executable was not found; provide --blender PATH or --inventory JSON.')
            if not args.blend.is_file():
                parser.error('Native Blender source does not exist.')
            output.mkdir(parents=True, exist_ok=True)
            inventory = output/'geometry-inventory.json'
            subprocess.run([binary, '--background', str(args.blend.resolve()), '--python-exit-code', '1',
                            '--python', str(INTERNAL/'extract_native_model.py'), '--', '--out', str(inventory)], check=True)
        from build_native_handoff import build
        build(inventory.resolve(), output/'drawings', args.config.resolve())
        package_review(output/'drawings', output/'review', args)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f'Interior design failed: {error}', file=sys.stderr)
        sys.exit(1)
