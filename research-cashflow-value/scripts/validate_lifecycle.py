#!/usr/bin/env python3
"""Validate lifecycle records and hashes, not financial truth or real agent execution."""
import argparse
import hashlib
import json
import math
import re
from datetime import date, datetime
from pathlib import Path, PurePosixPath

DIMENSIONS = ('accuracy', 'completeness', 'reasoning', 'coherence', 'calibration', 'outcome_assessment', 'workflow_reliability')
INVARIANTS = {'selection', 'valuation', 'evidence', 'history', 'delivery', 'orchestration', 'scope'}
CHECKS = ('invariants', 'regression', 'skill_validation', 'forward_test')
SHA = re.compile(r'^[0-9a-f]{64}$')
COMMIT = re.compile(r'^[0-9a-f]{40}$')


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def strings(value, allow_empty=True):
    return isinstance(value, list) and (allow_empty or bool(value)) and all(nonempty(v) for v in value)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_file(root, name):
    if not nonempty(name) or '\\' in name:
        raise ValueError('Expected relative artifact path')
    rel = PurePosixPath(name)
    if rel.is_absolute() or any(part in ('', '.', '..') for part in name.split('/')):
        raise ValueError('Artifact path must stay inside run directory')
    path = root.joinpath(*rel.parts)
    for component in (path, *path.parents):
        if component == root:
            break
        if component.is_symlink():
            raise ValueError('Symlink artifacts are not allowed')
    if not path.is_file() or not path.stat().st_size:
        raise ValueError(f'Missing or empty artifact: {name}')
    return path


def read_record(root, name):
    value = json.loads(local_file(root, name).read_text())
    if not isinstance(value, dict):
        raise ValueError(f'{name} must be an object')
    return value


def check_artifact(root, name, expected):
    path = local_file(root, name)
    if not isinstance(expected, str) or not SHA.fullmatch(expected) or digest(path) != expected:
        raise ValueError(f'Hash mismatch: {name}')
    return path


