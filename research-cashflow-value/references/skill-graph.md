# Modular skill graph

Treat `assets/skill-graph.json` as the coordinator's executable planning contract.
It declares skill identities, canonical package-relative paths, invocation phases,
input/output contracts, dependencies, readiness conditions, gate commands and
parallel fanouts. Keep each registry entry as its own SKILL.md module. Loading the
graph does not load every worker's instructions into the editor's context.

## Resolve and dispatch

1. Pin the repository commit and the graph SHA-256 at bootstrap. Resolve every
   registry path from that same package version. For separately installed skills,
   map the registry's stable skill name to the observed installed package identity
   and verify matching provenance before use; do not assume a generated package ID
   or combine versions. Retain the canonical paths for repository execution.
2. Validate with `python scripts/skill_graph.py assets/skill-graph.json
   --package-root .` from the package root. Read the selected node's SKILL.md and
   required references only when dispatching that node. A graph entry is a
   reference to a skill, never a replacement for the skill's instructions.
3. Store a separate run `graph-state.json`. Preserve the nine research tasks in
   `manifest.json` and the existing lifecycle contracts. The graph does not change
   their schemas. Mirror inspected acceptance and failure evidence into graph
   state; never use this sidecar to bypass an existing validator.
4. Ask `python scripts/skill_graph.py assets/skill-graph.json --state
   RUN_DIR/graph-state.json --available-slots N` for eligible aggregate nodes.
   Use actual free runtime capacity for N. This command returns a dispatch plan;
   it neither starts agents nor changes state, sends reports or writes repositories.
5. Give each worker its node/phase, allowed output paths, current input versions,
   concise predecessor handoffs and pointers to complete accepted artifacts.
   Accept outputs only after inspection and the skill's pass criteria. Cache the
   real result, then refresh state and dispatch newly eligible work.

## State and gate receipts

Use this shape, with actual hashes and evidence paths rather than the placeholders:

```json
{
  "decision": "undecided",
  "outcome": "running",
  "outcome_evidence_reference": null,
  "outcome_reason": null,
  "input_hashes": {},
  "nodes": {},
  "gates": {}
}
```

`decision` is `undecided`, `selected`, `no_selection` or `blocked`. `outcome` is
`running`, `blocked`, `interrupted`, `delivery_failed`, `delivered` or
`no_selection_delivered`. Keep it
`running` while required research or delivery is in progress. A terminal outcome
is an observed decision, not an instruction to report success. After it is fixed,
no research, assessment, assembly or delivery node can start from old accepted
predecessors; only terminal lifecycle nodes remain eligible. Finish an independent
assessment before fixing the outcome, or record its cancellation and restore it
under an explicitly resumed/new invocation rather than silently restarting work.

For every terminal outcome, require `outcome_evidence_reference` pointing to the
observed outcome record/receipt and `outcome_reason` preserving its actual cause.
Copy graph `outcome` unchanged to closeout `run_outcome`, and copy its evidence
reference to `run_outcome_evidence_reference`; retain the cause in closeout findings
and the referenced record. The JSON `outcome_contract` declares this exact mapping.

| Graph outcome | Closeout run_outcome | Observed condition |
|---|---|---|
| running | No terminal closeout value yet | Work or required reconciliation remains in progress |
| blocked | blocked | Evidence, capability or a failed quality gate prevents an eligible report |
| interrupted | interrupted | Invocation execution stopped before a report/delivery decision could finish |
| delivery_failed | delivery_failed | An actual supported delivery attempt failed after preparation/release |
| delivered | delivered | Selected-company report delivery has an observed receipt |
| no_selection_delivered | no_selection_delivered | No-selection report delivery has an observed receipt |

A node status `failed` remains valid, but a generic graph outcome `failed` is
rejected because it loses this distinction. Migrate an older sidecar only from
its actual evidence: a failed peer-data collection normally yields blocked; an
interrupted runtime yields interrupted; a failed delivery attempt yields
delivery_failed. If the cause cannot be established, keep it unresolved and
record the uncertainty instead of inventing a terminal outcome or receipt.

