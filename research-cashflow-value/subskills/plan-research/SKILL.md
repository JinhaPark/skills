---
name: plan-research
description: Plan one cash flow equity research run, restore checkpoints and publication history, and define dependency-aware delegation contracts. Use only for the planning stage delegated by research-cashflow-value.
---

# Plan the research run

## Scope and inputs
Read [selection policy](../../references/selection-policy.md) and the
[handoff contract](../../references/handoff-contract.md).
Require the request, skill version, run directory, reporting date, intended
price cutoff, available tools and existing manifest/publication records.
Prepare the executable plan; do not research a stock or draft the report.
Do not publish, change schedules or repositories, or launch sibling phases.

## Procedure
1. Inspect actual source, calculation, file, persistence and subagent tools.
   An instruction mentioning agents does not establish a callable agent tool.
2. Resume existing work only after checking artifact existence, versions,
   input dependencies and prior validation. Preserve independent completed work.
3. For new work, copy `../../assets/workflow-template.json` from this skill's
   directory to the run's `manifest.json` and fill its supported fields.
   Do not invent a different manifest schema or treat a template as execution.
4. Keep task IDs plan, industry, peers, selection, model, outline, writing,
   review, publish. Preserve the template DAG and no_selection/blocked branches.
5. Restore the cumulative publication ledger from accessible durable records.
   Compare legal entity, ticker, exchange, share classes and ADR relationships.
   Seed absent history with HP Inc. (HPQ), published 2026-10-24, explicitly
   marked user-provided history; do not invent its original report URL.
6. Preserve previous protagonists for peer comparison but flag them ineligible
   as new protagonists. State unrecoverable history gaps honestly.
7. Carry forward steel-company and politically dependent Alaska/Greenland
   oil-theme exclusions. Geography alone is not an exclusion criterion.
8. Assign each task an owner, inputs, prerequisites, bounded scope, output
   paths, completion evidence and permitted write paths. Avoid shared writes.
9. Plan industry demand and supply/dissent lanes in parallel; after pool
   approval, plan company extractions and separate CDS collection in parallel.
   Sequence selection, models, outline and dependent writing by their inputs.
10. Reserve independent factual/calculation and editorial review work.
    Plan one integrated Markdown deliverable, not separate final reports.
    Assign a reflection owner distinct from the editor and all report authors,
    plus a different peer reviewer for any proposed workflow changes.
    Start assess-track-record after history restore, parallel with industry work.
    Plan cache checkpoints after every accepted stage and every exit outcome.
    Assign a dashboard publisher for the two authorized public paths; prepare
    historical updates even if the current research report cannot be delivered.
    Preserve the nine research task IDs; use separate lifecycle artifacts for
    assessment, reflection, cache receipts and evolution decisions.
    Load prior validated improvements at bootstrap; freeze this invocation's
    skill commit. Include interrupted-run recovery and pending assessments.
11. If agents are unavailable, retain the same stages, artifacts and handoffs
    sequentially and record the limit; do not claim independent agent review.

## Outputs
- `workflow-plan.md`: owners, boundaries, dependencies and execution limits.
- `manifest.json`: populated template with truthful task states.
- `history-check.md`: ledger sources, restored identities and missing history.
- `handoffs/plan.json`: a shared-contract handoff.

## Pass gate and handoff
Require an acyclic plan, explicit owners, one delivery target, recoverable
output paths and capability limits. Hand off the plan and ledger references,
constraints and unresolved history issues to industry research. Never mark
later stages complete in advance. Return blocked inputs visibly to the parent.
