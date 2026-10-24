# Skills

투자 연구, 여행 사진 편집, 채팅 세션 인계에 사용하는 모듈형 스킬 저장소입니다. 각 스킬의 `SKILL.md`에 적용 범위와 실행 절차가 있습니다.

## 주요 스킬

| 스킬 | 역할 |
| --- | --- |
| [discover-value-stocks](discover-value-stocks/SKILL.md) | 독립된 하위 스킬을 **skill graph**로 연결하고 의존관계·병렬 실행·검증 조건을 관리하는 투자 연구 오케스트레이터입니다. 성장 산업의 비교기업 선정, 선행 FCF 수익률·CDS 비교, Damodaran 가치평가, 한국어 보고서 작성·검토·발행과 사후 평가를 조율합니다. |
| [travel-photo-to-illustration](travel-photo-to-illustration/SKILL.md) | 여행 사진을 수채화·색연필 일러스트로 변환하고, 모바일용 WebP 최적화와 기존 가이드 통합을 수행합니다. 이미지 캐시·편집 이력과 여러 사진의 병렬 처리를 관리합니다. |
| [chat-session-handoff](chat-session-handoff/SKILL.md) | 이전 인계 요약과 이후 대화를 누적·중복 제거하여, 결정 사항·작업 상태·남은 일과 새 채팅 세션에서 사용할 시작 프롬프트를 정리합니다. |

## Discover Value Stocks의 skill graph

오케스트레이터는 [graph 정의](discover-value-stocks/assets/skill-graph.json)와 [graph 실행 규약](discover-value-stocks/references/skill-graph.md)을 읽고, 선행 작업과 검증 조건이 충족된 노드에 해당 스킬을 할당합니다. 각 하위 스킬은 별도의 `SKILL.md`와 입출력·검증 기준을 유지합니다.

산업 조사와 과거 추천 평가는 병렬로 진행할 수 있습니다. 보고서 조립·독립 검토·실제 전달은 구분하며, 종목 미선정이나 작업 중단 시에도 해당 경로의 평가·회고·캐시 기록을 남깁니다. graph는 작업 의존관계를 정의하며, 실제 에이전트 실행에는 실행 환경의 위임 도구를 사용합니다.

| 하위 스킬 | 역할 |
| --- | --- |
| [cache-run](discover-value-stocks/subskills/cache-run/SKILL.md) | 체크포인트 저장·복구, 캐시 무결성과 근거의 최신성 확인 |
| [plan-research](discover-value-stocks/subskills/plan-research/SKILL.md) | 발행 이력 복구, 연구 계획과 단계별 위임 계약 수립 |
| [research-industry](discover-value-stocks/subskills/research-industry/SKILL.md) | 산업 성장 가설·반대 설명 검토와 비교기업군 구성 |
| [research-peers](discover-value-stocks/subskills/research-peers/SKILL.md) | 비교 가능한 선행 현금흐름·CDS 근거 수집과 공통 데이터셋 구축 |
| [select-candidate](discover-value-stocks/subskills/select-candidate/SKILL.md) | FCF 수익률·CDS 비교에 따른 후보 축소와 미선정 판단 |
| [model-value](discover-value-stocks/subskills/model-value/SKILL.md) | 영업 모델·Damodaran DCF·부실위험 비교 |
| [outline-report](discover-value-stocks/subskills/outline-report/SKILL.md) | 근거와 연결된 보고서 개요·섹션 의존관계 설계 |
| [write-section](discover-value-stocks/subskills/write-section/SKILL.md) | 승인된 근거·모델에 따른 한국어 섹션 집필·수정 |
| [review-report](discover-value-stocks/subskills/review-report/SKILL.md) | 사실·계산·인용·논리·한국어 문장의 독립 검토 |
| [publish-report](discover-value-stocks/subskills/publish-report/SKILL.md) | 보고서 조립, 실제 전달 확인과 발행 이력 갱신 |
| [assess-track-record](discover-value-stocks/subskills/assess-track-record/SKILL.md) | 기존 추천의 원래 Horizon·벤치마크·예측·투자 논거에 따른 평가 |
| [reflect-research](discover-value-stocks/subskills/reflect-research/SKILL.md) | 발행 전·실행 종료 시 독립 회고와 근거에 기반한 개선 과제 도출 |
| [update-dashboard](discover-value-stocks/subskills/update-dashboard/SKILL.md) | 검증된 발행·평가 기록으로 주간 투자 대시보드 갱신 |
| [evolve-workflow](discover-value-stocks/subskills/evolve-workflow/SKILL.md) | 회고 후 검증된 개선을 다음 실행에 적용하고 모듈 구성 유지 |

### 데이터와 계산 모듈

- [투자 대시보드](discover-value-stocks/subskills/data/README.md): 최근 12개 발행 주를 주당 최대 한 문단으로 표시하며, TP·SL·Horizon을 구분합니다.
- [전체 투자 기록](discover-value-stocks/subskills/data/cashflow-dashboard.json): 추천·평가 이력과 확인 불가능한 항목의 사유를 보존합니다.
- [distress-adjusted-dcf](discover-value-stocks/subskills/data/distress-adjusted-dcf/SKILL.md): 부도·부실위험을 반영하는 DCF 계산 모듈과 회귀 테스트입니다.
- [연구 정책](discover-value-stocks/references/), [실행·검증 스크립트](discover-value-stocks/scripts/), [테스트](discover-value-stocks/tests/)는 각 역할에 맞게 분리되어 있습니다.

### 검증과 GitHub Actions 설정

워크플로 파일은 [discover-value-stocks/.github/workflows/dcf-tests.yml](discover-value-stocks/.github/workflows/dcf-tests.yml)에 보관합니다. **현재 위치에서는 GitHub Actions가 자동 실행되지 않습니다.** GitHub는 [저장소 루트의 `.github/workflows`만 검색](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflows)하므로, 자동 실행을 다시 사용하려면 해당 파일을 루트 경로에 배치해야 합니다. 워크플로의 테스트 실행 기준 디렉터리는 `discover-value-stocks`입니다.

수동 검증은 저장소 루트에서 다음과 같이 실행합니다.

```bash
cd discover-value-stocks
python scripts/skill_graph.py assets/skill-graph.json --package-root .
python -m unittest discover -s subskills/data/distress-adjusted-dcf/tests -v
python -m unittest discover -s tests -v
python scripts/render_dashboard.py subskills/data/cashflow-dashboard.json subskills/data/README.md --check
```
