import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from package_module import materialize, module_files

COMMIT = 'a' * 40


class ModulePackagingTests(unittest.TestCase):
    def test_each_stage_is_one_skill(self):
        for entry in (ROOT / 'subskills').glob('*/SKILL.md'):
            files = module_files(ROOT, entry.parent.name, COMMIT)
            self.assertEqual([p for p in files if p.endswith('SKILL.md')], ['SKILL.md'])
            self.assertIn(f'name: {entry.parent.name}\n', files['SKILL.md'])
            self.assertNotIn('../../references/', files['SKILL.md'])

    def test_cache_resources_and_sentence_ending_template_are_included(self):
        files = module_files(ROOT, 'cache-run', COMMIT)
        for path in ('scripts/cache_run.py', 'references/cache-policy.md', 'assets/workflow-template.json'):
            self.assertIn(path, files)
        self.assertNotIn('scripts/render_dashboard.py', files)

    def test_bare_helper_names_are_included(self):
        files = module_files(ROOT, 'update-dashboard', COMMIT)
        self.assertIn('scripts/assess_barriers.py', files)
        self.assertIn('scripts/render_dashboard.py', files)

    def test_cross_skill_links_are_not_embedded(self):
        files = module_files(ROOT, 'research-industry', COMMIT)
        self.assertIn(f'/blob/{COMMIT}/research-cashflow-value/SKILL.md', files['references/selection-policy.md'])
        self.assertIn('name: research-industry', files['SKILL.md'])

    def test_provenance_records_every_source_and_result(self):
        files = module_files(ROOT, 'cache-run', COMMIT)
        provenance = json.loads(files['assets/source-provenance.json'])
        self.assertEqual(provenance['commit'], COMMIT)
        self.assertEqual({f['packaged_path'] for f in provenance['files']}, set(files) - {'assets/source-provenance.json'})
        for row in provenance['files']:
            self.assertEqual(len(row['source_sha256']), 64)
            self.assertEqual(len(row['packaged_sha256']), 64)

    def test_invalid_identity_or_commit_is_rejected(self):
        for name, commit in (('../cache-run', COMMIT), ('unknown-skill', COMMIT), ('cache-run', 'main')):
            with self.assertRaises(ValueError):
                module_files(ROOT, name, commit)

    def test_refuses_unrelated_destination_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / 'cache-run'
            dest.mkdir()
            (dest / 'important.txt').write_text('retain')
            with self.assertRaises(ValueError):
                materialize(ROOT, 'cache-run', COMMIT, dest)
            self.assertEqual((dest / 'important.txt').read_text(), 'retain')


if __name__ == '__main__':
    unittest.main()
