# Durable run cache

## Scope and ownership

Checkpoint every invocation, including blocked and failed runs, and every accepted stage. Preserve complete source evidence, canonical data/model versions, drafts, reviews, handoffs, the frozen published report, recommendation records and reflection/evolution results. Use separate immutable snapshots, never an overwritten "latest report" as history. The coordinator owns the cache index; workers return files and hashes. Store run data in supported private persistent storage, not the public skill repository. Do not include credentials, signed URLs, hidden reasoning traces or unnecessary personal data.

`scripts/cache_run.py` handles only local materialized bytes. It cannot save to Library, verify a provider receipt externally, deliver a report or certify financial truth. Its `durable:false` response is intentional. The orchestrator must perform the actual persistence actions using the current Library skill or the already established supported private storage provider.

## Discover, hydrate and checkpoint

1. During planning, use the logical private namespace `discover-value-stocks`. Search the exact default filenames `discover-value-stocks-cache-index.json` and `discover-value-stocks-publications.json` with the provider's supported search/read tools. Existing recorded object identities take precedence over filename discovery; preserve their returned identity and version on updates. If multiple matches exist, reconcile their run IDs, hashes and publication history; do not arbitrarily select a duplicate or discard history. For a first run, create an index/ledger only after the search, and retain returned identities and versions; never invent a storage URI. Record the provider, index identity, current version, retrieval method and state in the run manifest/lifecycle sidecar. An empty index is valid only after checking for existing history. Search the legacy filenames `research-cashflow-value-cache-index.json` and `research-cashflow-value-publications.json` as well. Reuse verified existing object identities and publication history; the workflow rename must not create an empty replacement ledger, duplicate caches, or rewrite historical report IDs. If both names exist, reconcile their records before choosing the canonical index.
2. Materialize needed snapshots and their receipt records using the provider's supported method. Verify all hashes before consuming any content. A missing index is not a cache hit. If unavailable, proceed with fresh research where feasible, mark persistence degraded, and retain local recovery artifacts; do not claim durable caching or complete historical evaluation.
3. At each stage acceptance, create a snapshot from an explicit artifact allowlist. Snapshot failed/blocked diagnostics as their actual status. Include useful partial results but never mark them completed. Each new invocation gets a distinct run ID; a retry/resume retains its invocation ID with append-only attempts.
4. Upload/save the immutable snapshot package first. Use a deterministic package of its manifest and `files/` contents or separately saved objects with a hash map. Record the actual returned provider reference and observed save result with `receipt`. Upload receipt records next, then replace the persistent index last using the provider's version guard. Do not claim completion if the index or snapshot write failed. Reconcile orphaned saved objects on resume by hash; never erase previously valid snapshots.
5. Regenerate the local index using `index`. Retain provider identity/version outside the immutable snapshot and carry it to the next invocation. The index is a discoverability pointer, not proof that referenced data still exists; hydrate and verify on reuse.

Use the same run ID and report hash to deduplicate delivery attempts. A cached report or publication-stage completion never proves delivery. Inspect an existing delivery receipt before retrying; uncertain delivery remains uncertain. Do not republish or append a stock to the coverage ledger solely because a report is cached.

## Key and freshness contract

Supply a descriptor JSON with exactly these keys:

```json
{
  "stage": "industry",
  "skill_commit": "FULL_40_CHARACTER_COMMIT_SHA",
  "input_hashes": {"pool": "SHA256_OF_ACCEPTED_INPUT"},
  "sources": [{"source_id": "filing-1", "as_of": "2026-10-24T00:00:00Z", "sha256": "SHA256_OF_SOURCE_SNAPSHOT"}],
  "settings": {"currency": "USD", "fcf_definition": "equity-fcf", "forecast_start": "2026-10-24", "forecast_end": "2027-10-24"},
  "volatility": "static"
}
```

