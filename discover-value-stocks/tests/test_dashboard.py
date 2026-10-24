import copy
from datetime import date, timedelta
import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location('render_dashboard', Path(__file__).parents[1] / 'scripts/render_dashboard.py')
dash = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dash)


def level(value=None):
    return {'value': value, 'currency': 'USD' if value is not None else None, 'na_reason': 'Not specified in the original report' if value is None else None}


def row(key='one', published='2026-10-24'):
    return {'publication_key': key, 'date': published, 'company': 'Example Corp', 'ticker': 'EXM', 'thesis': 'Durable cash conversion', 'thesis_na_reason': None, 'thesis_source': 'published_cover_letter', 'cover_sha256': 'a' * 64, 'origin': 'delivered_report', 'report_url': None, 'target_entry': level(100), 'take_profit': level(140), 'stop_loss': level(80), 'horizon': {'end_date': '2027-10-24', 'duration': '12 months', 'na_reason': None}, 'status': 'Monitoring', 'assessments': []}


def assessment(event='none', event_at=None):
    return {'assessed_at': '2026-11-02T00:00:00Z', 'event': event, 'event_at': event_at, 'summary': 'Thesis reviewed against original drivers', 'source_urls': ['https://example.com/filing']}


class DashboardTests(unittest.TestCase):
    def setUp(self):
        self.data = {'schema_version': 1, 'updated_at': '2026-11-03T00:00:00Z', 'rows': [row()]}

    def test_descending_dates_and_stable_ties(self):
        self.data['rows'] = [row('a', '2026-10-10'), row('b', '2026-10-24'), row('c', '2026-10-17')]
        output = dash.render(self.data)
        self.assertLess(output.index('**2026-10-24'), output.index('**2026-10-17'))
        self.assertLess(output.index('**2026-10-17'), output.index('**2026-10-10'))

    def test_all_three_exits_remain_visible_when_unavailable(self):
        item = self.data['rows'][0]
        item['take_profit'] = level()
        item['stop_loss'] = level()
        item['horizon'] = {'end_date': None, 'duration': None, 'na_reason': 'Original horizon unavailable'}
        output = dash.render(self.data)
        self.assertIn('TP: N/A; SL: N/A; Horizon: N/A.', output)
        self.assertNotIn('|---', output)
        self.assertEqual(item['horizon']['na_reason'], 'Original horizon unavailable')

    def test_incomplete_na_reason_and_nonfinite_price_rejected(self):
        for amount in (float('nan'), float('inf'), True, -1, 0):
            data = copy.deepcopy(self.data)
            data['rows'][0]['take_profit']['value'] = amount
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                dash.validate(data)
        self.data['rows'][0]['take_profit'] = {'value': None, 'currency': None, 'na_reason': None}
        with self.assertRaises(ValueError):
            dash.validate(self.data)

    def test_escapes_untrusted_table_text(self):
        self.data['rows'][0]['thesis'] = 'Cash | value\n<script>x</script> [fake](javascript:x)'
        output = dash.render(self.data)
        self.assertIn('Cash \\| value &lt;script&gt;', output)
        self.assertNotIn('<script>', output)
        self.assertIn('\\[fake\\]', output)
        self.assertEqual(len([line for line in output.splitlines() if line.startswith('**2026')]), 1)

    def test_unsafe_report_and_source_links_rejected(self):
        for bad in ('javascript:alert(1)', 'file:///secret', 'https://user:secret@example.com', 'https://example.com/\nsecret', 'https://example.com/<x>', 'https://example.com/a|b'):
            data = copy.deepcopy(self.data)
            data['rows'][0]['report_url'] = bad
            with self.subTest(url=bad), self.assertRaises(ValueError):
                dash.validate(data)
        self.data['rows'][0]['assessments'] = [assessment()]
        self.data['rows'][0]['assessments'][0]['source_urls'] = ['data:text/plain,hi']
        with self.assertRaises(ValueError):
            dash.validate(self.data)

    def test_idempotent_marker_replacement_preserves_other_readme(self):
        report = dash.render(self.data)
        original = '# Other skills\n\nKeep this exact text.\n' + dash.START + '\nold\n' + dash.END + '\n\n## Footer\nuntouched\n'
        result = dash.replace_block(original, report)
        self.assertTrue(result.startswith('# Other skills\n\nKeep this exact text.\n'))
        self.assertTrue(result.endswith('\n\n## Footer\nuntouched\n'))
        self.assertEqual(dash.replace_block(result, report), result)
        self.assertEqual(dash.replace_block('', report), report + '\n')

    def test_duplicate_or_broken_markers_rejected(self):
        for readme in (dash.START, dash.END, dash.END + dash.START, dash.START + dash.START + dash.END, dash.START + dash.END + dash.END):
            with self.subTest(readme=readme), self.assertRaises(ValueError):
                dash.replace_block(readme, 'new')

    def test_duplicate_keys_and_bad_dates_rejected(self):
        self.data['rows'].append(copy.deepcopy(self.data['rows'][0]))
        with self.assertRaises(ValueError):
            dash.validate(self.data)
        self.data['rows'].pop()
        self.data['rows'][0]['date'] = '2026-02-30'
        with self.assertRaises(ValueError):
            dash.validate(self.data)

    def test_event_times_must_be_after_publication_and_not_future(self):
        for event_at in ('2026-10-23T12:00:00Z', '2026-11-04T12:00:00Z'):
            self.data['rows'][0]['assessments'] = [assessment('tp', event_at)]
            with self.subTest(event_at=event_at), self.assertRaises(ValueError):
                dash.validate(self.data)
        self.data['rows'][0]['assessments'] = [assessment('tp', '2026-10-30T12:00:00Z')]
        self.assertIs(dash.validate(self.data), self.data)

    def test_missing_barrier_cannot_be_reported_as_reached(self):
        item = self.data['rows'][0]
        item['take_profit'] = level()
        item['assessments'] = [assessment('tp', '2026-10-30T12:00:00Z')]
        with self.assertRaises(ValueError):
            dash.validate(self.data)
        item['assessments'] = [assessment('tp_sl_ambiguous', '2026-10-30T12:00:00Z')]
        with self.assertRaises(ValueError):
            dash.validate(self.data)

    def test_early_period_end_rejected(self):
        self.data['rows'][0]['assessments'] = [assessment('period_end', '2026-10-30T12:00:00Z')]
        with self.assertRaises(ValueError):
            dash.validate(self.data)

    def test_original_commitments_cannot_change_during_upsert(self):
        changed = copy.deepcopy(self.data['rows'][0])
        changed['take_profit']['value'] = 200
        with self.assertRaises(ValueError):
            dash.upsert(self.data, changed, '2026-11-04T00:00:00Z')

    def test_assessment_append_is_idempotent_and_prior_record_immutable(self):
        changed = copy.deepcopy(self.data['rows'][0])
        changed['assessments'].append(assessment())
        changed['status'] = 'Reviewed'
        first = dash.upsert(self.data, changed, '2026-11-04T00:00:00Z')
        second = dash.upsert(first, changed, '2026-11-04T00:00:00Z')
        self.assertEqual(first, second)
        self.assertEqual(self.data['rows'][0]['assessments'], [])
        changed['assessments'][0]['summary'] = 'Rewritten history'
        with self.assertRaises(ValueError):
            dash.upsert(first, changed, '2026-11-05T00:00:00Z')

    def test_correction_is_new_linked_vintage(self):
        correction = row('corrected', '2026-10-26')
        correction['revision_of'] = 'one'
        correction['take_profit']['value'] = 135
        result = dash.upsert(self.data, correction, '2026-11-04T00:00:00Z')
        self.assertEqual(len(result['rows']), 2)
        self.assertEqual(result['rows'][0]['take_profit']['value'], 140)

    def test_unknown_and_cyclic_revisions_rejected(self):
        self.data['rows'][0]['revision_of'] = 'unknown'
        with self.assertRaises(ValueError):
            dash.validate(self.data)
        second = row('two')
        second['revision_of'] = 'one'
        self.data['rows'][0]['revision_of'] = 'two'
        self.data['rows'].append(second)
        with self.assertRaises(ValueError):
            dash.validate(self.data)

    def test_later_review_preserves_earlier_reached_event_in_display(self):
        first = assessment('tp', '2026-10-30T12:00:00Z')
        first['assessed_at'] = '2026-10-31T00:00:00Z'
        later = assessment()
        self.data['rows'][0]['assessments'] = [first, later]
        output = dash.render(self.data)
        self.assertIn('TP observed by 2026-10-30T12:00:00Z', output)
        self.assertIn('2026-11-02T00:00:00Z: Thesis reviewed', output)

    def test_unknown_private_fields_are_not_public_schema(self):
        self.data['rows'][0]['internal_cache_reference'] = 'private-state'
        with self.assertRaises(ValueError):
            dash.validate(self.data)

    def test_one_paragraph_per_iso_week_keeps_full_json(self):
        self.data['rows'] = [row('early', '2026-10-20'), row('late', '2026-10-24')]
        output = dash.render(self.data)
        paragraphs = [part for part in output.split('\n\n') if part.startswith('**')]
        self.assertEqual(len(paragraphs), 1)
        self.assertTrue(paragraphs[0].startswith('**2026-10-24'))
        self.assertIn('1 earlier same-week vintage(s)', paragraphs[0])
        self.assertIn('[Full record](cashflow-dashboard.json)', paragraphs[0])
        self.assertEqual(len(self.data['rows']), 2)

    def test_only_latest_twelve_publication_weeks_displayed(self):
        first = date(2026, 7, 4)
        self.data['rows'] = [row(str(i), (first + timedelta(weeks=i)).isoformat()) for i in range(17)]
        output = dash.render(self.data)
        paragraphs = [part for part in output.split('\n\n') if part.startswith('**')]
        self.assertEqual(len(paragraphs), 12)
        self.assertTrue(paragraphs[0].startswith('**2026-10-24'))
        self.assertNotIn('**2026-07-04', output)
        self.assertEqual(len(self.data['rows']), 17)

    def test_iso_year_boundary_groups_same_week(self):
        self.data['updated_at'] = '2027-01-09T00:00:00Z'
        self.data['rows'] = [row('year-end', '2026-12-31'), row('new-year', '2027-01-01'), row('next-week', '2027-01-08')]
        output = dash.render(self.data)
        paragraphs = [part for part in output.split('\n\n') if part.startswith('**')]
        self.assertEqual(len(paragraphs), 2)
        self.assertIn('(2026-W53)', paragraphs[1])
        self.assertTrue(paragraphs[1].startswith('**2027-01-01'))

    def test_assessment_update_does_not_add_weekly_paragraph(self):
        original = dash.render(self.data)
        updated_row = copy.deepcopy(self.data['rows'][0])
        updated_row['assessments'] = [assessment()]
        updated = dash.render(dash.upsert(self.data, updated_row, '2026-11-04T00:00:00Z'))
        self.assertEqual(sum(part.startswith('**') for part in original.split('\n\n')), 1)
        self.assertEqual(sum(part.startswith('**') for part in updated.split('\n\n')), 1)
        self.assertIn('Thesis reviewed against original drivers', updated)

    def test_cover_letter_provenance_required_and_legacy_not_fabricated(self):
        item = self.data['rows'][0]
        item['cover_sha256'] = None
        with self.assertRaises(ValueError):
            dash.validate(self.data)
        item.update(thesis=None, thesis_source=None, cover_sha256=None, thesis_na_reason='Original report unavailable')
        output = dash.render(self.data)
        self.assertIn('Investment thesis (cover letter): N/A', output)
        self.assertNotIn('Durable cash conversion', output)

    def test_word_limits_reject_instead_of_silently_truncating(self):
        item = self.data['rows'][0]
        item['thesis'] = ' '.join(['word'] * 51)
        with self.assertRaises(ValueError):
            dash.validate(self.data)
        item['thesis'] = ' '.join(['word'] * 50)
        item['assessments'] = [assessment()]
        item['assessments'][0]['summary'] = ' '.join(['review'] * 46)
        with self.assertRaises(ValueError):
            dash.validate(self.data)
        item['assessments'][0]['summary'] = ' '.join(['review'] * 45)
        item['status'] = ' '.join(['status'] * 40)
        with self.assertRaisesRegex(ValueError, '160 words'):
            dash.render(self.data)
        self.assertEqual(len(item['thesis'].split()), 50)
        self.assertEqual(len(item['assessments'][0]['summary'].split()), 45)

    def test_prices_do_not_gain_false_decimal_precision(self):
        output = dash.render(self.data)
        self.assertIn('Target entry: USD 100; TP: USD 140; SL: USD 80;', output)
        self.assertNotIn('100.0000', output)
        self.data['rows'][0]['target_entry']['value'] = 0.00001
        self.assertIn('Target entry: USD 0.00001;', dash.render(self.data))

    def test_backward_update_or_assessment_order_rejected(self):
        with self.assertRaises(ValueError):
            dash.upsert(self.data, row(), '2026-11-01T00:00:00Z')
        first = assessment()
        second = assessment()
        second['assessed_at'] = '2026-11-01T00:00:00Z'
        self.data['rows'][0]['assessments'] = [first, second]
        with self.assertRaises(ValueError):
            dash.validate(self.data)


if __name__ == '__main__':
    unittest.main()
