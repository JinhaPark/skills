---
name: outline-report
description: Build an evidence-linked report outline and section dependency graph from approved cash flow research and model artifacts. Use before delegated section writing.
---

# Outline Report

## Inputs

- Read the assignment, industry findings, frozen pool, peer comparison, selection, and handoffs.
- Read the approved model or explicit no-selection `not_applicable` result.
- Read [editorial policy](../../references/editorial-policy.md), [quality policy](../../references/quality-policy.md), and [handoff contract](../../references/handoff-contract.md).
- Confirm source register, data/model versions, valuation date, and unresolved issues.
- Read relevant original artifacts instead of relying on summary conclusions alone.

## Execute

1. State the central question and conditional investment or no-selection conclusion.
2. Trace industry demand through supply, competition, profit capture, cash conversion, and price.
3. Explain how peer comparison narrowed candidates before DCF established the final decision.
4. Preserve alternative explanations and strongest disconfirming evidence.
5. Build explicit section dependencies without forcing independent sections into a serial chain.
6. Assign parallel writing only after each section's required inputs are approved.
7. Make dependent sections wait for completed predecessor artifacts and handoffs.
8. Give each section one question, substantive claims, evidence IDs, tables, and a completion test.
9. Define exclusions so writers do not duplicate adjacent sections.
10. Specify an incoming connection and intended outgoing connection for each section.
11. Require full explanation linking business facts to profit, cash flow, value, and investor implications.
12. Distinguish industry growth from firm profit capture and shareholder cash growth.
13. Reserve detailed company forecasts, FCF bridge, and DCF for a selected candidate.
14. Keep all fixed peers in the opening comparison, including CDS-NA and covered companies.
15. Reserve the mandatory going-concern/distress comparison even when some cells are NA.
16. Allocate depth by analytical importance; do not impose quotas encouraging repetition.
17. Define terms once and identify later sections that should briefly refer back.
18. Do not preselect a target price or require writers to justify a buy conclusion.
19. For no selection, focus on comparison, rejection grounds, uncertainty, and reopening conditions.
20. Do not fabricate single-company sections or unperformed calculations for no selection.

## Outputs

- Write `outline/report-plan.json` with section IDs, order, titles, owners, dependencies, and outputs.
- Include questions, claim/source/metric IDs, approved model version, and required tables.
- Include preserve/exclude boundaries, unresolved issues, and section-specific pass criteria.
- Write `outline/thesis-map.md` linking the thesis and competing explanations to evidence.
- Write `outline/terminology.md` with stable terms, abbreviations, definitions, and units.
- Assign owned section files to `sections/<section-id>.md`.
- Schedule comparison-table generation and four cover paragraphs after body review.
- Return `handoffs/<task-id>.json` referencing approved plans and direct dependencies.

## Pass gate

- Require source-backed coverage of material questions needed for the conclusion.
- Require numerical claims to point to approved metric/model versions.
- Require every table to have data or explicit supported NA treatment.
- Reject circular dependencies, duplicate ownership, and unsupported conclusions.
- Return material evidence gaps to their responsible research/model owner.
- Record minor limitations where disclosure permits useful analysis to continue.
- Ask the orchestrator to approve the outline and dispatch scoped writers.
- Do not publish, independently launch unrelated phases, or mark `outline` complete without artifacts.
