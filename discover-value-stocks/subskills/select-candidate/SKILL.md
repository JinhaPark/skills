---
name: select-candidate
description: Shortlist valuation candidates from an approved industry peer pool using forward FCF yield and CDS comparisons, preserving dissent and no-selection branches. Use only for delegated candidate selection.
---

# Select candidates for valuation

## Scope and inputs
Read [selection policy](../../references/selection-policy.md) and the
[handoff contract](../../references/handoff-contract.md).
Require the approved industry thesis, value-chain map, pool, canonical
comparison version, comparability notes, publication history and source,
claim and metric records. Shortlist for valuation; relative cheapness is not
final investment approval. Do not publish, change canonical files or pool
membership, or launch sibling phases independently.

## Procedure
1. Check input versions, artifact existence and comparability issues.
   Return material period/definition conflicts for correction before selection.
2. Compare the entire pool's NTM normal FCF yields and actual CDS premiums.
   Preserve NA and its consequence. Do not claim both metrics are verified
   when credit observations or forecast inputs are unavailable.
3. Explain differences through growth exposure, share gains, price/margins,
   reinvestment, cash conversion, durable economics, debt and refinancing.
   Never subtract CDS from FCF yield or construct arbitrary weighted scores.
4. Challenge high yields: test cyclical peaks, working-capital releases,
   reduced necessary investment, decline, leverage and refinancing risks.
   Challenge low CDS: repayment capacity does not establish equity cheapness.
5. Examine two-to-three-year cash conversion without removing actual growth
   investment to improve the next-12-month cash comparison.
6. State the strongest opposing explanation for each serious candidate and
   evidence that would distinguish it from the investment thesis. Do not ask
   an independent dissent reviewer to endorse the proposed company.
7. Shortlist only where growth participation and cash generation appear
   underpriced enough to justify detailed Damodaran valuation. Keep count
   proportional to evidence and available analytical capacity.
8. Record reasons for major inclusions and rejections. Distinguish poor
   economics, rich price, insufficient evidence and prior publication.
9. Allow HPQ and previously published firms as benchmarks only. Enforce
   entity-level history across share classes, exchanges and ADRs. Preserve
   steel and politically dependent Alaska/Greenland oil-theme exclusions.
10. Return no_selection if no eligible candidate meets economic/evidence
    criteria; give observable price/business/credit revisit conditions.
    Return blocked if missing critical inputs prevent a reliable decision.
    Data blockage is not proof that every company is unattractive.
11. For candidates, define business questions, uncertainty ranges and adverse
    cases for the model task. Keep final selection conditional on absolute
    intrinsic value and the required distress comparison.

## Outputs
- `selection/candidate-review.md`: whole-pool comparison and rejection logic.
- `selection/decision.json`: candidate entity IDs or no_selection/blocked,
  reasons, model questions and revisit conditions.
- `handoffs/selection.json`: contract-compliant packet with input versions.

## Pass gate and handoff
Require traceable reasons and consideration of the entire approved pool
without convenient membership changes. Hand off exact data/pool versions,
candidates, valuation questions, counterarguments and original metric/source
pointers. For no_selection/blocked, inform the parent to route correctly;
do not fabricate target prices or mark the model stage completed.