def check_reflection(root, record, manifest, checkpoint):
    errors = []
    def fail(message):
        errors.append(f'{checkpoint}: {message}')
    if record.get('schema_version') != 1 or record.get('checkpoint') != checkpoint:
        fail('Wrong schema/checkpoint')
    if record.get('run_id') != manifest.get('run_id'):
        fail('Run ID differs from manifest')
    if record.get('status') != 'completed':
        fail('Reflection is not completed')
    if record.get('input_versions') != manifest.get('versions'):
        fail('Stale reflection input versions')
    if not isinstance(record.get('input_versions'), dict) or set(record.get('input_versions', {})) != {'data', 'model'} or any(type(v) is not int or v < 0 for v in record.get('input_versions', {}).values()):
        fail('Invalid input versions')
    for field in ('reviewer_id', 'editor_id', 'trace_reference'):
        if not nonempty(record.get(field)):
            fail(f'Missing {field}')
    authors = record.get('author_ids')
    if not strings(authors):
        fail('author_ids must be an array of actual IDs')
        authors = []
    mode = record.get('mode')
    if mode == 'independent':
        if record.get('reviewer_id') in [record.get('editor_id'), *authors]:
            fail('Independent reviewer cannot be editor or author')
    elif mode == 'self_review':
        if not strings(record.get('limitations'), allow_empty=False):
            fail('Self-review must disclose its limitations')
    else:
        fail('Invalid review mode')
    if not strings(record.get('limitations')):
        fail('limitations must be a string array')
    artifacts = record.get('reviewed_artifacts')
    names = set()
    if not isinstance(artifacts, list):
        fail('reviewed_artifacts must be an array')
        artifacts = []
    for artifact in artifacts:
        try:
            if not isinstance(artifact, dict):
                raise ValueError('Malformed reviewed artifact')
            name = artifact.get('path')
            check_artifact(root, name, artifact.get('sha256'))
            if name in names:
                raise ValueError(f'Duplicate reviewed artifact: {name}')
            names.add(name)
        except (OSError, ValueError, TypeError) as exc:
            fail(str(exc))
    if checkpoint == 'prepublish':
        for required in ('report.md', 'recommendation.json'):
            if required not in names:
                fail(f'{required} must be a hashed reviewed artifact')
    dimensions = record.get('dimensions', {})
    if not isinstance(dimensions, dict):
        dimensions = {}
    for key in DIMENSIONS:
        dimension = dimensions.get(key, {})
        if not isinstance(dimension, dict):
            dimension = {}
        status = dimension.get('status')
        if status not in ('pass', 'concern', 'fail', 'not_assessable'):
            fail(f'Missing/invalid dimension: {key}')
        if not strings(dimension.get('evidence_references')) or not strings(dimension.get('limitations')):
            fail(f'Invalid evidence/limitations for {key}')
        if status in ('pass', 'concern', 'fail') and not dimension.get('evidence_references'):
            fail(f'{key} requires evidence references')
        if status == 'concern' and not dimension.get('limitations'):
            fail(f'{key} concern requires explicit limitations')
        if status == 'not_assessable' and not dimension.get('limitations'):
            fail(f'{key} needs an unavailable reason')
        if checkpoint == 'prepublish' and key in ('accuracy', 'completeness', 'reasoning', 'coherence') and status in ('fail', 'not_assessable'):
            fail(f'{key} has not passed a publishable assessment')
    findings = record.get('findings')
    unresolved = 0
    if not isinstance(findings, list):
        fail('findings must be an array')
        findings = []
    for finding in findings:
        if not isinstance(finding, dict):
            fail('Malformed finding')
            continue
        severity, status = finding.get('severity'), finding.get('status')
        if severity not in ('critical', 'major', 'minor') or status not in ('open', 'resolved', 'accepted_limitation'):
            fail('Invalid finding severity/status')
        if not nonempty(finding.get('finding_id')) or not strings(finding.get('evidence_references'), allow_empty=False):
            fail('Finding needs identity and evidence')
        if status == 'resolved' and not strings(finding.get('verification_references'), allow_empty=False):
            fail('Resolved finding requires verification evidence')
        if severity == 'critical' and status != 'resolved':
            unresolved += 1
            if checkpoint == 'prepublish':
                fail('Unresolved critical finding blocks publication')
        if checkpoint == 'prepublish' and severity == 'major':
            if status == 'open':
                fail('Open major finding blocks publication')
            if status == 'accepted_limitation' and (not nonempty(finding.get('impact')) or not strings(finding.get('verification_references'), allow_empty=False)):
                fail('Accepted major limitation requires impact and explicit verification')
    if type(record.get('unresolved_critical')) is not int or record.get('unresolved_critical') != unresolved:
        fail('unresolved_critical does not match findings')
    if checkpoint == 'prepublish' and record.get('publication_gate') != 'passed':
        fail('Publication gate did not pass')
    assessment = record.get('assessment_reference')
    if assessment is None:
        if checkpoint == 'prepublish' or record.get('run_outcome') in ('delivered', 'no_selection_delivered'):
            fail('Published reports require an assessment record, including known legacy NA rows')
        if record.get('assessment_sha256') is not None or not nonempty(record.get('assessment_unavailable_reason')):
            fail('Missing assessment needs null hash and explicit reason')
    else:
        try:
            check_artifact(root, assessment, record.get('assessment_sha256'))
            errors.extend(check_assessment(root, read_record(root, assessment), manifest))
            if record.get('assessment_unavailable_reason') is not None:
                fail('Assessment exists but unavailable reason is not null')
        except (OSError, ValueError, TypeError) as exc:
            fail(str(exc))
    return errors


