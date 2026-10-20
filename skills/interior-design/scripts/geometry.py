"""Shared millimetre geometry. Origin: inside southwest corner, +X east, +Y north."""
WALLS = ('south', 'north', 'west', 'east')


def wall_length(room, wall):
    return room['width'] if wall in ('south', 'north') else room['depth']


def wall_panels(project):
    """Return actual wall solids; openings cut through, not painted over walls.

    Gridded partitioning supports multiple openings without Boolean tolerances.
    Wall offset is from west for N/S and south for E/W, on interior faces.
    """
    r = project['room']
    t, h = r['wall_thickness'], r['height']
    for wall in WALLS:
        length = wall_length(r, wall)
        holes = [o for o in project['openings'] if o['wall'] == wall]
        us = sorted({0, length, *(v for o in holes for v in (o['offset'], o['offset'] + o['width']))})
        zs = sorted({0, h, *(v for o in holes for v in (o['sill'], o['sill'] + o['height']))})
        for a, b in zip(us, us[1:]):
            for low, high in zip(zs, zs[1:]):
                u, z = (a+b)/2, (low+high)/2
                if any(o['offset'] < u < o['offset']+o['width'] and o['sill'] < z < o['sill']+o['height'] for o in holes):
                    continue
                if wall in ('south', 'north'):
                    center = (u, -t/2 if wall == 'south' else r['depth']+t/2, z)
                    size = (b-a, t, high-low)
                else:
                    center = (-t/2 if wall == 'west' else r['width']+t/2, u, z)
                    size = (t, b-a, high-low)
                yield wall, center, size
    # Corner posts outside the measured clear interior.
    for x in (-t/2, r['width']+t/2):
        for y in (-t/2, r['depth']+t/2):
            yield 'corner', (x,y,h/2), (t,t,h)


def overlaps(a, b):
    return (a['x'] < b['x']+b['width'] and b['x'] < a['x']+a['width']
            and a['y'] < b['y']+b['depth'] and b['y'] < a['y']+a['depth'])
