"""Validate shipped synthetic drawings and viewer against their build inputs."""
import hashlib
import json
from pathlib import Path


def inputs(root, kind):
    root = Path(root)
    if kind == 'viewer':
        base = root/'assets/viewer'
        paths = [base/name for name in ('index.html', 'package.json', 'package-lock.json', 'vite.config.js')]
        paths += [p for p in (base/'src').rglob('*') if p.is_file()]
    else:
        paths = [root/'scripts/_internal'/name for name in
                 ('build_drawing_studies.py', 'project.py', 'geometry.py')]
        paths += [root/'assets/project.schema.json']
        paths += list((root/'assets/style-studies').glob('*.json'))
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths)}


def available(root, directory, kind):
    """A stale or incomplete bundle falls back to the normal build path."""
    from output_ownership import verify_output_directory
    try:
        data = json.loads((directory/'bundle.json').read_text())
        if data['inputs'] != inputs(root, kind):
            return False
        verify_output_directory(directory, expected={'format': 'quickstart-'+kind+'-v1'},
                                manifest_name='bundle.json')
        return True
    except (OSError, ValueError, KeyError, TypeError):
        return False
