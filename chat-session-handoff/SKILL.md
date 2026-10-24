---
name: chat-session-handoff
description: Create cumulative, deduplicated conversation handoffs for continuing long ChatGPT chats across sessions, including iPhone.
---

# Chat Session Handoff

## Purpose
Produce a compact, cumulative, copy-ready handoff that preserves decisions and work state across ChatGPT sessions. Combine previous handoff summaries with newer messages; do not merely summarize the latest session.

## When to use
- User asks for "인계 요약", "컨텍스트 정리", "chat-session-handoff", or continuation in a new chat.
- If a reliable context-usage indicator explicitly reports at least 90%, suggest preparing a handoff.
- **Limitation:** In ordinary ChatGPT chats, exact context-window utilization is not exposed. Do not claim to detect 90% automatically, run unattended, or trigger while the iPhone app is closed. User invocation is the reliable fallback.

## Procedure
1. Read the current chat and all available earlier handoff summaries, ordered chronologically.
2. If prior conversation details are missing and tools permit it, retrieve relevant prior context. Clearly distinguish recovered evidence from assumptions.
3. Merge previous summaries with subsequent changes. Prefer explicit newer corrections; retain important historical decisions when needed to explain the current state.
4. Deduplicate by meaning, not just wording. Preserve key project identifiers, repository links, file paths, PRs, commits, dates, numerical values, and user preferences when relevant.
5. Separate **verified completed**, **user-reported completed**, **in progress**, **planned**, **blocked**, and **unverified**. Never turn a plan or assistant promise into a completed action.
6. Record facts vs interpretations, source dates, and outstanding verification requirements. Do not infer private information or include credentials.
7. Compress aggressively without losing durable context. Put next actions and blockers ahead of low-priority historical details.
8. End with a standalone prompt the user can paste into a fresh ChatGPT or Work conversation.
9. Check that the new handoff supersedes prior summaries without dropping still-relevant decisions.

## Output format (Korean)
# 누적 대화 인계 요약
- 작성 기준일 및 정보 범위
- 사용자 선호 및 작업 규칙
- 프로젝트별 목적과 최신 상태
- 핵심 결정 및 중요한 수정 이력
- 저장소·브랜치·PR·커밋·문서 링크
- 검증 완료 / 사용자 보고 / 진행 중 / 미완료 / 불확실
- 주요 사실·수치 및 출처·기준일
- 우선순위별 다음 작업
- 새 세션 시작용 복사 가능한 프롬프트

## Quality checks
- Are all earlier handoffs and later changes reconciled?
- Are duplicates removed and newer corrections respected?
- Are completed actions backed by evidence?
- Are unknowns explicitly identified?
- Is the output sufficiently compact for a new session?

## Example invocation
"지금까지의 모든 인계 요약과 이후 대화를 합쳐 누적 인계 요약을 작성해 주세요. 중복 제거, 최신 수정 우선, 완료/미완료 구분, 다음 세션용 시작 프롬프트 포함."
