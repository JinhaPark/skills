---
name: update-dashboard
description: Update the public README investment dashboard from frozen published recommendations and verified TP, SL, horizon and thesis assessments. Use after historical assessment and confirmed delivery, or for historical-only updates when the current research run is blocked.
---

# Update the investment dashboard

1. Read [dashboard policy](../../references/dashboard-policy.md), accepted historical
   assessment, frozen recommendations and actual delivery receipts. Read current
   JinhaPark/skills main, root README.md and data/cashflow-dashboard.json. Preserve
   the invocation's original skill commit; reading a newer head for a guarded
   dashboard write does not upgrade its executing instructions.
2. Reconcile every known confirmed publication vintage. Preserve original dates,
   cover-letter thesis, company, proposed entry, TP, SL and Horizon. Use N/A plus a
   reason for absent original terms; retain legacy HPQ without invented prices.
3. Have the historical assessor check all three exit conditions from sourced
   observations using assess_barriers.py. Keep pending entry, unknown coverage,
   ambiguous event order and hypothetical/reference monitoring explicit. Request
   event and thesis evaluation when a condition is reached; do not trade.
4. Project only the authorized public fields. Keep full private caches, internal
   traces and private/signed links out of both public files. Use original report
   values rather than recalculating targets from today's information.
5. Independently inspect the projection against originals and accepted assessment.
   Use render_dashboard.py to validate/upsert rows and render the marked README
   block as at most one paragraph per ISO publication week, latest week first,
   showing only the latest 12 weeks. Preserve all older records in the JSON archive.
   Keep paragraphs within 160 words, cover-derived thesis within 50 and latest
   evaluation within 45; do not truncate automatically or invent filler. Preserve prior rows and assessments.
   Add a new row only after actual delivery; a blocked current run may still update
   earlier published ideas. Do not confuse report delivery and dashboard success.
6. Verify all three exit fields and explicit N/A reasons, date ordering, safe
   links and unchanged surrounding README sections. Commit the JSON and README
   together using the observed main SHA. Reconcile concurrent updates and retry
   without force or duplicated rows/events.
7. Return actual commit/reference and concise handoff to the independent reflection
   owner. Cache the public projection, source hashes, review and update receipt.
   If access/save fails, record pending state and a retry key; never claim success.
   Leave skill-code evolution to its separate reviewed, next-run process.

Operate only on the two public paths above. The parent orchestrator owns scheduling
and accepts this lifecycle stage; workers do not independently publish other data.
