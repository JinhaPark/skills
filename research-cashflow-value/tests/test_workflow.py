import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('gate', ROOT/'scripts/validate_workflow.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = json.loads((ROOT/'assets/workflow-template.json').read_text())
        self.manifest.update(run_id='offline-fixture', decision='selected', versions={'data':1,'model':1}, review={'passed':True,'unresolved_critical':0})
        self.write('data.json', {'version':1})
        self.write('model.json', {'version':1})
        for i, name in enumerate(gate.STAGES):
            artifact = 'data.json' if name=='peers' else 'model.json' if name=='model' else 'report.md' if name=='publish' else f'{name}.md'
            if not (self.root/artifact).exists():
                (self.root/artifact).write_text(f'Offline fixture for {name}\n')
            inputs = {} if i<3 else {'data':1}
            if i>=5:
                inputs['model']=1
            handoff=f'handoffs/{name}.json'
            record={'task_id':name,'status':'completed','artifact_paths':[artifact],'input_versions':inputs,'summary':f'Offline fixture completed for {name}','claims':[],'key_metrics':[],'uncertainties':[],'next_inputs':[]}
            self.write(handoff, record)
            self.manifest['tasks'][name].update(status='completed',input_versions=inputs,artifacts=[{'path':artifact,'sha256':gate.sha256(self.root/artifact)}],handoff=handoff,handoff_sha256=gate.sha256(self.root/handoff))
        self.save()

    def write(self, path, data):
        p=self.root/path
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(data))

    def save(self):
        self.write('manifest.json',self.manifest)

    def check(self, through='publish'):
        self.save()
        return gate.validate_run(self.root,through)

    def test_complete_records_pass(self):
        self.assertEqual(self.check(),[])

    def test_stale_model_blocks(self):
        self.manifest['versions']['model']=2
        self.assertTrue(any('version' in x for x in self.check()))

    def test_changed_artifact_blocks(self):
        (self.root/'writing.md').write_text('Changed after approval')
        self.assertTrue(any('Hash mismatch' in x for x in self.check()))

    def test_pending_stage_blocks(self):
        self.manifest['tasks']['writing']['status']='pending'
        self.assertTrue(any('writing' in x for x in self.check()))

    def test_critical_review_blocks(self):
        self.manifest['review']['unresolved_critical']=1
        self.assertTrue(any('critical' in x for x in self.check()))

    def test_invalid_dag_blocks(self):
        self.manifest['tasks']['model']['deps']=['industry']
        self.assertTrue(any('dependencies' in x for x in self.check()))

    def test_handoff_tampering_blocks(self):
        path=self.root/self.manifest['tasks']['outline']['handoff']
        data=json.loads(path.read_text());data['summary']='New summary'
        path.write_text(json.dumps(data))
        self.assertTrue(any('handoff SHA' in x for x in self.check()))

    def test_path_escape_blocks(self):
        self.manifest['tasks']['review']['artifacts'][0]['path']='../outside.md'
        self.assertTrue(any('inside run directory' in x for x in self.check()))

    def test_no_selection_can_skip_model_only(self):
        self.manifest['decision']='no_selection'
        self.manifest['versions']['model']=0
        self.manifest['tasks']['model'].update(status='not_applicable',reason='No eligible new candidate',input_versions={'data':1})
        for name in gate.STAGES[5:]:
            task=self.manifest['tasks'][name]
            task['input_versions'].pop('model',None)
            path=self.root/task['handoff'];h=json.loads(path.read_text());h['input_versions']=task['input_versions'];path.write_text(json.dumps(h));task['handoff_sha256']=gate.sha256(path)
        self.assertEqual(self.check(),[])

    def test_selected_cannot_skip_model(self):
        self.manifest['tasks']['model']['status']='not_applicable'
        self.assertTrue(any('model' in x for x in self.check()))

    def test_review_gate_does_not_require_future_publish(self):
        self.manifest['tasks']['publish']['status']='pending'
        self.assertEqual(self.check('review'),[])

    def test_publish_requires_registered_report(self):
        (self.root/'report.md').unlink()
        self.assertTrue(any('report.md' in x for x in self.check()))


if __name__=='__main__':
    unittest.main()
