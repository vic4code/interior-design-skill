"""Real Blender subprocesses must refuse authored output before rendering."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]/'skills/interior-design'
INTERNAL = ROOT/'scripts/_internal'
BLENDER = shutil.which('blender')
if not BLENDER and Path('/Applications/Blender.app/Contents/MacOS/Blender').is_file():
    BLENDER = '/Applications/Blender.app/Contents/MacOS/Blender'


@unittest.skipUnless(BLENDER, 'Actual Blender early-refusal checks require Blender')
class RenderOutputTests(unittest.TestCase):
    def invoke(self, script, *arguments):
        result = subprocess.run([BLENDER, '--background', '--factory-startup',
                                 '--python-exit-code', '1', '--python', str(INTERNAL/script),
                                 '--', *map(str, arguments)], capture_output=True, text=True,
                                timeout=30)
        self.assertNotEqual(result.returncode, 0, result.stdout+result.stderr)
        return result.stdout+result.stderr

    def snapshot(self, root):
        return {p.relative_to(root).as_posix():p.read_bytes()
                for p in root.rglob('*') if p.is_file()}

    def test_style_renderer_preserves_existing_scene_image_and_all_style_subdirectories(self):
        for mode in ('single', 'all'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as folder:
                out = Path(folder)/'renders'
                existing = out/'japandi' if mode == 'all' else out
                existing.mkdir(parents=True)
                (existing/'scene.blend').write_bytes(b'authored Blender scene')
                (existing/'hero.png').write_bytes(b'authored presentation image')
                before = self.snapshot(out)
                message = self.invoke('render_style_studies.py', '--out', out,
                                      '--style', 'all' if mode == 'all' else 'mcm')
                self.assertIn('Output must be empty', message)
                self.assertEqual(self.snapshot(out), before)
                if mode == 'all':
                    self.assertEqual([p.name for p in out.iterdir()], ['japandi'])

    def test_style_renderer_rejects_output_symlink_without_writing_target(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); target=root/'author'; target.mkdir()
            output=root/'renders'; output.symlink_to(target, target_is_directory=True)
            message=self.invoke('render_style_studies.py', '--out', output, '--style', 'mcm')
            self.assertIn('Output cannot be a symlink', message)
            self.assertEqual(list(target.iterdir()), [])

    def test_hd_renderer_preserves_existing_image_and_dangling_symlink(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); target=root/'authored.png'; target.write_bytes(b'authored image')
            message=self.invoke('render_hd.py', '--out', target)
            self.assertIn('Output image already exists', message)
            self.assertEqual(target.read_bytes(), b'authored image')
            link=root/'linked.png'; link.symlink_to(root/'not-created.png')
            message=self.invoke('render_hd.py', '--out', link)
            self.assertIn('Output image already exists', message)
            self.assertTrue(link.is_symlink())
            self.assertFalse((root/'not-created.png').exists())

    def test_starter_renderer_checks_every_target_before_exporting_any_artifact(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder); out=root/'render'; out.mkdir()
            (out/'scene.blend').write_bytes(b'authored native scene')
            before=self.snapshot(out)
            message=self.invoke('blender_scene.py', ROOT/'assets/example-project.json', out)
            self.assertIn('Render output already exists', message)
            self.assertEqual(self.snapshot(out), before)


if __name__ == '__main__':
    unittest.main()
