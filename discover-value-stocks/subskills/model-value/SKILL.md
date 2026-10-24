---
name: model-value
description: Build a verified operating model, Damodaran DCF, and mandatory distress comparison for a comparison-selected cash flow candidate. Use for the delegated model stage.
---

# Model Value

## Inputs

- Read the assignment, selection decision, frozen data, source register, comparison, and incoming handoff.
- Read [evidence policy](../../references/evidence-policy.md), [valuation policy](../../references/valuation-policy.md), and [handoff contract](../../references/handoff-contract.md).
- Confirm candidate identity, data version, valuation date, NTM interval, currency, and share basis.
- Inspect original source artifacts and table locations; a summary is not source evidence.
- If selection is blocked, stop with the blocker.
- If a valid comparison-backed decision is `no_selection`, write an explicit `not_applicable` model result linked to that decision.

## Execute

1. Use the JinhaPark/skills commit already pinned by the parent; do not resolve a newer main.
2. Read discover-value-stocks/subskills/data/distress-adjusted-dcf/SKILL.md, code, and tests from that same commit.
3. Actually run `python -m unittest discover -s discover-value-stocks/subskills/data/distress-adjusted-dcf/tests -v` from the repository root.
4. Record command, commit, output, and limitations; distinguish local tests from observed remote CI.
5. Build three historical years, nonoverlapping TTM, and at least three forecast years.
6. Model segment drivers, revenue, margin, taxes, working capital, investment, and cash conversion.
7. Reconcile reported CFO through normalizations and investment to screening FCF and valuation cash flows.
8. Connect growth, reinvestment, and ROIC; allow sufficient convergence beyond the minimum forecast table.
9. Align FCFF/WACC or justified FCFE/cost of equity, currency, nominal/real basis, and timing.
10. Explain discount inputs, stable-state economics, terminal assumptions, and terminal-value share.
11. Bridge operating value to equity using excess cash, nonoperating assets, debt, priority claims, and dilution.
12. Check leases, pensions, restructuring, stock compensation, taxes, buybacks, and dilution for double counting.
13. Compare base DCF with `(1-p)*E_going + p*E_distress` on a consistent basis.
14. Define distress, probability horizon/measure, and present equity recovery after priority claims.
15. Distinguish risk-neutral Q from physical P and avoid duplicating risk across WACC, hazard, and mixture.
16. Keep mandatory adjustment rows as NA with reasons if required inputs cannot be verified.
17. Never substitute zero for missing p/recovery; label hypothetical sensitivities separately.
18. Use survival extension only with supported term data, separately from the mixture.
19. Use peer multiples and reverse DCF only as supporting checks after intrinsic valuation.
20. Separate business scenarios from rate, terminal-growth, and distress sensitivities.
21. Independently check arithmetic and resolve material contradictory evidence before freezing outputs.
22. If absolute valuation rejects all candidates, return no_selection to the parent while preserving completed model evidence; do not mark an executed model not_applicable.

## Outputs

- Write `model/inputs.json` with metric IDs, sources, units, periods, and classifications.
- Write canonical `model.json` with version, values, NA reasons, scenarios, and test provenance; register its hash.
- Write detailed `model/results.json` with the same accepted model version.
- Write `model/calculations.md` with reproducible formulas, FCF bridge, and verification.
- Write `model/value-comparison.md` with enterprise/equity/share values, price margins, p, recovery, and sensitivities.
- Preserve executable calculations or calculation tables in `model/` where supported.
- Return `handoffs/<task-id>.json` referencing actual files and approved versions.

## Pass gate

- Require consistent bases, reproducible calculations, linked evidence, and truthful test-status reporting.
- Keep unavailable distress adjustment distinct from unavailable going-concern DCF.
- Block materially unsupported base values rather than supplying plausible numbers.
- Send corrections to the data owner and identify affected downstream artifacts.
- Do not publish, change the peer pool, or modify the valuation skill repository.
- Let the orchestrator inspect artifacts before confirming the `model` task.
