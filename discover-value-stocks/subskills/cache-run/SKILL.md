---
name: cache-run
description: Persist immutable research checkpoints, verify cached evidence and enforce freshness before reuse. Use at every cash flow research invocation, stage acceptance, failure, resume and final lifecycle checkpoint.
---

# Cache research run

Read [cache policy](../../references/cache-policy.md) and [handoff contract](../../references/handoff-contract.md). Act on the coordinator's scoped stage or invocation. Do not select stocks, edit research, deliver reports or modify skills in this stage.

## Inputs

Receive the run ID, pinned skill commit, stage/status, accepted artifact paths, upstream hashes, source snapshots/as-of dates, semantic settings, explicit freshness decision and persistent index identity/version. For bootstrap, discover the actual index with the coordinator. Never infer that local scratch is durable storage.

## Procedure

1. Resolve supported persistent storage and its current skill instructions. Use namespace `discover-value-stocks` and discover exact filenames `discover-value-stocks-cache-index.json` and `discover-value-stocks-publications.json`, unless existing recorded identities are available. Reconcile multiple matches using run hashes/history instead of choosing arbitrarily. Read the actual index/ledger and materialize needed snapshots. Preserve returned identities/version guards. Create missing first-run objects only after the search and record their real identities. Search the legacy filenames `research-cashflow-value-cache-index.json` and `research-cashflow-value-publications.json` as well. Reuse verified existing object identities and publication history; the workflow rename must not create an empty replacement ledger, duplicate caches, or rewrite historical report IDs. If both names exist, reconcile their records before choosing the canonical index.
2. On each invocation, write a bootstrap checkpoint. On every accepted stage, blocked result, failure and completed lifecycle, snapshot its actual artifacts/status with `../../scripts/cache_run.py`. Hash source bytes and all material upstream inputs; classify time-sensitive evidence and derived outputs as market data. Document `valid_until` rather than inventing a universal expiry.
3. Before reuse, invoke `lookup` and `verify`; inspect rejection reasons and source versions. Only canonical IDs `source-evidence`, `industry`, `peers`, `model`, `outline` and `writing` may reuse static outputs across runs; all other IDs and unknown aliases require a fresh run. Revalidate current market observations for each new run and refresh any newly restated or superseded filings. Use cached static evidence only within its valid scope. A prior completed report, review or delivery record is history, not the next report.
4. Save the immutable snapshot to the supported provider. Retain its observed result, register its real receipt, save receipt records, then update the persistent index last with a version guard. Do not claim success after a local snapshot alone or a partial provider write. Reconcile conflicts by reading the latest index and merging append-only entries.
5. Return complete artifact references plus concise findings, cache hits/misses, invalidated descendants and persistence status. The coordinator refreshes current task/handoff records; old completion or delivery fields must not be copied. Cache every failed or blocked invocation for reflection without adding it to the publication ledger.

## Outputs

- Immutable snapshot manifests and artifact bytes under the materialized cache root.
- Verified provider receipt records and current persistent cache index reference/version.
- `cache/checkpoint-<stage>-<attempt>.json`: snapshot ID/key, actual source run ID, receipt references, freshness reasoning, hit/miss/rejection reasons and durable/pending/failed status.
- A scoped handoff pointing to the checkpoint record and next required actions; no hidden reasoning trace.

## Pass gate

Require readable nonempty artifacts, verified hashes, valid descriptor/expiry, observed provider saves and a successful guarded index update for `durable`. Otherwise retain local recovery data, state the specific failure and mark persistence degraded. Local `verify` is allowed on an unpersisted same-run checkpoint but cannot certify durable reuse. A cache hit never substitutes for financial verification, independent reflection or actual delivery.

## Handoff

Give the coordinator the saved object identities and current index version, accepted reusable artifacts, invalidation list and limitations. Give reflection the invocation/stage status and failure evidence. Do not make workers rediscover storage or import the entire archive into context.
