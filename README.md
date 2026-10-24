# Skills

A modular skill repository for investment research, travel-photo editing, and chat-session handoffs. Each skill's `SKILL.md` defines its scope and execution procedure.

## Main skills

| Skill | Role |
| --- | --- |
| [discover-value-stocks](discover-value-stocks/SKILL.md) | An investment research orchestrator that connects independent subskills through a **skill graph**, managing dependencies, parallel execution, and validation gates. Coordinates growth-industry peer selection, forward FCF yield and CDS comparisons, Damodaran valuation, Korean report writing, review, publication, and subsequent assessment. |
| [travel-photo-to-illustration](travel-photo-to-illustration/SKILL.md) | Creates watercolor and colored-pencil illustrations (수채화·색연필화), optimizes WebP assets, and manages source hashes, edit history, caches, and batch work; delegates repository publication. |
| [publish-github-assets](publish-github-assets/SKILL.md) | Publishes approved derivative assets and project files through verified GitHub app or authenticated Git transport; validates commits and PRs, and reports blocked binary transfers without false success claims. |
| [chat-session-handoff](chat-session-handoff/SKILL.md) | Reconciles earlier handoff summaries with subsequent conversation, removes duplicates, and preserves decisions, work status, next actions, and a starter prompt for a new chat session (누적 대화 인계 요약). |

## Discover Value Stocks skill graph

The orchestrator reads the [graph definition](discover-value-stocks/assets/skill-graph.json) and [graph execution contract](discover-value-stocks/references/skill-graph.md), then assigns the corresponding skill to each node whose prerequisites and validation gates are satisfied. Every subskill retains its own `SKILL.md`, input/output contract, and acceptance criteria.

Industry research and assessment of historical recommendations can run in parallel. Report assembly, independent review, and actual delivery are distinct phases. No-selection and interrupted runs also retain the applicable assessment, reflection, and cache records. The graph defines task dependencies; actual agent execution uses the runtime's delegation tools.

| Subskill | Role |
| --- | --- |
| [cache-run](discover-value-stocks/subskills/cache-run/SKILL.md) | Persist and restore checkpoints; verify cache integrity and evidence freshness. |
| [plan-research](discover-value-stocks/subskills/plan-research/SKILL.md) | Restore publication history and define the research plan and stage-specific delegation contracts. |
| [research-industry](discover-value-stocks/subskills/research-industry/SKILL.md) | Test industry-growth hypotheses and competing explanations; establish a comparable peer pool. |
| [research-peers](discover-value-stocks/subskills/research-peers/SKILL.md) | Collect comparable forward cash-flow and CDS evidence and build the canonical dataset. |
| [select-candidate](discover-value-stocks/subskills/select-candidate/SKILL.md) | Narrow candidates through FCF yield and CDS comparisons, including explicit no-selection decisions. |
| [model-value](discover-value-stocks/subskills/model-value/SKILL.md) | Build operating models, Damodaran DCF valuations, and distress-risk comparisons. |
| [outline-report](discover-value-stocks/subskills/outline-report/SKILL.md) | Design an evidence-linked report outline and section dependency graph. |
| [write-section](discover-value-stocks/subskills/write-section/SKILL.md) | Write and revise Korean sections using approved evidence and models. |
| [review-report](discover-value-stocks/subskills/review-report/SKILL.md) | Independently verify facts, calculations, citations, logic, and Korean prose. |
| [publish-report](discover-value-stocks/subskills/publish-report/SKILL.md) | Assemble the report, verify actual delivery, and update publication history. |
| [assess-track-record](discover-value-stocks/subskills/assess-track-record/SKILL.md) | Evaluate earlier recommendations against their original Horizon, benchmarks, forecasts, and investment theses. |
| [reflect-research](discover-value-stocks/subskills/reflect-research/SKILL.md) | Conduct independent prepublication and run-closeout reflection; identify evidence-backed improvements. |
| [update-dashboard](discover-value-stocks/subskills/update-dashboard/SKILL.md) | Update the weekly investment dashboard from verified publication and assessment records. |
| [evolve-workflow](discover-value-stocks/subskills/evolve-workflow/SKILL.md) | Apply validated improvements to subsequent runs after reflection while preserving modular skills. |

