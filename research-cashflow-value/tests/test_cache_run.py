import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("cache_run", Path(__file__).parents[1] / "scripts/cache_run.py")
cache = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cache)


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.run, self.store = self.root / "run", self.root / "cache"
        self.run.mkdir()
        (self.run / "facts.json").write_text('{"value":12}')
        self.descriptor = {"stage": "industry", "skill_commit": "a" * 40, "input_hashes": {"pool": "b" * 64}, "sources": [{"source_id": "s1", "as_of": "2026-10-20T00:00:00Z", "sha256": "c" * 64}], "settings": {"currency": "USD", "definition": "equity-fcf"}, "volatility": "static"}

    def save(self, status="completed", descriptor=None, artifacts=None, created="2026-10-24T00:00:00Z"):
        return cache.snapshot(self.run, self.store, descriptor or self.descriptor, "run-1", status, artifacts or ["facts.json"], created, "2026-11-01T00:00:00Z")

    def receipt(self, snapshot):
        result = self.run / "provider-result.txt"
        result.write_text('{"success":true,"reference":"test-provider:test-id"}')
        return cache.register_receipt(self.store, snapshot["snapshot_id"], "test-provider", "test-provider:test-id", "2026-10-24T00:01:00Z", result)

    def lookup(self, run_id="run-1", descriptor=None, now="2026-10-25T00:00:00Z"):
        return cache.lookup(self.store, descriptor or self.descriptor, run_id, now)

    def test_persisted_static_snapshot_reusable_across_runs(self):
        saved = self.save()
        self.receipt(saved)
        found = self.lookup("run-2")
        self.assertEqual(found["eligible"][0]["snapshot_id"], saved["snapshot_id"])
        self.assertFalse(saved["durable"])

    def test_local_snapshot_requires_durable_receipt_for_reuse(self):
        saved = self.save()
        self.assertEqual(cache.verify(self.store, saved["snapshot_id"])["status"], "completed")
        self.assertEqual(self.lookup()["rejected"][0]["reason"], "durable_receipt_missing")

    def test_current_market_refreshes_each_new_run(self):
        self.descriptor["volatility"] = "market"
        self.receipt(self.save())
        self.assertEqual(len(self.lookup()["eligible"]), 1)
        self.assertEqual(self.lookup("run-2")["rejected"][0]["reason"], "new_run_requires_refresh")

    def test_publish_not_reused_across_runs_even_with_static_label(self):
        self.descriptor["stage"] = "publish"
        self.receipt(self.save())
        self.assertFalse(self.lookup("run-2")["eligible"])

    def test_assessment_and_unknown_stages_cannot_cross_run(self):
        for stage in ("assessment", "prepublish", "closeout", "future-unrecognized-stage"):
            with self.subTest(stage=stage):
                self.descriptor["stage"] = stage
                self.receipt(self.save())
                result = self.lookup("run-2")
                self.assertFalse(result["eligible"])
                self.assertEqual(result["rejected"][0]["reason"], "new_run_requires_refresh")
                self.assertEqual(len(self.lookup("run-1")["eligible"]), 1)

    def test_failed_snapshot_saved_but_not_reused(self):
        self.receipt(self.save("failed"))
        self.assertEqual(self.lookup()["rejected"][0]["reason"], "incomplete_status")
        self.assertEqual(cache.index(self.store)["snapshots"][0]["status"], "failed")

    def test_expiry_is_exclusive_and_future_invalid(self):
        self.receipt(self.save())
        self.assertFalse(self.lookup(now="2026-11-01T00:00:00Z")["eligible"])
        self.assertFalse(self.lookup(now="2026-10-23T00:00:00Z")["eligible"])

    def test_all_semantic_inputs_change_key(self):
        baseline = cache.descriptor_key(self.descriptor)
        variants = [copy.deepcopy(self.descriptor) for _ in range(4)]
        variants[0]["skill_commit"] = "d" * 40
        variants[1]["input_hashes"]["pool"] = "d" * 64
        variants[2]["sources"][0]["as_of"] = "2026-10-21T00:00:00Z"
        variants[3]["settings"]["currency"] = "KRW"
        self.assertTrue(all(cache.descriptor_key(v) != baseline for v in variants))

    def test_source_order_does_not_change_key(self):
        self.descriptor["sources"].append({"source_id": "s2", "as_of": "2026-10-21T00:00:00Z", "sha256": "d" * 64})
        baseline = cache.descriptor_key(self.descriptor)
        self.descriptor["sources"].reverse()
        self.assertEqual(cache.descriptor_key(self.descriptor), baseline)

    def test_path_traversal_absolute_and_alias_rejected(self):
        for bad in ("../escape", "/etc/passwd", "./facts.json", "dir/../facts.json", "dir//file"):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.save(artifacts=[bad])

    def test_symlink_artifact_and_root_rejected(self):
        (self.run / "alias").symlink_to(self.run / "facts.json")
        with self.assertRaises(ValueError):
            self.save(artifacts=["alias"])
        (self.root / "alias-root").symlink_to(self.run)
        with self.assertRaises(ValueError):
            cache.safe_root(self.root / "alias-root")

    def test_output_tampering_detected(self):
        saved = self.save()
        (Path(saved["path"]) / "files/facts.json").write_text("tampered")
        with self.assertRaises(ValueError):
            cache.verify(self.store, saved["snapshot_id"])

    def test_metadata_tampering_detected(self):
        saved = self.save()
        path = Path(saved["path"]) / "manifest.json"
        manifest = json.loads(path.read_text())
        manifest["status"] = "failed"
        path.write_text(json.dumps(manifest))
        with self.assertRaises(ValueError):
            cache.verify(self.store, saved["snapshot_id"])

    def test_unregistered_snapshot_file_rejected(self):
        saved = self.save()
        (Path(saved["path"]) / "files/extra.txt").write_text("unregistered")
        with self.assertRaises(ValueError):
            cache.verify(self.store, saved["snapshot_id"])

    def test_future_receipt_cannot_support_earlier_lookup(self):
        saved = self.save()
        self.receipt(saved)
        result = self.lookup(now="2026-10-24T00:00:30Z")
        self.assertEqual(result["rejected"][0]["reason"], "durable_receipt_missing")

    def test_receipt_tampering_detected(self):
        saved = self.save()
        receipt = self.receipt(saved)
        (self.store / "receipts" / receipt["receipt_id"] / "provider-result.txt").write_text("changed")
        result = self.lookup()
        self.assertFalse(result["eligible"])
        self.assertEqual(result["quarantined"][0]["kind"], "receipt")
        self.assertEqual(result["rejected"][0]["reason"], "durable_receipt_missing")

    def test_interrupted_matching_receipt_pair_recovers_atomically(self):
        saved = self.save()
        receipt = self.receipt(saved)
        folder = self.store / "receipts" / receipt["receipt_id"]
        (folder / "receipt.json").unlink()
        recovered = self.receipt(saved)
        self.assertEqual(recovered["receipt_id"], receipt["receipt_id"])
        self.assertTrue((folder / "receipt.json").is_file())
        self.assertEqual(len(self.lookup()["eligible"]), 1)
        preserved = list((self.store / "receipts").glob(".partial-*"))
        self.assertEqual(len(preserved), 1)
        self.assertTrue((preserved[0] / "provider-result.txt").is_file())

    def test_unrelated_corruption_quarantined_without_hiding_valid_cache(self):
        good = self.save()
        self.receipt(good)
        other_descriptor = copy.deepcopy(self.descriptor)
        other_descriptor["stage"] = "peers"
        bad = self.save(descriptor=other_descriptor)
        (Path(bad["path"]) / "files/facts.json").write_text("corrupt")
        result = self.lookup("run-2")
        self.assertEqual(result["eligible"][0]["snapshot_id"], good["snapshot_id"])
        self.assertEqual(result["quarantined"][0]["entry"], bad["snapshot_id"])
        listing = cache.index(self.store)
        self.assertEqual(len(listing["snapshots"]), 1)
        self.assertEqual(listing["quarantined"][0]["entry"], bad["snapshot_id"])
        self.assertTrue((Path(bad["path"]) / "files/facts.json").is_file())

    def test_idempotent_snapshot_and_new_version_preserves_old(self):
        first = self.save()
        self.assertEqual(self.save()["snapshot_id"], first["snapshot_id"])
        (self.run / "facts.json").write_text('{"value":13}')
        second = self.save()
        self.assertNotEqual(first["snapshot_id"], second["snapshot_id"])
        self.assertEqual((Path(first["path"]) / "files/facts.json").read_text(), '{"value":12}')

    def test_naive_time_and_missing_expiry_rejected(self):
        with self.assertRaises(ValueError):
            self.save(created="2026-10-24T00:00:00")
        with self.assertRaises(ValueError):
            self.save(created="2026-11-01T00:00:00Z")

    def test_future_source_observation_rejected_on_snapshot_and_verify(self):
        future = copy.deepcopy(self.descriptor)
        future["sources"][0]["as_of"] = "2026-10-24T00:00:01Z"
        with self.assertRaises(ValueError):
            self.save(descriptor=future)
        saved = self.save()
        original = Path(saved["path"])
        manifest = json.loads((original / "manifest.json").read_text())
        manifest["descriptor"] = future
        manifest["key"] = cache.descriptor_key(future)
        manifest_bytes = cache.encoded(manifest)
        invalid_id = cache.digest(manifest_bytes)
        (original / "manifest.json").write_bytes(manifest_bytes)
        original.rename(original.parent / invalid_id)
        with self.assertRaisesRegex(ValueError, "observation cannot postdate"):
            cache.verify(self.store, invalid_id)


if __name__ == "__main__":
    unittest.main()
