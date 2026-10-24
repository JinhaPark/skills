import copy
import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location("assess_recommendation", Path(__file__).parents[1] / "scripts" / "assess_recommendation.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def price(value, date, basis="split_adjusted_ex_dividend"):
    return {"value": value, "observed_at": date + "T16:00:00-04:00", "currency": "USD",
            "basis": basis, "share_basis": "entry-share", "fx_to_base": 1,
            "source_refs": ["source:exchange-close"]}


def dividends(start, end, cash=2):
    return {"base_cash_per_entry_share": cash, "base_currency": "USD", "share_basis": "entry-share",
            "period_start": start["observed_at"], "period_end": end["observed_at"], "source_refs": ["source:dividends"]}


def fixture():
    entry = price(100, "2026-10-24")
    endpoint = price(110, "2027-10-24")
    record = {"report_id": "report-1", "original_snapshot_available": True,
              "publication_status": "delivered", "publication_at": "2026-10-24T15:00:00-04:00",
              "recommendation": "buy", "entry_convention": "next_executable_close", "base_currency": "USD",
              "entry_rule": "first_eligible_session_close",
              "entry_session": {"for_publication_at": "2026-10-24T15:00:00-04:00", "close_at": entry["observed_at"], "source_refs": ["synthetic:calendar"]},
              "entry": entry, "target_horizon": {"end_date": "2027-10-24", "exchange_timezone": "America/New_York", "market_close_rule": "first_session_on_or_after"},
              "thesis_criteria": [{"id": "margin", "metric_id": "operating-margin", "period_end": "2027-06-30",
                                   "unit": "ratio", "currency": None, "trigger_operator": "<", "trigger_threshold": .1}]}
    observations = {"endpoint": endpoint, "dividends": dividends(entry, endpoint),
                    "horizon_session": {"for_date": "2027-10-24", "close_at": endpoint["observed_at"], "source_refs": ["synthetic:calendar"]},
                    "thesis": {"margin": {"metric_id": "operating-margin", "period_end": "2027-06-30", "unit": "ratio", "currency": None,
                                           "value": .08, "available_at": "2027-07-31T00:00:00Z", "source_refs": ["source:filing"]}}}
    return record, observations


class AssessmentTests(unittest.TestCase):
    def test_missing_horizon_keeps_thesis_without_invented_return(self):
        record, observations = fixture()
        record['target_horizon']={'end_date':None,'reason':'No original investment period was specified.'}
        before=copy.deepcopy(record)
        result=MODULE.assess(record, observations, '2027-10-25T00:00:00Z')
        self.assertEqual(result['status'],'horizon_unavailable')
        self.assertIsNone(result['target_horizon_end'])
        self.assertIsNone(result['returns'])
        self.assertEqual(result['thesis_checks'][0]['status'],'falsification_triggered')
        self.assertEqual(record,before)

    def test_older_missing_horizon_is_na_not_rewritten(self):
        record, observations = fixture()
        record.pop('target_horizon')
        result=MODULE.assess(record, observations, '2027-10-25T00:00:00Z')
        self.assertEqual(result['status'],'horizon_unavailable')
        self.assertNotIn('target_horizon',record)
        self.assertIn('do not invent',result['reason'])

    def test_malformed_horizon_is_not_silently_na(self):
        record, observations = fixture()
        for value in ('not-a-date', ''):
            record['target_horizon']['end_date']=value
            with self.assertRaises(ValueError):
                MODULE.assess(record, observations, '2027-10-25T00:00:00Z')

    def test_mature_price_total_and_thesis_are_separate(self):
        record, observations = fixture()
        result = MODULE.assess(record, observations, "2027-10-25T00:00:00Z")
        self.assertEqual(result["status"], "matured")
        self.assertAlmostEqual(result["returns"]["price_return"], .1)
        self.assertAlmostEqual(result["returns"]["total_return"], .12)
        self.assertEqual(result["thesis_checks"][0]["status"], "falsification_triggered")

    def test_interim_is_not_mature_outcome(self):
        record, observations = fixture()
        observations["endpoint"] = price(125, "2027-04-24")
        observations["dividends"] = dividends(record["entry"], observations["endpoint"])
        observations["thesis"] = {}
        result = MODULE.assess(record, observations, "2027-04-25T00:00:00Z")
        self.assertEqual(result["status"], "interim")
        self.assertEqual(result["thesis_checks"][0]["status"], "pending")

    def test_cannot_choose_later_high(self):
        record, observations = fixture()
        observations["endpoint"] = price(200, "2027-11-24")
        with self.assertRaisesRegex(ValueError, "original horizon"):
            MODULE.assess(record, observations, "2027-12-01T00:00:00Z")

    def test_holiday_next_session_requires_evidence(self):
        record, observations = fixture()
        observations["endpoint"] = price(111, "2027-10-25")
        observations["horizon_session"]["close_at"] = observations["endpoint"]["observed_at"]
        observations["dividends"] = dividends(record["entry"], observations["endpoint"])
        result = MODULE.assess(record, observations, "2027-10-26T00:00:00Z")
        self.assertEqual(result["status"], "matured")

    def test_missing_data_remains_missing(self):
        record, observations = fixture()
        self.assertEqual(MODULE.assess(record, {}, "2027-10-25T00:00:00Z")["status"], "awaiting_horizon_data")
        observations.pop("dividends")
        self.assertIsNone(MODULE.assess(record, observations, "2027-10-25T00:00:00Z")["returns"]["total_return"])

    def test_legacy_na_and_unpublished_excluded(self):
        record = {"report_id": "HPQ-20261024", "original_snapshot_available": False, "publication_status": "delivered"}
        self.assertEqual(MODULE.assess(record, {}, "2027-10-25T00:00:00Z")["status"], "legacy_unavailable")
        record["publication_status"] = "ready"
        with self.assertRaisesRegex(ValueError, "confirmed published"):
            MODULE.assess(record, {}, "2027-10-25T00:00:00Z")

    def test_future_observation_rejected(self):
        record, observations = fixture()
        with self.assertRaisesRegex(ValueError, "future thesis"):
            MODULE.assess(record, observations, "2027-04-25T00:00:00Z")

    def test_executable_entry_before_publication_rejected(self):
        record, observations = fixture()
        record["publication_at"] = "2026-10-24T17:00:00-04:00"
        with self.assertRaisesRegex(ValueError, "precede publication"):
            MODULE.assess(record, observations, "2027-10-25T00:00:00Z")
        record["entry_convention"] = "publication_reference"
        self.assertIn("not a realized", MODULE.assess(record, observations, "2027-10-25T00:00:00Z")["return_interpretation"])

    def test_index_dividend_double_count_rejected(self):
        record, observations = fixture()
        record["entry"]["basis"] = "total_return_index"
        observations["endpoint"]["basis"] = "total_return_index"
        with self.assertRaisesRegex(ValueError, "do not add dividends"):
            MODULE.assess(record, observations, "2027-10-25T00:00:00Z")

    def test_share_basis_and_thesis_period_mismatch_rejected(self):
        record, observations = fixture()
        observations["endpoint"]["share_basis"] = "post-split-unadjusted"
        with self.assertRaisesRegex(ValueError, "share_basis"):
            MODULE.assess(record, observations, "2027-10-25T00:00:00Z")
        record, observations = fixture()
        observations["thesis"]["margin"]["period_end"] = "2027-03-31"
        with self.assertRaisesRegex(ValueError, "period_end"):
            MODULE.assess(record, observations, "2027-10-25T00:00:00Z")

    def test_benchmark_excess_and_watch_cohort(self):
        record, observations = fixture()
        record["benchmark"] = {"id": "frozen-benchmark", "entry": price(100, "2026-10-24")}
        observations["benchmark_endpoint"] = price(106, "2027-10-24")
        observations["benchmark_dividends"] = dividends(record["benchmark"]["entry"], observations["benchmark_endpoint"], 2)
        record["recommendation"] = "watch"
        result = MODULE.assess(record, observations, "2027-10-25T00:00:00Z")
        self.assertAlmostEqual(result["excess_total_return"], .04)
        self.assertFalse(result["buy_cohort_eligible"])

    def test_terminal_zero_is_not_dropped(self):
        record, observations = fixture()
        observations["endpoint"].update(value=0, kind="terminal_proceeds")
        observations["dividends"] = dividends(record["entry"], observations["endpoint"], 0)
        self.assertEqual(MODULE.assess(record, observations, "2027-10-25T00:00:00Z")["returns"]["total_return"], -1)

    def test_nan_and_unsourced_values_rejected(self):
        record, observations = fixture()
        observations["endpoint"]["value"] = float("nan")
        with self.assertRaisesRegex(ValueError, "finite"):
            MODULE.assess(record, observations, "2027-10-25T00:00:00Z")
        observations["endpoint"]["value"] = 110
        observations["endpoint"]["source_refs"] = []
        with self.assertRaisesRegex(ValueError, "source_refs"):
            MODULE.assess(record, observations, "2027-10-25T00:00:00Z")

    def test_executable_entry_must_match_first_session(self):
        record, observations = fixture()
        record["entry"] = price(98, "2026-10-25")
        with self.assertRaisesRegex(ValueError, "first eligible close"):
            MODULE.assess(record, observations, "2027-10-25T00:00:00Z")
        record.pop("entry_session")
        self.assertEqual(MODULE.assess(record, observations, "2027-10-25T00:00:00Z")["status"], "baseline_unavailable")

    def test_reference_price_cannot_be_future_at_publication(self):
        record, observations = fixture()
        record["entry_convention"] = "publication_reference"
        with self.assertRaisesRegex(ValueError, "cannot follow publication"):
            MODULE.assess(record, observations, "2027-10-25T00:00:00Z")

    def test_intraday_horizon_price_is_not_mature_close(self):
        record, observations = fixture()
        observations["endpoint"]["observed_at"] = "2027-10-24T12:00:00-04:00"
        with self.assertRaisesRegex(ValueError, "exact original horizon"):
            MODULE.assess(record, observations, "2027-10-25T00:00:00Z")

    def test_before_horizon_close_remains_interim(self):
        record, observations = fixture()
        observations["endpoint"]["observed_at"] = "2027-10-24T12:00:00-04:00"
        observations["dividends"] = dividends(record["entry"], observations["endpoint"])
        result = MODULE.assess(record, observations, "2027-10-24T13:00:00-04:00")
        self.assertEqual(result["status"], "interim")
        self.assertEqual(result["horizon_status"], "not_yet_matured")

    def test_receipt_join_checks_immutable_hash_links(self):
        snapshot = {"report_id": "report-1", "frozen_report_sha256": "r" * 64,
                    "publication_status": "ready", "publication_at": None}
        receipt = {"report_id": "report-1", "status": "delivered", "recommendation_sha256": "s" * 64,
                   "report_sha256": "r" * 64, "publication_at": "2026-10-24T15:00:00-04:00", "report_reference": "actual:report"}
        joined = MODULE.join_publication(snapshot, receipt, "s" * 64, "d" * 64)
        self.assertEqual(joined["publication_status"], "delivered")
        self.assertIsNone(snapshot["publication_at"])
        receipt["report_sha256"] = "wrong"
        with self.assertRaisesRegex(ValueError, "frozen report hash"):
            MODULE.join_publication(snapshot, receipt, "s" * 64, "d" * 64)


if __name__ == "__main__":
    unittest.main()
