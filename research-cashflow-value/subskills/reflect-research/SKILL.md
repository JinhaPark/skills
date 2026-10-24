---
name: reflect-research
description: Independently assess a cash flow research report, prior recommendation outcomes, and workflow failures, and produce an evidence-linked improvement backlog. Use before publication and at every run closeout, including blocked or no-selection runs.
---

# Reflect on research

## Inputs and independence

- Accept checkpoint `prepublish` or `closeout`, run directory, canonical versions, editor/author identities, and owned output paths.
- Read [reflection policy](../../references/reflection-policy.md), [quality policy](../../references/quality-policy.md), and [handoff contract](../../references/handoff-contract.md).
- Read the actual assembled report, source evidence, calculation traces, review findings, task/cache records, and historical assessment artifacts relevant to the checkpoint. A summary maps evidence; it does not replace evidence.
- Operate as a separate agent from the editor, section authors, and numerical model author. Record actual runtime identity and trace reference; an invented role label does not establish independence.
- Request corrections through the coordinator. Do not edit canonical data, approve your own proposed skill patch, publish independently, or change the pinned run package.

## Prepublication checkpoint

1. Inspect every quality dimension in the policy. Challenge the argument's weakest link and strongest counterexample; do not simply summarize ordinary review lanes.
2. Inspect the complete assembled `report.md`, including the opening peer table and cover, after assembly but before delivery. Verify all sections and the investment conclusion use the same accepted evidence/model versions.
3. Audit a risk-based sample of original claims and independently recompute all conclusion-changing calculations. Record sampling scope and unreviewed limits rather than claim exhaustive verification.
4. Trace selection bias, missing-data bias, stale cache reuse, peer pool changes, unsupported growth/profit capture, and overconfident conclusions. Preserve NA and valid no-selection outcomes.
5. Compare prior findings with actual repairs. A closed ticket without corrected artifacts remains unresolved.
6. Write `reviews/reflection-prepublish.json` using the policy contract. Block publication while a critical finding remains; ordinary review passing cannot override it.
7. Recheck corrections and affected descendants. Bind acceptance to exact versions and hashes of both the complete report and frozen recommendation record. Any subsequent material edit requires renewed reflection acceptance.

## Every-run closeout

1. Run even when research, publication, caching, or delivery failed. Record the real terminal state and accessible evidence; partial reflection is `blocked`, never silently omitted.
2. Read the full-cohort output of [assess-track-record](../assess-track-record/SKILL.md). Separate matured returns from interim marks, price outcomes from thesis validity, and process accuracy from investment luck. Identify missing original commitments and outcome data.
3. Inspect cache hit/miss/invalidation decisions, handoff failures, duplicated work, version drift, runtime limits, storage receipt, observed delivery and the README update. Check one bounded weekly paragraph, cover-derived thesis, frozen TP/SL/Horizon and event evidence; a failed dashboard update remains pending separately from delivery. A ready file does not prove delivery.
4. Attribute issues to supported causes, hypotheses, or unknown causes. Distinguish analyst mistakes, access limitations, market uncertainty, and workflow defects. A single poor return does not prove a broken method.
5. Write `reflection/closeout.json` and a prioritized backlog. For each proposed change preserve dissent, expected benefit, downside, acceptance test, and affected stages.
6. Send the accepted handoff to [evolve-workflow](../evolve-workflow/SKILL.md). Recommend `observe` when no adequately supported improvement exists; do not invent work to satisfy an edit quota.

## Completion gate

- Include exact evidence references, reviewed versions, actual identities, limitations, findings, and disposition.
- Retain prepublication and closeout records separately; neither overwrites the other or the original recommendation.
- Keep internal reviews and performance evidence durable with the run cache. Expose only material findings and brief prior-report follow-up in the user-facing report.
- When agents are unavailable, use `self_review`, disclose the limitation, and perform separated checks. Do not claim independent reflection; defer autonomous skill promotion until independent peer validation is available.
