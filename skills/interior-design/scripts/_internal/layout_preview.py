"""Readable furniture layout previews from registered spatial evidence only."""
import copy
import html
import math
import xml.etree.ElementTree as ET

SVG = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG)


def structured_layout(project):
    room = project.get('room', {})
    w, d = room.get('width'), room.get('depth')
    if not all(isinstance(v, (int, float)) and math.isfinite(v) and v > 0 for v in (w, d)):
        return None
    # This route is exclusively for the structured rectangular starter contract.
    parts = [f'<svg xmlns="{SVG}" viewBox="-400 -400 {w+800} {d+800}" role="img" aria-label="Furniture layout">',
             '<rect x="-400" y="-400" width="100%" height="100%" fill="#f8f6f0"/>',
             f'<rect width="{w}" height="{d}" fill="#e9e2d6" stroke="#35473e" stroke-width="30"/>']
    for opening in project.get('openings', []):
        offset, width = opening.get('offset', 0), opening.get('width', 0)
        wall = opening.get('wall')
        if wall in ('north', 'south'):
            x1, x2 = offset, offset+width
            y1 = y2 = 0 if wall == 'north' else d
        elif wall in ('east', 'west'):
            x1 = x2 = w if wall == 'east' else 0
            y1, y2 = d-offset-width, d-offset
        else:
            continue
        color = '#b8ced0' if opening.get('kind') == 'window' else '#f8f6f0'
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="48"/>')
    for item in project.get('furniture', []):
        x, y, iw, depth = (item.get(k, 0) for k in ('x', 'y', 'width', 'depth'))
        if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in (x, y, iw, depth)):
            raise ValueError('Invalid furniture layout geometry')
        # Nominal envelopes match source coordinates; no fabricated silhouettes.
        top = d-y-depth
        ident = html.escape(str(item.get('id', '')))
        name = html.escape(str(item.get('name', ident)))
        parts.append(f'<g><title>{ident} · {name}</title><rect x="{x}" y="{top}" width="{iw}" height="{depth}" rx="25" fill="#c3b49c" stroke="#556358" stroke-width="12"/><text x="{x+iw/2}" y="{top+depth/2}" text-anchor="middle" dominant-baseline="middle" font-size="95" fill="#253b30">{ident}</text></g>')
    parts.append('</svg>')
    return ''.join(parts)


def native_layout(path):
    """Retain actual native projected/cut geometry, omit sheet/dimension furniture.

    The native handoff writer reserves widths 0.10 and 0.38 for its mesh edge
    projections and triangle-plane cuts. Only those lines within its documented
    drawing region are extracted; unsupported SVGs produce no invented layout.
    """
    source = ET.parse(path).getroot()
    nodes, xs, ys = [], [], []
    for node in source.iter():
        if node.tag.rsplit('}', 1)[-1] != 'line':
            continue
        try:
            width = float(node.get('stroke-width', '0'))
            x1, y1, x2, y2 = (float(node.get(k)) for k in ('x1', 'y1', 'x2', 'y2'))
        except (TypeError, ValueError):
            continue
        if not (any(abs(width-v) < 1e-6 for v in (.10, .38)) and
                all(math.isfinite(v) for v in (x1, y1, x2, y2)) and
                15 <= min(x1, x2) <= max(x1, x2) <= 315 and
                40 <= min(y1, y2) <= max(y1, y2) <= 257):
            continue
        nodes.append(copy.deepcopy(node)); xs.extend((x1, x2)); ys.extend((y1, y2))
    if not nodes:
        return None
    lo_x, lo_y = min(xs)-4, min(ys)-4
    root = ET.Element(f'{{{SVG}}}svg', {'viewBox': f'{lo_x} {lo_y} {max(xs)-lo_x+4} {max(ys)-lo_y+4}', 'role': 'img', 'aria-label': 'Actual native geometry layout'})
    root.extend(nodes)
    return ET.tostring(root, encoding='unicode')


def create_layout(files, sheets, read_json):
    if 'selection.json' in files and 'views.json' in files:
        sheet = next((s for s in sheets if s.get('kind') == 'plan'), None)
        if sheet:
            svg = native_layout(files[sheet['file']])
            if svg:
                return svg, dict(file='layout.svg', title='空間與家具配置', kind='native-plan-extract', source_sheet=sheet['id'], basis='Actual native mesh projection and cut geometry; sheet annotations omitted')
        return None, None
    if 'project.json' in files:
        svg = structured_layout(read_json(files['project.json']))
        if svg:
            return svg, dict(file='layout.svg', title='空間與家具配置', kind='furniture-layout', source_sheet='A101' if 'A101.svg' in files else None, basis='Source room, openings and nominal furniture envelopes; not a construction drawing')
    return None, None