Each node record has `status`, `input_hash`, and `evidence` (nonempty observed
artifact/receipt paths). Allowed statuses are `pending`, `running`, `accepted`,
`not_applicable`, `blocked`, `failed`, `cancelled`. `accepted` means the coordinator
actually checked and accepted its current artifacts; it does not mean a worker
said it was done. `input_hash` must match `input_hashes[node_id]`, a SHA-256 of the
canonical serialized material inputs, versions, upstream hashes, graph hash and
pinned skill version. Preserve old attempts instead of editing their evidence.

Only `model` may be `not_applicable`, only for a comparison-backed `no_selection`,
with a reason and evidence. The model node is dispatchable on both report paths:
use `phase_by_decision.selected` for normal modeling and
`phase_by_decision.no_selection` to ask model-value to inspect the accepted
selection and emit an explicit not-applicable result. This latter invocation
must not compute fictitious valuations. The coordinator inspects its artifact,
reason and current fingerprint before recording not_applicable in graph state
and the compatible manifest record; merely seeing no_selection never skips it.
If modeling was already performed and rejected the candidates, retain its accepted
results without rerunning the skip phase. Failure/cancellation records likewise
require a reason, evidence and current input_hash. A stale failure from another
attempt cannot unlock dashboard or closeout; reconcile it and append a current
failure/cancellation record without rewriting history. Never convert a blocked
predecessor to accepted to unlock a descendant.

A gate receipt keyed by the graph's gate ID has `passed: true`, the exact declared
`command`, `input_hash` matching the target node's current input fingerprint, and
nonempty `evidence` pointers to actual execution output. The planner checks these
record bindings; it cannot attest that a command ran, a source is true or an agent
was independent. Inspect receipts and run the existing workflow/lifecycle scripts
as required. Financial verification, reflection and actual delivery confirmation
remain separate requirements.

## Parallelism and reusable phases

Assessment and industry become eligible together after accepted planning.
Industry demand and dissent, peer companies and credit, and independent review
lanes have bounded fanouts. Writing uses the accepted outline's section DAG:
validate unique IDs, acyclic dependencies and exclusive output ownership first;
launch only sections whose predecessor artifacts are accepted at current versions.
Supply their summaries and full artifact pointers to dependent writers. Do not
reduce completed sections to their summaries during integration.

A fanout consumes the coordinator's remaining slots; it does not create a new
unbounded agent pool. Materialize exact child IDs from the approved pool/outline,
preserve their receipts and join every required child before accepting its
aggregate node. Failed or missing children are not silently dropped. Only the
coordinator launches sibling work.

The same module may have separate phase-scoped invocations: `publish-report`
handles `publish` assembly and later `delivery`; `reflect-research` handles
prepublication and closeout; `cache-run` handles bootstrap, checkpoints and final
persistence. Keep separate invocation/attempt IDs, artifacts and receipts. Assembly
never implies delivery. The independent reflection owner cannot be the editor or
report author, and the improvement peer cannot approve their own candidate.

## Failure, cache and invalidation

On a blocked or failed report, stop new affected work, reconcile active workers
and record unstarted dependent nodes as cancelled with evidence of the cause.
Do not mark them complete in the research manifest. Whole-cohort assessment may
finish independently. Once its output is accepted and current delivery is terminal,
`dashboard` can update historical published recommendations without adding an
undelivered candidate. If assessment or access fails, record dashboard blocked or
failed with a pending retry; then close out the actual failure.

`reflection-closeout` waits for every research/delivery/dashboard invocation to
be terminal, including explicit cancellations. It runs for all outcomes. Evolution
requires accepted closeout, and remains observe/deferred when checks or independent
review are unavailable. Its skill still enforces the existing closeout validation
before any remote promotion. `cache-final` also runs after failed reflection or
cancelled evolution; do not lose failure evidence because the happy path stopped.

The checkpoint hook invokes `cache-run` after every accepted, not-applicable,
blocked, failed or cancelled stage, keyed by run/node/attempt/input hashes. It is
an event hook, not a cyclic dependency or a recursively triggered cache of itself.
Cache persistence failures retain recovery artifacts and degraded status; they
cannot fabricate durable receipts or automatically accept research. Save the
final closeout validator result even when it fails.

When a material input changes, recompute affected fingerprints and invalidate
transitive consumers, child joins, handoffs, gate receipts and cache reuse. Recheck
only affected work plus cross-section consistency. Published history stays
immutable. Validated skill changes update the graph/registry and affected tests
for the next invocation, while the current run keeps its pinned graph and skills.
