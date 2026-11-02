"""Evidence checks must reject incomplete professional deliveries and preserve inputs."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]/'skills/interior-design'
sys.path.insert(0, str(SKILL/'scripts/_internal'))
from verify_scope import assess


class ScopeAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.artifacts = self.root/'delivery'
        self.artifacts.mkdir()
        self.drawing = self.artifacts/'layout.svg'
        self.drawing.write_text('<svg xmlns="http://www.w3.org/2000/svg"><text>Fixture room R02</text></svg>')
        self.row = dict(id='PLAN',category='layout',room='fixture-room',status='delivered',
                        artifacts=[dict(path='layout.svg',revision='R02',sheet='A101',
                                        sha256=hashlib.sha256(self.drawing.read_bytes()).hexdigest())],
                        checks=[dict(id=name,result='pass',finding='Synthetic fixture review record',artifact='layout.svg')
                                for name in ('rooms_furniture_circulation','plan_agreement')])
        self.scope = dict(format='interior-delivery-scope-v1',profile='custom',revision='R02',
                          requested_purpose='coordination',scope_reason='Only a furniture layout is commissioned',
                          required_categories=['layout'],items=[self.row])

    def result(self):
        return assess(self.scope,self.artifacts)

    def test_valid_evidence_is_ready_for_review_never_construction_approval(self):
        self.assertEqual(self.result()['state'],'ready_for_review')
        self.scope['requested_purpose']='construction'
        self.assertEqual(self.result()['state'],'ready_for_review')
        self.assertIn('professional approval',self.result()['limitation'])

    def test_changed_missing_or_wrong_revision_drawing_is_incomplete(self):
        for failure in ('changed','missing','revision'):
            with self.subTest(failure=failure):
                data=copy.deepcopy(self.scope)
                self.drawing.write_text('<svg xmlns="http://www.w3.org/2000/svg"><text>Fixture room R02</text></svg>')
                if failure=='changed':self.drawing.write_text('changed')
                elif failure=='missing':data['items'][0]['artifacts'][0]['path']='absent.svg'
                else:data['items'][0]['artifacts'][0]['revision']='R01'
                self.assertEqual(assess(data,self.artifacts)['state'],'incomplete')

    def test_markdown_cannot_substitute_for_a_drawing(self):
        self.drawing.rename(self.artifacts/'layout.md')
        self.row['artifacts'][0]['path']='layout.md'
        for check in self.row['checks']:check['artifact']='layout.md'
        self.assertEqual(self.result()['state'],'incomplete')

    def test_pending_and_unrecorded_catalog_checks_cannot_pass(self):
        self.row['checks'][0]['result']='pending'
        self.assertEqual(self.result()['state'],'incomplete')
        self.row['checks']=self.row['checks'][1:]
        self.assertEqual(self.result()['state'],'incomplete')

    def test_held_work_with_owner_and_milestone_is_still_incomplete(self):
        self.row.update(status='held',artifacts=[],checks=[],issues=[dict(id='RFI-1',
            question='Is the ceiling height before the new floor finish?',owner_role='Surveyor',
            required_before='Ceiling setting-out',consequence='Finished clear height is unknown')])
        self.assertEqual(self.result()['state'],'incomplete')
        self.row['issues'][0].pop('owner_role')
        self.assertTrue(any('milestone' in p for p in self.result()['items'][0]['problems']))

    def test_full_profile_requires_distinct_disciplines_and_each_room(self):
        self.scope.update(profile='full-residential',rooms=['living','bedroom'])
        result=self.result()
        self.assertIn('ceiling',result['missing_categories'])
        self.assertIn('hvac',result['missing_categories'])
        self.assertIn('lighting_controls',result['missing_categories'])
        self.assertEqual(len(result['missing_room_coverage']),4)
        self.assertEqual(result['state'],'incomplete')

    def test_exclusions_need_reasons_and_duplicate_ids_are_rejected(self):
        self.row.update(status='not_applicable')
        self.assertEqual(self.result()['state'],'incomplete')
        self.row['reason']='The room is outside the commissioned work'
        self.assertEqual(self.result()['state'],'ready_for_review')
        self.scope['items'].append(copy.deepcopy(self.row))
        with self.assertRaisesRegex(ValueError,'unique ID'):self.result()

    def test_escape_and_linked_evidence_cannot_be_used(self):
        outside=self.root/'private.svg';outside.write_text('private')
        for name in ('../private.svg',str(outside)):
            self.row['artifacts'][0]['path']=name
            self.assertEqual(self.result()['state'],'incomplete')
        (self.artifacts/'linked.svg').symlink_to(outside)
        self.row['artifacts'][0]['path']='linked.svg'
        self.assertEqual(self.result()['state'],'incomplete')

    def test_cli_runs_without_site_packages_and_preserves_unrelated_outputs(self):
        source=self.root/'scope.json';source.write_text(json.dumps(self.scope))
        out=self.root/'report.json'
        command=[sys.executable,'-S',str(SKILL/'scripts/interior_design.py'),'acceptance',
                 '--scope',str(source),'--root',str(self.artifacts),'--out',str(out)]
        result=subprocess.run(command,capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(out.read_text())['state'],'ready_for_review')
        self.drawing.write_text('authored revision')
        result=subprocess.run(command,capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,2,result.stderr)
        self.assertEqual(self.drawing.read_text(),'authored revision')
        out.write_text('unrelated author document')
        result=subprocess.run(command,capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,1)
        self.assertEqual(out.read_text(),'unrelated author document')
