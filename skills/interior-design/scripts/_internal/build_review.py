#!/usr/bin/env python3
"""Package verified existing drawings and optional presentation for the generic viewer.

This copies deliverables; it neither changes geometry nor generates images.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import shutil
import tempfile
import xml.etree.ElementTree as ET
from layout_preview import create_layout
from pdf_preview import render_pdf_pages

ALLOWED = {'.json', '.svg', '.pdf', '.csv', '.dxf', '.md', '.txt', '.png', '.jpg', '.jpeg', '.webp', '.glb'}
IMAGE_TYPES = {'.png', '.jpg', '.jpeg', '.webp'}


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def safe_file(root, name):
    part = PurePosixPath(name)
    if not name or part.as_posix() != name or '\\' in name or part.is_absolute() or '..' in part.parts or ':' in name:
        raise ValueError('Unsafe artifact path: ' + name)
    path = root.joinpath(*part.parts)
    if any(p.is_symlink() for p in (path, *path.parents) if p != root.parent):
        raise ValueError('Symlink artifact is not supported: ' + name)
    if not path.is_file() or not path.resolve().is_relative_to(root):
        raise ValueError('Missing artifact: ' + name)
    return path


def registered_files(source, manifest, *, browser=False):
    files = manifest.get('files')
    if isinstance(files, dict):
        entries = [dict(name=name, sha256=sha) for name, sha in files.items()]
    elif isinstance(files, list):
        entries = files
    else:
        raise ValueError('Source manifest must register checksummed files')
    result = {}
    for entry in entries:
        name = entry['name']
        if name in result or name == 'manifest.json' or (name == 'source-manifest.json' and not browser):
            raise ValueError('Duplicate or reserved artifact: ' + name)
        path = safe_file(source, name)
        if not isinstance(entry.get('sha256'), str) or digest(path) != entry['sha256']:
            raise ValueError('Source artifact checksum mismatch: ' + name)
        if 'bytes' in entry and path.stat().st_size != entry['bytes']:
            raise ValueError('Source artifact size mismatch: ' + name)
        # Inventories and native authoring files are not browser deliverables.
        if path.suffix.lower() in ALLOWED and 'inventory' not in path.name.lower():
            result[name] = path
    return result


def sheet_details(path):
    root = ET.parse(path).getroot()
    texts = [(node.attrib, ''.join(node.itertext()).strip()) for node in root.iter() if node.tag.endswith('}text') or node.tag == 'text']
    title = next((text for attrs, text in texts if attrs.get('y') == '29'), '')
    if not title:
        title = next((text for attrs, text in texts if text and attrs.get('font-size') in ('5', '5.1')), path.stem)
    scale = next((text for _, text in texts if re.fullmatch(r'1\s*:\s*[\d.]+', text)), None)
    return title, scale


def project_and_sheets(files, manifest):
    project = dict(name='Existing design project', brief='', revision=manifest.get('revision', 'Unspecified'))
    sheets = []
    if 'selection.json' in files and 'views.json' in files:
        selection, views = read_json(files['selection.json']), read_json(files['views.json'])
        name = selection.get('project')
        if isinstance(name, str):
            project['name'] = name
        project.update(brief=selection.get('brief', ''), revision=selection.get('revision', 'N01'))
        for view in views:
            name = view['sheet'] + '.svg'
            if name not in files:
                raise ValueError('Native view sheet is not registered: ' + name)
            sheets.append(dict(id=view['sheet'], title=view['title'], file=name, kind=view['kind'], scale=f"1:{view['scale']:g}" if isinstance(view.get('scale'), (float, int)) else view.get('scale')))
    else:
        if 'project.json' in files:
            data = read_json(files['project.json'])
            project.update({key: data.get('project', {})[key] for key in ('name', 'brief', 'revision') if key in data.get('project', {})})
            room = data.get('room', {})
            if all(isinstance(room.get(k), (int, float)) and room[k] > 0 for k in ('width', 'depth')):
                project['area_m2'] = room['width'] * room['depth'] / 1e6
            if isinstance(room.get('height'), (int, float)) and room['height'] > 0:
                project['ceiling_height_mm'] = room['height']
        for name, path in files.items():
            if path.suffix.lower() == '.svg':
                title, scale = sheet_details(path)
                sheets.append(dict(id=path.stem, title=title, file=name, kind='drawing', scale=scale))
    if not sheets:
        raise ValueError('No registered drawing sheets found')
    if len({sheet['id'] for sheet in sheets}) != len(sheets):
        raise ValueError('Duplicate sheet IDs')
    return project, sheets


def build(source, out, presentation=None, base_image=None, provenance=None, model=None, metadata=None):
    source = Path(source).resolve()
    original_out = Path(out).absolute()
    if original_out.is_symlink():
        raise ValueError('Output cannot be a symlink')
    out = original_out.resolve()
    if source == out or source in out.parents or out in source.parents:
        raise ValueError('Output must be separate from source')
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        if not (out / 'manifest.json').is_file() or read_json(out / 'manifest.json').get('schema_version') not in ('1.0', '2.0'):
            raise ValueError('Refusing to replace a directory without a browser package manifest')
    issued = read_json(safe_file(source, 'manifest.json'))
    files = registered_files(source, issued)
    project, sheets = project_and_sheets(files, issued)
    metadata_config = read_json(metadata) if metadata else {}
    if metadata:
        display = metadata_config.get('project', {key: value for key, value in metadata_config.items() if key not in ('presentations', 'mep')})
        if set(display) - {'name', 'brief', 'revision', 'area_m2', 'ceiling_height_mm'}:
            raise ValueError('Metadata contains unsupported display fields')
        for key, value in display.items():
            if key in ('area_m2', 'ceiling_height_mm'):
                if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or value <= 0:
                    raise ValueError('Invalid display measurement: ' + key)
            elif not isinstance(value, str):
                raise ValueError('Invalid display text: ' + key)
        project.update(display)
    if bool(presentation) != bool(provenance) or (base_image and not presentation):
        raise ValueError('Presentation and provenance must be paired; base requires presentation')
    extra = {}
    view = dict(image=None, kind='none', base_image=None, provenance=None, review_status='unavailable')
    if presentation:
        presentation = Path(presentation)
        if presentation.suffix.lower() not in IMAGE_TYPES:
            raise ValueError('Presentation must be a PNG, JPEG or WebP image')
        evidence = read_json(provenance)
        mode = evidence.get('mode')
        if mode not in ('completion-simulation', 'concept'):
            raise ValueError('Unsupported presentation provenance mode')
        if evidence.get('review_status') not in ('pending', 'accepted-for-visualization'):
            raise ValueError('Presentation review_status must be pending or accepted-for-visualization')
        if evidence.get('image_sha256') != digest(presentation):
            raise ValueError('Presentation checksum differs from provenance')
        if mode == 'completion-simulation' and not base_image:
            raise ValueError('Completion simulation requires its actual base image')
        if base_image:
            base_image = Path(base_image)
            if base_image.suffix.lower() not in IMAGE_TYPES or evidence.get('base_sha256') != digest(base_image):
                raise ValueError('Base image checksum differs from provenance')
            extra['presentation/base' + base_image.suffix.lower()] = base_image
            view['base_image'] = 'presentation/base' + base_image.suffix.lower()
        elif evidence.get('base_sha256'):
            raise ValueError('Provenance declares a base image but none was supplied')
        name = 'presentation/image' + presentation.suffix.lower()
        extra[name] = presentation
        extra['presentation/provenance.json'] = Path(provenance)
        view.update(image=name, kind=mode, provenance='presentation/provenance.json', review_status=evidence['review_status'])
    else:
        render = next((name for name in ('render.png', 'hero.png', 'render.jpg') if name in files), None)
        if render:
            view.update(image=render, kind='model-render', review_status='pending')
    model_name = None
    if model:
        if Path(model).suffix.lower() != '.glb':
            raise ValueError('Model must be a GLB')
        extra['geometry/model.glb'] = Path(model)
        model_name = 'geometry/model.glb'
    elif 'scene.glb' in files:
        model_name = 'scene.glb'
    presentations = []
    if view.get('image'):
        presentations.append(dict(view, id='primary', title='空間整體', space=''))
    metadata_root = Path(metadata).resolve().parent if metadata else source

    def attachment(value, suffixes, label):
        if not isinstance(value, str) or not value or '\\' in value:
            raise ValueError('Invalid ' + label + ' attachment path')
        given = Path(value)
        candidate = given if given.is_absolute() else metadata_root / given
        if any(part.is_symlink() for part in (candidate, *candidate.parents)):
            raise ValueError('Symlink attachment is not supported')
        path = candidate.resolve()
        if not path.is_file() or path.suffix.lower() not in suffixes:
            raise ValueError('Unsupported or missing ' + label + ' attachment')
        if path == out or out in path.parents:
            raise ValueError('Attachments must be outside output')
        return path

    seen_views = {'primary'}
    for item in metadata_config.get('presentations', []):
        ident = str(item.get('id', ''))
        if not re.fullmatch(r'[a-z0-9][a-z0-9_-]*', ident) or ident in seen_views:
            raise ValueError('Presentation ID must be unique safe lowercase slug')
        seen_views.add(ident)
        image = attachment(item.get('image'), IMAGE_TYPES, 'presentation')
        evidence_path = attachment(item.get('provenance'), {'.json'}, 'provenance')
        evidence = read_json(evidence_path)
        kind, status = evidence.get('mode'), evidence.get('review_status')
        if kind not in ('completion-simulation', 'concept') or status not in ('pending', 'accepted-for-visualization'):
            raise ValueError('Invalid additional presentation provenance mode or review_status')
        if evidence.get('image_sha256') != digest(image):
            raise ValueError('Additional presentation checksum differs from provenance')
        prefix = 'presentation/views/' + ident + '/'
        entry = dict(id=ident, title=item.get('title', ident), space=item.get('space', ''), image=prefix+'image'+image.suffix.lower(), base_image=None, provenance=prefix+'provenance.json', kind=kind, review_status=status)
        if not all(isinstance(entry[k], str) for k in ('title', 'space')):
            raise ValueError('Presentation title and space must be strings')
        extra[entry['image']] = image
        extra[entry['provenance']] = evidence_path
        if item.get('base_image'):
            base = attachment(item['base_image'], IMAGE_TYPES, 'base image')
            if evidence.get('base_sha256') != digest(base):
                raise ValueError('Additional base image checksum differs from provenance')
            entry['base_image'] = prefix+'base'+base.suffix.lower()
            extra[entry['base_image']] = base
        elif kind == 'completion-simulation' or evidence.get('base_sha256'):
            raise ValueError('Additional completion simulation requires its actual base image')
        presentations.append(entry)

    mep = []
    # A102 is a bundled reflected-ceiling / electrical-intent sheet, never a
    # substitute for coordinated circuits, HVAC, plumbing or specialist design.
    if 'A102.svg' in files:
        sheet = next((s for s in sheets if s['file'] == 'A102.svg'), None)
        mep.append(dict(id='A102', title=sheet['title'] if sheet else 'Reflected ceiling and electrical intent', file='A102.svg', kind='lighting-electrical-intent', status=issued.get('status', 'coordination_draft'), reference='Source registered drawing; engineering review required'))
    seen_mep = {item['id'] for item in mep}
    for item in metadata_config.get('mep', []):
        ident = str(item.get('id', ''))
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]*', ident) or ident in seen_mep:
            raise ValueError('MEP ID must be a unique safe slug')
        seen_mep.add(ident)
        path = attachment(item.get('source'), {'.svg', '.pdf'}, 'MEP')
        if not isinstance(item.get('sha256'), str) or item['sha256'] != digest(path):
            raise ValueError('MEP attachment checksum must match explicit registration')
        name = 'mep/' + ident + path.suffix.lower()
        extra[name] = path
        entry = dict(id=ident, title=item.get('title', ident), file=name, kind=item.get('kind', 'engineering-reference'), status=item.get('status', 'pending'), reference=item.get('reference', ''))
        if not all(isinstance(entry[k], str) and (bool(entry[k]) or k == 'reference') for k in ('title', 'kind', 'status', 'reference')):
            raise ValueError('Invalid MEP descriptive metadata')
        mep.append(entry)
    layout_svg, layout = create_layout(files, sheets, read_json)
    if layout and layout['file'] in files:
        raise ValueError('Source artifact conflicts with layout path')
    if set(extra) & set(files):
        raise ValueError('Source artifact conflicts with presentation package paths')
    out.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.review-', dir=out.parent))
    try:
        for name, path in {**files, **extra}.items():
            target = staging / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
        preview_mep = []
        for entry in mep:
            if Path(entry['file']).suffix.lower() != '.pdf':
                preview_mep.append(entry)
                continue
            original = entry['file']
            preview_prefix = 'mep/previews/' + entry['id'] + '/'
            pages = render_pdf_pages(staging/original, staging/preview_prefix)
            for number, filename in enumerate(pages, 1):
                preview_mep.append(dict(entry, id=entry['id']+f'-p{number:03d}', title=entry['title']+f' · {number}/{len(pages)}', file=preview_prefix+filename, original_file=original, source_page=number))
        mep = preview_mep
        if len({item['id'] for item in mep}) != len(mep):
            raise ValueError('MEP page IDs conflict with registered attachment IDs')
        if layout_svg:
            (staging/'layout.svg').write_text(layout_svg, encoding='utf-8')
        shutil.copyfile(source / 'manifest.json', staging / 'source-manifest.json')
        names = sorted(p.relative_to(staging).as_posix() for p in staging.rglob('*') if p.is_file())
        result = dict(schema_version='2.0', revision=project['revision'], status=issued.get('status', 'coordination_draft'), project=project, presentation=view, presentations=presentations, layout=layout, mep=mep, model=model_name, sheets=sheets,
                      files=[dict(name=name, bytes=(staging/name).stat().st_size, sha256=digest(staging/name)) for name in names])
        (staging/'manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        if out.exists():
            shutil.rmtree(out)
        staging.rename(out)
        return result
    finally:
        if staging.exists():
            shutil.rmtree(staging)



def build_variants(config, out):
    """Build one browser package with independently verified, same-space variants.

    Config is {"variants": [{"id", "label", "source", "presentation", ...}]}.
    Relative input paths resolve against the config directory. Each drawing source
    must register identical project/joinery inputs or native source/inventory hashes;
    finish/style choices may vary. Native groups do not need starter room JSON.
    """
    config = Path(config).resolve()
    spec = read_json(config)
    variants = spec.get('variants') if isinstance(spec, dict) else None
    if not isinstance(variants, list) or not variants:
        raise ValueError('Variants config must contain a nonempty variants list')
    output = Path(out).absolute()
    if output.is_symlink():
        raise ValueError('Output cannot be a symlink')
    output = output.resolve()
    if config == output or output in config.parents:
        raise ValueError('Output must be separate from variants configuration')
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        if not (output/'manifest.json').is_file() or read_json(output/'manifest.json').get('schema_version') != '2.0':
            raise ValueError('Refusing to replace a directory without a browser package manifest')
    entries, identities, base_hashes = [], [], []
    seen = set()
    for item in variants:
        if not isinstance(item, dict) or not re.fullmatch(r'[a-z0-9][a-z0-9_-]*', str(item.get('id', ''))):
            raise ValueError('Variant ID must be a safe lowercase slug')
        ident = item['id']
        if ident in seen:
            raise ValueError('Duplicate variant ID: ' + ident)
        seen.add(ident)
        if not isinstance(item.get('label'), str) or not item['label'].strip():
            raise ValueError('Variant label is required: ' + ident)
        if item.get('swatch') is not None and not re.fullmatch(r'#[0-9a-fA-F]{6}', item['swatch']):
            raise ValueError('Variant swatch must be a six-digit hex color')
        paths = {}
        for key in ('source', 'presentation', 'base_image', 'provenance', 'model', 'metadata'):
            if item.get(key) is not None:
                if not isinstance(item[key], str):
                    raise ValueError('Variant input path must be text: ' + key)
                path = Path(item[key])
                paths[key] = (config.parent/path).resolve() if not path.is_absolute() else path.resolve()
                if paths[key] == output or output in paths[key].parents or paths[key] in output.parents:
                    raise ValueError('Output must be separate from all variant inputs')
        if 'source' not in paths:
            raise ValueError('Variant source is required: ' + ident)
        issued = read_json(safe_file(paths['source'], 'manifest.json'))
        files = registered_files(paths['source'], issued)
        if issued.get('format') == 'native-handoff-v1':
            hashes = issued.get('source_hashes')
            if not isinstance(hashes, dict) or any(not isinstance(hashes.get(key), str) or
                    not re.fullmatch(r'[0-9a-f]{64}', hashes[key]) for key in ('native_file', 'inventory')):
                raise ValueError('Native variants require valid native_file and inventory source hashes')
            identities.append(('native', hashes['native_file'], hashes['inventory']))
        else:
            if not {'project.json', 'joinery.json'} <= files.keys():
                raise ValueError('Same-space variants require registered project.json and joinery.json')
            # Include room shape, opening IDs, furniture coordinates and joinery
            # dimensions, not just area. Native groups never use this contract.
            identities.append(('structured', *(digest(files[key]) for key in ('project.json', 'joinery.json'))))
        if paths.get('provenance'):
            base_hashes.append(read_json(paths['provenance']).get('base_sha256'))
        entries.append((item, paths))
    if len(set(identities)) != 1:
        raise ValueError('Same-space variants must share identical project and joinery geometry inputs, or identical native geometry source hashes; native and structured groups cannot mix')
    if base_hashes and (not all(base_hashes) or len(base_hashes) != len(entries) or len(set(base_hashes)) != 1):
        raise ValueError('Same-space presentations must share one conditioning base image')
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.variants-', dir=output.parent))
    try:
        children, first = [], None
        for item, paths in entries:
            prefix = 'variants/' + item['id'] + '/'
            child = build(out=staging/prefix, **paths)
            if first is None:
                first = (child, prefix)
            entry = dict(id=item['id'], label=item['label'], manifest=prefix+'manifest.json')
            if child['presentation'].get('image'):
                entry['thumbnail'] = prefix + child['presentation']['image']
            if item.get('swatch'):
                entry['swatch'] = item['swatch']
            children.append(entry)
        child, prefix = first
        presentation = dict(child['presentation'])
        for key in ('image', 'base_image', 'provenance'):
            if presentation.get(key):
                presentation[key] = prefix + presentation[key]
        sheets = [dict(sheet, file=prefix+sheet['file']) for sheet in child['sheets']]
        layout = dict(child['layout'], file=prefix+child['layout']['file']) if child.get('layout') else None
        mep = [dict(item, **{key: prefix+item[key] for key in ('file', 'original_file') if item.get(key)}) for item in child.get('mep', [])]
        presentations = [dict(item, **{key: prefix+item[key] for key in ('image', 'base_image', 'provenance') if item.get(key)}) for item in child.get('presentations', [])]
        names = sorted(path.relative_to(staging).as_posix() for path in staging.rglob('*') if path.is_file())
        result = dict(schema_version='2.0', revision=child['revision'], status=child['status'],
                      project=child['project'], presentation=presentation, presentations=presentations, layout=layout, mep=mep,
                      model=prefix+child['model'] if child.get('model') else None,
                      sheets=sheets, default_variant=children[0]['id'], variants=children,
                      files=[dict(name=name, bytes=(staging/name).stat().st_size, sha256=digest(staging/name)) for name in names])
        (staging/'manifest.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        if output.exists():
            shutil.rmtree(output)
        staging.rename(output)
        return result
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'out', 'presentation', 'base-image', 'provenance', 'model', 'metadata'):
        parser.add_argument('--' + name, type=Path, required=name in ('source', 'out'))
    args = parser.parse_args()
    try:
        result = build(**vars(args))
    except (ValueError, OSError, KeyError, TypeError, ET.ParseError) as error:
        parser.exit(1, f'Review package failed: {error}\n')
    print(f'Built {len(result["sheets"])} actual sheets and {len(result["files"])} verified files in {args.out}')


if __name__ == '__main__':
    main()
