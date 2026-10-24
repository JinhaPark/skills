# Independent reflection and workflow evolution

## Contents

- Roles and checkpoints
- Quality and attribution
- Record contracts
- Protected invariants
- Promotion and rollback

## Roles and checkpoints

Keep three responsibilities distinct: the editor integrates research, the reflection agent challenges the report and process, and an independent peer evaluates proposed workflow changes. Actual agent identities and traces establish separation. The patch peer must also differ from the reflection owner; the editor, reflection owner, and patch peer are three distinct roles with distinct actual agents. A worker cannot approve a patch it authored. Share evidence, but independently check conclusions.

Use two checkpoints. `prepublish` examines the complete assembled `report.md`, including overview and cover, after assembly but before delivery. It can block critical issues. `closeout` follows the observed terminal publication/delivery outcome, including blocked, interrupted, and no-selection runs; it incorporates historical assessment and creates the improvement backlog. Ordinary factual/editorial review and reflection are complementary. Freeze and hash accepted inputs. Material claim/value edits invalidate affected checks.

Run historical assessment alongside current research after restoring durable history. Missing or immature historical evidence is a disclosed limitation, not a reason to invent or silently skip evaluation. Historical analysis may identify controls already required by the current skill; only validated evolution changes later-run instructions.

Without independent agents, keep separated self-review records and disclose the limitation. Do not label this peer assessment, invent agent IDs, or automatically promote a candidate lacking independent validation. Resume pending experiments in a later capable run.

## Quality and attribution

Assess each dimension with `pass`, `concern`, `fail`, or `not_assessable`, evidence references, and limitations:

| Key | Required question |
|---|---|
| accuracy | Do original sources support definitions, periods, claims, and calculations? |
| completeness | Are comparison, operating model, mandatory valuations, risks, and constraints present? |
| reasoning | Does evidence connect industry economics to reinvestment, cash flow, value, and decision? |
| coherence | Do sections, opening table, cover, scenarios, and conclusion match frozen inputs? |
| calibration | Are uncertainty, counterevidence, NA, assumptions, and confidence proportionate to evidence? |
| outcome_assessment | Are all eligible historical recommendations evaluated at original horizons without hindsight? |
| workflow_reliability | Did delegation, handoffs, invalidation, caching, persistence, and delivery operate as recorded? |

Do not collapse these dimensions into one self-awarded quality score. Track observable measures such as material errors, unsupported claims, stale inputs, unresolved blockers, duplicate work, data coverage, forecast error, thesis violations, and mature return/benchmark outcomes with denominators and sample sizes. Do not optimize only for rising prices, length, tool-call count, or reviewer agreement.

Separate process quality from outcomes. A stock can rise for unrelated reasons or fall despite supported reasoning. Compare realized operating drivers and original falsification thresholds as well as price/total return. Distinguish forecast error, execution error, changed conditions, and unknown attribution. Avoid general performance claims from small or immature cohorts; retain negative and delisted cases. Probability calibration applies only where defensible probabilities were originally recorded, never retrospectively invented probabilities.

Each finding contains `finding_id`, `severity` (`critical|major|minor`), `evidence_references`, `affected_artifacts`, `affected_stages`, `root_cause_status` (`supported|hypothesis|unknown`), `impact`, `remedy`, `status` (`open|resolved|accepted_limitation`), and `verification_references`. An issue that could change selection, value, or judgment is critical until resolved. Major issues require correction or evidence-backed visible limitation and explicit acceptance. Cosmetic issues do not block useful research. Critical issues cannot be accepted as limitations to bypass publication gates.

## Record contracts

Use schema version 1 for sidecar records. Store them privately with the persistent run package and reference path/SHA-256 in workflow records. Do not commit confidential live run artifacts to the public source repository. Use null plus a reason for unavailable fields; never invent identities, timestamps, hashes, commands, or receipts.

Use [reflection template](../assets/reflection-template.json) for `reviews/reflection-prepublish.json`. Required keys are:

- `schema_version`, `checkpoint: prepublish`, `run_id`, `status: completed|blocked`, `mode: independent|self_review`;
- `reviewer_id`, `editor_id`, `author_ids`, `trace_reference` using actual identities/traces;
- `input_versions: {data, model}` and `reviewed_artifacts: [{path, sha256}]`, including exact complete `report.md` and frozen `recommendation.json` bytes;
- `dimensions` with all seven keys above; each contains `status`, `evidence_references`, and `limitations`;
- `findings`, `unresolved_critical`, `publication_gate: passed|blocked`, and `limitations`;
- `assessment_reference`, `assessment_sha256`, and `assessment_unavailable_reason` (null when assessment exists).

Prepublication requires an assessment record, even when it can only preserve the known cohort and legacy NA rows with coverage gaps. A null assessment reference with a reason is allowed only for a blocked, interrupted, or delivery-failed closeout; it cannot bypass release.

A completed reflection may correctly block publication. No-selection uses model version 0 when no model exists. `self_review` may support publication only with explicit disclosure and normal quality gates; it never counts as independent evolution evidence. A passed gate requires zero unresolved critical findings, no failed accuracy/completeness/reasoning/coherence dimension, and no unexamined critical calculation.

`reflection/closeout.json` uses the same identity/input/dimension/finding fields but `checkpoint: closeout`; omit `publication_gate` and do not require a report artifact on failed runs. Add:

- `run_outcome: delivered|no_selection_delivered|blocked|interrupted|delivery_failed` and `run_outcome_evidence_reference`;
- `assessment_reference`, `assessment_sha256`, and `assessment_unavailable_reason` (null when assessment exists);
- `cache_status: {status: persisted|partial|failed|unavailable, receipt_references: [], uncovered_artifacts: []}`;
- `delivery_status: {status: delivered|failed|pending|unknown, receipt_references: []}`;
- `backlog`: objects with issue ID, finding IDs, priority, affected stages, mechanism, expected gain, regression risk, acceptance test, and disposition `investigate|candidate|observe|resolved`;
- `next_run_handoff`: preserved constraints, unresolved risks, experiment IDs, and durable artifact references.