def check_assessment(root, assessment, manifest):
    errors = []
    def fail(message):
        errors.append(f'assessment: {message}')
    if assessment.get('run_id') != manifest.get('run_id'):
        fail('Run ID differs from manifest')
    try:
        stamp = datetime.fromisoformat(assessment.get('as_of', '').replace('Z','+00:00'))
        if stamp.tzinfo is None:
            raise ValueError('No timezone')
    except (ValueError, TypeError, AttributeError):
        fail('Missing timezone-aware assessment cutoff')
    try:
        check_artifact(root, assessment.get('ledger_reference'), assessment.get('ledger_sha256'))
        ledger = read_record(root, assessment['ledger_reference'])
    except (OSError, ValueError, TypeError, KeyError) as exc:
        fail(str(exc))
        return errors
    for source, record in (('ledger',ledger),('assessment',assessment)):
        if type(record.get('coverage_complete')) is not bool:
            fail(f'{source} must state coverage completeness')
        elif record['coverage_complete'] and record.get('coverage_gap_reason') is not None:
            fail(f'{source} complete coverage cannot carry a gap reason')
        elif not record['coverage_complete'] and not nonempty(record.get('coverage_gap_reason')):
            fail(f'{source} incomplete coverage needs a reason')
    if assessment.get('coverage_complete') != ledger.get('coverage_complete'):
        fail('Assessment coverage contradicts restored ledger')
    publications = ledger.get('publications')
    if not isinstance(publications, list):
        fail('Ledger publications must be an array')
        publications = []
    expected = {}
    for item in publications:
        if not isinstance(item, dict) or not nonempty(item.get('publication_key')):
            fail('Ledger entry needs a stable publication key')
            continue
        key = item['publication_key']
        if key in expected:
            fail('Duplicate ledger publication key')
        if item.get('status') != 'delivered' or item.get('provenance') not in ('user_provided','delivery_receipt'):
            fail('Normalized ledger must contain confirmed publication provenance')
        report_id = item.get('report_id')
        if report_id is not None and not nonempty(report_id):
            fail('Invalid original report ID')
        if report_id is None and item.get('provenance') != 'user_provided':
            fail('Missing original report ID needs legacy user-provided provenance')
        expected[key] = report_id
    rows = assessment.get('rows')
    if not isinstance(rows, list):
        fail('Assessment rows must be an array')
        rows = []
    actual = {}
    statuses = {'matured','interim','pending_horizon','awaiting_horizon_data','legacy_unavailable','baseline_unavailable','not_a_stock_recommendation'}
    for row in rows:
        if not isinstance(row, dict) or not nonempty(row.get('publication_key')):
            fail('Assessment row needs original publication key')
            continue
        key = row['publication_key']
        if key in actual:
            fail('Duplicate assessed publication key')
        actual[key] = row.get('report_id')
        if row.get('status') not in statuses:
            fail('Invalid historical assessment status')
        if row.get('report_id') is None and row.get('status') != 'legacy_unavailable':
            fail('Missing original report must remain legacy_unavailable')
    if actual != expected:
        fail('Assessment rows must match every confirmed ledger vintage exactly')
    return errors


def permitted_skill_path(name):
    if not nonempty(name) or '\\' in name:
        return False
    parts = name.split('/')
    if any(part in ('', '.', '..') for part in parts) or parts[0] != 'research-cashflow-value':
        return False
    if len(parts) == 2:
        return parts[1] == 'SKILL.md'
    if len(parts) < 3 or parts[1] not in ('agents', 'assets', 'references', 'scripts', 'tests', 'subskills'):
        return False
    return not any(part in ('runs', 'reports', 'cache', 'private', 'state', '__pycache__', '.git') for part in parts[2:])


