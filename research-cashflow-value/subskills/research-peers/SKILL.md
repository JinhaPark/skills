---
name: research-peers
description: Extract comparable forward cash flow data or verified CDS observations for an approved industry peer pool and build a canonical dataset. Use only for a delegated peer evidence stage.
---

# Research and normalize the peer comparison

## Scope and inputs
Read [evidence policy](../../references/evidence-policy.md), comparison rules in
[editorial policy](../../references/editorial-policy.md), and the
[handoff contract](../../references/handoff-contract.md).
Require the approved pool version, industry handoff, price cutoff, exact NTM
period, common definitions and assigned lane/output paths.
Lanes: company-<entity>, credit or integrate. Do not select a winner, change
pool membership, publish or independently launch sibling phases.

## Company extraction lane
1. Read filings, actual cash flow statements and material notes; record primary
   document periods and exact table/note locations rather than search snippets.
2. Extract price/time/currency, latest shares, market capitalization, cash,
   debt and business exposures. Separate latest shares from EPS diluted shares.
3. Bridge CFO through normalization and cash investment to normal FCF.
   Explain working capital, recurring restructuring, leases, software,
   compensation and company-versus-analyst FCF definitions.
4. Build an evidence-backed NTM forecast with exact start/end dates.
   Label guidance, verified consensus and own estimates separately.
   Explain fiscal-year weighting and seasonality; do not relabel FY1 as NTM.
5. Calculate comparable equity-oriented normal FCF/current market cap in
   consistent currency. Do not divide FCFF by market cap. State interest,
   tax, lease and reinvestment treatment; exclude financing from operating cash.
6. Preserve negative FCF. Store unavailable values as null plus NA reasons,
   never zero. Record metric/source/claim IDs, units, formulas, assumptions
   and fact/estimate/scenario classification.
7. Explain two-to-three-year reinvestment and cash conversion so necessary
   growth investment is not confused with structurally weak economics.

## Credit lane
1. Seek actual CDS for every approved peer. Record reference entity, tenor,
   currency, seniority, restructuring clause, quote type, date and liquidity;
   prefer comparable five-year contracts and aligned observation dates.
2. Distinguish par/converted spreads, standard coupons and upfront payments.
   Never present the standard coupon as a market CDS premium.
3. Keep missing CDS as NA with access/search reason. Do not substitute ratings,
   bond spreads, another entity or estimated CDS in that column. Name any
   alternative credit measures separately and cite their actual definitions.
4. Extract maturity, refinancing and interest-coverage evidence. Do not infer
   physical default probability directly from CDS.

## Integration lane
Read all company/credit artifacts and cited inputs. Align forecast periods,
definitions, currencies, observation dates and shares. Submit changes to the
data owner rather than overwriting another worker's artifact. Preserve raw
observations, adjustments and material comparability limits. Missing CDS must
not remove a company from the approved pool.

## Outputs and pass gate
Company: `peers/<entity>/evidence.json`, `peers/<entity>/analysis.md`.
Credit: `peers/credit.json`, `peers/credit-notes.md`.
Integration: canonical `data.json` with its integer version and registered SHA-256,
`data/comparison.json`, `peers/comparability.md`.
Write `handoffs/peers-<lane>.json` or integration `handoffs/peers.json`.
Require one metric record or explicit NA for every pool member, source
traceability, forecast provenance and consistent definitions. Hand off data
and pool versions, limitations, material differences and original pointers.
