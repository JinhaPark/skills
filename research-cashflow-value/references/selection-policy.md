# Industry and candidate selection policy

## Purpose and operating boundaries
Investigate an industry expected to grow, then form a pool of listed companies
that compete economically within it. Compare the pool's next-12-month (NTM)
expected normalized FCF yields and verifiable CDS premiums to narrow candidates.
Use Damodaran intrinsic valuation to make the final current-price judgment.
Search globally and select one previously unpublished protagonist only when it
meets the criteria; allow `no_selection` otherwise. Write the final report in
polite, natural Korean so an individual investor can verify the industry thesis,
company differences, investment argument and potential losses.

Do not generate the whole report in one pass. Follow the
[orchestrator](../SKILL.md) to separate research, modeling, logical structure,
section writing and review into actual tasks and artifacts. Delegate explicitly
when callable subagent tools exist. Give each worker common principles and its
own input/output contract, not the entire instruction history; use the
[handoff contract](handoff-contract.md).

Preserve the analytical order: industry growth thesis → competitive structure
and fixed peer pool → comparable NTM FCF/CDS evidence → shortlist and challenges
→ Damodaran DCF with mandatory distress comparison → final selection or none.
Never pick a preferred stock first and choose an industry, peers or metrics
retrospectively. The report may display the resulting comparison table first
for readability; this does not change the actual order of investigation.

Industry analysis defines the search universe, FCF/CDS comparison drives
candidate selection, and Damodaran valuation is the primary test of absolute
value against price. Multiples and reverse DCF are secondary checks. Do not
select using arbitrary weighted scores, subtract CDS from FCF yield or rely on
mechanical rankings. Apply the valuation, probability-measure, distress and
missing-input rules in [valuation policy](valuation-policy.md) with priority.
Apply senior-analyst depth and verification without claiming professional
employment, credentials or data access that are not actually held.

Deliver one Markdown report containing the industry/peer overview table, four
short cover-letter paragraphs and deep research, using the scheduled task's
supported delivery route. Save through an available persistent file service
and provide an actual file link. Never claim unsupported storage, delivery,
chat movement or pinning. Do not publish to JinhaPark/news, mix the report into
AI-news deliveries, send separate Discord messages, or change schedule,
timezone, enabled state or delivery route while executing research.

## Industry growth and value capture
Compare candidate industries by growth horizon, demand drivers, verified
evidence and conditions that would refute the thesis before fixing this run's
industry and scope. Policy slogans, total-addressable-market forecasts and
claims of AI exposure are insufficient selection grounds.

Investigate demand alongside capacity additions, price competition, technological
substitution and customer bargaining. Explain who captures revenue, profit and
cash along the value chain. Do not equate industry growth with company earnings
or shareholder cash-flow growth. An industry may recur across reports, but
explain why it is being revisited and identify new observations.

## Fix the peer pool before stock selection
Check source reliability, business comprehensibility, trading liquidity and
accounting comparability. Normally fix three to five companies based on
products, customers, value-chain position, revenue model and actual competition,
not merely an industry label. Record inclusion and exclusion reasons. Do not
force a company count. For materially different business mixes, identify the
relevant exposure and comparison limitations.

Do not replace peers retrospectively to favor a candidate. If new evidence
requires changing the pool, record that evidence and the reason. CDS availability
must not determine membership: retain economically relevant companies with
unavailable CDS marked NA. Previously published protagonists may remain peers
but must not be selected as new weekly protagonists.

## Compress candidates using comparable metrics
Apply the NTM FCF and CDS definitions in [editorial policy](editorial-policy.md)
to the entire pool, aligning forecast periods, observation dates and metric
definitions. Explain differences through growth participation, market share,
margins, required reinvestment, cash conversion, durability, leverage and
refinancing risk.

High FCF yield and low CDS alone do not identify a winner. Low CDS does not
establish equity undervaluation and does not cover every shareholder business
or price risk. Challenge whether high yield compensates for temporary working
capital releases, investment cuts, a cyclical peak, business decline or debt risk.

Keep NTM yield as the main comparison metric while explaining the next two to
three years of cash conversion, required reinvestment and ROIC, particularly for
companies whose growth spending depresses near-term FCF. Do not remove actual
investment arbitrarily to favor growth companies. Establish comparably supported
forecasts across the pool, while concentrating detailed segment models and full
DCF work on shortlisted candidates and the final subject. Disclose when uneven
data quality materially determines the apparent ranking.

For unavailable CDS, examine other credit evidence under its actual name, but
do not claim a selection supported by two verified metrics. Briefly record
shortlist and major rejection reasons. Value the candidate with the strongest
evidence of underpricing relative to growth participation and cash conversion.
Reject it if absolute intrinsic value does not support the current price,
regardless of relative cheapness. High dividends, low P/E or the highest FCF
yield are insufficient alone.

## Publication history and exclusions
Read the cumulative publication ledger, checking company name, legal identifier,
main tickers, exchange, ADR/local-share relationships, publication date, report
identifier and artifact link. A new share class, listing venue or name is not a
new company. Distinguish work in progress from completed delivery and mark only
actually delivered reports as published. Keep the ledger in supported persistent
storage and link it to reports so subsequent runs can locate it.

If the ledger is unavailable, reconstruct it from accessible records. If recovery
fails, disclose duplicate risk and execution constraints; do not claim that
history was checked successfully.

HP Inc. (HPQ) was already published as the first subject on 2026-10-24. If absent
from the ledger, add this explicitly as user-provided history. Do not select HPQ
as a new protagonist; it may appear in peer comparisons or checks of past views.
Exclude steel companies and Alaska/Greenland oil-development themes whose thesis
primarily depends on political events or policy slogans. Judge substantive thesis
dependence rather than excluding every company because of a geographic name.

## No-selection and blocked outcomes
Return `no_selection` when no eligible new company meets growth-thesis,
valuation-attractiveness and evidence-quality criteria. Do not force a buy idea
or recycle a past protagonist. Still provide the verifiable peer comparison,
industry thesis, rejection reasons and observable price/business/credit
conditions for reconsideration. Do not fabricate a long single-company analysis
or completed DCF for an unresolved candidate; identify unperformed work.
Record a no-selection run separately from a company publication. If critical
missing inputs prevent a reliable decision, retain a blocked outcome rather
than treating missing evidence as proof that every candidate is unattractive.