def check_evolution(root, record, manifest, closeout):
    errors = []
    def fail(message):
        errors.append(f'evolution: {message}')
    if record.get('schema_version') != 1 or record.get('run_id') != manifest.get('run_id'):
        fail('Wrong schema/run ID')
    status = record.get('status')
    if status not in ('observe', 'proposed', 'validated', 'promoted', 'deferred', 'rejected', 'rolled_back'):
        fail('Invalid decision status')
    if not nonempty(record.get('reason')):
        fail('Decision requires a reason')
    if record.get('next_run_only') is not True:
        fail('Changes must apply only to the next run')
    if record.get('current_run_commit') != manifest.get('repository_commit') or not COMMIT.fullmatch(str(record.get('current_run_commit', ''))):
        fail('Current invocation commit must match the pinned manifest')
    changes = record.get('changes')
    if not isinstance(changes, list) or len(changes) > 3:
        fail('At most three coherent changes are allowed')
        changes = []
    change_ids = set()
    for change in changes:
        if not isinstance(change, dict) or not nonempty(change.get('id')):
            fail('Each change needs an ID')
            continue
        if change['id'] in change_ids:
            fail('Duplicate change ID')
        change_ids.add(change['id'])
        paths = change.get('changed_paths')
        if not strings(paths, allow_empty=False) or not all(permitted_skill_path(path) for path in paths):
            fail('Change contains missing or out-of-scope paths')
        for field in ('mechanism', 'acceptance_test', 'regression_risk'):
            if not nonempty(change.get(field)):
                fail(f'Change missing {field}')
        if not strings(change.get('finding_ids'), allow_empty=False):
            fail('Change needs supporting finding IDs')
    if status in ('validated', 'promoted'):
        if not changes:
            fail('Validated/promoted decisions require changes')
        if closeout.get('mode') != 'independent':
            fail('Self-review cannot support automatic promotion')
        for field in ('base_commit', 'candidate_commit'):
            if not COMMIT.fullmatch(str(record.get(field, ''))):
                fail(f'{field} must be a full commit SHA')
        if record.get('candidate_commit') == record.get('current_run_commit'):
            fail('Candidate cannot replace the current invocation commit')
        for field in ('proposer_id', 'peer_reviewer_id', 'editor_id', 'experiment_id'):
            if not nonempty(record.get(field)):
                fail(f'Missing {field}')
        authors = record.get('affected_author_ids')
        if not strings(authors):
            fail('affected_author_ids must be an array')
            authors = []
        authors = list(set(authors + closeout.get('author_ids', []))) if strings(closeout.get('author_ids')) else authors
        if record.get('editor_id') != closeout.get('editor_id'):
            fail('Candidate editor must match closeout editor')
        if record.get('reflection_owner_id') != closeout.get('reviewer_id'):
            fail('Reflection owner must match closeout reviewer')
        if record.get('peer_reviewer_id') in [record.get('proposer_id'), record.get('editor_id'), closeout.get('reviewer_id'), *authors]:
            fail('Patch peer must be distinct from proposer, editor, reflector and authors')
        if not strings(record.get('trace_references'), allow_empty=False):
            fail('Missing actual experiment traces')
        if record.get('invariants_unchanged') is not True or not strings(record.get('checked_invariant_ids')) or not INVARIANTS.issubset(set(record.get('checked_invariant_ids', []))):
            fail('Protected invariants are not all checked and preserved')
        checks = record.get('checks', {})
        if not isinstance(checks, dict):
            checks = {}
        for key in CHECKS:
            check = checks.get(key, {})
            if not isinstance(check, dict) or check.get('status') != 'passed' or any(not nonempty(check.get(field)) for field in ('task', 'evidence_reference', 'result')):
                fail(f'{key} must pass with actual task, evidence and result')
                continue
            try:
                if any(check.get(field) != record.get(field) for field in ('base_commit', 'candidate_commit')):
                    raise ValueError(f'{key} check is bound to another candidate/base')
                evidence_path = check_artifact(root, check['evidence_reference'], check.get('evidence_sha256'))
                evidence = json.loads(evidence_path.read_text())
                if not isinstance(evidence, dict) or any(evidence.get(field) != record.get(field) for field in ('base_commit', 'candidate_commit')) or not nonempty(evidence.get('evaluator_id')) or evidence.get('result') != check['result']:
                    raise ValueError(f'{key} evidence must bind candidate/base, evaluator and result')
                if key == 'forward_test':
                    evaluator = check.get('evaluator_id')
                    if not nonempty(evaluator) or evaluator != evidence.get('evaluator_id') or evaluator in [record.get('proposer_id'), record.get('editor_id'), closeout.get('reviewer_id'), *authors]:
                        raise ValueError('Fresh forward-test evaluator must be independent of prior authors and reflection')
                    for field in ('task_artifacts', 'input_artifacts', 'produced_artifacts'):
                        artifacts = check.get(field)
                        if not isinstance(artifacts, list) or not artifacts or artifacts != evidence.get(field):
                            raise ValueError(f'forward_test needs matching {field}')
                        for artifact in artifacts:
                            if not isinstance(artifact, dict):
                                raise ValueError('Invalid forward-test artifact')
                            check_artifact(root, artifact.get('path'), artifact.get('sha256'))
                    baseline = check.get('baseline_comparison')
                    if not isinstance(baseline, dict) or baseline != evidence.get('baseline_comparison'):
                        raise ValueError('forward_test needs a baseline comparison')
                    check_artifact(root, baseline.get('path'), baseline.get('sha256'))
            except (OSError, ValueError, TypeError) as exc:
                fail(str(exc))
        peer = record.get('peer_assessment', {})
        if not isinstance(peer, dict) or peer.get('status') != 'approved' or not strings(peer.get('evidence_references'), allow_empty=False) or peer.get('unresolved_material_concerns') != [] or not nonempty(peer.get('justification')):
            fail('Independent peer approval is incomplete or has unresolved concerns')
        if not isinstance(record.get('discovery'), list) or not record.get('discovery'):
            fail('Existing-skill discovery must be recorded')
    if status == 'promoted':
        receipt = record.get('promotion_receipt', {})
        if not isinstance(receipt, dict) or receipt.get('repository') != 'JinhaPark/skills' or receipt.get('branch') != 'main' or receipt.get('previous_sha') != record.get('base_commit') or receipt.get('new_sha') != record.get('candidate_commit') or not nonempty(receipt.get('reference')):
            fail('Promotion needs an observed guarded main-branch update receipt')
    elif status not in ('rolled_back',) and record.get('promotion_receipt') is not None:
        fail('Unpromoted candidate cannot carry a promotion receipt')
    if status == 'rolled_back' and not COMMIT.fullmatch(str(record.get('rollback_commit', ''))):
        fail('Rollback requires an observed revert commit')
    return errors


