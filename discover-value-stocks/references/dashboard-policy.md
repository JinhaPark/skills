# README investment dashboard

## Contents

- Public scope and ownership
- Frozen terms and three exit conditions
- Monitor and assess events
- Public data and safe update

## Public scope and ownership

The user authorizes a public investment dashboard in JinhaPark/skills
`discover-value-stocks/subskills/data/README.md`, backed by `discover-value-stocks/subskills/data/cashflow-dashboard.json`. Publish only this reviewed
summary subset, not private research caches, full internal assessments, agent
traces, account details, private Library links or signed URLs. Preserve unrelated
README content and repository files. Only the assigned dashboard publisher may
write these two paths; this does not authorize research authors to edit skill
code. Skill evolution remains a separate gated next-run process.

Use English field labels and concise repository prose. Keep the full investment
report in Korean. Include every confirmed published vintage in the dashboard,
newest **original publication week first**. Render at most 12 weekly paragraphs;
retain the complete record in the public JSON archive. Within a week, show the
latest publication vintage and note any other archived vintages in that same
paragraph. Add at most one paragraph per week; later assessments update it in place.
Later assessment dates update the same row; they do not move an old idea to the
newest-publication position. Keep corrections as new linked vintages in the archive and preserve
the original; never add a second paragraph for the same publication week. Keep known legacy rows such as HPQ even without its original report.

## Frozen terms and three exit conditions

Render one paragraph per ISO publication week: Date, company/ticker, cover-letter
investment thesis, target entry, TP, SL, Horizon, status and latest evaluation.
TP, SL and Horizon expiry are the three exit conditions. Always display
each named field. Null means `N/A` with a reason, never zero, an omitted field or an
invented value. Target entry is the original proposed inclusion price, not an
observed fill, current quote or the DCF value. Preserve its currency and original
share basis. Keep actual/reference entry observations separate.

Freeze `target_entry`, `take_profit` and `stop_loss` in recommendation.json as
`{value,currency,na_reason}`. Numeric values must be finite and positive; missing
values need a reason. Freeze the Horizon in the existing `target_horizon`, retaining
its end date, duration/start basis if stated, calendar rule and exchange time zone.
Do not substitute a conventional 12-month horizon when none was published.
The public `horizon` is a projection of that frozen horizon, not a
second model. Do not derive SL from a downside scenario or relabel an intrinsic
DCF value as TP unless the original judgment explicitly sets it as that target.

Record numeric barriers in `barrier_basis` with currency, split-adjusted
ex-dividend price basis and original share basis. Reconcile splits, ADR changes
and other corporate actions using sourced adjustments in derived observations;
never change the original price commitments. Do not use total-return indices for
price-barrier checks. Watch/avoid rows do not imply long/short positions.

Use a consistent paragraph budget: target 100–140 English words for fully recorded
ideas, hard maximum 160. Keep the cover-derived thesis within 50 words and the
latest evaluation within 45 words; preserve all required fields. Legacy N/A entries
may be shorter. Do not pad unknowns or automatically truncate facts. Revise verbose
summaries before publishing. The renderer enforces the upper bound; the reviewer
checks similar depth and emphasis across weeks.

Derive the public investment thesis from the four published cover-letter paragraphs,
not a new thesis written from later information. During assembly save their exact
text as cover.md and freeze recommendation.cover_letter={path,sha256,summary}.
The summary is a faithful concise English rendering of that cover; preserve its
judgment, catalyst, cash-flow logic and material caveat. Public row thesis equals
that summary, thesis_source is published_cover_letter, and cover_sha256 matches.
For an unavailable original cover use N/A with a reason and null source/hash.

## Monitor and assess events

Check each historical row on every scheduled research invocation, including runs
with no new selection or a blocked new report. This is a weekly observation
process, not real-time alerts or automatic trading. Refresh sourced observations
covering the interval since the last confirmed check and reconcile earlier gaps.
A latest quote below TP is not evidence that TP was never touched in between.

Use `scripts/assess_barriers.py` for explicit, sourced activation/price intervals
and horizon sessions. It is a consistency/calculation aid, not proof of source
truth or a trading engine. Establish the monitoring basis before judging hits:
a pending target-entry opportunity is not an invested position. A hypothetical
entry requires a sourced activation event; reference-price monitoring must be
labeled as such. Never infer that the user bought or sold.

Check intraday high/low only when that observation convention and coverage are
supported. Record the observed time interval and sources. If TP and SL are both
within the same bar, or the activation/horizon lies within a coarse bar, report
order uncertainty. Do not select the favorable event or assign a fictitious fill
at TP/SL; gaps and slippage can differ from those thresholds. Missing observations
mean unknown, not not-hit. Preserve all prior events append-only; an incremental
helper's first event is first only within its supplied interval unless complete
history establishes otherwise. Unset sides stay N/A independently of set sides.

When TP, SL or the evidenced original horizon is reached, append an assessment
with event date/interval, observation cutoff, source links, price/total/benchmark
outcomes where verifiable, and independent thesis/scenario evaluation. Keep a
pending assessment explicit if evidence is missing. Distinguish first-trigger
review from the original-horizon return evaluation; early TP/SL does not rewrite
that horizon or retroactively turn the recommendation into an executed strategy.
Use the existing assess-track-record and reflection owners for analysis. Preserve
losses and invalidated theses as carefully as successful outcomes.

## Public data and safe update

`render_dashboard.py` defines and validates the exact public schema. Each row
contains a stable publication_key, publication date, company/ticker, frozen thesis
(or thesis_na_reason), source origin, optional public report URL, three price
objects, projected horizon, current status and append-only assessments.
Each assessment has assessed_at, event, event_at/null, summary and source_urls.
An event timestamp is the observation boundary, not an invented exact hit time;
state any observed interval/order uncertainty in the short assessment. Use `tp_sl_ambiguous` when both price conditions were observed without order;
explain any price-versus-Horizon ambiguity in status/summary. `not_assessable` is
valid for missing legacy inputs. Never imply complete historical coverage when
only the known ledger subset is available.

Read current main and both public files immediately before updating. Reconcile
rows with the cumulative ledger; a new row requires confirmed report delivery or
explicit user-confirmed legacy provenance. Prepare and independently review the
public projection. Use the helper's immutable upsert/check before rendering.
Replace only the `cashflow-dashboard:start/end` marked block in README, preserving
other sections. Commit README and data together with an expected-head guard.
On conflict, fetch/reconcile the new head and rerender; never force-push or drop
concurrent rows/assessments. A dashboard-only commit may advance main before skill
evolution; rebase the candidate onto that actual head and revalidate its exact
commit. The running research package stays pinned throughout.

Record actual dashboard commit/result in the private run cache. On failure retain
the pending projection and retry idempotently next invocation; do not mark the
README updated or redo an already delivered report. Dashboard failure is separate
from report delivery. After a report is delivered, add its row and complete any
historical updates; if delivery is blocked, publish only verified historical
updates and never add the undelivered candidate. Keep the report as one deliverable
and use README as the explicitly requested cumulative dashboard.

A delivered no-selection report may use a No selection entry with N/A prices and
Horizon, reflecting its actual cover conclusion. It does not become a stock
recommendation or a simulated position.
