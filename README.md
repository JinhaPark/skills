# Skills

A modular skill repository for investment research, travel-photo editing, and chat-session handoffs. Each skill's `SKILL.md` defines its scope and execution procedure.

## Main skills

| Skill | Role |
| --- | --- |
| [discover-value-stocks](discover-value-stocks/SKILL.md) | An investment research orchestrator that connects independent subskills through a **skill graph**, managing dependencies, parallel execution, and validation gates. Coordinates growth-industry peer selection, forward FCF yield and CDS comparisons, Damodaran valuation, Korean report writing, review, publication, and subsequent assessment. |
| [travel-photo-to-illustration](travel-photo-to-illustration/SKILL.md) | Converts travel photos into watercolor and colored-pencil illustrations (수채화·색연필화), optimizes mobile WebP assets, and integrates them into existing guides. Manages image caches, edit history, and parallel processing of photo batches. |
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
