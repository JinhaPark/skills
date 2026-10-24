---
name: research-industry
description: Establish an evidence-backed industry growth thesis, opposing supply explanations, and a comparable peer pool before stock selection. Use only for a delegated industry research stage.
---

# Research the industry and fix the peer pool

## Scope and inputs
Read [selection policy](../../references/selection-policy.md), source rules in
[evidence policy](../../references/evidence-policy.md), and the
[handoff contract](../../references/handoff-contract.md).
Require the planning handoff, reporting date, history/exclusions, assigned
lane (demand, supply-dissent or integrate), source access and output paths.
Do not select the final stock, estimate DCF targets, publish or independently
launch sibling phases. Perform only the assigned research lane.

## Procedure
1. Start with the economic question, not an attractive ticker or market theme.
   Identify candidate industries and the horizon of expected growth.
2. Demand lane: investigate adoption, customer economics, volumes, replacement
   cycles, pricing and investment commitments through primary evidence.
   Separate historical facts, management forecasts and analyst estimates.
3. Supply-dissent lane: investigate capacity, entry, substitution, customer
   bargaining and margin compression. Find the strongest explanation under
   which demand grows but shareholders receive little extra cash.
4. State observable indicators and dates supporting or refuting each case.
   Distinguish market growth from company revenue and shareholder cash growth.
5. Map the value chain: who captures revenue, margins and cash; who funds
   reinvestment; and where competition can destroy capital returns.
6. Record source IDs and claim IDs with URLs, dates, original table/section
   locations, units and access limits. Search snippets and promotional market
   sizes are not verified facts.
7. Integration lane: read both lane artifacts and their original references.
   Reconcile definitions and contrary evidence; preserve unresolved disagreement.
   Choose the industry on evidence quality and economic relevance.
8. Fix a normally three-to-five-company listed peer pool using products,
   customers, value-chain position, economics and actual competition.
   Do not force the count or mix dissimilar conglomerates without explanation.
9. Record legal entity, ticker, exchange, share class/ADR relationships,
   relevant exposure and inclusion/exclusion reasons for each peer.
10. Keep relevant peers when CDS may be missing. Allow already covered firms
    such as HPQ in the pool but flag their protagonist ineligibility.
11. Require documented new evidence before a later pool change. Do not
    replace peers to make a shortlisted company look relatively cheaper.

## Outputs
- Lane artifacts: `industry/demand.md` and `industry/supply-dissent.md`.
- Integration artifacts: `industry/thesis.md`, `industry/peer-pool.json`.
- `handoffs/industry-<lane>.json`, or `handoffs/industry.json` for integration.
- Source/claim records submitted to their canonical registry owner.

## Pass gate and handoff
Require a growth horizon, value-capture explanation, counterevidence,
falsification conditions and justified membership before approving integration.
Hand off the pool version, thesis summary, source/claim pointers, unresolved
issues and metrics needed for peer comparison. If the thesis fails, return
that failure to the parent rather than manufacturing a pool or selecting a stock.
