import copy
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('barriers', ROOT/'scripts/assess_barriers.py')
MODULE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(MODULE)


def fixture():
    basis = {'currency': 'USD', 'price_basis': 'split_adjusted_ex_dividend', 'share_basis': 'one-original-share'}
    record = {'report_id': 'fixture', 'barrier_basis': basis,
              'take_profit': {'value': 120, 'currency': 'USD', 'na_reason': None},
              'stop_loss': {'value': 80, 'currency': 'USD', 'na_reason': None},
              'target_horizon': {'end_date': '2026-10-30', 'exchange_timezone': 'America/New_York', 'reason': None}}
    observations = {'activation': {'at': '2026-10-20T09:30:00-04:00', 'kind': 'hypothetical_entry', **basis, 'source_refs': ['entry-record']},
                    'coverage': {'start_at': '2026-10-20T09:30:00-04:00', 'end_at': '2026-10-24T18:00:00Z', 'complete': True, 'source_refs': ['source-session-series'], 'gaps': []},
                    'bars': [{'start_at': '2026-10-21T09:30:00-04:00', 'end_at': '2026-10-21T16:00:00-04:00', 'high': 110, 'low': 90, **basis, 'source_refs': ['bar-1']}]}
    return record, observations


class BarrierTests(unittest.TestCase):
    def assess(self, r, o, cutoff='2026-10-24T18:00:00Z'):
        return MODULE.assess(r, o, cutoff)

    def test_no_touch_only_with_complete_coverage(self):
        r,o=fixture();out=self.assess(r,o)
        self.assertEqual(out['sides']['take_profit']['status'],'not_observed')
        self.assertEqual(out['sides']['stop_loss']['status'],'not_observed')
        self.assertEqual(out['sides']['horizon']['status'],'pending')
        self.assertEqual(out['first_event']['status'],'none_observed')

    def test_tp_equality_touches_without_assumed_fill(self):
        r,o=fixture();o['bars'][0]['high']=120
        out=self.assess(r,o)
        self.assertEqual(out['sides']['take_profit']['status'],'triggered')
        self.assertEqual(out['first_event']['possible_sides'],['take_profit'])
        self.assertNotIn('execution_price',out['first_event'])

    def test_both_same_bar_is_ambiguous(self):
        r,o=fixture();o['bars'][0].update(high=121,low=79)
        out=self.assess(r,o)
        self.assertEqual(out['first_event']['status'],'ambiguous')
        self.assertEqual(set(out['first_event']['possible_sides']),{'take_profit','stop_loss'})
        self.assertTrue(out['assessment_required'])

    def test_bar_input_order_does_not_choose_winner(self):
        r,o=fixture();late=copy.deepcopy(o['bars'][0]);late.update(start_at='2026-10-22T09:30:00-04:00',end_at='2026-10-22T16:00:00-04:00',low=79)
        o['bars'][0]['high']=121;o['bars'].insert(0,late)
        out=self.assess(r,o)
        self.assertEqual(out['first_event']['possible_sides'],['take_profit'])

    def test_pending_entry_does_not_count_historical_touch(self):
        r,o=fixture();o['activation']=None;o['bars'][0]['high']=121
        out=self.assess(r,o)
        self.assertEqual(out['sides']['take_profit']['status'],'pending')
        self.assertNotEqual(out['first_event']['status'],'observed')

    def test_activation_inside_bar_is_uncertain(self):
        r,o=fixture();o['activation']['at']='2026-10-21T12:00:00-04:00';o['bars'][0]['high']=121
        out=self.assess(r,o)
        self.assertEqual(out['sides']['take_profit']['status'],'unknown')
        self.assertEqual(out['first_event']['status'],'ambiguous')

    def test_pre_activation_bars_ignored(self):
        r,o=fixture();o['activation']['at']='2026-10-22T09:30:00-04:00';o['bars'][0]['high']=121
        out=self.assess(r,o)
        self.assertNotEqual(out['sides']['take_profit']['status'],'triggered')

    def test_incomplete_coverage_not_not_hit(self):
        r,o=fixture();o['coverage']['complete']=False
        self.assertEqual(self.assess(r,o)['sides']['take_profit']['status'],'unknown')
        o['bars'][0]['high']=121
        out=self.assess(r,o)
        self.assertEqual(out['sides']['take_profit']['status'],'triggered')
        self.assertEqual(out['first_event']['status'],'ambiguous')
        self.assertTrue(out['first_global_event_not_established'])

    def test_gap_invalidates_clean_not_observed(self):
        r,o=fixture();o['coverage']['gaps']=['One trading session unavailable']
        self.assertEqual(self.assess(r,o)['sides']['stop_loss']['status'],'unknown')

    def test_missing_terms_remain_not_set(self):
        r,o=fixture();r['take_profit']={'value':None,'currency':None,'na_reason':'No published TP'};r['target_horizon']['end_date']=None;r['target_horizon']['reason']='No original horizon'
        out=self.assess(r,o)
        self.assertEqual(out['sides']['take_profit']['status'],'not_set')
        self.assertEqual(out['sides']['horizon']['status'],'not_set')
        r['take_profit']['na_reason']=None
        with self.assertRaises(ValueError):self.assess(r,o)

    def test_due_horizon_requires_sourced_exact_session(self):
        r,o=fixture();r['target_horizon']['end_date']='2026-10-23'
        self.assertEqual(self.assess(r,o)['sides']['horizon']['status'],'unknown')
        o['horizon_session']={'for_date':'2026-10-23','close_at':'2026-10-23T16:00:00-04:00','source_refs':['calendar']}
        self.assertEqual(self.assess(r,o)['sides']['horizon']['status'],'triggered')

    def test_horizon_and_tp_same_interval_order_not_inferred(self):
        r,o=fixture();r['target_horizon']['end_date']='2026-10-21';o['bars'][0]['high']=121
        o['horizon_session']={'for_date':'2026-10-21','close_at':'2026-10-21T16:00:00-04:00','source_refs':['calendar']}
        self.assertEqual(self.assess(r,o)['first_event']['status'],'ambiguous')

    def test_incremental_scope_does_not_claim_global_first(self):
        r,o=fixture();o['previous_cutoff']='2026-10-21T09:30:00-04:00';o['coverage']['start_at']=o['previous_cutoff'];o['bars'][0]['high']=121
        out=self.assess(r,o)
        self.assertTrue(out['first_global_event_not_established'])
        self.assertEqual(out['first_event']['scope'],'provided_interval_only')
        self.assertEqual(out['first_event']['status'],'observed')

    def test_incremental_gap_rejected(self):
        r,o=fixture();o['previous_cutoff']='2026-10-20T08:00:00-04:00'
        with self.assertRaises(ValueError):self.assess(r,o)

    def test_basis_currency_and_total_return_index_rejected(self):
        for key,value in [('currency','EUR'),('share_basis','post-split-share'),('price_basis','total_return_index')]:
            r,o=fixture();o['bars'][0][key]=value
            with self.assertRaises(ValueError):self.assess(r,o)

    def test_missing_basis_cannot_trigger(self):
        r,o=fixture();r['barrier_basis']=None;o['bars'][0]['high']=121
        self.assertEqual(self.assess(r,o)['sides']['take_profit']['status'],'unknown')

    def test_future_naive_nonfinite_and_unsourced_rejected(self):
        r,o=fixture();o['bars'][0]['end_at']='2026-10-25T16:00:00-04:00'
        with self.assertRaises(ValueError):self.assess(r,o)
        r,o=fixture();o['activation']['at']='2026-10-20T09:30:00'
        with self.assertRaises(ValueError):self.assess(r,o)
        r,o=fixture();r['take_profit']['value']=float('nan')
        with self.assertRaises(ValueError):self.assess(r,o)
        r,o=fixture();o['bars'][0]['source_refs']=[]
        with self.assertRaises(ValueError):self.assess(r,o)

    def test_missing_price_evidence_cannot_certify_horizon_as_first(self):
        r,o=fixture();o['bars']=[];r['target_horizon']['end_date']='2026-10-23'
        o['horizon_session']={'for_date':'2026-10-23','close_at':'2026-10-23T16:00:00-04:00','source_refs':['calendar']}
        out=self.assess(r,o)
        self.assertEqual(out['sides']['horizon']['status'],'triggered')
        self.assertEqual(out['first_event']['status'],'ambiguous')
        self.assertTrue(out['first_global_event_not_established'])

    def test_unverified_due_horizon_prevents_price_first_certainty(self):
        r,o=fixture();r['target_horizon']['end_date']='2026-10-20';o['bars'][0]['high']=121
        out=self.assess(r,o)
        self.assertEqual(out['sides']['take_profit']['status'],'triggered')
        self.assertEqual(out['sides']['horizon']['status'],'unknown')
        self.assertEqual(out['first_event']['status'],'ambiguous')
        self.assertIn('horizon',out['first_event']['possible_sides'])
        self.assertIsNone(out['first_event']['interval_start'])
        self.assertTrue(out['first_global_event_not_established'])

    def test_unverified_due_horizon_prevents_clean_no_event(self):
        r,o=fixture();r['target_horizon']['end_date']='2026-10-20'
        out=self.assess(r,o)
        self.assertEqual(out['first_event']['status'],'unknown')
        self.assertTrue(out['assessment_required'])
        self.assertTrue(out['first_global_event_not_established'])

    def test_future_horizon_does_not_obscure_observed_price_first(self):
        r,o=fixture();o['bars'][0]['high']=121
        out=self.assess(r,o)
        self.assertEqual(out['sides']['horizon']['status'],'pending')
        self.assertEqual(out['first_event']['status'],'observed')
        self.assertEqual(out['first_event']['possible_sides'],['take_profit'])
        self.assertFalse(out['first_global_event_not_established'])

    def test_reference_monitoring_is_labeled_separately(self):
        r,o=fixture();o['activation']['kind']='publication_reference'
        self.assertEqual(self.assess(r,o)['monitoring_mode'],'publication_reference')


if __name__=='__main__':unittest.main()
