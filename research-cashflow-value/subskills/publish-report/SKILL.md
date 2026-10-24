---
name: publish-report
description: Assemble reviewed sections into one complete Korean Markdown investment report, verify its delivery, and update publication history. Use only for an assigned final publication stage.
---

# Publish Report

## Inputs

- Require explicit publication assignment from the orchestrator.
- Read approved outline, complete sections, latest comparison/model basis, and both review lanes.
- Read [editorial policy](../../references/editorial-policy.md), [quality policy](../../references/quality-policy.md), and [handoff contract](../../references/handoff-contract.md).
- Read manifest, publication ledger, incoming handoffs, and the parent HPQ seed exclusion.
- Confirm all required stages passed at current versions by inspecting actual artifacts.
- Refuse publication with unresolved material findings or missing required sections.

## Assemble

1. Combine complete reviewed sections in order without replacing them with a new short summary.
2. Preserve reasoning, tables, original links, assumptions, counterevidence, and important limits.
3. Harmonize transitions, terminology, dates, units, and conditional conclusions.
4. Generate the opening peer table from the frozen comparison basis after body review.
5. Keep NTM FCF yield and actual CDS premium in the same table, retaining NA reasons.
6. Include the fixed pool, including covered companies and CDS-NA peers permitted for comparison.
7. State price/data date, NTM interval, forecast/FCF basis, CDS conditions, and sources near the table.
8. Write exactly four short cover paragraphs last, reflecting the reviewed body.
9. Cover industry/profit capture, peer differences/selection, valuation/price, then approach/risks.
10. For no selection, explain rejection grounds and reopening conditions instead of fabricated values.
11. Place table and necessary notes first, then cover paragraphs and full deep report.
12. Use the prescribed selected-company or industry/no-selection title.
13. Preserve the going-concern/distress comparison, price margins, p basis, recovery, and sensitivities.
14. Keep hypothetical assumptions separate from verified estimates and do not backfill NA.
15. Check comparison, cover, and body use the same approved data/model versions.
16. Return substantive late changes for targeted review rather than bypassing gates.

## Persist and deliver

- Write one user-facing `report.md` with opening table, four cover paragraphs, full body, and sources.
- Preserve supporting models, drafts, handoffs, and reviews as durable internal artifacts.
- Use the available persistent file mechanism and existing supported delivery channel.
- Do not post to JinhaPark/news, mix AI-news feeds, create Discord routing, or claim chat relocation.
- Do not present scattered partial sections as the requested final deliverable.
- Return the actual report link and concise completion status.
- Write the immutable pre-delivery `publication.json` with report ID, artifact path/version and ready status.
- After observed delivery write a separate `delivery-receipt.json` with actual saved link/outcome; do not alter hashed pre-delivery artifacts.
- Confirm actual artifact availability and supported delivery before ledger completion.
- Distinguish selected-company publication, no-selection report, blocked run, and interrupted delivery.
- Do not add unconfirmed attempts to the completed-company exclusion set.

## Pass gate and handoff

- Run the parent report gate against the manifest and inspect final Markdown structure and links.
- Require current-version reviews, one complete report, and matching table/cover/body inputs.
- Require the opening comparison and four cover paragraphs; preserve no-selection data limitations.
- Report blocked fields and delivery failures without claiming publication success.
- Write `handoffs/<task-id>.json` with final artifact and ledger references.
- Let the orchestrator accept publish-stage assembly artifacts and run --through publish before delivery.
- Stage completion means assembly passed; actual delivery remains separate and is confirmed afterward.
- Do not mutate schedules, skills repositories, other reports, or external destinations.
