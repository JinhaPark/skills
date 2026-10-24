import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('lifecycle', ROOT/'scripts/validate_lifecycle.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = {'schema_version':1, 'run_id':'fixture', 'repository_commit':'a'*40, 'decision':'selected', 'versions':{'data':1,'model':1}}
        self.write('manifest.json', self.manifest)
        cover='Growth supports demand.\n\nPeers convert cash differently.\n\nValuation supports watching the price.\n\nMargin weakness would challenge the thesis.'
        (self.root/'cover.md').write_text(cover+'\n')
        (self.root/'report.md').write_text('# Synthetic report\n\n'+cover+'\n\nA complete synthetic report fixture.\n')
        self.recommendation = {'schema_version':1, 'report_id':'report-1', 'entity_id':'synthetic-entity', 'skill_commit':'a'*40, 'publication_status':'ready', 'publication_at':None, 'report_reference':None, 'frozen_report_sha256':gate.digest(self.root/'report.md'), 'recommendation':'watch', 'entry':{'value':100}, 'target_horizon':{'end_date':'2027-10-24','exchange_timezone':'America/New_York','market_close_rule':'first_session_on_or_after'}}
        self.recommendation.update(original_snapshot_available=True,base_currency='USD',entry_convention='publication_reference',entry={'value':100,'observed_at':'2026-10-23T16:00:00-04:00','currency':'USD','basis':'split_adjusted_ex_dividend','share_basis':'entry-share','fx_to_base':1,'source_refs':['fixture:price']},return_convention={'dividends':'cash_received_not_reinvested','tax':'pre_tax','fx':'actual_receipt_date_for_distributions','terminal_proceeds':'hold_cash_without_interest_to_original_horizon'},benchmark={'entity':'industry-index'},expected_return=None,thesis_narrative='Cash conversion will improve.',thesis_criteria=[{'id':'fcf-threshold','metric_id':'normalized-fcf','period_end':'2027-06-30','unit':'USD million','currency':'USD','trigger_operator':'<','trigger_threshold':80}],unavailable_fields=[{'field':'expected_return','reason':'No single probability-weighted expected return; conditional scenarios are preserved.'}])
        self.recommendation.update(barrier_basis={'currency':'USD','price_basis':'split_adjusted_ex_dividend','share_basis':'entry-share'},target_entry={'value':95,'currency':'USD','na_reason':None},take_profit={'value':125,'currency':'USD','na_reason':None},stop_loss={'value':None,'currency':None,'na_reason':'No price-based stop was specified.'})
        self.recommendation['cover_letter']={'path':'cover.md','sha256':gate.digest(self.root/'cover.md'),'summary':'Growth and cash conversion support further research, while valuation and margins determine the decision.'}
        self.write('recommendation.json', self.recommendation)
        self.ledger={'publications':[{'publication_key':'legacy:HP-Inc:2026-10-24','report_id':None,'status':'delivered','provenance':'user_provided'}],'coverage_complete':True,'coverage_gap_reason':None}
        self.write('assessment/ledger-snapshot.json', self.ledger)
        self.assessment={'run_id':'fixture','as_of':'2026-10-24T20:00:00Z','ledger_reference':'assessment/ledger-snapshot.json','ledger_sha256':gate.digest(self.root/'assessment/ledger-snapshot.json'),'coverage_complete':True,'coverage_gap_reason':None,'rows':[{'publication_key':'legacy:HP-Inc:2026-10-24','report_id':None,'status':'legacy_unavailable'}]}
        self.write('assessment/track-record.json', self.assessment)
        self.reflection = json.loads((ROOT/'assets/reflection-template.json').read_text())
        self.reflection.update(run_id='fixture',status='completed',reviewer_id='reflector',editor_id='editor',author_ids=['author-1'],trace_reference='fixture-trace:reflection',input_versions={'data':1,'model':1},unresolved_critical=0,publication_gate='passed',assessment_reference='assessment/track-record.json',assessment_sha256=gate.digest(self.root/'assessment/track-record.json'),assessment_unavailable_reason=None)
        for dimension in self.reflection['dimensions'].values():
            dimension.update(status='pass',evidence_references=['fixture-evidence'],limitations=[])
        self.reflection['reviewed_artifacts'] = [{'path':p,'sha256':gate.digest(self.root/p)} for p in ('report.md','recommendation.json','cover.md')]
        self.closeout = copy.deepcopy(self.reflection)
        self.closeout.update(checkpoint='closeout',run_outcome='delivered',run_outcome_evidence_reference='fixture:delivery',cache_status={'status':'persisted','receipt_references':['fixture:cache'],'uncovered_artifacts':[]},delivery_status={'status':'delivered','receipt_references':['fixture:delivery']},backlog=[],next_run_handoff={})
        self.closeout.pop('publication_gate')
        self.evolution = json.loads((ROOT/'assets/evolution-template.json').read_text())
        self.evolution.update(run_id='fixture',current_run_commit='a'*40,status='observe',reason='No supported workflow defect in this fixture.')

    def write(self, relative, value):
        path=self.root/relative
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(value))

    def check(self, phase='release'):
        self.write('reviews/reflection-prepublish.json',self.reflection)
        self.write('reflection/closeout.json',self.closeout)
        self.write('evolution/decision.json',self.evolution)
        return gate.validate_lifecycle(self.root,phase)

    def promotion(self):
        self.evolution.update(status='promoted',experiment_id='fixture-exp',reflection_owner_id='reflector',base_commit='a'*40,candidate_commit='b'*40,proposer_id='proposer',peer_reviewer_id='peer',editor_id='editor',affected_author_ids=['author-1'],trace_references=['fixture:experiment'],invariants_unchanged=True,checked_invariant_ids=sorted(gate.INVARIANTS),discovery=[{'source':'existing skills','result':'inspected'}],changes=[{'id':'repair-1','finding_ids':['f-1'],'changed_paths':['research-cashflow-value/subskills/cache-run/SKILL.md'],'mechanism':'Clarify an observed ambiguity','acceptance_test':'Fresh scoped execution','regression_risk':'Existing cache semantics'}],promotion_receipt={'repository':'JinhaPark/skills','branch':'main','previous_sha':'a'*40,'new_sha':'b'*40,'reference':'fixture:remote-update'})
        for key, check in self.evolution['checks'].items():
            evidence = {'base_commit':'a'*40,'candidate_commit':'b'*40,'evaluator_id':'fresh-evaluator','result':'Observed pass'}
            check.update(status='passed',task='Synthetic task',base_commit='a'*40,candidate_commit='b'*40,result='Observed pass')
            if key == 'forward_test':
                for field in ('task_artifacts','input_artifacts','produced_artifacts'):
                    path=f'evolution/fixtures/{field}.json'
                    self.write(path,{'synthetic':field})
                    evidence[field]=[{'path':path,'sha256':gate.digest(self.root/path)}]
                    check[field]=evidence[field]
                path='evolution/fixtures/baseline.json'
                self.write(path,{'baseline':'observed behavior','candidate':'observed behavior'})
                evidence['baseline_comparison']={'path':path,'sha256':gate.digest(self.root/path)}
                check.update(evaluator_id='fresh-evaluator',baseline_comparison=evidence['baseline_comparison'])
            path=f'evolution/evidence/{key}.json'
            self.write(path,evidence)
            check.update(evidence_reference=path,evidence_sha256=gate.digest(self.root/path))
        self.evolution['peer_assessment'].update(status='approved',evidence_references=['fixture:peer'],unresolved_material_concerns=[],justification='Evidence supports scoped change')

    def save_recommendation(self):
        self.write('recommendation.json',self.recommendation)
        self.reflection['reviewed_artifacts'][1]['sha256']=gate.digest(self.root/'recommendation.json')

    def test_explicit_na_targets_and_period_are_publishable(self):
        for field in ('target_entry','take_profit','stop_loss'):
            self.recommendation[field]={'value':None,'currency':None,'na_reason':'Original policy did not specify this term.'}
        self.recommendation['target_horizon']={'end_date':None,'reason':'No investment-period endpoint specified.'}
        self.save_recommendation()
        self.assertEqual(self.check(),[])

    def test_missing_target_or_na_reason_blocks(self):
        self.recommendation.pop('take_profit')
        self.save_recommendation()
        self.assertTrue(any('take_profit' in error for error in self.check()))
        self.recommendation['take_profit']={'value':None,'currency':None,'na_reason':None}
        self.recommendation['target_horizon']={'end_date':None,'reason':None}
        self.save_recommendation()
        result=self.check()
        self.assertTrue(any('take_profit N/A' in error for error in result))
        self.assertTrue(any('Investment-period N/A' in error for error in result))

    def test_nonfinite_or_nonpositive_targets_rejected(self):
        for value in (float('nan'),float('inf'),True,0,-1):
            with self.subTest(value=value):
                self.recommendation['stop_loss']={'value':value,'currency':'USD','na_reason':None}
                self.save_recommendation()
                self.assertTrue(any('stop_loss must be a positive finite' in error for error in self.check()))

    def test_target_value_requires_currency_and_not_na(self):
        self.recommendation['take_profit']={'value':125,'currency':None,'na_reason':'Unknown'}
        self.save_recommendation()
        result=self.check()
        self.assertTrue(any('take_profit needs its price currency' in error for error in result))
        self.assertTrue(any('both a price and N/A' in error for error in result))

    def test_numeric_barriers_require_frozen_comparable_basis(self):
        for basis in (None,{}, {'currency':'USD','price_basis':'total_return_index','share_basis':'entry-share'}, {'currency':'JPY','price_basis':'split_adjusted_ex_dividend','share_basis':'entry-share'}):
            with self.subTest(basis=basis):
                self.recommendation['barrier_basis']=basis
                self.save_recommendation()
                self.assertTrue(any('basis' in error for error in self.check()))

    def test_no_selection_still_requires_explicit_terms(self):
        self.manifest['decision']='no_selection'
        self.write('manifest.json',self.manifest)
        self.recommendation['recommendation']='no_selection'
        for field in ('target_entry','take_profit','stop_loss'):
            self.recommendation[field]={'value':None,'currency':None,'na_reason':'No company selected.'}
        self.recommendation['target_horizon']={'end_date':None,'reason':'No company selected.'}
        self.save_recommendation()
        self.assertEqual(self.check(),[])
        self.recommendation.pop('stop_loss')
        self.save_recommendation()
        self.assertTrue(any('stop_loss' in error for error in self.check()))

    def test_cover_hash_must_match_original_bytes(self):
        self.recommendation['cover_letter']['sha256']='0'*64
        self.save_recommendation()
        self.assertTrue(any('Hash mismatch: cover.md' in error for error in self.check()))

    def test_rehashed_cover_outside_published_report_blocks(self):
        (self.root/'cover.md').write_text('Different first paragraph.\n\nDifferent second.\n\nDifferent third.\n\nDifferent fourth.\n')
        self.recommendation['cover_letter']['sha256']=gate.digest(self.root/'cover.md')
        self.reflection['reviewed_artifacts'][2]['sha256']=gate.digest(self.root/'cover.md')
        self.save_recommendation()
        self.assertTrue(any('occur verbatim in report.md' in error for error in self.check()))

    def test_cover_is_a_required_reviewed_artifact(self):
        self.reflection['reviewed_artifacts']=[a for a in self.reflection['reviewed_artifacts'] if a['path']!='cover.md']
        self.assertTrue(any('cover.md must be a hashed reviewed artifact' in error for error in self.check()))

    def test_cover_summary_is_one_short_paragraph(self):
        for summary in ('', 'word '*51, 'First paragraph.\nSecond paragraph.'):
            with self.subTest(summary=summary):
                self.recommendation['cover_letter']['summary']=summary
                self.save_recommendation()
                self.assertTrue(any('Cover summary must be' in error for error in self.check()))

    def test_release_and_observe_closeout_pass(self):
        self.assertEqual(self.check(),[])
        self.assertEqual(self.check('closeout'),[])

    def test_editor_cannot_pose_as_independent_reflector(self):
        self.reflection['reviewer_id']='editor'
        self.assertTrue(any('Independent reviewer' in e for e in self.check()))

    def test_author_cannot_pose_as_independent_reflector(self):
        self.reflection['reviewer_id']='author-1'
        self.assertTrue(any('Independent reviewer' in e for e in self.check()))

    def test_self_review_requires_disclosure(self):
        self.reflection.update(mode='self_review',reviewer_id='editor')
        self.assertTrue(any('Self-review' in e for e in self.check()))
        self.reflection['limitations']=['Independent agents were unavailable.']
        self.assertEqual(self.check(),[])

    def test_changed_final_report_invalidates_reflection(self):
        (self.root/'report.md').write_text('Changed conclusion after approval')
        self.assertTrue(any('Hash mismatch' in e for e in self.check()))

    def test_stale_model_version_blocks(self):
        self.reflection['input_versions']['model']=0
        self.assertTrue(any('Stale' in e for e in self.check()))

    def test_blank_template_dimension_does_not_pass(self):
        self.reflection['dimensions']['accuracy'].update(status='not_assessable',limitations=['Not assessed yet.'])
        self.assertTrue(any('accuracy has not passed' in e for e in self.check()))

    def test_outcomes_may_be_unassessable_with_reason(self):
        self.reflection['dimensions']['outcome_assessment'].update(status='not_assessable',evidence_references=[],limitations=['No mature original horizons yet.'])
        self.assertEqual(self.check(),[])

    def test_hidden_critical_finding_blocks_despite_zero_counter(self):
        self.reflection['findings']=[{'finding_id':'f-1','severity':'critical','status':'accepted_limitation','evidence_references':['fixture:bad-dcf'],'verification_references':[]}]
        result=self.check()
        self.assertTrue(any('critical finding' in e for e in result))
        self.assertTrue(any('does not match' in e for e in result))

    def test_resolved_critical_needs_recheck(self):
        self.reflection['findings']=[{'finding_id':'f-1','severity':'critical','status':'resolved','evidence_references':['fixture:bad-dcf'],'verification_references':[]}]
        self.assertTrue(any('verification evidence' in e for e in self.check()))

    def test_assessment_tamper_blocks(self):
        self.write('assessment/track-record.json',{'rows':['silently omitted loss']})
        self.assertTrue(any('Hash mismatch' in e for e in self.check()))

    def test_recommendation_report_link_must_match(self):
        self.recommendation['frozen_report_sha256']='c'*64
        self.write('recommendation.json',self.recommendation)
        self.reflection['reviewed_artifacts'][1]['sha256']=gate.digest(self.root/'recommendation.json')
        self.assertTrue(any('Frozen report hash' in e for e in self.check()))

    def test_blocked_run_can_close_out_without_report(self):
        self.closeout.update(run_outcome='blocked',reviewed_artifacts=[],delivery_status={'status':'pending','receipt_references':[]},cache_status={'status':'unavailable','receipt_references':[],'uncovered_artifacts':['report.md']},assessment_reference=None,assessment_sha256=None,assessment_unavailable_reason='History provider unavailable')
        (self.root/'report.md').unlink()
        self.assertEqual(self.check('closeout'),[])

    def test_promoted_candidate_requires_all_gates(self):
        self.promotion()
        self.assertEqual(self.check('closeout'),[])
        self.evolution['checks']['forward_test']['status']='failed'
        self.assertTrue(any('forward_test must pass' in e for e in self.check('closeout')))

    def test_patch_peer_cannot_self_approve(self):
        self.promotion();self.evolution['peer_reviewer_id']='proposer'
        self.assertTrue(any('Patch peer must be distinct' in e for e in self.check('closeout')))

    def test_no_automatic_promotion_from_self_review(self):
        self.promotion();self.closeout.update(mode='self_review',limitations=['Agents unavailable'])
        self.assertTrue(any('Self-review cannot support' in e for e in self.check('closeout')))

    def test_outside_skill_changes_block_promotion(self):
        self.promotion();self.evolution['changes'][0]['changed_paths']=['distress-adjusted-dcf/scripts/calculate.py']
        self.assertTrue(any('out-of-scope' in e for e in self.check('closeout')))

    def test_receipt_must_match_expected_base_and_candidate(self):
        self.promotion();self.evolution['promotion_receipt']['previous_sha']='c'*40
        self.assertTrue(any('guarded main-branch' in e for e in self.check('closeout')))

    def test_skill_changes_cannot_apply_to_current_run(self):
        self.promotion();self.evolution['next_run_only']=False
        self.assertTrue(any('next run' in e for e in self.check('closeout')))

    def test_cache_success_needs_receipts(self):
        self.closeout['cache_status']['receipt_references']=[]
        self.assertTrue(any('Persisted cache needs receipts' in e for e in self.check('closeout')))

    def test_delivery_outcome_cannot_conflict_with_receipt(self):
        self.closeout['delivery_status']={'status':'pending','receipt_references':[]}
        self.assertTrue(any('contradicts delivery status' in e for e in self.check('closeout')))

    def test_traversal_and_symlink_artifacts_rejected(self):
        self.reflection['reviewed_artifacts'][0]['path']='../report.md'
        self.assertTrue(any('inside run directory' in e for e in self.check()))
        self.reflection['reviewed_artifacts'][0]['path']='linked-report.md'
        (self.root/'linked-report.md').symlink_to(self.root/'report.md')
        self.assertTrue(any('Symlink' in e for e in self.check()))


    def test_empty_recommendation_cannot_pass_by_hashing(self):
        self.write('recommendation.json',{})
        self.reflection['reviewed_artifacts'][1]['sha256']=gate.digest(self.root/'recommendation.json')
        self.assertTrue(any('recommendation:' in e for e in self.check()))

    def test_untouched_recommendation_template_blocks(self):
        self.write('recommendation.json',json.loads((ROOT/'assets/recommendation-template.json').read_text()))
        self.reflection['reviewed_artifacts'][1]['sha256']=gate.digest(self.root/'recommendation.json')
        self.assertTrue(any('recommendation:' in e for e in self.check()))

    def test_empty_reference_price_object_blocks(self):
        self.recommendation['entry']={}
        self.write('recommendation.json',self.recommendation)
        self.reflection['reviewed_artifacts'][1]['sha256']=gate.digest(self.root/'recommendation.json')
        self.assertTrue(any('original price' in e for e in self.check()))

    def test_check_evidence_cannot_belong_to_other_candidate(self):
        self.promotion()
        check=self.evolution['checks']['regression']
        path=self.root/check['evidence_reference']
        evidence=json.loads(path.read_text());evidence['candidate_commit']='c'*40
        self.write(check['evidence_reference'],evidence)
        check['evidence_sha256']=gate.digest(path)
        self.assertTrue(any('bind candidate/base' in e for e in self.check('closeout')))

    def test_forward_output_tampering_blocks(self):
        self.promotion()
        path=self.evolution['checks']['forward_test']['produced_artifacts'][0]['path']
        self.write(path,{'fabricated':'pass'})
        self.assertTrue(any('Hash mismatch' in e for e in self.check('closeout')))

    def test_reflector_cannot_approve_own_patch_assessment(self):
        self.promotion();self.evolution['peer_reviewer_id']='reflector'
        self.assertTrue(any('Patch peer must be distinct' in e for e in self.check('closeout')))

    def test_validated_candidate_passes_before_remote_promotion(self):
        self.promotion();self.evolution.update(status='validated',promotion_receipt=None)
        self.assertEqual(self.check('closeout'),[])


    def test_empty_assessment_cannot_omit_known_publications(self):
        self.assessment['rows']=[]
        self.write('assessment/track-record.json',self.assessment)
        self.reflection['assessment_sha256']=gate.digest(self.root/'assessment/track-record.json')
        self.assertTrue(any('every confirmed ledger vintage' in e for e in self.check()))

    def test_duplicate_assessment_vintage_blocks(self):
        self.assessment['rows'].append(copy.deepcopy(self.assessment['rows'][0]))
        self.write('assessment/track-record.json',self.assessment)
        self.reflection['assessment_sha256']=gate.digest(self.root/'assessment/track-record.json')
        self.assertTrue(any('Duplicate assessed' in e for e in self.check()))

    def test_missing_legacy_report_cannot_become_matured_win(self):
        self.assessment['rows'][0]['status']='matured'
        self.write('assessment/track-record.json',self.assessment)
        self.reflection['assessment_sha256']=gate.digest(self.root/'assessment/track-record.json')
        self.assertTrue(any('must remain legacy_unavailable' in e for e in self.check()))


    def test_release_cannot_skip_assessment_with_excuse(self):
        self.reflection.update(assessment_reference=None,assessment_sha256=None,assessment_unavailable_reason='Legacy history unavailable')
        self.assertTrue(any('require an assessment record' in e for e in self.check()))


    def test_candidate_cannot_hide_an_author_to_approve_itself(self):
        self.promotion();self.evolution.update(affected_author_ids=[],peer_reviewer_id='author-1')
        self.assertTrue(any('Patch peer must be distinct' in e for e in self.check('closeout')))


    def test_known_report_with_unavailable_baseline_is_retained(self):
        self.ledger['publications'].append({'publication_key':'report:known','report_id':'known','status':'delivered','provenance':'delivery_receipt'})
        self.write('assessment/ledger-snapshot.json',self.ledger)
        self.assessment['ledger_sha256']=gate.digest(self.root/'assessment/ledger-snapshot.json')
        self.assessment['rows'].append({'publication_key':'report:known','report_id':'known','status':'baseline_unavailable'})
        self.write('assessment/track-record.json',self.assessment)
        self.reflection['assessment_sha256']=gate.digest(self.root/'assessment/track-record.json')
        self.assertEqual(self.check(),[])


    def test_known_report_with_unavailable_horizon_is_retained(self):
        self.ledger['publications'].append({'publication_key':'report:known','report_id':'known','status':'delivered','provenance':'delivery_receipt'})
        self.write('assessment/ledger-snapshot.json',self.ledger)
        self.assessment['ledger_sha256']=gate.digest(self.root/'assessment/ledger-snapshot.json')
        self.assessment['rows'].append({'publication_key':'report:known','report_id':'known','status':'horizon_unavailable'})
        self.write('assessment/track-record.json',self.assessment)
        self.reflection['assessment_sha256']=gate.digest(self.root/'assessment/track-record.json')
        self.assertEqual(self.check(),[])

    def test_malformed_thesis_criteria_block_frozen_baseline(self):
        valid=copy.deepcopy(self.recommendation['thesis_criteria'][0])
        malformed=[{'id':'fcf-threshold'},{**valid,'trigger_threshold':True},{**valid,'trigger_threshold':float('inf')},{**valid,'trigger_operator':'!='},{**valid,'period_end':'next year'}]
        for criterion in malformed:
            with self.subTest(criterion=criterion):
                self.recommendation['thesis_criteria']=[criterion]
                self.write('recommendation.json',self.recommendation)
                self.reflection['reviewed_artifacts'][1]['sha256']=gate.digest(self.root/'recommendation.json')
                self.assertTrue(any('thesis' in e.lower() for e in self.check()))

    def test_duplicate_thesis_criterion_ids_block(self):
        self.recommendation['thesis_criteria']*=2
        self.write('recommendation.json',self.recommendation)
        self.reflection['reviewed_artifacts'][1]['sha256']=gate.digest(self.root/'recommendation.json')
        self.assertTrue(any('criterion IDs' in e for e in self.check()))

    def test_empty_thesis_criteria_need_explicit_reason(self):
        self.recommendation['thesis_criteria']=[]
        self.recommendation['unavailable_fields'].append({'field':'thesis_criteria','reason':'No defensible numerical trigger; narrative falsification evidence retained.'})
        self.write('recommendation.json',self.recommendation)
        self.reflection['reviewed_artifacts'][1]['sha256']=gate.digest(self.root/'recommendation.json')
        self.assertEqual(self.check(),[])


if __name__=='__main__':
    unittest.main()
