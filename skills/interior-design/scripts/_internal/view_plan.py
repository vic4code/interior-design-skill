#!/usr/bin/env python3
"""Plan bounded image-generation work from measured spaces and existing cameras.

This module does not generate images or infer room dimensions from pictures.
Polygon coordinates are millimetres; concave polygon area uses the shoelace
formula, never its bounding rectangle. Paths resolve relative to the input JSON.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re


def number(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f'{label} must be a finite number')
    return float(value)


def cross(a, b, c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])


def intersects(a, b, c, d):
    def on_segment(p, q, r):
        return min(p[0], r[0]) <= q[0] <= max(p[0], r[0]) and min(p[1], r[1]) <= q[1] <= max(p[1], r[1])
    values = cross(a, b, c), cross(a, b, d), cross(c, d, a), cross(c, d, b)
    if values[0]*values[1] < 0 and values[2]*values[3] < 0:
        return True
    return any(v == 0 and on_segment(p, q, r) for v, p, q, r in
               ((values[0], a, c, b), (values[1], a, d, b),
                (values[2], c, a, d), (values[3], c, b, d)))


def polygon_area(points):
    if not isinstance(points, list) or len(points) < 3:
        raise ValueError('polygon_mm requires at least three [x, y] vertices')
    parsed = []
    for p in points:
        if not isinstance(p, (list, tuple)) or len(p) != 2:
            raise ValueError('polygon_mm vertices must be [x, y] pairs')
        parsed.append(tuple(number(v, 'polygon coordinate') for v in p))
    if parsed[-1] == parsed[0]:
        parsed.pop()
    if len(set(parsed)) != len(parsed) or len(parsed) < 3:
        raise ValueError('polygon_mm must have distinct non-repeated vertices')
    edges = list(zip(parsed, parsed[1:]+parsed[:1]))
    for i, (a, b) in enumerate(edges):
        for j, (c, d) in enumerate(edges[i+1:], start=i+1):
            if j == i+1 or (i == 0 and j == len(edges)-1):
                continue
            if intersects(a, b, c, d):
                raise ValueError('polygon_mm must be a simple non-self-intersecting outline')
    area = abs(sum(a[0]*b[1]-b[0]*a[1] for a, b in edges))/2/1_000_000
    if area <= 0:
        raise ValueError('polygon_mm must enclose a positive area')
    return area


def labels(items, label):
    if not isinstance(items, list):
        raise ValueError(f'{label} must be a list')
    result = []
    for item in items:
        value = item if isinstance(item, str) else item.get('name', item.get('id')) if isinstance(item, dict) else None
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f'{label} entries must be named strings or objects')
        result.append(value.strip())
    return list(dict.fromkeys(result))


def proposed_slots(space, area):
    name = space['name']
    slots = [('overview', f'{name} · 全景／入口視角')]
    if area is None:
        return slots
    if area is not None and area > 8:
        slots.append(('diagonal', f'{name} · 對角配置'))
    if area is not None and area > 20:
        slots.append(('reverse', f'{name} · 反向視角'))
    if area is not None and area > 40:
        slots.append(('connection', f'{name} · 空間連接與動線'))
    functions = labels(space.get('functions', space.get('zones', [])), 'functions/zones')
    if len(functions) > 1:
        slots.extend(('zone', f'{name} · {zone}') for zone in functions)
    # Details require a declared design feature, never an invented joinery item.
    slots.extend(('detail', f'{name} · {feature}細節') for feature in labels(space.get('features', []), 'features'))
    return slots


def candidate_views(candidates, base_dir, spaces):
    if not isinstance(candidates, list):
        raise ValueError('existing_views must be a list')
    result = []
    for index, value in enumerate(candidates):
        if not isinstance(value, dict):
            raise ValueError('existing_views entries must be objects')
        item = dict(value)
        scope = item.get('space')
        if scope is None and len(spaces) == 1:
            scope = spaces[0]['id']
        item['space'] = scope
        base = item.get('base_image')
        if base is not None and not isinstance(base, str):
            raise ValueError('base_image must be a path string')
        path = (base_dir / base).resolve() if base else None
        exists = bool(path and path.is_file())
        item['base_image'] = str(path) if exists else None
        item['base_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest() if exists else None
        item['missing_base'] = base if base and not exists else None
        item['id'] = str(item.get('id', f'reference-{index+1:02d}'))
        result.append(item)
    return result


def plan(data, base_dir, budget=12):
    if isinstance(budget, bool) or not isinstance(budget, int) or not 1 <= budget <= 100:
        raise ValueError('budget must be an integer from 1 to 100')
    spaces = data.get('spaces') if isinstance(data, dict) else data
    if not isinstance(spaces, list) or not spaces:
        raise ValueError('Input must contain a non-empty spaces list')
    ids = set()
    prepared, candidates = [], []
    if isinstance(data, dict):
        shared = data.get('existing_views', [])
        if not isinstance(shared, list):
            raise ValueError('existing_views must be a list')
        candidates.extend(shared)
    for value in spaces:
        if not isinstance(value, dict) or not isinstance(value.get('id'), str) or not value['id'].strip():
            raise ValueError('Every space requires a non-empty string id')
        space = dict(value)
        if space['id'] in ids:
            raise ValueError('Space ids must be unique')
        ids.add(space['id'])
        space['name'] = space.get('name') or space['id']
        if not isinstance(space['name'], str):
            raise ValueError('Space name must be a string')
        if 'polygon_mm' in space:
            area, source = polygon_area(space['polygon_mm']), 'polygon_mm-shoelace'
        elif space.get('area_m2') is not None:
            area, source = number(space['area_m2'], 'area_m2'), 'provided-area_m2'
            if area <= 0:
                raise ValueError('area_m2 must be positive')
        else:
            area, source = None, 'unknown'
        slots = proposed_slots(space, area)
        prepared.append(dict(id=space['id'], name=space['name'], area_m2=area,
                             area_source=source, proposed_views=len(slots), slots=slots))
        local = space.get('existing_views', [])
        if not isinstance(local, list):
            raise ValueError('existing_views must be a list')
        if not all(isinstance(item, dict) for item in local):
            raise ValueError('existing_views entries must be objects')
        candidates.extend(dict(item, space=space['id']) for item in local)
    references = candidate_views(candidates, Path(base_dir), spaces)
    used, jobs = set(), []
    # Breadth-first allocation gives each room an overview before extra angles.
    for level in range(max(len(space['slots']) for space in prepared)):
        for space in prepared:
            if level >= len(space['slots']) or len(jobs) >= budget:
                continue
            role, title = space['slots'][level]
            matching = [(index, ref) for index, ref in enumerate(references)
                        if index not in used and ref['space'] == space['id'] and ref['base_image']]
            exact = [(index, ref) for index, ref in matching if ref.get('role') == role]
            flexible = [(index, ref) for index, ref in matching if not ref.get('role')]
            chosen = (exact or flexible)[:1]
            ref = chosen[0][1] if chosen else {}
            if chosen:
                used.add(chosen[0][0])
            safe_id = re.sub(r'[^a-zA-Z0-9_-]+', '-', space['id']).strip('-') or 'space'
            jobs.append(dict(id=f'view-{len(jobs)+1:02d}-{safe_id}', space=space['id'],
                             title=title, role=role, area_m2=space['area_m2'],
                             base_image=ref.get('base_image'), base_sha256=ref.get('base_sha256'),
                             reference_id=ref.get('id'),
                             status='pending-image-generation' if ref else 'needs-base'))
    for space in prepared:
        del space['slots']
        space['planned_views'] = sum(job['space'] == space['id'] for job in jobs)
    unknown = [space['id'] for space in prepared if space['area_m2'] is None]
    return dict(schema_version='1.0', kind='image-generation-view-plan', budget=budget,
                spaces=prepared, jobs=jobs,
                deferred_views=sum(s['proposed_views']-s['planned_views'] for s in prepared),
                measurement_requests=[dict(space=ident, request='Provide a measured area or scaled polygon outline; no dimensions were inferred.') for ident in unknown],
                missing_reference_files=[dict(id=ref['id'], path=ref['missing_base']) for ref in references if ref['missing_base']],
                instructions=['This is a work plan, not generated imagery.',
                              'Use the actual base image with an image-capable generation tool; preserve camera, openings and furniture placement.',
                              'Compare each result with its base and record image provenance and spatial drift before review.',
                              'Generated images do not certify dimensions; retain authoritative geometry and construction drawings.'])


def build(source, out, budget=12):
    source, out = Path(source).resolve(), Path(out).resolve()
    if source == out:
        raise ValueError('Output must not overwrite the input spaces JSON')
    result = plan(json.loads(source.read_text(encoding='utf-8')), source.parent, budget)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--spaces', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--budget', type=int, default=12)
    args = parser.parse_args()
    build(args.spaces, args.out, args.budget)


if __name__ == '__main__':
    main()
