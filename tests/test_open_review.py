"""Exercise the actual detached server and package boundary, without Node or a browser."""
import importlib.util
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/interior-design/scripts/_internal/open_review.py'
sys.path.insert(0, str(SCRIPT.parent))
spec = importlib.util.spec_from_file_location('open_review', SCRIPT)
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


class OpenReviewTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.review = self.root / 'review'
        self.viewer = self.root / 'dist'
        self.review.mkdir()
        self.viewer.mkdir()
        (self.review / 'drawing.pdf').write_bytes(b'%PDF-test')
        (self.review / 'manifest.json').write_text(json.dumps({'schema_version': '2.0', 'files': [{'name': 'drawing.pdf', 'sha256': hashlib.sha256(b'%PDF-test').hexdigest()}]}))
        (self.viewer / 'index.html').write_text('<h1>Review viewer</h1>')
        (self.root / 'private.txt').write_text('must not be served')

    def tearDown(self):
        launcher.stop(self.review)
        self.temporary.cleanup()

    def get(self, url):
        with urllib.request.build_opener(urllib.request.ProxyHandler({})).open(url, timeout=3) as response:
            return response.read()

    def test_real_server_routes_reuse_and_authenticated_shutdown(self):
        with patch.object(launcher.webbrowser, 'open', return_value=True) as browser:
            session = launcher.launch(self.review, self.viewer)
            browser.assert_called_once_with(session['url'])
        self.assertIn(b'Review viewer', self.get(session['url']))
        self.assertEqual(self.get(session['url'] + 'generated/drawing.pdf'), b'%PDF-test')
        self.assertEqual(json.loads(self.get(session['url'] + 'generated/manifest.json'))['schema_version'], '2.0')
        again = launcher.launch(self.review, self.viewer, open_browser=False)
        self.assertEqual(again['pid'], session['pid'])
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.get(session['url'] + '__review_health')
        self.assertEqual(error.exception.code, 403)
        error.exception.close()
        request = urllib.request.Request(session['url'] + '__review_shutdown', method='POST')
        with self.assertRaises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(request, timeout=3)
        self.assertEqual(error.exception.code, 403)
        error.exception.close()
        self.assertTrue(launcher.stop(self.review))
        self.assertFalse((self.review / launcher.SESSION).exists())
        self.assertFalse(launcher.stop(self.review))

    def test_workspace_traversal_and_symlink_escape_are_blocked(self):
        (self.review / 'escape.txt').symlink_to(self.root / 'private.txt')
        (self.viewer / 'escape.txt').symlink_to(self.root / 'private.txt')
        session = launcher.launch(self.review, self.viewer, open_browser=False)
        for route in ('generated/../private.txt', 'generated/%2e%2e/private.txt',
                      'generated/escape.txt', 'escape.txt', 'generated/.viewer-session.json',
                      'generated/', '%2e%2e/private.txt'):
            with self.subTest(route=route), self.assertRaises(urllib.error.HTTPError) as error:
                self.get(session['url'] + route)
            self.assertIn(error.exception.code, (403, 404))
            error.exception.close()

    def test_no_open_cli_and_stop_work_from_unrelated_directory(self):
        result = subprocess.run([sys.executable, str(SCRIPT), '--review', str(self.review),
                                 '--viewer', str(self.viewer), '--no-open'], cwd=self.root,
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.startswith('http://127.0.0.1:'))
        stopped = subprocess.run([sys.executable, str(SCRIPT), '--review', str(self.review), '--stop'],
                                 cwd=self.root, capture_output=True, text=True, timeout=10)
        self.assertEqual(stopped.returncode, 0, stopped.stderr)
        self.assertIn('stopped', stopped.stdout)

    def test_startup_failure_terminates_child_and_writes_no_session(self):
        class FailedProcess:
            stdout = None
            def __init__(self):
                import io
                self.stdout = io.StringIO('')
                self.terminated = False
                self.waited = False
            def terminate(self):
                self.terminated = True
            def wait(self, timeout):
                self.waited = True
        child = FailedProcess()
        with patch.object(launcher.subprocess, 'Popen', return_value=child), \
             patch.object(launcher.queue.Queue, 'get', side_effect=launcher.queue.Empty):
            with self.assertRaisesRegex(RuntimeError, '10 seconds'):
                launcher.launch(self.review, self.viewer, open_browser=False)
        self.assertTrue(child.terminated)
        self.assertTrue(child.waited)
        self.assertFalse((self.review / launcher.SESSION).exists())

    def test_invalid_packages_and_remote_session_urls_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'manifest.json'):
            launcher.launch(self.root, self.viewer, open_browser=False)
        with self.assertRaisesRegex(ValueError, 'index.html'):
            launcher.build_viewer(self.root)
        for url in ('https://example.com/', 'http://localhost:1234/',
                    'http://127.0.0.1:1234/secret', 'http://127.0.0.1:1234/?x=1'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                launcher.local_url({'url': url})

    def test_missing_or_changed_registered_files_fail_before_browser_launch(self):
        drawing = self.review / 'drawing.pdf'
        with patch.object(launcher.webbrowser, 'open') as browser:
            drawing.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                launcher.launch(self.review, self.viewer)
            drawing.unlink()
            with self.assertRaisesRegex(ValueError, 'Missing artifact'):
                launcher.launch(self.review, self.viewer)
            browser.assert_not_called()


if __name__ == '__main__':
    unittest.main()
