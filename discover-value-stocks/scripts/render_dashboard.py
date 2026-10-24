#!/usr/bin/env python3
"""Render a public recommendation dashboard without changing frozen commitments.

This utility validates supplied records, not market evidence, trade execution or
external publication. Preserve private source artifacts outside the public JSON.
"""
import argparse
import copy
from datetime import date, datetime, timezone
from decimal import Decimal
import html
import json
import math
from pathlib import Path
import re
from urllib.parse import urlsplit

START = '<!-- cashflow-dashboard:start -->'
END = '<!-- cashflow-dashboard:end -->'
EVENTS = {'none', 'tp', 'sl', 'period_end', 'tp_sl_ambiguous', 'not_assessable'}
MUTABLE = {'status', 'assessments'}
PRICE_FIELDS = ('target_entry', 'take_profit', 'stop_loss')
REQUIRED_ROW = {'publication_key', 'date', 'company', 'ticker', 'thesis', 'thesis_na_reason', 'thesis_source', 'cover_sha256', 'origin', 'report_url', *PRICE_FIELDS, 'horizon', 'status', 'assessments'}


def text(value, label, nullable=False):
    if nullable and value is None:
        return value
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{label} must be nonempty text')
    return value


def iso_date(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError('Dates must be YYYY-MM-DD')
    return date.fromisoformat(value)


def timestamp(value):
    text(value, 'timestamp')
    parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('Timestamps must include a timezone')
    return parsed.astimezone(timezone.utc)


def url(value):
    text(value, 'URL')
    if any(ch.isspace() or ord(ch) < 32 or ch in '<>\\"|' for ch in value):
        raise ValueError('Unsafe URL characters')
    parsed = urlsplit(value)
    if parsed.scheme not in ('https', 'http') or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Only public HTTP(S) URL shapes without credentials are allowed')
    return value


def price(value, label):
    if not isinstance(value, dict) or set(value) != {'value', 'currency', 'na_reason'}:
        raise ValueError(f'{label} needs value, currency and na_reason')
    amount = value['value']
    if value['currency'] is not None and (not isinstance(value['currency'], str) or not re.fullmatch(r'[A-Z]{3}', value['currency'])):
        raise ValueError(f'{label} needs a three-letter currency code')
    if amount is None:
        text(value['na_reason'], f'{label} N/A reason')
    else:
        if type(amount) not in (int, float) or not math.isfinite(amount) or amount <= 0:
            raise ValueError(f'{label} must be finite and positive')
        if value['currency'] is None or value['na_reason'] is not None:
            raise ValueError(f'{label} needs currency and a null N/A reason')


def validate_row(row, updated_at):
    if not isinstance(row, dict) or not REQUIRED_ROW.issubset(row) or set(row) - (REQUIRED_ROW | {'revision_of'}):
        raise ValueError('Incomplete dashboard row')
    for field in ('publication_key', 'company', 'ticker', 'origin', 'status'):
        text(row[field], field)
    published = iso_date(row['date'])
    if published > updated_at.date():
        raise ValueError('Publication date follows dashboard update')
    if row['thesis'] is None:
        text(row['thesis_na_reason'], 'Thesis N/A reason')
        if row['thesis_source'] is not None or row['cover_sha256'] is not None:
            raise ValueError('Missing cover thesis needs null source and hash')
    else:
        text(row['thesis'], 'thesis')
        if len(row['thesis'].split()) > 50:
            raise ValueError('Cover-letter thesis summary must not exceed 50 words')
        if row['thesis_source'] != 'published_cover_letter' or not isinstance(row['cover_sha256'], str) or not re.fullmatch(r'[0-9a-f]{64}', row['cover_sha256']):
            raise ValueError('Thesis must identify the published cover letter and its SHA-256')
        if row['thesis_na_reason'] is not None:
            raise ValueError('Available thesis cannot have an N/A reason')
    if row['report_url'] is not None:
        url(row['report_url'])
    for field in PRICE_FIELDS:
        price(row[field], field)
    period = row['horizon']
    if not isinstance(period, dict) or set(period) != {'end_date', 'duration', 'na_reason'}:
        raise ValueError('Investment period needs end_date, duration and na_reason')
    if period['end_date'] is not None:
        if iso_date(period['end_date']) < published:
            raise ValueError('Investment period ends before publication')
    if period['duration'] is not None:
        text(period['duration'], 'Investment duration')
    if period['end_date'] is None:
        text(period['na_reason'], 'Investment period end-date N/A reason')
    elif period['na_reason'] is not None:
        raise ValueError('Known period end cannot have an N/A reason')
    if row.get('revision_of') is not None:
        text(row['revision_of'], 'revision_of')
        if row['revision_of'] == row['publication_key']:
            raise ValueError('A revision cannot refer to itself')
    assessments = row['assessments']
    if not isinstance(assessments, list):
        raise ValueError('assessments must be an array')
    last = None
    seen = set()
    for assessment in assessments:
        if not isinstance(assessment, dict) or set(assessment) != {'assessed_at', 'event', 'event_at', 'summary', 'source_urls'}:
            raise ValueError('Assessment needs assessed_at, event, event_at, summary and source_urls')
        assessed = timestamp(assessment['assessed_at'])
        if assessed > updated_at or assessed.date() < published:
            raise ValueError('Assessment time outside the published history')
        if last is not None and assessed < last:
            raise ValueError('Assessments must be appended chronologically')
        last = assessed
        identity = (assessment['assessed_at'], assessment['event'], assessment['event_at'])
        if identity in seen:
            raise ValueError('Duplicate assessment event')
        seen.add(identity)
        text(assessment['summary'], 'assessment summary')
        if len(assessment['summary'].split()) > 45:
            raise ValueError('Assessment summary must not exceed 45 words')
        event = assessment['event']
        if event not in EVENTS:
            raise ValueError('Unsupported assessment event')
        if not isinstance(assessment['source_urls'], list):
            raise ValueError('source_urls must be an array')
        for source in assessment['source_urls']:
            url(source)
        event_at = assessment['event_at']
        if event in ('none', 'not_assessable'):
            if event_at is not None:
                raise ValueError('No confirmed event must have a null event_at')
        else:
            observed = timestamp(event_at)
            if observed > assessed or observed.date() < published:
                raise ValueError('Event time outside the observation window')
            if not assessment['source_urls']:
                raise ValueError('Confirmed barrier events require public evidence links')
            if event in ('tp', 'tp_sl_ambiguous') and row['take_profit']['value'] is None:
                raise ValueError('Cannot reach an unspecified TP')
            if event in ('sl', 'tp_sl_ambiguous') and row['stop_loss']['value'] is None:
                raise ValueError('Cannot reach an unspecified SL')
            if event == 'period_end' and (period['end_date'] is None or observed.date() < iso_date(period['end_date'])):
                raise ValueError('Cannot mature before a specified investment endpoint')


def validate(data):
    if not isinstance(data, dict) or set(data) != {'schema_version', 'updated_at', 'rows'} or type(data.get('schema_version')) is not int or data.get('schema_version') != 1 or not isinstance(data.get('rows'), list):
        raise ValueError('Expected dashboard schema version 1 with rows')
    updated = timestamp(data.get('updated_at'))
    seen = set()
    for row in data['rows']:
        validate_row(row, updated)
        if row['publication_key'] in seen:
            raise ValueError('Duplicate publication_key')
        seen.add(row['publication_key'])
    lookup = {row['publication_key']: row for row in data['rows']}
    for row in data['rows']:
        parent = row.get('revision_of')
        if parent is not None:
            if parent not in lookup or iso_date(lookup[parent]['date']) > iso_date(row['date']):
                raise ValueError('Revision must reference an existing earlier publication')
            chain = {row['publication_key']}
            while parent is not None:
                if parent in chain:
                    raise ValueError('Revision links cannot contain cycles')
                chain.add(parent)
                parent = lookup[parent].get('revision_of')
    return data


def upsert(data, row, updated_at):
    """Append a vintage or assessments; never rewrite original commitments."""
    validate(data)
    if timestamp(updated_at) < timestamp(data['updated_at']):
        raise ValueError('Dashboard update cannot move backward')
    result = copy.deepcopy(data)
    result['updated_at'] = updated_at
    index = next((i for i, prior in enumerate(result['rows']) if prior['publication_key'] == row.get('publication_key')), None)
    if index is None:
        result['rows'].append(copy.deepcopy(row))
    else:
        prior = result['rows'][index]
        old_frozen = {key: val for key, val in prior.items() if key not in MUTABLE}
        new_frozen = {key: val for key, val in row.items() if key not in MUTABLE}
        if old_frozen != new_frozen:
            raise ValueError('Original commitments are immutable; append a new revision vintage')
        previous = prior['assessments']
        current = row.get('assessments')
        if not isinstance(current, list) or current[:len(previous)] != previous:
            raise ValueError('Assessment history is append-only')
        result['rows'][index] = copy.deepcopy(row)
    return validate(result)


def cell(value):
    value = ' '.join(str(value).split())
    value = html.escape(value, quote=False)
    return re.sub(r'([\\|`*_[\]])', r'\\\1', value)


def price_cell(record):
    if record['value'] is None:
        return f"N/A ({cell(record['na_reason'])})"
    amount = format(Decimal(str(record['value'])), ",f")
    if "." in amount:
        amount = amount.rstrip("0").rstrip(".")
    return f"{record['currency']} {amount}"


def week_key(row):
    calendar = iso_date(row['date']).isocalendar()
    return calendar.year, calendar.week


def paragraph(row, archived_count):
    thesis = cell(row['thesis']).rstrip('.') if row['thesis'] is not None else 'N/A (original cover letter unavailable)'
    company = f"{cell(row['company'])} ({cell(row['ticker'])})"
    if row['report_url']:
        company = f"[{company}](<{row['report_url']}>)"
    prices = [price_cell(row[field]) if row[field]['value'] is not None else 'N/A' for field in PRICE_FIELDS]
    horizon = row['horizon']
    duration = cell(horizon['duration']) + ', ' if horizon['duration'] else ''
    window = duration + ('ends ' + horizon['end_date'] if horizon['end_date'] else 'N/A (end date unspecified)')
    if horizon['duration'] is None and horizon['end_date'] is None:
        window = 'N/A'
    status = cell(row['status']).rstrip('.')
    observed = {}
    labels = {'tp': 'TP', 'sl': 'SL', 'period_end': 'Horizon', 'tp_sl_ambiguous': 'TP/SL order uncertain'}
    for assessment in row['assessments']:
        event = assessment['event']
        if event in labels and (event not in observed or timestamp(assessment['event_at']) < timestamp(observed[event])):
            observed[event] = assessment['event_at']
    if observed:
        status += '; ' + '; '.join(f"{labels[event]} observed by {cell(when)}" for event, when in sorted(observed.items(), key=lambda item: timestamp(item[1])))
    latest = row['assessments'][-1] if row['assessments'] else None
    evaluation = f"{cell(latest['assessed_at'])}: {cell(latest['summary']).rstrip('.')}" if latest else 'N/A (not assessed yet)'
    year, week = week_key(row)
    result = (f"**{row['date']} — {company}** ({year}-W{week:02d}). "
              f"Investment thesis (cover letter): {thesis}. "
              f"Target entry: {prices[0]}; TP: {prices[1]}; SL: {prices[2]}; Horizon: {window}. "
              f"Status: {status}. Evaluation: {evaluation}. ")
    if archived_count:
        result += f"{archived_count} earlier same-week vintage(s) retained in the archive. "
    result += '[Full record](cashflow-dashboard.json).'
    if len(result.split()) > 160:
        raise ValueError(f"Weekly paragraph exceeds 160 words for {row['publication_key']}; shorten the supplied summaries without automatic truncation")
    return result


def render(data):
    validate(data)
    groups = {}
    for row in sorted(data['rows'], key=lambda item: (item['date'], item['publication_key']), reverse=True):
        groups.setdefault(week_key(row), []).append(row)
    lines = [START, '## Cash flow investment dashboard', '',
             'Latest 12 publication weeks; one paragraph per week. TP, SL and Horizon are separate review conditions. N/A reasons and all vintages remain in the archive. Checks occur during scheduled runs, not continuously; records do not imply executed trades.', '']
    for week in sorted(groups, reverse=True)[:12]:
        rows = groups[week]
        lines.extend([paragraph(rows[0], len(rows) - 1), ''])
    if not groups:
        lines.extend(['No confirmed publications are available.', ''])
    lines.append(END)
    return '\n'.join(lines)


def replace_block(readme, dashboard):
    starts, ends = readme.count(START), readme.count(END)
    if starts == ends == 0:
        return readme + ('\n\n' if readme and not readme.endswith('\n') else '\n' if readme else '') + dashboard + '\n'
    if starts != 1 or ends != 1 or readme.index(START) > readme.index(END):
        raise ValueError('README dashboard markers are malformed or duplicated')
    begin = readme.index(START)
    finish = readme.index(END) + len(END)
    return readme[:begin] + dashboard + readme[finish:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('data', type=Path)
    parser.add_argument('readme', type=Path)
    parser.add_argument('--check', action='store_true', help='Exit nonzero if README differs from the supplied data')
    parser.add_argument('--upsert', type=Path, help='Append a row or append-only assessment update before rendering')
    parser.add_argument('--updated-at', help='Timezone-aware update timestamp required with --upsert')
    args = parser.parse_args()
    try:
        data = json.loads(args.data.read_text())
        if args.upsert:
            if not args.updated_at:
                raise ValueError('--upsert requires --updated-at')
            data = upsert(data, json.loads(args.upsert.read_text()), args.updated_at)
        elif args.updated_at:
            raise ValueError('--updated-at is only valid with --upsert')
        original = args.readme.read_text() if args.readme.exists() else ''
        updated = replace_block(original, render(data))
        if args.check:
            if args.upsert:
                raise ValueError('--check cannot be combined with --upsert')
            if updated != original:
                raise ValueError('README dashboard differs from current data')
        else:
            if args.upsert:
                args.data.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
            args.readme.write_text(updated)
    except (ValueError, TypeError, KeyError, OSError) as exc:
        parser.exit(1, f'dashboard error: {exc}\n')


if __name__ == '__main__':
    main()
