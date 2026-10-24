---
name: write-section
description: Write one complete Korean investment report section from approved evidence and models. Use for scoped parallel writing, dependency-aware handoffs, and targeted revisions.
---

# Write Section

## Inputs

- Receive section ID, scope, exclusions, pass criteria, and an owned output path.
- Read the approved outline, terminology, data/model versions, and direct predecessor handoffs.
- Read [editorial policy](../../references/editorial-policy.md) and [handoff contract](../../references/handoff-contract.md).
- Read [evidence policy](../../references/evidence-policy.md) for business/FCF sections.
- Read [valuation policy](../../references/valuation-policy.md) for valuation/risk sections.
- Open original source/model artifacts as needed; handoff summaries are navigation, not evidence.
- Start only when actual section dependencies are complete at current versions.

## Execute

1. Produce publication-ready Korean honorific prose, not a synopsis or expanded outline.
2. Answer the assigned question using evidence-linked claims and the required tables.
3. Respect adjacent-section boundaries and begin with the agreed incoming connection.
4. Explain mechanisms and their effects on earnings, investment, cash conversion, or value.
5. Use enough explanation to assess the argument; tables cannot replace reasoning.
6. Use approved metric/model outputs with periods, currency, units, and share basis intact.
7. Distinguish facts, management statements, consensus, own estimates, scenarios, and hypotheses.
8. Cite original URLs and document/table locations near important facts and figures.
9. Preserve NA and specific reasons; never replace unavailable values with guesses or zero.
10. Include the strongest relevant counterevidence, uncertainty, and inference limits.
11. Follow the terminology file and avoid repeating earlier definitions at full length.
12. Briefly refer to established findings while developing this section's new contribution.
13. Supply complete required tables with explanatory paragraphs and consistent labels.
14. Preserve NTM/TTM, FCF/FCFF/FCFE, Q/P, and value-margin/future-return distinctions.
15. Do not invent assumptions, change the candidate/pool, or recompute target values ad hoc.
16. Send new evidence or contradictions to the designated data/model owner as a change request.
17. Identify affected claims, metrics, and downstream sections; wait when the issue is material.
18. Revise with approved updated inputs and report their versions.
19. End with a connection to the next question without inventing its result.
20. Maintain depth through evidence and explanation rather than repetition or padded length.

## Outputs

- Write full prose to `sections/<section-id>.md` or the explicitly assigned owned path.
- Write `sections/<section-id>.claims.json` mapping material claims/table values to evidence and metrics.
- Write requested corrections to `changes/<task-id>.json`, or an empty list if none are outstanding.
- Write the outgoing `handoffs/<task-id>.json` under the shared contract.
- Include a concise summary, predecessor connection, key figures, limits, and next-stage input.
- Reference full prose, source artifacts, and calculations so summaries do not become the only evidence.
- Declare missing required content explicitly rather than calling the section complete.

## Pass gate

- Require full prose, required tables, nearby citations, counterevidence, and the section question answered.
- Require versions to match the approved data/model basis.
- Reject invented values, unapproved changes, duplicated neighboring sections, and contradictions.
- Do not write the cover, final report, or unrelated sections unless explicitly assigned.
- Do not edit another writer's files or launch sibling phases.
- Return owned artifact references and completion evidence to the orchestrator.
- Let the orchestrator close aggregate `writing` only after every required section passes.