def check_price_record(record, base_currency, label):
    errors = []
    if not isinstance(record, dict):
        return [f'recommendation: {label} must be a sourced price record']
    value, fx = record.get('value'), record.get('fx_to_base')
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        errors.append(f'recommendation: {label} needs a positive finite original price')
    if type(fx) not in (int, float) or not math.isfinite(fx) or fx <= 0:
        errors.append(f'recommendation: {label} needs a positive finite FX basis')
    try:
        stamp = datetime.fromisoformat(record.get('observed_at', '').replace('Z','+00:00'))
        if stamp.tzinfo is None:
            raise ValueError('No timezone')
    except (ValueError, TypeError, AttributeError):
        errors.append(f'recommendation: {label} needs timezone-aware observation time')
    if not nonempty(record.get('currency')) or not nonempty(record.get('share_basis')) or record.get('basis') not in ('split_adjusted_ex_dividend','total_return_index') or not strings(record.get('source_refs'), allow_empty=False):
        errors.append(f'recommendation: {label} needs currency/share/adjustment basis and source references')
    if record.get('currency') == base_currency:
        if fx != 1:
            errors.append(f'recommendation: {label} same-currency FX must equal 1')
    elif not strings(record.get('fx_source_refs'), allow_empty=False):
        errors.append(f'recommendation: {label} foreign FX needs sources')
    return errors


