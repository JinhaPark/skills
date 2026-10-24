#!/usr/bin/env python3
"""Assess sourced TP/SL/horizon observations without trades or inferred fill prices.

CLI: assess_barriers.py RECOMMENDATION.json OBSERVATIONS.json --as-of TIMESTAMP
Frozen record: take_profit/stop_loss={value,currency,na_reason}; barrier_basis=
{currency,price_basis:'split_adjusted_ex_dividend',share_basis}; target_horizon=
{end_date,exchange_timezone,reason}. Missing legacy fields stay explicitly unset.
Observations: activation={at,kind:hypothetical_entry|publication_reference,
currency,price_basis,share_basis,source_refs} or null; coverage={start_at,end_at,
complete,source_refs,gaps:[]}; optional previous_cutoff; bars=[{start_at,end_at,
high,low,currency,price_basis,share_basis,source_refs}]; optional horizon_session=
{for_date,close_at,source_refs}. Coverage is a supplied claim, not verified truth.
First events refer ONLY to the supplied interval; preserve earlier events outside
this helper. All prices/thresholds must already use one sourced split/share basis.
"""
import argparse
from datetime import date, datetime
import json
import math
from pathlib import Path
from zoneinfo import ZoneInfo

BASIS = 'split_adjusted_ex_dividend'


def stamp(value):
    if not isinstance(value, str):
        raise ValueError('timestamp must be a timezone-aware string')
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('timestamp needs a timezone')
    return result


def refs(record, label):
    values = record.get('source_refs')
    if not isinstance(values, list) or not values or any(not isinstance(x, str) or not x.strip() for x in values):
        raise ValueError(f'{label} needs source_refs')
    return values


def positive(value, label):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f'{label} must be a positive finite number')
    return value


def basis_valid(record):
    return isinstance(record, dict) and record.get('price_basis') == BASIS and all(isinstance(record.get(k), str) and record[k].strip() for k in ('currency', 'share_basis'))


def same_basis(item, frozen, label):
    if any(item.get(k) != frozen.get(k) for k in ('currency', 'price_basis', 'share_basis')):
        raise ValueError(f'{label} differs from the frozen price/currency/share basis')


def price_term(record, key):
    term = record.get(key)
    if term is None:
        return None, 'Not recorded in the original recommendation.'
    if not isinstance(term, dict):
        raise ValueError(f'{key} must be an object')
    if term.get('value') is None:
        if not isinstance(term.get('na_reason'), str) or not term['na_reason'].strip():
            raise ValueError(f'{key} N/A requires a reason')
        return None, term['na_reason']
    value = positive(term['value'], key)
    if not isinstance(term.get('currency'), str) or not term['currency'].strip():
        raise ValueError(f'{key} needs a currency')
    if term.get('na_reason') is not None:
        raise ValueError(f'{key} cannot have both a value and an N/A reason')
    return value, None


def side(status, reason, events=None):
    return {'status': status, 'reason': reason, 'events': events or []}


