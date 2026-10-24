# 중앙아시아 가이드 통합

대상: `JinhaPark/codex`, https://jinhapark.github.io/codex/ . 아래 구조는2026-10-19 main `bd69f8b`에서 확인했다. 최신 코드와 적용 가능한 `AGENTS.md`를 우선하라. 이 스킬 생성 자체는 가이드 코드 변경을 뜻하지 않는다.

## 시작 시 읽을 파일

- `src/itinerary.json`, `src/illustrations.json`, `src/illustrations.js`
- `src/render-guide.js`와 실제 일정·도시·유적·종합 해설 렌더러, 이미지 CSS
- `public/illustrations/`, `public/sw.js`
- `docs/audit/destination-images.md`/`.json`, 관련 사진 배치 감사 기록
- `tests/illustrations.test.js`, `tests/service-worker.test.js`
- `scripts/verify-image-assets.py`, `scripts/verify-browser.cjs`, `package.json`

최신 기본 브랜치와 PR을 확인하라. 같은 그림이 다른 PR에서 진행 중이거나 병합되었으면 재작업하지 말라. 원본↔장소↔ID와 정정 이력을 우선하고 사진 작업 때문에 기존 도시 해설을 다시 쓰지 말라.

## Manifest와 배치

- 그림별 필수 필드: `id`, `original`, `style`, `placement`, 한글 `caption`·`alt`, `sourceWidth/Height`, 게시 `width/height`, `variants`.
- 변형별 필드: 실제 `width`, `height`, `bytes`, `quality`, `file`. 수치를 추정하지 말라. 작은 폭부터 정렬하고 게시 width/height를 실제 기준 변형의 크기로 기록하라.
- 생성 일러스트에는 실제 `generatedWidth/Height`를, 재편집에는 기존 `editInputWidth/Height`를 기록하라. 전시 패널은 `documentary-photo`로 유지하고 generated 크기를 발명하지 말라.
- 외부 출처에는 `sourceKind`, `sourceUrl`, 고정판 URL, `creator`, `license`, `licenseUrl`, `changes`를 기록하라. 필수 공개 크레딧을 렌더링하는지도 확인하라.
- ID·placement·원본 대응의 유일성을 유지하고 한 그림은 한 편집 위치에 배치하라. 승인된 교체는 ID/위치를 유지하며 자산·해시·감사 기록을 갱신하라. 중복 원본을 새 그림으로 세지 말라.
- `city:chapter:paragraph`는 실제 배열 인덱스, `city:chapter:detail`은 해당 장 설명 뒤 슬롯이다. `day:index:hotel/places/dinner/tip` 등은 최신 호출부에서 확인하라. 슬롯 충돌로 다른 그림을 덮어쓰지 말라.
- 원본과 기존 편집본의 **양축 이내** 변형을 유지하라. 기본480/800/1200 외에 작은 원본의370·574·590 같은 실제 제한 폭도 정상이다. 큰 생성본을 원본 업스케일의 허가로 해석하지 말라.
- 픽셀 검사는 원본 대비 비율 오차0.3% 미만을 요구한다. 현 상단 확장 예외 `outpaint-top-and-clean-foreground`는 IMG_9082/비비하눔 ID만 허용한다. 다른 사진에 복사하지 말라. 사용자가 특정 결과의 구도 변경(세로→가로 포함)을 명시적으로 지시하거나 사후 승인하면 해당 사진에 한정하여 비율 예외를 허용한다. 원본과 결과의 실제 크기, 구도 변경 내용, 지시·승인 근거를 기록하고 해당 asset ID에만 적용되는 검증을 구현하라. 다른 사진에는 기본 0.3% 검사를 그대로 적용하며 공통 검사를 통째로 완화하지 말라.
- 현 렌더러는800px가 있으면 기본 src로, 없으면 마지막 변형을 사용한다. `srcset`, `sizes`, 실제 width/height, lazy loading을 유지하고 HTML 하드코딩으로 우회하지 말라.

## 기록과 캐시

- 처리 캐시·수정 그래프·비동기 병렬 처리는 [cache-and-parallel.md](cache-and-parallel.md)를 따르라. `docs/image-lineage.json`은 manifest와 연결하는 영속 대응표이며 방문자 브라우저 캐시와 구분하라.

- `destination-images.json`/`.md`에서 해당 장소와 요청 번호만 갱신하라. 일부 전경만 있으면 `부분 확보`로 유지하고 방문 예정만으로 실제 방문을 확정하지 말라.
- manifest와 자산 파일의 정확한 대응을 유지하라. 교체 후 안 쓰는 옛 변형만 제거하고 다른 PR의 파일을 일괄 삭제하지 말라.
- 감사 기록에 실제 프롬프트·도구, 원본/생성/게시 크기, 프레이밍 변경, 품질·용량·해시, 출처와 검증 결과를 보존하라. 원본JPEG/HEIC·생성PNG·사적 경로를 공개하지 말라.
- 캐시 변경이 필요하면 최신 `public/sw.js`를 읽고 충돌 없는 다음 버전을 선택하라. 이 스킬에 특정 캐시 번호를 고정하지 말라. 서비스워커 검사와 브라우저 fixture 설명을 함께 갱신하라.

## 검증과 완료

1. `npm test`, `npm run build`, `python scripts/verify-image-assets.py`를 실행하라. 실패 원인을 고치고 검사를 제거하지 말라.
2. 브라우저 도구가 있으면 기존 검사 스크립트를 실행하라. 필요한 경우 설치된 Chromium을 `QA_CHROMIUM`으로 지정하라. 없는 도구를 실행했다고 기록하지 말라.
3. 375/390/430px에서 각 그림1회, 올바른 도시·장·캡션, 디코딩과 비율, alt, srcset, 넘침 없음, 한글 캡션 줄바꿈을 확인하고 실제 화면을 육안 검토하라.
4. 방문한 그림의 오프라인 재열람·캐시 전환·다른 앱 캐시 보존을 확인하라. 미방문 자산도 오프라인 보장된다고 주장하지 말라. 실제 iPhone Safari와 데스크톱 에뮬레이션을 구분하라.
5. 사용자 승인 범위와 저장소 지침에 따라 저장하라. 최종 이미지·해시·메타데이터가 준비되면 저장소 오케스트레이터가 [publish-github-assets](../../publish-github-assets/SKILL.md)를 호출하여 GitHub 전송·커밋·PR을 처리한다. 이 스킬은 게시 수단을 구현하지 않는다. 앱을 사용하면 실제 게시 객체와 참조를 검증하고, 전송 장애 시 게시 완료로 기록하지 말라. main 변경·병합·배포는 실제 승인 범위에서만 수행하라.
