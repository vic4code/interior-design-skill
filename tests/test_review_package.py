"""Public package boundaries: real sheet identities, evidence and optional geometry."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'skills/interior-design/scripts/_internal'))
from build_review import build, build_variants, digest, registered_files


class ReviewPackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root/'delivery'
        self.source.mkdir()
        self.out = self.root/'browser'

    def register(self, entries, as_list=False):
        for name, content in entries.items():
            path = self.source/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(content) if isinstance(content, (dict, list)) else content)
        files = {name: digest(self.source/name) for name in entries}
        files = [dict(name=name, sha256=sha, bytes=(self.source/name).stat().st_size) for name, sha in files.items()] if as_list else files
        (self.source/'manifest.json').write_text(json.dumps(dict(format='native-handoff-v1', files=files)))

    def native(self):
        self.register({'selection.json': dict(project='Existing irregular residence', revision='R07'),
                       'views.json': [dict(sheet='N301', title='Actual angled-wall section', kind='section', scale=5)],
                       'N301.svg': '<svg xmlns="http://www.w3.org/2000/svg"><text>Existing section</text></svg>',
                       'native-coordination.pdf': '%PDF-test',
                       'dimension-evidence.csv': 'id,value_mm\nD01,373\n'})

    def test_native_retains_actual_sheets_unknown_area_and_complete_registered_files(self):
        self.native()
        (self.source/'inventory.json').write_text('private unregistered inventory')
        result = build(self.source, self.out)
        self.assertEqual(result['schema_version'], '2.0')
        self.assertEqual(result['project']['name'], 'Existing irregular residence')
        self.assertNotIn('area_m2', result['project'])
        self.assertNotIn('ceiling_height_mm', result['project'])
        self.assertEqual(result['sheets'], [dict(id='N301', title='Actual angled-wall section', file='N301.svg', kind='section', scale='1:5')])
        self.assertEqual((self.out/'source-manifest.json').read_bytes(), (self.source/'manifest.json').read_bytes())
        self.assertFalse((self.out/'inventory.json').exists())
        self.assertTrue((self.out/'dimension-evidence.csv').exists())
        for entry in result['files']:
            self.assertEqual(entry['sha256'], digest(self.out/entry['name']))

    def test_starter_list_registration_uses_actual_svg_title_and_source_room_only(self):
        self.register({'project.json': dict(project=dict(name='Synthetic fixture', revision='S01'), room=dict(width=6000, depth=4800, height=2800)),
                       'A101.svg': '<svg xmlns="http://www.w3.org/2000/svg"><text y="29">Actual furniture plan</text><text>1:50</text></svg>'}, as_list=True)
        result = build(self.source, self.out)
        self.assertEqual(result['sheets'][0]['title'], 'Actual furniture plan')
        self.assertEqual(result['sheets'][0]['scale'], '1:50')
        self.assertEqual(result['project']['area_m2'], 28.8)
        self.assertEqual(result['project']['ceiling_height_mm'], 2800)

    def test_hash_mismatch_fails_before_replacing_existing_package(self):
        self.native()
        build(self.source, self.out)
        original = (self.out/'manifest.json').read_bytes()
        (self.source/'N301.svg').write_text('tampered')
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
            build(self.source, self.out)
        self.assertEqual((self.out/'manifest.json').read_bytes(), original)

    def provenance(self, review='pending'):
        self.image, self.base, self.evidence = [self.root/name for name in ('image.png', 'base.png', 'provenance.json')]
        self.image.write_bytes(b'generated image fixture')
        self.base.write_bytes(b'geometry base fixture')
        self.evidence.write_text(json.dumps(dict(mode='completion-simulation', image_sha256=digest(self.image), base_sha256=digest(self.base), review_status=review)))

    def test_conditioned_presentation_preserves_source_base_image_and_provenance_separately(self):
        self.native(); self.provenance()
        result = build(self.source, self.out, presentation=self.image, base_image=self.base, provenance=self.evidence)
        self.assertEqual(result['presentation']['kind'], 'completion-simulation')
        self.assertEqual(result['presentation']['review_status'], 'pending')
        for field, source in [('image', self.image), ('base_image', self.base), ('provenance', self.evidence)]:
            self.assertEqual((self.out/result['presentation'][field]).read_bytes(), source.read_bytes())

    def test_generated_image_or_base_mismatch_and_rejected_review_fail(self):
        self.native(); self.provenance()
        original = self.image.read_bytes()
        self.image.write_bytes(b'changed generated image')
        with self.assertRaisesRegex(ValueError, 'Presentation checksum'):
            build(self.source, self.out, self.image, self.base, self.evidence)
        self.image.write_bytes(original)
        self.base.write_bytes(b'wrong base')
        with self.assertRaisesRegex(ValueError, 'Base image checksum'):
            build(self.source, self.out, self.image, self.base, self.evidence)
        self.provenance(review='rejected')
        with self.assertRaisesRegex(ValueError, 'review_status'):
            build(self.source, self.out, self.image, self.base, self.evidence)

    def test_no_fake_3d_or_ai_claim_and_rebuild_clears_previous_presentation(self):
        self.native(); self.provenance()
        build(self.source, self.out, self.image, self.base, self.evidence)
        result = build(self.source, self.out)
        self.assertIsNone(result['model'])
        self.assertEqual(result['presentation']['kind'], 'none')
        self.assertIsNone(result['presentation']['image'])
        self.assertFalse((self.out/'presentation/image.png').exists())

    def test_path_traversal_symlinks_and_source_overlap_are_rejected(self):
        self.native()
        with self.assertRaisesRegex(ValueError, 'separate'):
            build(self.source, self.source/'browser')
        manifest = json.loads((self.source/'manifest.json').read_text())
        manifest['files']['../secret.pdf'] = '0'*64
        (self.source/'manifest.json').write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, 'Unsafe artifact'):
            build(self.source, self.out)
        self.native()
        (self.source/'N301.svg').unlink()
        (self.source/'N301.svg').symlink_to(self.source/'native-coordination.pdf')
        with self.assertRaisesRegex(ValueError, 'Symlink artifact'):
            build(self.source, self.out)

    def test_metadata_changes_display_only_and_unknown_outputs_are_preserved(self):
        self.native()
        metadata = self.root/'metadata.json'
        metadata.write_text(json.dumps(dict(name='Display title', area_m2=105.2)))
        result = build(self.source, self.out, metadata=metadata)
        self.assertEqual(result['project']['name'], 'Display title')
        self.assertEqual(json.loads((self.out/'selection.json').read_text())['project'], 'Existing irregular residence')
        other = self.root/'unrelated'; other.mkdir(); (other/'notes.txt').write_text('keep')
        with self.assertRaisesRegex(ValueError, 'Refusing to replace'):
            build(self.source, other)
        self.assertTrue((other/'notes.txt').exists())


class SameSpaceVariantTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.out = self.root/'review'
        self.base = self.root/'base.jpg'
        self.base.write_bytes(b'one camera and room geometry reference')
        self.items = []
        for ident in ('mcm', 'japandi'):
            source = self.root/ident
            source.mkdir()
            project = dict(project=dict(id='ROOM01', name='One shared room', revision='S01'),
                           room=dict(width=6000, depth=4800, height=2800), openings=[dict(id='W01', width=2800)])
            (source/'project.json').write_text(json.dumps(project))
            (source/'joinery.json').write_text(json.dumps(dict(cabinet='F05', thickness_mm=18)))
            (source/'A101.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"><text y="29">Room plan</text></svg>')
            self.register(source)
            image = self.root/(ident+'.jpg')
            image.write_bytes(('generated '+ident).encode())
            evidence = self.root/(ident+'-provenance.json')
            evidence.write_text(json.dumps(dict(mode='completion-simulation', image_sha256=digest(image),
                                               base_sha256=digest(self.base), review_status='pending')))
            self.items.append(dict(id=ident, label=ident.title(), source=ident, presentation=image.name,
                                   base_image='base.jpg', provenance=evidence.name))
        self.config = self.root/'variants.json'
        self.save_config()

    def register(self, source):
        files = {name: digest(source/name) for name in ('project.json', 'joinery.json', 'A101.svg')}
        (source/'manifest.json').write_text(json.dumps(dict(files=files)))

    def save_config(self):
        self.config.write_text(json.dumps(dict(variants=self.items)))

    def test_two_variants_keep_individual_sheets_images_and_flattened_checksums(self):
        result = build_variants(self.config, self.out)
        self.assertEqual(result['default_variant'], 'mcm')
        self.assertEqual([v['id'] for v in result['variants']], ['mcm', 'japandi'])
        self.assertTrue(result['presentation']['image'].startswith('variants/mcm/'))
        files = registered_files(self.out.resolve(), result)
        for variant in result['variants']:
            child = json.loads(files[variant['manifest']].read_text())
            parent = files[variant['manifest']].parent
            for artifact in child['files']:
                self.assertEqual(digest(parent/artifact['name']), artifact['sha256'])
            self.assertEqual((parent/'A101.svg').read_bytes(), (self.root/variant['id']/'A101.svg').read_bytes())
            self.assertEqual((parent/child['presentation']['image']).read_bytes(), (self.root/(variant['id']+'.jpg')).read_bytes())

    def test_mismatched_room_or_opening_id_is_rejected_before_existing_output_changes(self):
        build_variants(self.config, self.out)
        before = (self.out/'manifest.json').read_bytes()
        source = self.root/'japandi'
        project = json.loads((source/'project.json').read_text())
        project['openings'][0]['id'] = 'DIFFERENT_WINDOW'
        (source/'project.json').write_text(json.dumps(project))
        self.register(source)
        with self.assertRaisesRegex(ValueError, 'identical project'):
            build_variants(self.config, self.out)
        self.assertEqual((self.out/'manifest.json').read_bytes(), before)

    def test_variant_artifact_traversal_and_tampering_rejected(self):
        source = self.root/'mcm'
        manifest = json.loads((source/'manifest.json').read_text())
        manifest['files']['../base.jpg'] = digest(self.base)
        (source/'manifest.json').write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, 'Unsafe artifact'):
            build_variants(self.config, self.out)
        self.register(source)
        (source/'A101.svg').write_text('tampered')
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
            build_variants(self.config, self.out)
        self.items[0]['id'] = '../escape'
        self.save_config()
        with self.assertRaisesRegex(ValueError, 'safe lowercase slug'):
            build_variants(self.config, self.out)

    def make_native_variant(self, ident, native_hash='a'*64, inventory_hash='b'*64):
        source = self.root/ident
        for name in ('project.json', 'joinery.json'):
            (source/name).unlink(missing_ok=True)
        (source/'selection.json').write_text(json.dumps(dict(project='Irregular multi-room apartment', revision='N01')))
        (source/'views.json').write_text(json.dumps([dict(sheet='A101', title='Existing plan', kind='plan', scale=75)]))
        names = ('selection.json', 'views.json', 'A101.svg')
        manifest = dict(format='native-handoff-v1', source_hashes=dict(native_file=native_hash, inventory=inventory_hash),
                        files={name: digest(source/name) for name in names})
        (source/'manifest.json').write_text(json.dumps(manifest))

    def test_native_variants_use_identical_geometry_hashes_without_starter_room_json(self):
        for ident in ('mcm', 'japandi'):
            self.make_native_variant(ident)
        result = build_variants(self.config, self.out)
        self.assertEqual(result['project']['name'], 'Irregular multi-room apartment')
        for variant in result['variants']:
            child_root = self.out/Path(variant['manifest']).parent
            self.assertFalse((child_root/'project.json').exists())
            self.assertFalse((child_root/'joinery.json').exists())
            self.assertTrue((self.out/variant['thumbnail']).is_file())

    def test_native_geometry_mismatch_invalid_hash_and_mixed_contracts_are_rejected(self):
        self.make_native_variant('mcm')
        with self.assertRaisesRegex(ValueError, 'cannot mix'):
            build_variants(self.config, self.out)
        self.make_native_variant('japandi', native_hash='c'*64)
        with self.assertRaisesRegex(ValueError, 'identical native geometry'):
            build_variants(self.config, self.out)
        self.make_native_variant('japandi', inventory_hash='c'*64)
        with self.assertRaisesRegex(ValueError, 'identical native geometry'):
            build_variants(self.config, self.out)
        self.make_native_variant('japandi', inventory_hash='invalid')
        with self.assertRaisesRegex(ValueError, 'valid native_file and inventory'):
            build_variants(self.config, self.out)

    def test_config_inside_output_is_never_deleted(self):
        with self.assertRaisesRegex(ValueError, 'separate from variants configuration'):
            build_variants(self.config, self.root)
        self.assertTrue(self.config.is_file())

    def test_different_conditioning_reference_is_rejected(self):
        provenance = self.root/self.items[1]['provenance']
        evidence = json.loads(provenance.read_text())
        evidence['base_sha256'] = '0'*64
        provenance.write_text(json.dumps(evidence))
        with self.assertRaisesRegex(ValueError, 'one conditioning base'):
            build_variants(self.config, self.out)


if __name__ == '__main__':
    unittest.main()
