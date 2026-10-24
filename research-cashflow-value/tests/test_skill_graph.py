import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from skill_graph import MANIFEST_TASKS, ready_nodes, validate_graph


class SkillGraphTests(unittest.TestCase):
    def setUp(self):
        self.graph = json.loads((ROOT / 'assets/skill-graph.json').read_text())
        self.state = {'decision': 'undecided', 'outcome': 'running', 'nodes': {}, 'input_hashes': {}, 'gates': {}}

    def record(self, name, status='accepted', reason=None):
        self.state['input_hashes'][name] = 'a' * 64
        self.state['nodes'][name] = {'status': status, 'input_hash': 'a' * 64, 'evidence': [f'handoffs/{name}.json']}
        if reason:
            self.state['nodes'][name]['reason'] = reason

    def gate(self, name, target):
        self.state['input_hashes'][target] = 'a' * 64
        self.state['gates'][name] = {'passed': True, 'command': self.graph['gate_commands'][name], 'input_hash': 'a' * 64, 'evidence': [f'checks/{name}.json']}

    def ready(self, slots=99):
        return ready_nodes(self.graph, self.state, slots)

    def test_registry_matches_all_modules_and_preserves_manifest(self):
        self.assertEqual(validate_graph(self.graph, ROOT), [])
        names = {p.parent.name for p in (ROOT / 'subskills').glob('*/SKILL.md')}
        self.assertEqual(set(self.graph['registry']), names)
        mapped = [n['manifest_task'] for n in self.graph['nodes'].values() if 'manifest_task' in n]
        self.assertCountEqual(mapped, MANIFEST_TASKS)

    def test_only_bootstrap_is_initially_ready(self):
        self.assertEqual(self.ready(), ['cache-bootstrap'])
        self.assertEqual(self.ready(0), [])

    def test_industry_and_assessment_run_in_parallel_after_plan(self):
        self.record('cache-bootstrap')
        self.record('plan')
        self.assertCountEqual(self.ready(), ['assessment', 'industry'])
        self.assertEqual(len(self.ready(1)), 1)

    def test_unaccepted_or_stale_predecessor_blocks_descendant(self):
        self.record('cache-bootstrap')
        self.record('plan', 'running')
        self.assertNotIn('industry', self.ready())
        self.record('plan')
        self.state['input_hashes']['plan'] = 'b' * 64
        self.assertNotIn('industry', self.ready())

    def test_completed_label_without_evidence_cannot_dispatch(self):
        self.record('plan')
        self.state['nodes']['plan']['evidence'] = []
        self.assertNotIn('assessment', self.ready())

    def test_blocked_dependency_is_not_success(self):
        self.record('industry', 'blocked', 'source unavailable')
        self.assertNotIn('peers', self.ready())

    def test_no_selection_requires_explicit_evidenced_model_skip(self):
        self.state['decision'] = 'no_selection'
        self.record('selection')
        self.assertNotIn('model', self.ready())
        self.assertNotIn('outline', self.ready())
        self.record('model', 'not_applicable', 'No eligible candidates after comparison')
        self.assertIn('outline', self.ready())
        self.assertEqual(self.state['nodes']['model']['status'], 'not_applicable')
        self.state['nodes']['model'].pop('reason')
        self.assertNotIn('outline', self.ready())

    def test_executed_model_remains_valid_after_valuation_rejects_candidates(self):
        self.state['decision'] = 'no_selection'
        self.record('selection')
        self.record('model')
        self.assertIn('outline', self.ready())

    def test_selected_candidate_cannot_skip_model(self):
        self.state['decision'] = 'selected'
        self.record('selection')
        self.record('model', 'not_applicable', 'Skip without modeling')
        self.assertNotIn('outline', self.ready())

    def test_assembly_requires_review_gate_bound_to_current_inputs(self):
        self.state['decision'] = 'selected'
        self.record('review')
        self.assertNotIn('publish', self.ready())
        self.gate('workflow-review', 'publish')
        self.assertIn('publish', self.ready())
        self.state['input_hashes']['publish'] = 'b' * 64
        self.assertNotIn('publish', self.ready())

    def test_delivery_waits_for_full_assessment_reflection_and_gates(self):
        self.state['decision'] = 'selected'
        self.record('publish')
        self.assertNotIn('reflection-prepublish', self.ready())
        self.record('assessment')
        self.assertIn('reflection-prepublish', self.ready())
        self.assertNotIn('delivery', self.ready())
        self.record('reflection-prepublish')
        self.gate('workflow-publish', 'delivery')
        self.assertNotIn('delivery', self.ready())
        self.gate('lifecycle-release', 'delivery')
        self.assertIn('delivery', self.ready())
        self.state['gates']['lifecycle-release']['command'] = 'echo passed'
        self.assertNotIn('delivery', self.ready())

    def test_historical_dashboard_after_blocked_current_report(self):
        self.state.update(decision='blocked', outcome='blocked')
        self.record('assessment')
        self.record('delivery', 'cancelled', 'Research blocked; no new report delivered')
        self.assertIn('dashboard', self.ready())
        self.state['nodes']['assessment']['status'] = 'blocked'
        self.assertNotIn('dashboard', self.ready())

    def test_blocked_run_closeout_requires_explicit_terminal_records(self):
        self.state.update(decision='blocked', outcome='blocked')
        deps = self.graph['nodes']['reflection-closeout']['deps']
        for dep in deps:
            self.record(dep['node'], 'cancelled', 'Bootstrap failure prevented work')
        self.record('cache-bootstrap', 'failed', 'Persistent provider unavailable')
        self.assertIn('reflection-closeout', self.ready())
        self.state['nodes']['peers']['status'] = 'running'
        self.assertNotIn('reflection-closeout', self.ready())
        self.state['nodes']['peers']['status'] = 'pending'
        self.assertNotIn('reflection-closeout', self.ready())

    def test_final_cache_survives_failed_reflection_and_deferred_evolution(self):
        self.state.update(decision='blocked', outcome='failed')
        self.record('reflection-closeout', 'failed', 'Evidence missing')
        self.record('evolution', 'cancelled', 'No accepted reflection')
        self.record('dashboard', 'blocked', 'Assessment unavailable')
        self.assertIn('cache-final', self.ready())
        self.assertNotIn('evolution', self.ready())

    def test_current_running_worker_blocks_terminal_side_effects(self):
        self.state.update(decision='blocked', outcome='blocked')
        self.record('assessment')
        self.record('delivery', 'cancelled', 'No delivery')
        self.record('peers', 'running')
        self.assertNotIn('dashboard', self.ready())

    def test_cycle_unknown_skill_and_missing_skill_file_fail(self):
        broken = copy.deepcopy(self.graph)
        broken['nodes']['cache-bootstrap']['deps'] = [{'node': 'plan', 'requires': 'accepted'}]
        self.assertTrue(any('Cycle' in e for e in validate_graph(broken)))
        broken = copy.deepcopy(self.graph)
        broken['nodes']['plan']['skill'] = 'unknown'
        self.assertTrue(any('unknown skill' in e for e in validate_graph(broken)))
        broken = copy.deepcopy(self.graph)
        broken['registry']['plan-research']['path'] = 'missing/SKILL.md'
        self.assertTrue(any('missing skill file' in e for e in validate_graph(broken, ROOT)))

    def test_path_traversal_duplicate_manifest_and_unbounded_dispatch_fail(self):
        broken = copy.deepcopy(self.graph)
        broken['registry']['plan-research']['path'] = '../external/SKILL.md'
        broken['nodes']['assessment']['manifest_task'] = 'plan'
        broken['dispatch']['workers_launch_siblings'] = True
        errors = validate_graph(broken)
        self.assertTrue(any('package-relative' in e for e in errors))
        self.assertTrue(any('exactly once' in e for e in errors))
        self.assertTrue(any('coordinator-owned' in e for e in errors))

    def test_unknown_dependency_status_or_slots_fail(self):
        broken = copy.deepcopy(self.graph)
        broken['nodes']['plan']['deps'] = [{'node': 'missing', 'requires': 'accepted'}]
        with self.assertRaises(ValueError):
            ready_nodes(broken, self.state, 1)
        with self.assertRaises(ValueError):
            ready_nodes(self.graph, self.state, -1)
        self.state['nodes']['plan'] = {'status': 'completed-in-advance'}
        with self.assertRaises(ValueError):
            self.ready()

    def test_terminal_outcome_does_not_restart_research_or_delivery(self):
        self.state['decision'] = 'selected'
        for name in ('cache-bootstrap', 'plan', 'industry', 'peers', 'selection', 'model', 'outline', 'writing', 'review', 'publish', 'reflection-prepublish'):
            self.record(name)
        self.gate('workflow-review', 'publish')
        self.gate('workflow-publish', 'delivery')
        self.gate('lifecycle-release', 'delivery')
        for outcome in ('failed', 'blocked', 'delivered', 'no_selection_delivered'):
            self.state['outcome'] = outcome
            for candidate in ('industry', 'peers', 'model', 'publish', 'delivery', 'assessment'):
                before = copy.deepcopy(self.state['nodes'])
                self.state['nodes'].pop(candidate, None)
                self.assertNotIn(candidate, self.ready(), (outcome, candidate))
                self.state['nodes'] = before

    def test_stale_assessment_cannot_update_historical_dashboard(self):
        self.state.update(decision='blocked', outcome='failed')
        self.record('assessment')
        self.record('delivery', 'cancelled', 'No new report')
        self.state['input_hashes']['assessment'] = 'b' * 64
        self.assertNotIn('dashboard', self.ready())
        self.state['nodes']['dashboard'] = {'status': 'blocked', 'reason': 'Assessment stale', 'evidence': ['checks/assessment-stale.json']}
        self.assertNotIn('delivery', self.ready())

    def test_readiness_is_pure_and_never_marks_delivery(self):
        before = copy.deepcopy(self.state)
        self.ready()
        self.assertEqual(self.state, before)


if __name__ == '__main__':
    unittest.main()
