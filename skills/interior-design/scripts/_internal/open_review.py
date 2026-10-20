#!/usr/bin/env python3
"""Build the bundled viewer, serve one review package, and open its browser URL.

Only the built frontend and the selected package are exposed over loopback.
The server survives the CLI; --stop uses an authenticated local shutdown route.
"""
from __future__ import annotations

import argparse
import functools
import hmac
import json
import mimetypes
import os
from pathlib import Path
import secrets
import queue
import shutil
import subprocess
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from build_review import registered_files

SESSION = '.viewer-session.json'
# Retain and reap children started by an embedding Python caller. CLI children detach.
_CHILDREN: dict[int, subprocess.Popen] = {}


def build_viewer(viewer: Path | None = None) -> Path:
    if viewer is not None:
        dist = viewer.resolve()
    else:
        root = Path(__file__).resolve().parents[2] / 'assets/viewer'
        dist = root / 'dist'
        inputs = []
        for directory, subdirectories, filenames in os.walk(root):
            subdirectories[:] = [name for name in subdirectories
                                 if name not in ('node_modules', 'dist', 'generated', '.git')]
            inputs.extend(Path(directory) / name for name in filenames)
        fresh = (dist / 'index.html').is_file() and all(
            p.stat().st_mtime <= (dist / 'index.html').stat().st_mtime for p in inputs)
        if not fresh:
            npm = shutil.which('npm')
            if not npm or not shutil.which('node'):
                raise RuntimeError('Node.js and npm are required to build the viewer. Install Node.js, or pass --viewer /path/to/prebuilt/dist.')
            if not (root / 'node_modules/.bin/vite').is_file():
                subprocess.run([npm, 'ci', '--ignore-scripts'], cwd=root, check=True)
            subprocess.run([npm, 'run', 'build'], cwd=root, check=True)
    if not (dist / 'index.html').is_file():
        raise ValueError('The viewer must contain a built index.html.')
    return dist


def local_url(session: dict) -> str:
    url = session['url']
    parsed = urllib.parse.urlsplit(url)
    if (parsed.scheme != 'http' or parsed.hostname != '127.0.0.1'
            or not parsed.port or parsed.path not in ('', '/')
            or parsed.query or parsed.fragment or parsed.username or parsed.password):
        raise ValueError('Invalid local viewer session URL.')
    return url.rstrip('/')


def request_session(session: dict, route: str, method: str = 'GET') -> dict:
    request = urllib.request.Request(local_url(session) + route, method=method,
                                     headers={'Authorization': 'Bearer ' + session['token']})
    # Avoid user proxy settings even for loopback requests.
    with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(request, timeout=2) as response:
        return json.load(response)


def read_live_session(review: Path) -> dict | None:
    try:
        session = json.loads((review / SESSION).read_text())
        health = request_session(session, '/__review_health')
        if health.get('session_id') == session.get('session_id'):
            return session
    except (OSError, ValueError, KeyError, urllib.error.URLError):
        pass
    return None


def stop(review: Path) -> bool:
    session = read_live_session(review)
    if not session:
        return False
    request_session(session, '/__review_shutdown', 'POST')
    (review / SESSION).unlink(missing_ok=True)
    child = _CHILDREN.pop(session.get('pid'), None)
    if child is not None:
        child.wait(timeout=5)
    return True


class ReviewHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, review: Path, viewer: Path, token: str, session_id: str, **kwargs):
        self.review, self.viewer = review, viewer
        self.token, self.session_id = token, session_id
        super().__init__(*args, **kwargs)

    def log_message(self, *_args):
        pass

    def json_response(self, status: int, value: dict):
        data = json.dumps(value).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(data)

    def allowed_host(self) -> bool:
        return self.headers.get('Host') == f'127.0.0.1:{self.server.server_port}'

    def authenticated(self) -> bool:
        return hmac.compare_digest(self.headers.get('Authorization', ''), 'Bearer ' + self.token)

    def do_POST(self):
        if not self.allowed_host() or not self.authenticated():
            self.send_error(403)
            return
        if self.path != '/__review_shutdown':
            self.send_error(404)
            return
        self.json_response(200, {'stopped': True})
        threading.Thread(target=self.server.shutdown, daemon=True).start()

    def do_GET(self):
        if not self.allowed_host():
            self.send_error(403)
            return
        path = urllib.parse.unquote(urllib.parse.urlsplit(self.path).path)
        if path == '/__review_health':
            if not self.authenticated():
                self.send_error(403)
            else:
                self.json_response(200, {'ready': True, 'session_id': self.session_id})
            return
        generated = path.startswith('/generated/')
        root = self.review if generated else self.viewer
        relative = path[len('/generated/'):] if generated else path.lstrip('/') or 'index.html'
        parts = Path(relative).parts
        if '\x00' in relative or '\\' in relative or any(p.startswith('.') for p in parts):
            self.send_error(403)
            return
        candidate = (root / relative).resolve()
        if not candidate.is_relative_to(root) or not candidate.is_file():
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header('Content-Type', mimetypes.guess_type(candidate.name)[0] or 'application/octet-stream')
        self.send_header('Content-Length', str(candidate.stat().st_size))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        with candidate.open('rb') as source:
            shutil.copyfileobj(source, self.wfile)


class ReviewServer(ThreadingHTTPServer):
    # Room galleries can request many images while two browser tabs are open.
    request_queue_size = 64


def serve(review: Path, viewer: Path, token: str, session_id: str):
    handler = functools.partial(ReviewHandler, review=review, viewer=viewer,
                                token=token, session_id=session_id)
    with ReviewServer(('127.0.0.1', 0), handler) as server:
        print(json.dumps({'url': f'http://127.0.0.1:{server.server_port}/',
                          'pid': os.getpid(), 'token': token, 'session_id': session_id}), flush=True)
        server.serve_forever(poll_interval=0.1)


def launch(review: Path, viewer: Path | None = None, open_browser: bool = True) -> dict:
    review = review.resolve()
    if not (review / 'manifest.json').is_file():
        raise ValueError('The review package must contain manifest.json. Build a review package first.')
    registered_files(review, json.loads((review / 'manifest.json').read_text()), browser=True)
    dist = build_viewer(viewer)
    session = read_live_session(review)
    if session is None:
        child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), '--review', str(review),
                                  '--viewer', str(dist), '--serve', '--token', secrets.token_urlsafe(32),
                                  '--session-id', secrets.token_hex(16)], stdin=subprocess.DEVNULL,
                                 stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                 text=True, start_new_session=True)
        try:
            ready = queue.Queue()
            threading.Thread(target=lambda: ready.put(child.stdout.readline()), daemon=True).start()
            try:
                line = ready.get(timeout=10)
            except queue.Empty:
                raise RuntimeError('Viewer server did not become ready within 10 seconds.') from None
            if not line:
                raise RuntimeError('Viewer server exited before becoming ready.')
            session = json.loads(line)
            if request_session(session, '/__review_health').get('session_id') != session['session_id']:
                raise RuntimeError('Viewer server readiness check failed.')
            (review / SESSION).write_text(json.dumps(session, indent=2) + '\n')
            _CHILDREN[child.pid] = child
        except BaseException:
            child.terminate()
            child.wait(timeout=5)
            raise
        finally:
            child.stdout.close()
    if open_browser and not webbrowser.open(session['url']):
        print('Could not open the browser automatically. Open the URL below.', file=sys.stderr)
    return session


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--review', required=True, type=Path)
    parser.add_argument('--viewer', type=Path, help='Use a prebuilt viewer dist directory.')
    parser.add_argument('--no-open', action='store_true')
    parser.add_argument('--stop', action='store_true')
    parser.add_argument('--serve', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--token', help=argparse.SUPPRESS)
    parser.add_argument('--session-id', help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        if args.serve:
            serve(args.review.resolve(), args.viewer.resolve(), args.token, args.session_id)
        elif args.stop:
            print('Viewer stopped.' if stop(args.review.resolve()) else 'No running viewer for this package.')
        else:
            print(launch(args.review, args.viewer, not args.no_open)['url'])
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Cannot open review: {error}\n')


if __name__ == '__main__':
    main()
