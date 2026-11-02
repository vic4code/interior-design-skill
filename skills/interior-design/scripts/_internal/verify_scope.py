"""Verify declared delivery coverage and artifact integrity; never approve a design."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys

CATALOG = Path(__file__).resolve().parents[2]/'assets/delivery-scope.json'


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def assess(scope, root):
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError('Artifact root must be an existing directory')
    if scope.get('format') != 'interior-delivery-scope-v1' or not nonempty(scope.get('revision')):
        raise ValueError('A scope format and revision are required')
    if scope.get('requested_purpose') not in ('concept', 'coordination', 'quotation', 'construction', 'fabrication'):
        raise ValueError('Declare the requested purpose')
    catalog = {row['id']: row for row in json.loads(CATALOG.read_text())['categories']}
    if scope.get('profile') == 'full-residential':
        required = set(catalog)
        rooms = scope.get('rooms')
        if not isinstance(rooms, list) or not rooms or not all(nonempty(r) for r in rooms) or len(rooms) != len(set(rooms)):
            raise ValueError('A full residential scope needs unique room IDs')
    elif scope.get('profile') == 'custom' and nonempty(scope.get('scope_reason')):
        values = scope.get('required_categories')
        if not isinstance(values, list) or not values or not all(nonempty(v) for v in values):
            raise ValueError('A custom scope needs nonempty required_categories')
        required = set(values)
        rooms = []
    else:
        raise ValueError('Choose full-residential or a justified custom profile')
    items = scope.get('items')
    if not isinstance(items, list) or not items:
        raise ValueError('The scope must contain requirement items')
    results, ids, covered = [], set(), set()
    for item in items:
        if not isinstance(item, dict) or not nonempty(item.get('id')) or item['id'] in ids:
            raise ValueError('Each requirement needs a unique ID')
        ids.add(item['id'])
        category = item.get('category')
        if not nonempty(category):
            raise ValueError('Each requirement needs a category')
        covered.add(category)
        problems = []
        status = item.get('status')
        if status == 'not_applicable':
            if not nonempty(item.get('reason')):
                problems.append('Out-of-scope work needs a reason')
        elif status == 'held':
            issues = item.get('issues')
            if not isinstance(issues, list) or not issues:
                problems.append('Held work needs a specific issue')
            elif any(not isinstance(issue, dict) or not all(nonempty(issue.get(k)) for k in
                         ('id', 'question', 'owner_role', 'required_before', 'consequence')) for issue in issues):
                problems.append('Issues need question, proposed role, milestone and consequence')
            problems.append('Required work remains held')
        elif status == 'delivered':
            artifacts = item.get('artifacts')
            paths = set()
            if not isinstance(artifacts, list) or not artifacts:
                problems.append('Delivered work needs actual artifacts')
                artifacts = []
            for artifact in artifacts:
                if not isinstance(artifact, dict):
                    problems.append('Invalid artifact record')
                    continue
                name = artifact.get('path')
                if not nonempty(name):
                    problems.append('Missing artifact path')
                    continue
                part = PurePosixPath(name)
                candidate = root/part
                if (part.is_absolute() or '..' in part.parts or '\\' in name or ':' in name
                        or '\x00' in name or part.as_posix() != name
                        or not candidate.resolve().is_relative_to(root)
                        or any(p.is_symlink() for p in (candidate, *candidate.parents) if p != root.parent)):
                    problems.append('Unsafe artifact path: '+name)
                    continue
                if not candidate.is_file() or candidate.stat().st_size == 0:
                    problems.append('Missing or empty artifact: '+name)
                    continue
                expected = artifact.get('sha256')
                with candidate.open('rb') as source:
                    actual = hashlib.file_digest(source, 'sha256').hexdigest()
                if (not isinstance(expected, str) or not re.fullmatch('[0-9a-f]{64}', expected)
                        or actual != expected):
                    problems.append('Artifact checksum mismatch: '+name)
                if artifact.get('revision') != scope['revision']:
                    problems.append('Artifact revision mismatch: '+name)
                if 'page' in artifact and (type(artifact['page']) is not int or artifact['page'] < 1):
                    problems.append('Page locators must be positive integers: '+name)
                if candidate.suffix.lower() in ('.pdf', '.svg') and not nonempty(artifact.get('sheet')):
                    problems.append('Drawing evidence needs a sheet locator: '+name)
                if candidate.suffix.lower() == '.pdf' and 'page' not in artifact:
                    problems.append('PDF evidence needs a page locator: '+name)
                paths.add(name)
            expected_types = catalog.get(category, {}).get('artifact_types', [])
            if expected_types and not any(Path(name).suffix.lower() in expected_types for name in paths):
                problems.append('No artifact of the required drawing/image/record type')
            checks = item.get('checks')
            if not isinstance(checks, list) or not checks:
                problems.append('Delivered work needs recorded acceptance checks')
                checks = []
            check_ids = []
            for check in checks:
                if not isinstance(check, dict) or not nonempty(check.get('id')):
                    problems.append('Invalid acceptance check')
                    continue
                check_ids.append(check['id'])
                if check.get('result') != 'pass' or not nonempty(check.get('finding')) or check.get('artifact') not in paths:
                    problems.append('Check lacks a passed finding and actual artifact: '+check['id'])
            if len(check_ids) != len(set(check_ids)):
                problems.append('Duplicate acceptance check IDs')
            for check_id in catalog.get(category, {}).get('checks', []):
                if check_id not in check_ids:
                    problems.append('Missing catalog check: '+check_id)
            if item.get('issues'):
                problems.append('Delivered work still has unresolved issues; mark it held')
        else:
            problems.append('Unknown requirement status')
        results.append(dict(id=item['id'], category=category, status=status, problems=problems))
    missing = sorted(required-covered)
    missing_rooms = [dict(room=room, category=category) for room in rooms for category in ('elevations', 'visualizations')
                     if not any(item.get('room') == room and item.get('category') == category for item in items)]
    return dict(format='interior-acceptance-report-v1', revision=scope['revision'],
                requested_purpose=scope['requested_purpose'],
                state='incomplete' if missing or missing_rooms or any(r['problems'] for r in results) else 'ready_for_review',
                missing_categories=missing, missing_room_coverage=missing_rooms, items=results,
                limitation='Coverage and recorded evidence integrity only; geometry, page/sheet content, technical correctness and professional approval require actual review.')


def main(arguments=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scope', type=Path, required=True)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(arguments)
    try:
        target = args.out.absolute()
        if target.is_symlink() or target.resolve().is_relative_to(args.root.resolve()) or target.resolve() == args.scope.resolve():
            raise ValueError('Report must be outside the artifact root and distinct from its scope input')
        if target.exists():
            previous = json.loads(target.read_text())
            if not isinstance(previous, dict) or previous.get('format') != 'interior-acceptance-report-v1':
                raise ValueError('Refusing to replace an unrelated output file')
        scope = json.loads(args.scope.read_text())
        if not isinstance(scope, dict):
            raise ValueError('Scope must be an object')
        result = assess(scope, args.root)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
        print(result['state']+': '+str(target))
        return 0 if result['state'] == 'ready_for_review' else 2
    except (OSError, ValueError, TypeError) as error:
        parser.exit(1, f'Cannot verify acceptance scope: {error}\n')


if __name__ == '__main__':
    sys.exit(main())
