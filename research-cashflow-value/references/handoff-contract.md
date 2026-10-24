# Stage artifacts and handoffs

Use one run directory per report. Resolve its persistent storage reference during planning and record the actual retrieval method/URI, never an invented Library ID. The reusable skill contains no live run state. Never commit private research, cache, publication or assessment state into the skill repository. The user-authorized exception is the reviewed public summary in root README.md and data/cashflow-dashboard.json, owned by update-dashboard. The authorized evolution stage may commit reviewed workflow code and synthetic regression fixtures only.

## Ownership and evidence

The coordinator owns manifest.json and the cumulative ledger. Assign data.json and model.json to designated owners. Workers own only assigned files under research/, sections/, reviews/ and handoffs/.

sources.json records source_id, canonical URL, issuer, document title, publication date, accounting period, exact table/note/location, access time and accessible scope. Claims connect claim_id to source_id/location. Metrics add metric_id, entity ID, period, currency/unit, definition, value/null, fact/guidance/consensus/estimate/scenario, assumptions and unavailable reason.

data.json and model.json each carry an integer version >=1. Model version 0 means not created, never computed zero. Manifest versions.data/model represent current canonical versions. Reconcile evidence before freezing; register data/model hashes in task artifacts. Increment material versions and invalidate affected descendants; stale input versions fail gates.

## Task records and handoff JSON

Use assets/workflow-template.json. Each task has status pending/running/completed/not_applicable/blocked, deps, input_versions, artifacts (path and sha256), handoff (relative JSON path), and handoff_sha256 (its SHA-256 digest). Artifact/handoff paths resolve inside the run directory, must be nonempty regular files, and must exist before completion. Include data.json/model.json as appropriate. Hash after writing with SHA-256. Never hash a future file, invent a hash or use manifest as its own artifact.

Every completed stage handoff JSON contains:
- task_id; status: completed; artifact_paths; input_versions
- summary: substantive findings and their relevance to the next stage
- claims: claim/source/metric references and raw locations; [] only when no evidential claim is made
- key_metrics: values/units/periods/definitions, or [] for non-numeric work
- uncertainties: counterevidence, issues, NA reasons, conditions; [] if none found
- next_inputs: downstream inputs and conditions to preserve

Scoped lane/section IDs and handoffs sit beneath the nine main stage records; coordinator accepts/aggregates their results while preserving actual agent IDs/tool traces and source references. Handoffs contain concise summaries plus artifact pointers, not hidden reasoning traces or full conversation history. Full drafts/evidence remain directly accessible.

## Branches and review

Required DAG: plan → industry → peers → selection → model → outline → writing → review → publish. Independent lanes within stages may run in parallel; dependent sections wait for accepted predecessor drafts. Only the coordinator schedules phases.

decision is selected/no_selection/blocked. Only model may be not_applicable, only for no_selection, with reason and current inputs. Still complete comparison, outline, writing, review and publish. Blocked runs cannot pass final gates or enter the stock publication ledger. Review sets passed=true and unresolved_critical=0 only after findings are resolved and checked.

## Artifacts and delivery

Use research/industry.md, research/pool.json, research/peer-evidence.json, data.json, selection.json, model.json when applicable, outline.json, sections/*.md, reviews/*.json, handoffs/*.json and report.md. Add entity/section identifiers as needed and register exact paths. Keep task artifacts immutable once accepted; create a new version instead of overwriting an upstream artifact.

report.md is the sole user-facing deliverable. Keep the rest as internal durable evidence/checkpoints. Preserve source links/calculations in the report where useful. After actual delivery set delivery.status=delivered and report_reference to the observed saved report link; before delivery use ready/pending. A gate never certifies external delivery or financial truth automatically.

## Lifecycle sidecars

Keep the nine-stage manifest compatible. Assessment runs after plan in parallel
with industry and finishes before prepublication reflection. Prepublication
reflection reviews the assembled report before delivery, so it is not a dependency
of the publish assembly task itself. Any assembled-report change invalidates that
approval. Run the independent lifecycle release gate before external delivery.

Cache checkpoints cover every invocation, accepted stage and exit, with real
provider receipts and content hashes; follow cache-policy.md. Persist the cache
index only after its referenced objects. A local snapshot is not durable storage.
Keep a stable run ID for a retried scheduled run and distinct attempt/checkpoint
IDs; reconcile actual delivered receipts before any retry to avoid duplicate
delivery. New weekly runs receive new IDs and refreshed market observations.

Use assessment/track-record.json for the full known publication cohort; retain
legacy missing-data rows. Store immutable recommendation.json before delivery,
then link the real delivery receipt. Store reviews/reflection-prepublish.json,
reflection/closeout.json and evolution/decision.json using their documented
contracts. Keep actual role IDs and invocation provenance; summaries never claim
independence in place of runtime agent evidence. Evolution may be deferred;
publication must not falsely imply the skill was successfully updated.

Dashboard is a lifecycle stage after accepted historical assessment and the current delivery outcome. Record its actual commit or pending failure separately from report delivery, and checkpoint it before reflection closeout. Historical updates still run after a blocked current report; never add an undelivered candidate.