def validate_lifecycle(run_dir, phase='release'):
    root = Path(run_dir).resolve()
    manifest = read_record(root, 'manifest.json')
    errors = []
    if not nonempty(manifest.get('run_id')):
        errors.append('Missing manifest run ID')
    if not COMMIT.fullmatch(str(manifest.get('repository_commit', ''))):
        errors.append('Missing pinned repository commit')
    if phase == 'release':
        reflection = read_record(root, 'reviews/reflection-prepublish.json')
        errors.extend(check_reflection(root, reflection, manifest, 'prepublish'))
        # The reflection pins recommendation/report together. Content reconciliation
        # remains an actual reviewer responsibility, not a hash-based claim.
        recommendation = read_record(root, 'recommendation.json')
        if recommendation.get('schema_version') != 1 or not nonempty(recommendation.get('report_id')):
            errors.append('recommendation: Missing schema/report ID')
        if recommendation.get('frozen_report_sha256') != digest(local_file(root, 'report.md')):
            errors.append('recommendation: Frozen report hash differs from report.md')
        if recommendation.get('skill_commit') != manifest.get('repository_commit'):
            errors.append('recommendation: Skill commit differs from pinned manifest')
        if recommendation.get('publication_status') != 'ready' or recommendation.get('publication_at') is not None or recommendation.get('report_reference') is not None:
            errors.append('recommendation: Pre-delivery snapshot must remain ready without future receipt values')
        decision = recommendation.get('recommendation')
        if decision not in ('buy', 'watch', 'avoid', 'no_selection'):
            errors.append('recommendation: Invalid original decision')
        if (manifest.get('decision') == 'no_selection') != (decision == 'no_selection'):
            errors.append('recommendation: Decision contradicts research manifest')
        if decision in ('buy', 'watch', 'avoid'):
            horizon = recommendation.get('target_horizon', {})
            try:
                if not isinstance(horizon, dict):
                    raise ValueError('Missing horizon')
                date.fromisoformat(horizon.get('end_date', ''))
                if not nonempty(horizon.get('exchange_timezone')) or horizon.get('market_close_rule') != 'first_session_on_or_after':
                    raise ValueError('Missing horizon calendar convention')
            except (ValueError, TypeError):
                errors.append('recommendation: Stock judgment needs a frozen target horizon/calendar')
            if not nonempty(recommendation.get('entity_id')) or not nonempty(recommendation.get('base_currency')) or recommendation.get('original_snapshot_available') is not True:
                errors.append('recommendation: Stock judgment needs entity, base currency and original snapshot')
            unavailable = recommendation.get('unavailable_fields', [])
            if not isinstance(unavailable, list) or any(not isinstance(item, dict) or not nonempty(item.get('field')) or not nonempty(item.get('reason')) for item in unavailable):
                errors.append('recommendation: Unavailable fields need field/reason objects')
                unavailable = []
            missing_reasons = {item['field'] for item in unavailable}
            convention = recommendation.get('entry_convention')
            if convention not in ('publication_reference', 'next_executable_close'):
                errors.append('recommendation: Missing frozen entry convention')
            entry = recommendation.get('entry')
            if entry is None:
                if 'entry' not in missing_reasons:
                    errors.append('recommendation: Missing entry needs explicit reason')
                if convention == 'next_executable_close' and recommendation.get('entry_rule') != 'first_eligible_session_close':
                    errors.append('recommendation: Future entry needs a frozen executable rule')
            else:
                errors.extend(check_price_record(entry, recommendation.get('base_currency'), 'entry'))
            reference = recommendation.get('reference_entry')
            if convention == 'next_executable_close':
                if reference is None and 'reference_entry' not in missing_reasons:
                    errors.append('recommendation: Executable study needs original reference price or explicit unavailable reason')
                elif reference is not None:
                    errors.extend(check_price_record(reference, recommendation.get('base_currency'), 'reference_entry'))
            returns = recommendation.get('return_convention')
            if not isinstance(returns, dict) or any(not nonempty(returns.get(field)) for field in ('dividends','tax','fx','terminal_proceeds')):
                errors.append('recommendation: Missing original return conventions')
            for field in ('benchmark','expected_return','thesis_narrative','thesis_criteria'):
                value = recommendation.get(field)
                if value in (None, [], {}, '') and field not in missing_reasons:
                    errors.append(f'recommendation: Missing {field} needs explicit reason')
            criteria = recommendation.get('thesis_criteria')
            if not isinstance(criteria, list):
                errors.append('recommendation: thesis_criteria must be an array')
                criteria = []
            criterion_ids = set()
            for criterion in criteria:
                if not isinstance(criterion, dict):
                    errors.append('recommendation: Invalid thesis criterion')
                    continue
                identity = criterion.get('id')
                if not nonempty(identity) or identity in criterion_ids:
                    errors.append('recommendation: Thesis criterion IDs must be nonempty and unique')
                if nonempty(identity):
                    criterion_ids.add(identity)
                if any(not nonempty(criterion.get(field)) for field in ('metric_id','unit','currency')):
                    errors.append('recommendation: Thesis criterion needs metric, unit and currency')
                try:
                    date.fromisoformat(criterion.get('period_end', ''))
                except (ValueError, TypeError):
                    errors.append('recommendation: Thesis criterion needs a valid accounting-period end date')
                if criterion.get('trigger_operator') not in ('<','<=','>','>=','=='):
                    errors.append('recommendation: Unsupported thesis trigger operator')
                threshold = criterion.get('trigger_threshold')
                if type(threshold) not in (int, float) or not math.isfinite(threshold):
                    errors.append('recommendation: Thesis trigger threshold must be a finite number')
            if manifest.get('report_id') is not None and recommendation.get('report_id') != manifest['report_id']:
                errors.append('recommendation: Report ID differs from manifest')
    elif phase == 'closeout':
        closeout = read_record(root, 'reflection/closeout.json')
        errors.extend(check_reflection(root, closeout, manifest, 'closeout'))
        outcome = closeout.get('run_outcome')
        if outcome not in ('delivered', 'no_selection_delivered', 'blocked', 'interrupted', 'delivery_failed') or not nonempty(closeout.get('run_outcome_evidence_reference')):
            errors.append('closeout: Missing actual terminal outcome evidence')
        cache = closeout.get('cache_status', {})
        if not isinstance(cache, dict):
            cache = {}
        if cache.get('status') not in ('persisted', 'partial', 'failed', 'unavailable') or not strings(cache.get('receipt_references')) or not strings(cache.get('uncovered_artifacts')):
            errors.append('closeout: Invalid cache status')
        elif cache['status'] == 'persisted' and (not cache['receipt_references'] or cache['uncovered_artifacts']):
            errors.append('closeout: Persisted cache needs receipts and no uncovered artifacts')
        delivery = closeout.get('delivery_status', {})
        if not isinstance(delivery, dict):
            delivery = {}
        if delivery.get('status') not in ('delivered', 'failed', 'pending', 'unknown') or not strings(delivery.get('receipt_references')):
            errors.append('closeout: Invalid delivery status')
        elif delivery['status'] == 'delivered' and not delivery['receipt_references']:
            errors.append('closeout: Delivery needs actual receipt evidence')
        if outcome in ('delivered', 'no_selection_delivered') and delivery.get('status') != 'delivered':
            errors.append('closeout: Delivered outcome contradicts delivery status')
        if outcome in ('blocked', 'interrupted', 'delivery_failed') and delivery.get('status') == 'delivered':
            errors.append('closeout: Undelivered outcome contradicts delivery receipt')
        if not isinstance(closeout.get('backlog'), list) or not isinstance(closeout.get('next_run_handoff'), dict):
            errors.append('closeout: Missing backlog or next-run handoff')
        evolution = read_record(root, 'evolution/decision.json')
        errors.extend(check_evolution(root, evolution, manifest, closeout))
    else:
        raise ValueError('phase must be release or closeout')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_dir')
    parser.add_argument('--phase', choices=('release', 'closeout'), default='release')
    args = parser.parse_args()
    try:
        errors = validate_lifecycle(args.run_dir, args.phase)
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        errors = [f'Invalid lifecycle artifacts: {exc}']
    print(json.dumps({'passed': not errors, 'errors': errors}, ensure_ascii=False, indent=2))
    return bool(errors)


if __name__ == '__main__':
    raise SystemExit(main())