Placeholders are illustrative and intentionally invalid. Derive real digests from bytes. Include all upstream artifact hashes and semantic settings: entity/peer IDs, periods, currency/units, valuation date, methodology, model/library version and applicable assumptions. Source `as_of` is an observation timestamp, not a forward financial period; it requires a time zone and must not be later than snapshot creation. Keep forecast periods in semantic settings or source metadata. The key canonicalizes source ordering. A change to inputs, source bytes/as-of, semantics or skill commit creates a different key; invalidate all dependent outputs. Cached prose is eligible only with the same accepted data/model, thesis and predecessor hashes.

Every snapshot requires `created_at` and an explicit `valid_until` justified by the data owner's freshness policy. No universal long-lived TTL. Reject reuse at or beyond expiry or before creation. Market prices, FX, CDS, current credit observations, fresh news and forecasts derived from them use `volatility:market`: refresh for every new run even before expiry. Same-run resume still checks the cutoff and new filings/events. Static filings may be reused after confirming they remain the correct reporting version; a restatement invalidates them. Missing/old CDS remains NA with its reason.

Only canonical stage IDs `source-evidence`, `industry`, `peers`, `model`, `outline` and `writing` are eligible for cross-run reuse, and only with static inputs, exact descriptor matches, unexpired freshness and verified receipts. Every other stage ID defaults to fresh per run, including `plan`, `selection`, `review`, `publish`, `assessment`, `reflection`, `evolution`, `prepublish`, `closeout` and any unknown alias. Do not relabel stages or mark market data static to bypass freshness. Use canonical IDs for cached stage artifacts; keep lane identifiers in semantic settings. Raw verified evidence may be reused by fresh stages. New runs must not reuse a prior report as their final output. Failed/blocked snapshots are recovery evidence only, never eligible completed work. Cache lookup requires an observed durable receipt; local verification can inspect an unpersisted same-run checkpoint but does not turn it into durable cache reuse.

## Commands

Run from the pinned skill package. Arguments below are task-local example paths; replace times/IDs with the actual run values.

```bash
python scripts/cache_run.py snapshot --run-root RUN_DIR --cache-root CACHE_DIR --descriptor RUN_DIR/cache/industry-descriptor.json --run-id RUN_ID --status completed --created-at 2026-10-24T01:00:00Z --valid-until 2026-10-31T01:00:00Z --artifact research/industry.md --artifact handoffs/industry.json
python scripts/cache_run.py verify --cache-root CACHE_DIR --snapshot-id SNAPSHOT_SHA256
python scripts/cache_run.py receipt --cache-root CACHE_DIR --snapshot-id SNAPSHOT_SHA256 --provider ACTUAL_PROVIDER --storage-reference OBSERVED_REFERENCE --saved-at 2026-10-24T01:01:00Z --evidence-file RUN_DIR/cache/provider-save-result.txt
python scripts/cache_run.py index --cache-root CACHE_DIR > RUN_DIR/cache/index.json
python scripts/cache_run.py lookup --cache-root CACHE_DIR --descriptor RUN_DIR/cache/industry-descriptor.json --run-id RUN_ID --now 2026-10-24T01:05:00Z
```

Call `receipt` only after observing the successful provider action. Store a minimal sanitized result proving object identity/status, not an authentication token or signed transfer URL. The helper checks record integrity, not truth of a caller-created receipt. Upload that receipt record and the index before declaring the stage durably cached.

Inspect lookup rejections and `quarantined` diagnostics explicitly. Lookup/index isolate corrupt or incomplete entries without deleting their bytes or hiding unrelated valid entries. Quarantined entries never support reuse; retain their diagnostics for reflection and repair from independently verified source copies. Receipt writes install both files via a temporary directory and atomic rename; a matching interrupted pair is preserved in a `.partial-...` directory before retry installs a complete pair. A conflicting pair fails instead of being overwritten. Read eligible artifacts before accepting them and regenerate the new run's task records/handoffs with the original source run and snapshot ID. Do not copy an old task's completion, delivery status, review approval or ledger writes into the new run. No automatic cache eviction: preserve published baselines and evaluation evidence; any later retention policy must keep those records and provenance intact.