def assess(record, observations, as_of):
    cutoff = stamp(as_of)
    thresholds = {key: price_term(record, key) for key in ('take_profit', 'stop_loss')}
    if all(thresholds[k][0] is not None for k in thresholds) and thresholds['take_profit'][0] <= thresholds['stop_loss'][0]:
        raise ValueError('Long-study TP must exceed SL')
    frozen = record.get('barrier_basis')
    activation = observations.get('activation')
    active_at = None
    if activation is not None:
        if not isinstance(activation, dict) or activation.get('kind') not in ('hypothetical_entry', 'publication_reference'):
            raise ValueError('activation must identify hypothetical entry or publication reference')
        refs(activation, 'activation')
        active_at = stamp(activation.get('at'))
        if active_at > cutoff:
            raise ValueError('observed activation cannot follow the assessment cutoff')
        if basis_valid(frozen):
            same_basis(activation, frozen, 'activation')
    coverage = observations.get('coverage')
    start = end = None
    complete = False
    if coverage is not None:
        if not isinstance(coverage, dict) or type(coverage.get('complete')) is not bool or not isinstance(coverage.get('gaps'), list):
            raise ValueError('coverage requires complete boolean and gaps array')
        refs(coverage, 'coverage')
        start, end = stamp(coverage.get('start_at')), stamp(coverage.get('end_at'))
        if end < start or end > cutoff:
            raise ValueError('coverage must be ordered and not extend past cutoff')
        complete = coverage['complete'] and not coverage['gaps'] and end == cutoff
    previous = observations.get('previous_cutoff')
    if previous is not None:
        previous = stamp(previous)
        if previous > cutoff or (start is not None and start > previous):
            raise ValueError('incremental coverage must not skip the previous cutoff')
    interval_start = previous if previous is not None else start
    requested_start = max(x for x in (active_at, interval_start) if x is not None) if active_at is not None or interval_start is not None else None
    if requested_start is None or start is None or start > requested_start:
        complete = False
    full_history = bool(complete and active_at is not None and start <= active_at and (previous is None or previous <= active_at))
    result = {
        'schema_version': 1, 'report_id': record.get('report_id'), 'as_of': as_of,
        'monitoring_mode': activation['kind'] if activation else 'not_activated',
        'interpretation': 'Hypothetical/reference monitoring; no actual trade, execution price or return is inferred.',
        'requested_interval_start': requested_start.isoformat() if requested_start else None,
        'coverage_complete_for_interval': complete,
        'first_global_event_not_established': not full_history,
        'sides': {},
    }
    bars = observations.get('bars', [])
    if not isinstance(bars, list):
        raise ValueError('bars must be an array')
    parsed = []
    seen = set()
    for bar in bars:
        if not isinstance(bar, dict):
            raise ValueError('bar must be an object')
        refs(bar, 'bar')
        lo, hi = positive(bar.get('low'), 'bar low'), positive(bar.get('high'), 'bar high')
        a, b = stamp(bar.get('start_at')), stamp(bar.get('end_at'))
        if b < a or b > cutoff or lo > hi:
            raise ValueError('bar is unordered, future-dated or has invalid high/low')
        if (a, b) in seen:
            raise ValueError('duplicate bar interval')
        seen.add((a, b))
        if start is not None and (a < start or b > end):
            raise ValueError('bar lies outside declared coverage')
        if basis_valid(frozen):
            same_basis(bar, frozen, 'bar')
        elif bar.get('price_basis') != BASIS:
            raise ValueError('total-return or undefined price basis cannot monitor price barriers')
        parsed.append((a, b, bar))
    parsed.sort(key=lambda x: (x[0], x[1]))
    candidates = []
    for key, (threshold, unavailable) in thresholds.items():
        if threshold is None:
            result['sides'][key] = side('not_set', unavailable)
            continue
        if active_at is None:
            result['sides'][key] = side('pending', 'Entry/reference activation is not evidenced; pre-entry price touches do not count.')
            continue
        if not basis_valid(frozen):
            result['sides'][key] = side('unknown', 'Frozen price/currency/share basis is unavailable.')
            continue
        if record[key]['currency'] != frozen['currency']:
            raise ValueError(f'{key} currency differs from frozen barrier basis')
        events = []
        uncertain = []
        relevant = 0
        for a, b, bar in parsed:
            if b < active_at or (requested_start is not None and b < requested_start):
                continue
            relevant += 1
            touched = bar['high'] >= threshold if key == 'take_profit' else bar['low'] <= threshold
            if not touched:
                continue
            boundary = max(active_at, requested_start) if requested_start else active_at
            uncertain_touch = a < boundary <= b
            event = {'side': key, 'interval_start': a.isoformat(), 'interval_end': b.isoformat(),
                     'source_refs': bar['source_refs'], 'certainty': 'uncertain_boundary' if uncertain_touch else 'observed',
                     'reason': 'Bar overlaps activation/request boundary; touch order is unknown.' if uncertain_touch else 'Threshold touched within the supplied bar; exact time and fill price are unknown.'}
            (uncertain if uncertain_touch else events).append(event)
            candidates.append((a, b, event))
        if events:
            result['sides'][key] = side('triggered', 'At least one post-activation threshold touch is evidenced; this is not an execution.', events + uncertain)
        elif uncertain:
            result['sides'][key] = side('unknown', 'Only a boundary-overlapping bar touches the threshold.', uncertain)
        elif complete and relevant:
            result['sides'][key] = side('not_observed', 'No touch observed in the supplied complete interval; retain earlier event history separately.')
        else:
            result['sides'][key] = side('unknown', 'Price coverage is incomplete or contains no usable post-activation bars.')
    horizon = record.get('target_horizon') or {}
    if not isinstance(horizon, dict):
        raise ValueError('target_horizon must be an object')
    horizon_date = horizon.get('end_date')
    if horizon_date is None:
        result['sides']['horizon'] = side('not_set', horizon.get('reason') or 'Original horizon was not recorded.')
    else:
        target_date = date.fromisoformat(horizon_date)
        zone = ZoneInfo(horizon['exchange_timezone']) if horizon.get('exchange_timezone') else cutoff.tzinfo
        session = observations.get('horizon_session')
        if session is None:
            status = 'pending' if cutoff.astimezone(zone).date() < target_date else 'unknown'
            result['sides']['horizon'] = side(status, 'Exact first eligible horizon close has not been evidenced.')
        else:
            refs(session, 'horizon session')
            close = stamp(session.get('close_at'))
            if session.get('for_date') != horizon_date or close.astimezone(zone).date() < target_date:
                raise ValueError('horizon session does not map to the original horizon')
            if close > cutoff:
                result['sides']['horizon'] = side('pending', 'Original horizon session has not closed.')
            else:
                event = {'side': 'horizon', 'interval_start': close.isoformat(), 'interval_end': close.isoformat(),
                         'source_refs': session['source_refs'], 'certainty': 'observed',
                         'reason': 'Original horizon endpoint reached; no holding return or exit is inferred.'}
                result['sides']['horizon'] = side('triggered', event['reason'], [event])
                if requested_start is None or close >= requested_start:
                    candidates.append((close, close, event))
    unresolved_price = any(result['sides'][k]['status'] in ('unknown', 'pending') for k in thresholds)
    # An already-due horizon with no verified session may precede any price hit.
    # A genuinely future/pending horizon cannot be an earlier exit at this cutoff.
    unresolved_horizon = result['sides']['horizon']['status'] == 'unknown'
    candidates.sort(key=lambda x: (x[0], x[1], x[2]['side']))
    if not candidates:
        result['first_event'] = {'status': 'unknown' if unresolved_price or unresolved_horizon or not complete else 'none_observed',
                                 'scope': 'provided_interval_only', 'possible_sides': ['horizon'] if unresolved_horizon else [],
                                 'reason': 'No first event established outside the supplied evidence interval.'}
    else:
        first_start, first_end, first = candidates[0]
        overlapping = [x for x in candidates if x[0] <= first_end and x[1] >= first_start]
        possible = sorted({x[2]['side'] for x in overlapping} | ({'horizon'} if unresolved_horizon else set()))
        ambiguous = len(possible) > 1 or any(x[2]['certainty'] != 'observed' for x in overlapping) or not complete or unresolved_price or unresolved_horizon
        result['first_event'] = {'status': 'ambiguous' if ambiguous else 'observed', 'scope': 'provided_interval_only',
                                 'possible_sides': possible, 'interval_start': None if unresolved_horizon else first_start.isoformat(),
                                 'interval_end': None if unresolved_horizon else max(x[1] for x in overlapping).isoformat(),
                                 'reason': 'Bar order, boundary overlap, missing coverage or an unverified due horizon prevents first-exit certainty.' if ambiguous else 'Earliest evidenced event in this interval only; no fill is inferred.'}
    result['first_global_event_not_established'] = not (full_history and result['first_event']['status'] in ('observed', 'none_observed'))
    result['assessment_required'] = any(s['status'] == 'triggered' for s in result['sides'].values()) or result['first_event']['status'] == 'ambiguous' or unresolved_horizon
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('recommendation', type=Path)
    parser.add_argument('observations', type=Path)
    parser.add_argument('--as-of', required=True)
    args = parser.parse_args()
    try:
        result = assess(json.loads(args.recommendation.read_text()), json.loads(args.observations.read_text()), args.as_of)
    except (ValueError, TypeError, KeyError, OSError) as error:
        parser.exit(1, f'barrier assessment error: {error}\n')
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
