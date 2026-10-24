---
name: review-report
description: Independently verify facts, calculations, citations, logic, or Korean prose in a staged cash flow investment report. Use for assigned review lanes before publication.
---

# Review Report

## Inputs

- Receive lane `facts-and-model` or `logic-and-editorial` and owned review paths.
- Read outline, sections, comparison data, model artifacts, and incoming handoffs.
- Read [quality policy](../../references/quality-policy.md), [editorial policy](../../references/editorial-policy.md), and [handoff contract](../../references/handoff-contract.md).
- For numerical work also read [evidence policy](../../references/evidence-policy.md) and [valuation policy](../../references/valuation-policy.md).
- Inspect original filings/calculations instead of comparing summaries only.
- Do not treat author confidence or the intended investment conclusion as verification.

## Facts and model lane

1. Check primary links support associated claims, periods, and definitions.
2. Reconcile identity, ADR ratios, prices, currencies, shares, and observation dates.
3. Recompute NTM yields and inspect numerator/denominator and FCF-definition alignment.
4. Check CDS entity, maturity, currency, seniority, terms, quote/date, liquidity, and NA.
5. Verify TTM, segment totals, margins, EPS, CFO/investment/FCF, and normalization.
6. Check growth/reinvestment/ROIC, discount pairing, timing, and terminal assumptions.
7. Inspect value bridge, leases, dilution, taxes, and stock-compensation double counting.
8. Verify mandatory distress comparison, p horizon/measure, equity recovery, and duplicated risk.
9. Verify actual tests at the documented commit; distinguish local tests from remote CI.
10. Recalculate price margins, total returns, scenarios, and sensitivity classifications.
11. Check comparison-backed selection order and covered-company exclusion.

## Logic and editorial lane

1. Trace demand growth to profit capture, reinvestment, cash flow, and final judgment.
2. Test the strongest alternative explanation for high FCF yield or low CDS.
3. Inspect peer inclusion/exclusion, data-access bias, and economic comparability.
4. Check each section answers its question with substantive explanation and evidence.
5. Identify contradictions, repeated definitions, missing transitions, and unsupported leaps.
6. Preserve useful depth while removing repetition; do not force arbitrary compression.
7. Check Korean honorific prose, terminology, readable tables, and restrained precision.
8. Check no-selection scope and ensure unavailable data are not narrated as observations.

## Outputs

- Write `reviews/<lane>.json` with finding ID, severity, affected section/claim/metric, evidence, and remedy.
- Distinguish material blockers, required corrections, and editorial improvements.
- Write `reviews/<lane>.md` with reasoning and independent verification results.
- Keep review conclusions separate from author agreement or disagreement.
- Return `handoffs/<task-id>.json` with reviewed versions and outstanding findings.
- Request targeted fixes through the orchestrator; do not silently alter shared values.

## Pass gate

- Resolve and recheck material factual, numerical, and methodological findings.
- Identify dependent calculations, tables, prose, and summaries invalidated by each change.
- Recheck affected work plus cross-section consistency, not unrelated completed tasks.
- Disclose minor residual limitations and adjust confidence where appropriate.
- Return blocked when an unresolved finding could change selection or value.
- Evaluate actual artifacts rather than the presence of checklist labels.
- Do not publish or mark delivery complete.
- Let the orchestrator close `review` only when both required lanes pass current versions.
