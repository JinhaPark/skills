---
name: evolve-workflow
description: Discover or create targeted research subskills and promote tested workflow improvements from independent reflection findings for later runs. Use only after a cash flow research closeout; never mutate the package used by an active report.
---

# Evolve the workflow

## Inputs and scope

- Read [reflection policy](../../references/reflection-policy.md), accepted `reflection/closeout.json`, pinned commit, durable backlog, previous experiment results, and actual runtime capabilities.
- Use the user's authorization to improve this research skill. Restrict changes to workflow code under `discover-value-stocks/`, excluding the entire `discover-value-stocks/subskills/data/` subtree; preserve financial/user invariants and leave unrelated repositories, the distress calculation dependency, automations, delivery channels, and credentials unchanged.
- Create a separate candidate checkout or patch. Preserve the active run's pinned package and original reports, recommendations, reviews, and assessments.
- Assign a proposer and independent peer evaluator. The evaluator must differ from the proposer, editor, reflection owner, and authors of affected code/content; retain actual identities and traces.

## Diagnose and choose a bounded change

1. Rank evidence-backed issues by materiality, recurrence, and repair cost. Default to one candidate batch containing at most three coherent changes per run. Retain other issues in the durable backlog.
2. Before editing, specify the failing behavior, finding IDs, affected stages, proposed mechanism, expected gain, regression risk, and observable acceptance test.
3. Search the available skill catalog and pinned repository. Read candidate SKILL.md files and needed scripts/references; record provenance, version/commit, dependencies, compatibility, and reuse/rejection rationale. Search snippets do not vet a skill.
4. Reuse suitable capabilities. Otherwise follow skill-creator to create the smallest required subskill. Do not copy untrusted instructions or invent tools. Discovery does not authorize new external disclosure or unrelated actions.
5. Integrate adopted subskills into orchestration dependencies, ownership, inputs/outputs, handoffs, cache keys/invalidation, failure paths, and tests. An unreferenced instruction is not integration.

## Validate and peer assess

1. Run applicable existing regression tests, skill validation, new failure-case tests, and original user-invariant checks. Record actual commands, versions, outputs, scope, and failures in hashed local JSON evidence bound to the exact base and candidate commits; bare pass labels do not count.
2. Have a fresh-context agent execute a representative task using the candidate and raw fixture artifacts. Do not reveal intended answers, suspected bugs, diagnoses, or private evaluator expectations. Keep evaluation fixtures separate from examples used to author the patch. The fresh execution agent must differ from proposer, editor, reflection owner, and affected authors. Preserve the exact task, raw inputs, produced outputs, and baseline comparison as verified hashed artifacts in the policy contract.
3. Give the independent peer the patch, requirements, raw evaluation artifacts, baseline comparison, and test traces. Require evidence-based assessment of the repair and possible regressions. Agent agreement is not proof; unresolved material dissent blocks promotion.
4. Compare candidate and frozen baseline on identical cases. Include missing-data, stale-input, failure/no-selection, and relevant numerical/coherence cases. Fix regressions within the bounded batch or defer; never weaken tests or discard failures to obtain a pass.
5. Write `evolution/decision.json`. `validated` requires passing checks, fresh-context execution evidence, independent peer acceptance, and unchanged invariants. Missing capabilities yield `deferred`, never invented validation.

## Promote for the next invocation

1. Promote after the current report decision, delivery outcome, and closeout are fixed. An evolution failure does not invalidate an otherwise correctly delivered report; preserve the last accepted skill and record the failure separately.
2. Commit the candidate before final evaluation so all check evidence names its exact commit. Set the decision to `validated` and run `python scripts/validate_lifecycle.py RUN_DIR --phase closeout` before any remote branch update. Inspect its result and actual peer evidence. Only then update the intended branch with its expected head SHA; never force-push. Reconcile concurrent changes and rerun affected validation before retrying.
3. Verify the returned commit and actual remote head. Record promotion receipt, new commit, parent, next-run applicability, and rollback target. Set `promoted` and rerun the closeout validator with the actual receipt. Local edits or test success alone are not promotion.
4. Keep the current report bound to its original commit. The next invocation resolves the accepted branch head once and pins it; never modify a live run in place.
5. On an observed material regression, revert the offending source commit with an ordinary reviewed commit and expected-head guard. Preserve experiment history and add the failure to regression coverage before re-promotion.
6. Treat `observe`, `deferred`, and `rejected` as legitimate outcomes. Do not claim improvement merely because instructions changed; identify the tested behavior and remaining uncertainty.