Closeout assesses the terminal research snapshot; then persist closeout/evolution as additional immutable snapshots. Put their own persistence receipts in the final cache index, avoiding self-hash dependencies or a record claiming it already saved itself.

Use [evolution template](../assets/evolution-template.json) for `evolution/decision.json`:

- `status: observe|proposed|validated|promoted|deferred|rejected|rolled_back`;
- `current_run_commit`, `base_commit`, `candidate_commit` (null before commit), `next_run_only: true`;
- `proposer_id`, `peer_reviewer_id`, `editor_id`, `reflection_owner_id` (equal to the closeout reviewer), `affected_author_ids`, actual `trace_references`;
- `changes`: at most three coherent objects with `id`, `finding_ids`, `changed_paths`, `mechanism`, `acceptance_test`, `regression_risk`;
- `discovery`: consulted skill/source/version/commit, inspected files, capability/dependency assessment, reuse/rejection rationale;
- `checks` keys `invariants`, `regression`, `skill_validation`, `forward_test`, each with `status: passed|failed|not_run`, `task`, `base_commit`, `candidate_commit`, local `evidence_reference`, `evidence_sha256`, and `result`;
- `peer_assessment`: `status: approved|changes_requested|rejected|not_run`, evidence references, unresolved material concerns, and justification;
- `invariants_unchanged`, `checked_invariant_ids`, actual `promotion_receipt` or null, `rollback_commit`, `reason`, `remaining_uncertainty`.

Use full 40-character commit SHAs. A promotion receipt contains `repository`, `branch`, `previous_sha`, `new_sha`, and actual tool-result `reference`; it must refer to the observed remote update, not an intended update.

Every passed check must point to a nonempty local JSON evidence file whose SHA-256 is verified. Its `base_commit` and `candidate_commit` must exactly match the outer check and evolution decision, and it must contain the actual `evaluator_id` and `result`. A generic pass string, a log for another candidate, or a claimed tool run without evidence cannot satisfy a check. Capture actual command/task traces and machine results in or alongside the evidence; hashes preserve integrity but do not prove truthful execution.

For `forward_test`, add these outer fields and repeat them exactly inside its hashed JSON evidence:

- `evaluator_id`: actual fresh execution agent identity, distinct from proposer, editor, reflection owner, and affected authors;
- `task_artifacts`: nonempty array of `{path, sha256}` for the exact task given to the fresh agent;
- `input_artifacts`: nonempty array of `{path, sha256}` for raw fixture inputs;
- `produced_artifacts`: nonempty array of `{path, sha256}` for actual output artifacts;
- `baseline_comparison`: `{path, sha256}` for the recorded comparison against the frozen baseline on the same task and inputs.

Resolve every evidence/artifact path inside the run directory and verify its bytes; do not accept traversal, symlinks, nonexistent files, placeholder hashes, or stale candidate bindings. Preserve actual task, observed behavior, baseline behavior, and unresolved differences. The patch peer differs from proposer, editor, reflection owner, and affected authors. An author cannot certify evaluation by filling in its own expected output. Missing or fabricated traces block promotion; structural validation alone cannot prove actual agent execution.

## Protected invariants

Check these IDs explicitly in every candidate patch:

- `selection`: Growth-industry economic peers precede NTM FCF/CDS comparison and absolute valuation; no mechanical FCF-minus-CDS ranking, invented CDS, or exclusion solely for missing CDS.
- `valuation`: Damodaran remains primary; growth/reinvestment/ROIC, FCFF/WACC, value bridge, mandatory distress/NA, P versus Q, and no double risk counting remain intact; multiples/reverse DCF remain auxiliary.
- `evidence`: No invented inputs, probabilities, sources, tests, reviews, delivery, or capabilities; retain timing/units, primary sources, uncertainty, and independent checks.
- `history`: Immutable publication commitments, whole-cohort evaluation, actual-delivery ledger, HPQ protagonist exclusion, steel/theme exclusions, and valid no-selection branch.
- `delivery`: One complete Korean Markdown report, opening NTM FCF/CDS table then four-paragraph cover and deep body; unchanged schedule/channel, no news-feed/Discord posting.
- `orchestration`: Staged full-section writing, dependencies/handoffs, canonical ownership, invalidation, separate reflection/independent patch peer, durable cache, honest failure states.
- `scope`: Only this skill package changes; no unrelated repo/account, dependency calculation code, original report, user constraint, or permission changes.

Retain proposals requiring changed constraints as separately explained recommendations, not silently applied patches. Routine in-scope improvements are already authorized and need no repeated confirmation.

## Promotion and rollback

Do not impose an improvement quota. `observe` succeeds when no change is justified; `deferred` preserves candidates blocked by missing capabilities. Keep failed experiment reasons privately without polluting reusable instructions with run-specific prose.

Promotion requires passing checks, actual fresh-context execution, independent peer acceptance without unresolved material concerns, unchanged invariants, and successful guarded remote commit/ref update. Keep regression fixtures and forward-test tasks distinct. Never remove failures, narrow cohorts, or weaken checks to improve apparent results. An evidenced workflow repair does not guarantee future returns.

Apply changes only to later invocations. Record the accepted version in the durable index, verify the next run pins it, and compare later reliability to baseline with sample size/uncertainty. Revert material regressions using new commits and expected-head guards; preserve history and extend regression coverage. Never force-push or improve old predictions by overwriting them.
