---
name: assess-track-record
description: Evaluate every previously published cash flow recommendation against its original investment horizon, benchmark, forecasts and thesis, preserving pending and unavailable outcomes. Use for the independent historical assessment lane on each research invocation.
---

# Assess the Published Track Record

## Inputs and independence

- Read [assessment policy](../../references/assessment-policy.md) and [handoff contract](../../references/handoff-contract.md).
- Receive the complete cumulative publication ledger, immutable recommendation/report snapshots, delivery receipts, prior assessment index, current cutoff and owned output paths.
- Use an assessor distinct from the final editor and current report authors where agents exist. Do not accept the editor's preferred interpretation as evidence.
- Read the original report and frozen forecast, not only its summary or a later revised thesis.
- Resolve missing prior files through their actual persistent references; retain missing-history records explicitly.

## Assess every invocation

1. Reconcile all delivered report IDs with assessment rows, including delisted, acquired, withdrawn and losing recommendations. Keep unsuccessful delivery attempts separate.
2. Recover each original decision, horizon, reference/entry convention, benchmark, scenario and thesis criteria without hindsight reconstruction.
3. Separate newly matured, still-interim, already-finalized, no-selection and unavailable records. Reuse immutable mature results only after hash and correction-event checks; fetch current evidence for interim/due records.
4. Fetch sourced prices, corporate actions, dividends, FX and business observations with dates and definitions. Verify first-session horizon mapping from the relevant exchange calendar.
5. Assemble derived inputs from frozen snapshots and appended observation events; never overwrite the original recommendation or delivery receipt.
6. Run `scripts/assess_recommendation.py` for supported cases. Inspect arithmetic and return conventions independently. Unsupported corporate-action paths require an explicit sourced bridge, not an invented quote.
7. Compare original scenario drivers and forecasts with actual matching periods. Evaluate falsification conditions and catalyst timing independently of stock-price direction.
8. Record supported/weakened/falsified/mixed/not-yet-evaluable thesis conclusions with sources, counterevidence and unresolved questions.
9. Aggregate only compatible, clearly labeled cohorts. Show sample size, maturity, missing-data coverage, absolute and excess outcomes; do not rank workflow changes by a noisy short-term win rate.
10. Send evidence-backed method/data/execution findings to reflection, distinguishing them from outcome luck and unobservable counterfactuals.

## Outputs and gate

- Write `assessment/track-record.json` using the policy's exact outer schema: hash-pinned local restored ledger, coverage fields and one uniquely keyed row for every confirmed publication. Preserve null report IDs for legacy history keys; include source/snapshot/input/output hashes, dates, statuses, returns, thesis conclusions and uncertainties.
- Write `assessment/track-record.md` with a compact evaluation table and substantive explanations of changes, failures and data gaps. This is internal support for the single report, not a second unsolicited deliverable.
- Preserve per-record helper inputs, observations and results in `assessment/records/`; persist them through the cache stage.
- Return `handoffs/assessment.json` with task ID `assessment`, current input versions, artifact references and concise findings for the independent reflection owner.
- Accept only when every confirmed publication is represented, including explicit unavailable rows. Missing historical data can reduce confidence without blocking a new report; falsely claiming complete evaluation is a blocker.
- Mark missing original HPQ inputs `legacy_unavailable`; keep its duplicate-selection exclusion.
- Never change a published horizon, count an interim peak as a mature win, infer a short position from avoidance, or claim realized user returns.
- If independent agents are unavailable, disclose separated self-assessment; do not manufacture peer-review independence.
