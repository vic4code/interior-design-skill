"""Source-preservation boundaries shared by every portable build workflow."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'skills/interior-design/scripts/_internal'))
from output_ownership import (verify_output_directory, require_empty_output,
                              verify_inputs_outside, write_output_manifest)


class OutputOwnershipTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.out = self.root/'output'

    def managed(self):
        path = self.out/'drawings/plan.svg'
        path.parent.mkdir(parents=True)
        path.write_bytes(b'generated plan')
        return write_output_manifest(self.out, 'test-output-v1')

    def test_new_empty_and_verified_registered_outputs_are_accepted_without_mutation(self):
        self.assertEqual(require_empty_output(self.out), self.out.resolve())
        self.assertFalse(self.out.exists())
        self.out.mkdir()
        self.assertEqual(verify_output_directory(self.out), self.out.resolve())
        self.out.rmdir()
        manifest = self.managed()
        before = (self.out/'manifest.json').read_bytes()
        self.assertEqual(verify_output_directory(self.out, expected={'format':'test-output-v1'}), self.out.resolve())
        self.assertEqual((self.out/'manifest.json').read_bytes(), before)
        # Hash-dictionary producers have the same ownership requirements.
        manifest['files'] = {item['name']:item['sha256'] for item in manifest['files']}
        (self.out/'manifest.json').write_text(json.dumps(manifest))
        verify_output_directory(self.out, expected={'format':'test-output-v1'})

    def test_unmanaged_files_wrong_producer_and_changed_registered_bytes_are_preserved(self):
        self.managed()
        with self.assertRaisesRegex(ValueError, 'expected producer'):
            verify_output_directory(self.out, expected={'format':'other-producer'})
        plan = self.out/'drawings/plan.svg'
        plan.write_bytes(b'authored edit')
        before = plan.read_bytes()
        with self.assertRaisesRegex(ValueError, 'modified output artifact'):
            verify_output_directory(self.out, expected={'format':'test-output-v1'})
        self.assertEqual(plan.read_bytes(), before)
        with self.assertRaisesRegex(ValueError, 'empty'):
            require_empty_output(self.out)
        other = self.root/'authored'; other.mkdir(); (other/'scene.blend').write_bytes(b'original')
        with self.assertRaisesRegex(ValueError, 'unmanaged nonempty'):
            verify_output_directory(other)
        self.assertEqual((other/'scene.blend').read_bytes(), b'original')

    def test_unknown_files_empty_directories_symlinks_and_runtime_sessions_block_replacement(self):
        self.managed()
        for name in ('authored.blend','scene.blend1','.viewer-session.json'):
            path=self.out/name;path.write_text('preserve')
            with self.subTest(name=name), self.assertRaises(ValueError):
                verify_output_directory(self.out, expected={'format':'test-output-v1'})
            self.assertEqual(path.read_text(),'preserve');path.unlink()
        directory=self.out/'unregistered';directory.mkdir()
        with self.assertRaisesRegex(ValueError,'unregistered'):
            verify_output_directory(self.out)
        directory.rmdir()
        link=self.out/'drawings/link.svg';link.symlink_to(self.out/'drawings/plan.svg')
        with self.assertRaisesRegex(ValueError,'symlink'):
            verify_output_directory(self.out)

    def test_unsafe_or_duplicate_registration_and_input_overlap_fail_before_writes(self):
        manifest=self.managed()
        manifest['files'].append(dict(manifest['files'][0]))
        (self.out/'manifest.json').write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            verify_output_directory(self.out)
        manifest['files']=[dict(name='../outside.blend',sha256='0'*64)]
        (self.out/'manifest.json').write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError,'Unsafe'):
            verify_output_directory(self.out)
        for path in (self.out, self.out/'input.json', self.root):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError,'outside and separate'):
                verify_inputs_outside(self.out,[path])
        verify_inputs_outside(self.out,[None,self.root/'separate.json'])
        link=self.root/'output-link';link.symlink_to(self.out,target_is_directory=True)
        with self.assertRaisesRegex(ValueError,'symlink'):
            verify_output_directory(link)


if __name__ == '__main__':
    unittest.main()