### Data and calculation modules

- [Investment dashboard](discover-value-stocks/subskills/data/README.md): Show the latest 12 publication weeks, with at most one paragraph per week and separate TP, SL, and Horizon conditions.
- [Complete investment record](discover-value-stocks/subskills/data/cashflow-dashboard.json): Preserve recommendation and assessment history, including reasons for unavailable information.
- [distress-adjusted-dcf](discover-value-stocks/subskills/data/distress-adjusted-dcf/SKILL.md): DCF calculations incorporating default and distress risk, with regression tests.
- [Research policies](discover-value-stocks/references/), [execution and validation scripts](discover-value-stocks/scripts/), and [tests](discover-value-stocks/tests/) remain organized by responsibility.

### Validation and GitHub Actions configuration

The workflow file is stored at [discover-value-stocks/.github/workflows/dcf-tests.yml](discover-value-stocks/.github/workflows/dcf-tests.yml). **GitHub Actions does not run automatically from this location.** GitHub [searches only the repository-root `.github/workflows` directory](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows); enabling automatic execution again requires placing the file there. The workflow runs its test commands from `discover-value-stocks`.

To validate manually, start at the repository root:

```bash
cd discover-value-stocks
python scripts/skill_graph.py assets/skill-graph.json --package-root .
python -m unittest discover -s subskills/data/distress-adjusted-dcf/tests -v
python -m unittest discover -s tests -v
python scripts/render_dashboard.py subskills/data/cashflow-dashboard.json subskills/data/README.md --check
```

## Scoped work and deferred merge

- Batch related small changes into one focused PR; reuse that PR for follow-ups to the same unfinished change. Reuse existing artifacts and validation evidence only when their inputs, relevant dependencies, tool versions, and check scope remain applicable; record the revision checked.
- Before opening or updating a small-change PR, inspect the diff and run only checks needed for the affected files and behavior. Defer the complete test suite to an explicit user merge request. State checks run and deferred in the PR; never claim unperformed tests passed.
- Keep the PR open until the user explicitly requests its merge. Do not enable auto-merge. A request for a previous change does not authorize this merge.
- When merge is requested, refresh main and the PR head, resolve conflicts, run the complete repository test suite and required build/integration checks on the combined result, and merge only after they pass. Report unavailable checks or failures instead of merging an unverified result.
- Skip unrelated full audits, repeated status polling, and extra image generation. Use a bounded status check when needed; repeat only for new evidence or an explicit request. These instructions do not disable existing CI or bypass required checks.
- Interpret the following original user instruction subject to the deferred-merge rule above; “지정한 병합 단계” means stop at an open PR unless merge was explicitly requested:

> 이번 요청 범위만 처리하세요. 기존 결과와 검증 기록을 재사용하고 변경된 부분만 확인하세요. 관련 없는 전체 감사, 반복 상태 조회, 추가 이미지 생성은 생략하세요. 필요한 검증을 마치면 지정한 병합 단계까지 진행하고 결과를 간결하게 보고하세요.

## Efficient recurring work and modular skill graphs

- Separate deterministic discovery and eligibility checks from model reasoning: compare canonical URLs, publication dates, source digests and delivery ledgers in code; research and summarize only verified new or changed eligible material. No notification does not mean no model usage. Access failure is not evidence of no new material.
- Reuse unchanged reviewed Markdown, research artifacts and models after checking integrity, freshness and provenance. Never bypass delivery checkpoints, reconciliation, or publication approval. This policy does not itself change schedules or deploy a new monitoring system.
- Keep skills modular. Load only resources required by ready graph nodes, pass scoped artifacts to workers, and invalidate changed nodes plus their transitive dependents. Reuse unaffected accepted nodes after validity checks; retain mandatory independent review and release gates. Parallel agents reduce elapsed time, not necessarily credits.
